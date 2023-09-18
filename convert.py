import sys
import os
import json
from datetime import datetime

VERSION = "1.1"
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


# TODO: Reorganize!
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

# TODO: Combine LevelSet UnpackedSet
# Referenced in build.py and main.py
class LevelSet:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.level_offsets = []
        with open(filename, "rb") as f:
            if f.read(4) != b"SKBN":
                #return -1
                sys.exit()
            temp = b""
            return_count = 0
            offset = 0
            while True:
                byte = f.read(1)
                offset += 1
                if byte == b"\n":
                    return_count += 1
                    if return_count == 1:
                        self.title = temp.decode()
                    else:
                        self.description = temp.decode()
                        break
                    temp = b""
                else:
                    temp += byte
            self.length = int.from_bytes(f.read(1), 'big')
            offset += 1
            record_end = 65536
            while True:
                byte = f.read(2)
                offset += 2
                if offset > record_end:
                    break
                else:
                    self.level_offsets += [int.from_bytes(byte, 'big')]
                    if record_end == 65536:
                        record_end = self.level_offsets[0]
    def get_level(self, level: int) -> list:
        with open(self.filename, mode='rb') as f:
            f_content = f.read()
        map_data = [[]]
        y = 0
        repeat = False
        repeatNum = 0
        for index in range(self.level_offsets[level], len(f_content)):
            f_byte = "{:08b}".format(f_content[index])
            if (nibble := int(f_byte[:4], 2)) == 00:
                y += 1
                map_data.append([])
            elif repeat:
                if repeatNum == 0:
                    repeatNum = nibble+3
                else:
                    for i in range(0, repeatNum):
                        map_data[y].append(nibble)
                    repeat = False
                    repeatNum = 0
            elif nibble == 13:
                repeat = True
            elif nibble == 15:
                break
            else:
                map_data[y].append(nibble)
            if (nibble := int(f_byte[4:], 2)) == 00:
                y += 1
                map_data.append([])
            elif repeat:
                if repeatNum == 0:
                    repeatNum = nibble+3
                else:
                    for i in range(0, repeatNum):
                        map_data[y].append(nibble)
                    repeat = False
                    repeatNum = 0
            elif nibble == 13:
                repeat = True
            elif nibble == 15:
                break
            else:
                map_data[y].append(nibble)
        return map_data
    def get_levels_as_text(self) -> list:
        output = []
        for i in range(self.length):
            lvl_data = self.get_level(i)
            for l in lvl_data:
                lvl_list = []
                for i, r in enumerate(lvl_data):
                    lvl_list += [[]]
                    for c in r:
                        lvl_list[i] += [NUM_TO_BLOCKS[c]]
            output += [lvl_list]
        return output


