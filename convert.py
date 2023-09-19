import sys
import os
from datetime import datetime

VERSION = "2.0"
# This file can be used to convert sokoban levels in a format like below:
#    ; Level 1
#       ###
#      ## # ####
#     ##  ###  #
#    ## $      #
#    #   @$ #  #
#    ### $###  #
#      #  #..  #
#     ## ##.# ##
#     #      ##
#     #     ##
#     #######
# into a custom binary levelpack format.


BLOCKS_TO_NIBBLE = {
    "!": "0000",  # New line
    " ": "0010",  # Empty
    "@": "0011",  # Player
    "#": "0100",  # Block
    "$": "0101",  # Crate
    ".": "0110",  # Target
    "*": "0111",  # Crate on Target
    "+": "1000"   # Player on Target
    #     1101      Next nibble is number of times to repeat the nibble after.
    #     1111      End Of Level Data
}
NUM_TO_BLOCKS = [
    "!", "!", " ", "@",
    "#", "$", ".", "*",
    "+"
]


def bytes_to_bitstring(b: bytes, n=None) -> str:
    """
    Converts bytes into a string representation.
    """
    # https://stackoverflow.com/questions/60579197/python-bytes-to-bit-string
    s = ''.join(f'{x:08b}' for x in b) # Fucking Black Magic
    return s if n is None else s[:n + n // 8 + (0 if n % 8 else -1)]


def bitstring_to_bytes(s: str) -> bytes:
    """
    Converts a string representation of bytes into actual bytes
    """
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])


