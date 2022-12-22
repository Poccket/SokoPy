import sys


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
    "!": "0000",
    " ": "0010",  # Empty
    "@": "0011",  # Player
    "#": "0100",  # Block
    "$": "0101",  # Crate
    ".": "0110",  # Target
    "*": "0111",  # Crate on Target
    "+": "1000"   # Player on Target
}


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
    with open(filename + '.lvl', "w+b") as outfile:
        outfile.write(outdata)
    print("INFO: Wrote", len(outdata), "bytes to", filename + '.lvl')


def textlist_to_lvl(lvldata: list) -> bytes:
    """
    Converts a list (each item being a line) into level data (in binary)
    """
    lvl_binary = ""
    crate_count = 0
    target_count = 0
    for x in lvldata:
        for y in x:
            if y == "$":
                crate_count += 1
            if y == ".":
                target_count += 1
            if y == "*":
                crate_count += 1
                target_count += 1
            lvl_binary += Blocks[y]
        lvl_binary += "0000"
    if len(lvl_binary) % 8:
        lvl_binary += "0000"
    return (bitstring_to_bytes(lvl_binary), crate_count, target_count)


# TODO: Make it so this script produces one file that is a levelpack, metadata included if possible
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please give a file to convert\n\
               Like so: python3 converter.py example.txt")
        sys.exit()
    
    with open(sys.argv[1], "r") as f:
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