class UnpackedSet:
    """
    This class represents a collection of metadata, and various states of\n
    level data.
    It stores an uncompressed version, a text version, a compressed version,\n
    and a binary version of the level data for this set.
    It can also create a text file or binary file for the levelset.
    """
    def __init__(self, title: str, desc: str, year = datetime.now().year,
                 author = "Unknown", length = 0, level_data=None, data_format=None) -> None:
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
        if data_format == "text":
            self.process_text()
        if data_format == "binary":
            self.process_binary()
        self.last_update = {
            "uncompressed": datetime.now() if data_format == "uncompressed" else 0,
            "compressed": datetime.now() if data_format == "compressed" else 0,
            "binary": datetime.now() if data_format == "binary" else 0,
            "text": datetime.now() if data_format == "text" else 0,
        }

    def __len__(self) -> int:
        if not self.meta["length"]:
            self.decompress_data()
            self.meta["length"] = len(self.level_data["uncompressed"])
        return self.meta["length"]

    def process_binary(self) -> None:
        """
        Processes a binary format of a levelset into the class, including the\n
        title, description, etc.
        This replaces all data in the class! Be warned.
        """
        if not self.level_data["binary"] in [None, []]:
            # Metadata retrieval
            print("INFO: Unzipping data...")
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
            print("INFO: Getting levels...")
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
            print("INFO: Processing text...")
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
            print("INFO: Decompressing levelset...")
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
            self.last_update["uncompressed"] = datetime.now()

    def compress_data(self) -> None:
        """
        Processes the uncompressed level data into a list of strings\n
        representing byte data (referred to as compressed level data)
        """
        # TODO: Clean up this code, the nesting is way too deep.
        # Legacy code! Touch this at your own peril.
        if (self.level_data["compressed"] in [None, []] or
            self.last_update["compressed"]<self.last_update["uncompressed"]):
            print("INFO: Compressing levelset...")
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
            self.last_update["compressed"] = datetime.now()

    def create_text(self):
        """
        Creates a text file representation of the uncompressed level data, for\n
        human readability.
        """
        print("INFO: Creating text...")
        self.decompress_data()
        self.level_data["text"] = ""
        for level_number, level in enumerate(self.level_data["uncompressed"]):
            self.level_data["text"] += f"; {level_number+1}\n"
            for line in level:
                self.level_data["text"] += line + "\n"

    def create_binary(self):
        """
        Combines metadata and compressed level data to create the binary\n
        representation of the levelset.
        """
        print("INFO: Compressing data...")
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

    def write_text(self, filename: str, output_folder="./") -> bool:
        """
        Creates a text file from the level data.
        """
        self.create_text()
        if os.path.isfile(filename + ".txt"):
            os.rename(filename + ".txt", filename + ".old.txt")
            print(f"Old version backed up! Renamed to {filename + '.lvl.old'}")
        with open(output_folder + filename + ".txt", "w") as outfile:
            outfile.write(self.level_data["text"])
        print(f"INFO: Created text file {filename[:filename.rfind('.')]}.txt")
        return True

    def write_binary(self, filename: str, output_folder="./") -> bool:
        """
        Creates a binary file from the level data.
        """
        self.create_binary()
        if os.path.isfile(filename + ".lvl"):
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
            if level_data[-1] == []:
                del level_data[-1]
            self.level_data["game"] += [level_data]
            level_data = [[]]
        return

# create_packed_levelset() pack_levelset() create_unpacked_levelset()
def write_lvl(filename: str, outdata: bytes, output_folder="levels/") -> None:
    """
    Writes level data (in binary) to a file
    """
    with open(output_folder + filename + '.lvl', "w+b") as outfile:
        outfile.write(outdata)
    print("INFO: Wrote", len(outdata), "bytes to", filename + '.lvl')

# create_packed_levelset() create_unpacked_levelset()
def textlist_to_lvlnew(lvldata: list) -> tuple:
    """
    Converts a list (each item being a line) into level data (in binary)
    """
    lvl_binary = ""
    crate_count = 0
    target_count = 0
    for x in lvldata:
        last_block = None
        block_count = 1
        for n, y in enumerate(x + " "):
            if n == 0:
                last_block = y
                continue
            if y == last_block and block_count < 18:
                block_count += 1
            elif block_count < 4:
                for b in range(0, block_count):
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
    return lvl_binary, crate_count, target_count

# Referenced in build.py
# update_levelset() recompress()
def create_packed_levelset(title: str, desc: str, filename: str) -> None:
    print(filename)
    with open(filename, "r") as f:
        data = f.readlines()
    master_record = []
    level_data = ""
    started = False
    total_offset = 0
    lvl_num = 1
    lvl = []
    for line in data:
        if line[0] == ";":
            if started:
                to_write = textlist_to_lvlnew(lvl)
                if to_write[1] != to_write[2]:
                    print(f"WARNING: Level may be incorrect!\n    Filename: {sys.argv[1]}, Level #: {lvl_num}\n",
                          f"   {to_write[1]} crates seen, but {to_write[2]} targets seen.\nPress ENTER to continue, CTRL+C to quit execution")
                    input()
                level_data += to_write[0]
                level_size = int(len(to_write[0])/8)
                print(f"INFO: Level {lvl_num} finished at {level_size} bytes")
                master_record += [total_offset]
                total_offset += level_size
                lvl_num += 1
            else:
                started = True
            lvl = []
        elif line.rstrip():
            lvl += [line.rstrip()]
    if lvl:
        to_write = textlist_to_lvlnew(lvl)
        if to_write[1] != to_write[2]:
            print(f"WARNING: Level may be incorrect!\n    Filename: {sys.argv[1]}, Level #: {lvl_num}\n",
                  f"   {to_write[1]} crates seen, but {to_write[2]} targets seen.\nPress ENTER to continue, CTRL+C to quit execution")
            input()
        level_data += to_write[0]
        level_size = int(len(to_write[0])/8)
        print(f"INFO: Level {lvl_num} finished at {level_size} bytes")
        master_record += [total_offset]

    final_data_str = bytes_to_bitstring(bytes("SKBN" + title + "\n" + desc + "\n", 'ascii')) + format(lvl_num, '08b')
    master_record_str = ""
    master_offset = int(len(final_data_str)/8) + (len(master_record)*2)
    for i in master_record:
        master_record_str += format(i + master_offset, '016b')
    final_data_str += master_record_str
    final_data_str += level_data
    filename = filename[:filename.index(".")]
    if os.path.isfile(filename + ".lvl"):
        print(f"Old version backed up! Renamed to {filename + '.lvl.old'}")
        os.rename(filename + ".lvl", filename + ".lvl.old")
    write_lvl(filename, bitstring_to_bytes(final_data_str))
    print("INFO: Done!")
    return