class LevelSet:
    """
    This class represents a collection of metadata, and various states of\n
    level data.
    It stores an uncompressed version, a text version, a compressed version,\n
    and a binary version of the level data for this set.
    It can also create a text file or binary file for the levelset.
    """
    def __init__(self, level_data=None, data_format=None, title="Unknown",
                 desc="Unknown", year = datetime.now().year,
                 author = "Unknown", length = 0) -> None:
        if level_data and not data_format:
            raise TypeError("A data_format must be designated if the level_data is defined.")
        self.meta = {
            "title": title,
            "description": desc,
            "year": year,
            "author": author,
            "length": length
        }
        self.level_offsets = []
        self.level_data = {
            "uncompressed": level_data if data_format == "uncompressed" else None,
            "compressed": level_data if data_format == "compressed" else None,
            "binary": level_data if data_format == "binary" else None,
            "text": level_data if data_format == "text" else None,
            "game": None
        }
        if data_format == "file":
            if level_data[-4:] == ".txt":
                with open(level_data, "r", encoding="utf-8") as file:
                    self.level_data["text"] = file.read().splitlines()
                    self.process_text()
            elif level_data[-4:] == ".lvl":
                with open(level_data, "rb") as file:
                    self.level_data["binary"] = file.read()
                    self.process_binary()
        elif data_format == "text":
            self.process_text()
        elif data_format == "binary":
            self.process_binary()
        current_time = datetime.utcnow().timestamp()
        self.last_update = {
            "uncompressed": current_time if data_format == "uncompressed" else 0,
            "compressed": current_time if data_format == "compressed" else 0,
            "binary": current_time if data_format == "binary" else 0,
            "text": current_time if data_format == "text" else 0,
        }
        self.create_game_data()

    def __len__(self) -> int:
        if not self.meta["length"]:
            self.decompress_data()
            self.meta["length"] = len(self.level_data["uncompressed"])
        return self.meta["length"]

    def update_title(self) -> None:
        """
        Retrieves year and author from outdated levelpacks
        """
        if "(" in self.meta["title"]:
            old_title = self.meta["title"]
            open_paren = old_title.index("(")
            self.meta["title"] = old_title[:open_paren].rstrip()
            dash = old_title.index("-")
            self.meta["year"] = int(old_title[open_paren+1:dash])
            closing_paren = old_title.index(")")
            self.meta["author"] = old_title[dash+1:closing_paren]

    def process_binary(self) -> None:
        """
        Processes a binary format of a levelset into the class, including the\n
        title, description, etc.
        This replaces all data in the class! Be warned.
        """
        if not self.level_data["binary"] in [None, []]:
            # Metadata retrieval
            #print("INFO: Unzipping data...")
            self.level_offsets = []
            if self.level_data["binary"][:4] != b"SKBN":
                raise ValueError("File is not a level file!")
            # Grab title and description
            temp = b""
            return_count = 0
            offset = 0
            # TODO: Grab author and year once implemented properly.
            for offset, byte in enumerate(self.level_data["binary"][4:]):
                byte = byte.to_bytes(1, sys.byteorder)
                if byte == b"\n":
                    return_count += 1
                    if return_count == 1:
                        self.meta["title"] = temp.decode()
                    else:
                        self.meta["description"] = temp.decode()
                        break
                    temp = b""
                else:
                    temp += byte
            # This is how many levels are in the set
            self.meta["length"] = self.level_data["binary"][offset+5]
            offset += 6
            # Now we read the master record to get the level offsets.
            record_end = 65536
            temp = b""
            for byte in self.level_data["binary"][offset:]:
                byte = byte.to_bytes(1, sys.byteorder)
                if temp:
                    temp += byte
                    self.level_offsets += [int.from_bytes(temp, 'big')]
                    if record_end == 65536:
                        record_end = self.level_offsets[0]
                    temp = b""
                else:
                    temp += byte
                offset += 1
                if offset > record_end:
                    break
            # Process the binary data back into compressed data.
            #print("INFO: Getting levels...")
            level_data = ''
            self.level_data["compressed"] = []
            for byte in self.level_data["binary"][record_end:]:
                byte = f"{byte:08b}"
                nibbles = [byte[:4], byte[4:]]
                for nibble in nibbles:
                    level_data += nibble
                    if nibble == "1111":
                        self.level_data["compressed"] += [level_data]
                        level_data = ''
                        continue

    def process_text(self) -> None:
        """
        Processes a text representation of level data (typically from a text\n
        file or user input) into a list of levels in text format (referred to\n
        as uncompressed level data)
        """
        if not self.level_data["text"] in [None, []]:
            #print("INFO: Processing text...")
            self.level_data["uncompressed"] = []
            level_data = []
            for line in self.level_data["text"]:
                if line:
                    if line[0] == ";":
                        if level_data:
                            self.level_data["uncompressed"] += [level_data]
                        level_data = []
                    elif line.rstrip():
                        level_data += [line.rstrip()]
            if level_data:
                self.level_data["uncompressed"] += [level_data]

    def decompress_data(self) -> None:
        """
        Processes the compressed level data into a list of levels in text\n
        format (referred to as uncompressed level data)
        """
        if (self.level_data["uncompressed"] in [None, []] or
            self.last_update["uncompressed"]<self.last_update["compressed"]):
            #print("INFO: Decompressing levelset...")
            self.level_data["uncompressed"] = []
            repeating = 0
            repeat_count = 0
            for level in self.level_data["compressed"]:
                text_level = [""]
                for offset in range(0, len(level), 4):
                    nibble = int(level[offset:offset+4], 2)
                    if repeating:
                        if repeating == 2:
                            repeat_count = nibble
                        else:
                            text_level[-1] += NUM_TO_BLOCKS[nibble] * (repeat_count+3)
                        repeating -= 1
                    else:
                        if nibble == 15:
                            if text_level[-1] == "":
                                del text_level[-1]
                            self.level_data["uncompressed"] += [text_level]
                        elif nibble == 0:
                            text_level += [""]
                        elif nibble == 13:
                            repeating = 2
                        else:
                            try:
                                text_level[-1] += NUM_TO_BLOCKS[nibble]
                            except IndexError:
                                print(nibble, "Oops!")
                                sys.exit()
            self.last_update["uncompressed"] = datetime.utcnow().timestamp()

    def compress_data(self) -> None:
        """
        Processes the uncompressed level data into a list of strings\n
        representing byte data (referred to as compressed level data)
        """
        # TODO: Clean up this code, the nesting is way too deep.
        # Legacy code! Touch this at your own peril.
        if (self.level_data["compressed"] in [None, []] or
            self.last_update["compressed"]<self.last_update["uncompressed"]):
            #print("INFO: Compressing levelset...")
            self.level_data["compressed"] = []
            for level_number, level in enumerate(self.level_data["uncompressed"]):
                lvl_binary = ""
                crate_count = 0
                target_count = 0
                for x in level:
                    last_block = None
                    block_count = 1
                    for n, y in enumerate(x + " "):
                        if n == 0:
                            last_block = y
                            continue
                        if y == last_block and block_count < 18:
                            block_count += 1
                        elif block_count < 4:
                            for _ in range(0, block_count):
                                if last_block == "$":
                                    crate_count += 1
                                if last_block in [".", "+"]:
                                    target_count += 1
                                if last_block == "*":
                                    crate_count += 1
                                    target_count += 1
                                lvl_binary += BLOCKS_TO_NIBBLE[last_block]
                            last_block = y
                            block_count = 1
                        else:
                            if block_count > 18:
                                print("Uh-oh!!")
                            if last_block == "$":
                                crate_count += block_count
                            if last_block in [".", "+"]:
                                target_count += block_count
                            if last_block == "*":
                                crate_count += block_count
                                target_count += block_count
                            lvl_binary += "1101" + format(block_count-3, '04b') + BLOCKS_TO_NIBBLE[last_block]
                            last_block = y
                            block_count = 1


                    lvl_binary += "0000"
                lvl_binary += "1111"
                if len(lvl_binary) % 8:
                    lvl_binary += "0000"
                if crate_count != target_count:
                    print("WARNING: Level may be incorrect!\n",
                        f"    Filename: {sys.argv[1]}, Level #: {level_number}\n",
                        f"   {crate_count} crates seen, but {target_count} targets seen.\n",
                        "Press ENTER to continue, CTRL+C to quit execution")
                    input()
                print(f"INFO: Level {level_number} finished at {len(lvl_binary)/8} bytes")
                self.level_data["compressed"] += [lvl_binary]
            self.last_update["compressed"] = datetime.utcnow().timestamp()

    def create_text(self) -> None:
        """
        Creates a text file representation of the uncompressed level data, for\n
        human readability.
        """
        #print("INFO: Creating text...")
        self.decompress_data()
        self.level_data["text"] = ""
        for level_number, level in enumerate(self.level_data["uncompressed"]):
            self.level_data["text"] += f"; {level_number+1}\n"
            for line in level:
                self.level_data["text"] += line + "\n"

    def create_binary(self) -> None:
        """
        Combines metadata and compressed level data to create the binary\n
        representation of the levelset.
        """
        #print("INFO: Compressing data...")
        self.compress_data()
        master_record = []
        level_data = ""
        total_offset = 0
        for level in self.level_data["compressed"]:
            level_data += level
            level_size = int(len(level)/8)
            master_record += [total_offset]
            total_offset += level_size
        #meta_data = f"2KBN{self.title}\n{self.desc}\n{self.year}\n{self.author}\n"
        meta_data = f"SKBN{self.meta['title']} ({self.meta['year']} - {self.meta['author']})\n{self.meta['description']}\n"
        bitstring = bytes_to_bitstring(bytes(meta_data, 'ascii')) + format(len(self.level_data["compressed"]), '08b')
        master_record_str = ""
        master_offset = int(len(bitstring)/8) + (len(master_record)*2)
        for i in master_record:
            master_record_str += format(i + master_offset, '016b')
        bitstring += master_record_str
        bitstring += level_data
        self.level_data["binary"] = bitstring_to_bytes(bitstring)
        if len(self.level_data["binary"]) < 4:
            raise Exception("Something went wrong! File size is abnormally small.")
        print(f"INFO: Finished compressing at {len(self.level_data['binary'])} bytes")

    def write_text(self, filename: str, output_folder="./", overwrite_policy=0) -> bool:
        """
        Creates a text file from the level data.
        """
        self.create_text()
        if os.path.isfile(filename + ".txt"):
            if overwrite_policy == 0:
                raise OSError("File already exists!")
            elif overwrite_policy == 1:
                os.rename(filename + ".txt", filename + ".old.txt")
                print(f"Old version backed up! Renamed to {filename + '.lvl.old'}")
        with open(output_folder + filename + ".txt", "w") as outfile:
            outfile.write(self.level_data["text"])
        print(f"INFO: Created text file {filename[:filename.index('.')]}.txt")
        return True

    def write_binary(self, filename: str, output_folder="./", overwrite_policy=0) -> bool:
        """
        Creates a binary file from the level data.
        """
        self.create_binary()
        if os.path.isfile(filename + ".lvl"):
            if overwrite_policy == 0:
                raise OSError("File already exists!")
            elif overwrite_policy == 1:
                os.rename(filename + ".lvl", filename + ".old.lvl")
                print(f"Old version backed up! Renamed to {filename + '.old.lvl'}")
        with open(output_folder + filename + '.lvl', "w+b") as outfile:
            outfile.write(self.level_data["binary"])
        print("INFO: Wrote", len(self.level_data["binary"]), "bytes to", filename + '.lvl')
        return True

    def create_game_data(self) -> None:
        """
        Converts uncompressed data into the format used by the game engine.
        """
        self.decompress_data()
        self.level_data["game"] = []
        level_data = [[]]
        for level in self.level_data["uncompressed"]:
            for line in level:
                for char in line:
                    if char == "\n":
                        continue
                    level_data[-1] += [int(BLOCKS_TO_NIBBLE[char], 2)]
                level_data += [[]]
            self.level_data["game"] += [level_data]
            level_data = [[]]
        return

