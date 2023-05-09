import sys
import os
import json

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
# into the binary level format I made.


Blocks = {
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


Blocks2 = [
    "!", "!", " ", "@",
    "#", "$", ".", "*",
    "+"
]


class LevelSet:
    def __init__(self, filename: str):
        self.filename = filename
        self.level_offsets = []
        with open(filename, "rb") as f:
            if f.read(4) != b"SKBN":
                return -1
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
        # x = 0 ???
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
                        lvl_list[i] += [Blocks2[c]]
            output += [lvl_list]
        return output



def bytes_to_bitstring(b: bytes, n=None) -> str:
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


def write_lvl(filename: str, outdata: bytes) -> None:
    """
    Writes level data (in binary) to a file
    """
    with open('data/levels/' + filename + '.lvl', "w+b") as outfile:
        outfile.write(outdata)
    print("INFO: Wrote", len(outdata), "bytes to", filename + '.lvl')


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
                    lvl_binary += Blocks[last_block]
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
                print(block_count, format(block_count, '04b'), "|", format(block_count-3, '04b'))
                lvl_binary += "1101" + format(block_count-3, '04b') + Blocks[last_block]
                last_block = y
                block_count = 1


        lvl_binary += "0000"
    lvl_binary += "1111"
    if len(lvl_binary) % 8:
        lvl_binary += "0000"
    return lvl_binary, crate_count, target_count


def create_packed_levelset(title: str, desc: str, filename: str, levelname=()) -> None:
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
    write_lvl(title, bitstring_to_bytes(final_data_str))
    print("INFO: Done!")
    return


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


def create_unpacked_levelset(filename):
    with open(filename, "r") as f:
        data = f.readlines()

    started = False
    lvl_num = 1
    lvl = []

    for line in data:
        if line[0] == ";":
            if started:
                to_write = textlist_to_lvl(lvl)
                if to_write[1] != to_write[2]:
                    print(f"WARNING: Level may be incorrect!\n    Filename: {sys.argv[1]}, Level #: {lvl_num}\n",
                          f"   {to_write[1]} crates seen, but {to_write[2]} targets seen.\nPress ENTER to continue, CTRL+C to quit execution")
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
        to_write = textlist_to_lvl(lvl)
        write_lvl(str(lvl_num).zfill(2), to_write[0])
    print("INFO: Done!")


def create_text_levelset(filename):
    fileset = LevelSet(filename)
    outlvl = ""
    for i in range(0, fileset.length):
        filelvl = fileset.get_level(i)
        outlvl += f"; {i+1}\n\n"
        for l in filelvl:
            for c in l:
                print(c)
                outlvl += Blocks2[c]
            outlvl += "\n"
    with open(f"{filename[:filename.rfind('.')]}.txt", "w") as f:
        f.write(outlvl)
    print(f"INFO: Created text file {filename[:filename.rfind('.')]}.txt")


def update_levelset(textname, setname):
    fileset = LevelSet(setname)
    create_packed_levelset(fileset.title, fileset.description, textname)
    print(f"INFO: Finished updating of {setname}")


def recompress(filename):
    fileset = LevelSet(filename)
    create_text_levelset(filename)
    create_packed_levelset(fileset.title, fileset.description, f"{filename[:filename.rfind('.')]}.txt")
    os.remove(f"{filename[:filename.rfind('.')]}.txt")
    print(f"INFO: Removed text file {filename[:filename.rfind('.')]}.txt")
    print(f"INFO: Finished recompression of {filename}")


# TODO: Make it so this script produces one file that is a levelpack, metadata included if possible
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please give a file to convert\n\
               Like so: python3 convert.py create example.txt")
        sys.exit()

    if sys.argv[1] == "createunpacked":
        print(f"WARNING: This format is no longer supported!\n",
              f"   Press ENTER to continue, CTRL+C to quit execution")
        input()
        create_unpacked_levelset(sys.argv[2])
    elif sys.argv[1] == "create":
        create_packed_levelset(sys.argv[3], sys.argv[4], sys.argv[2])
    elif sys.argv[1] == "unpack":
        lvlset = LevelSet(sys.argv[2])
        print(f"    TITLE:{lvlset.title}\n     DESC:{lvlset.description}\n   LENGTH:{lvlset.length}\n  OFFSETS:{lvlset.level_offsets}")
    elif sys.argv[1] == "pack":
        pack_levelset(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "packj":
        pack_levelset(sys.argv[2])
    elif sys.argv[1] == "txt":
        create_text_levelset(sys.argv[2])
    elif sys.argv[1] == "recompress":
        recompress(sys.argv[2])
    elif sys.argv[1] == "update":
        update_levelset(sys.argv[3], sys.argv[2])