# Referenced in level.py
def unpack_levelset(filename: str) -> dict:
    output = {
        "title": "Title Not Found",
        "desc": "Desc Not Found",
        "length": 0,
        "offsets": []
    }
    with open(filename, "rb") as f:
        if f.read(4) != b"SKBN":
            return 0
        temp = b""
        return_count = 0
        offset = 0
        while True:
            byte = f.read(1)
            offset += 1
            if byte == b"\n":
                return_count += 1
                if return_count == 1:
                    output["title"] = temp.decode()
                else:
                    output["desc"] = temp.decode()
                    break
                temp = b""
            else:
                temp += byte
        output["length"] = int.from_bytes(f.read(1), 'big')
        offset += 1
        record_end = 65536
        while True:
            byte = f.read(2)
            offset += 2
            if offset > record_end:
                break
            else:
                output["offsets"] += [int.from_bytes(byte, 'big')]
                if record_end == 65536:
                    record_end = output["offsets"][0]
    return output

# Referenced in level.py
def pack_levelset(dirname, title=None, desc=None):
    if title == None:
        jsonf = os.path.join(dirname, 'metadata.json')
        if os.path.isfile(jsonf):
            with open(jsonf, mode='r') as f:
                f_content = f.read()
                meta = json.loads(f_content)
                title = meta['levelpack']['title']
                desc = meta['levelpack']['desc']
    master_record = []
    level_data = ""

    level_files = []
    for filename in os.listdir(dirname):
        f = os.path.join(dirname, filename)
        if os.path.isfile(f):
            if filename[-3:] == "lvl":
                level_files += [f]
    level_files.sort() # I don't trust the OS to sort.

    total_offset = 0
    lvl_num = 0
    for fn in level_files:
        with open(fn, 'rb') as f:
            fd = f.read()
            lvl_num += 1
            master_record += [total_offset]
            total_offset += len(fd)+1
            level_data += bytes_to_bitstring(fd) + "11110000"

    final_data_str = bytes_to_bitstring(bytes("SKBN" + title + "\n" + desc + "\n", 'ascii')) + format(lvl_num, '08b')
    master_record_str = ""
    master_offset = int(len(final_data_str)/8) + (len(master_record)*2)
    for i in master_record:
        master_record_str += format(i + master_offset, '016b')
    final_data_str += master_record_str
    final_data_str += level_data
    write_lvl(title, bitstring_to_bytes(final_data_str))
    print("INFO: Done!")
    return

# Not referenced, clear for removal.
def create_unpacked_levelset(filename):
    with open(filename, "r") as f:
        data = f.readlines()

    started = False
    lvl_num = 1
    lvl = []

    for line in data:
        if line[0] == ";":
            if started:
                to_write = textlist_to_lvlnew(lvl)
                if to_write[1] != to_write[2]:
                    print("WARNING: Level may be incorrect!\n",
                          f"    Filename: {sys.argv[1]}, Level #: {lvl_num}\n",
                          f"   {to_write[1]} crates seen, but {to_write[2]} targets seen.\n",
                          "Press ENTER to continue, CTRL+C to quit execution")
                    input()
                write_lvl(str(lvl_num).zfill(2), to_write[0])
                lvl_num += 1
                lvl = []
            else:
                started = True
                lvl = []
        elif line.rstrip():
            lvl += [line.rstrip()]
    if lvl:
        to_write = textlist_to_lvlnew(lvl)
        write_lvl(str(lvl_num).zfill(2), to_write[0])
    print("INFO: Done!")