# TODO: Make a nicer interface for the script.
if __name__ == "__main__":
    import argparse
    print(f"SokoPy conversion script v{VERSION} by @Poccket")
    parser = argparse.ArgumentParser(
        prog='convert.py',
        epilog="See '<command> --help' to read about a specific sub-command."
    )
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("filename", help="source file")

    subparsers = parser.add_subparsers(dest='act', help='sub-commands')
    base_parser.add_argument('-f', '--force', action='store_true', help="force overwriting")
    base_parser.add_argument('-v', '--verbose', action='store_true')

    A_parser = subparsers.add_parser('compile', help='compiles text', parents=[base_parser])
    A_parser.add_argument('-t', '--title', required=True, help="title of levelset, required")
    A_parser.add_argument('-d', '--desc', required=False, help="description of levelset, optional")
    A_parser.add_argument('-y', '--year', required=False, help="year of release, optional")
    A_parser.add_argument('-a', '--author', required=False, help="author of levelset, optional")
    A_parser.add_argument('-o', '--output', required=False)

    B_parser = subparsers.add_parser('decompile', help='decompiles binary', parents=[base_parser])
    B_parser.add_argument('-o', '--output', required=False)
    args = parser.parse_args()
    if args.act == "compile":
        tempLevelSet = LevelSet(args.filename, "file")
        tempLevelSet.meta["title"] = args.title
        tempLevelSet.meta["description"] = args.desc if args.desc else "No description."
        tempLevelSet.meta["year"] = args.year if args.year else datetime.now().year
        tempLevelSet.meta["author"] = args.author if args.author else "Unknown Author"
        tempLevelSet.write_binary(args.filename[:args.filename.index(".")])
    elif args.act == "decompile":
        tempLevelSet = LevelSet(args.filename, "file")
        tempLevelSet.write_text(args.filename[:args.filename.index(".")])