# recompress()
def create_text_levelset(filename):
    fileset = LevelSet(filename)
    outlvl = ""
    for i in range(0, fileset.length):
        filelvl = fileset.get_level(i)
        outlvl += f"; {i+1}\n\n"
        for l in filelvl:
            for c in l:
                outlvl += NUM_TO_BLOCKS[c]
            outlvl += "\n"
    with open(f"{filename[:filename.rfind('.')]}.txt", "w") as file_content:
        file_content.write(outlvl)
    print(f"INFO: Created text file {filename[:filename.rfind('.')]}.txt")

# Not referenced, clear for removal.
def update_levelset(textname, setname):
    fileset = LevelSet(setname)
    create_packed_levelset(fileset.title, fileset.description, textname)
    print(f"INFO: Finished updating of {setname}")

# Not referenced, clear for removal.
def recompress(filename):
    fileset = LevelSet(filename)
    create_text_levelset(filename)
    create_packed_levelset(fileset.title,
                           fileset.description,
                           f"{filename[:filename.rfind('.')]}.txt")
    os.remove(f"{filename[:filename.rfind('.')]}.txt")
    print(f"INFO: Removed text file {filename[:filename.rfind('.')]}.txt")
    print(f"INFO: Finished recompression of {filename}")


# TODO: Make a nicer interface for the script.
if __name__ == "__main__":
    print("This tool is currently being reworked! Please download an older stable version.")
    sys.exit()
    HAS_EXECUTABLE = int(sys.argv[0][:6] == "python")
    if len(sys.argv) == 1+HAS_EXECUTABLE:
        print(f"SokoPy conversion script v{VERSION} by @Poccket")
    elif len(sys.argv) < 3+HAS_EXECUTABLE:
        print("Please give a file to convert\n\
               Like so: python3 convert.py recompress example.txt")
    else:
        if sys.argv[1] == "createunpacked":
            print("WARNING: This format is no longer supported!\n",
                "   Press ENTER to continue, CTRL+C to quit execution")
            input()
            create_unpacked_levelset(sys.argv[HAS_EXECUTABLE])
        elif sys.argv[1] == "create":
            if len(sys.argv) < 5:
                print("Creation requires a description and title!\n",
                    f"Like so: python3 convert.py create {sys.argv[2+HAS_EXECUTABLE]} 'My Title!' 'This is a compelling description!'")
            else:
                create_packed_levelset(sys.argv[3+HAS_EXECUTABLE],
                                       sys.argv[4+HAS_EXECUTABLE],
                                       sys.argv[2+HAS_EXECUTABLE])
        elif sys.argv[1] == "unpack":
            lvlset = LevelSet(sys.argv[HAS_EXECUTABLE])
            print(f"    TITLE:{lvlset.title}\n",
                  f"     DESC:{lvlset.description}\n",
                  f"   LENGTH:{lvlset.length}\n",
                  f"  OFFSETS:{lvlset.level_offsets}")
        elif sys.argv[1] == "pack":
            pack_levelset(sys.argv[HAS_EXECUTABLE],
                          sys.argv[1+HAS_EXECUTABLE],
                          sys.argv[2+HAS_EXECUTABLE])
        elif sys.argv[1] == "packj":
            pack_levelset(sys.argv[HAS_EXECUTABLE])
        elif sys.argv[1] == "txt":
            create_text_levelset(sys.argv[2+HAS_EXECUTABLE])
        elif sys.argv[1] == "recompress":
            recompress(sys.argv[2+HAS_EXECUTABLE])
        elif sys.argv[1] == "update":
            update_levelset(sys.argv[1+HAS_EXECUTABLE], sys.argv[HAS_EXECUTABLE])
