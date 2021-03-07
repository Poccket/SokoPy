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


Blocks = {
    "!": "0000",
    " ": "0010",
    "@": "0011",
    "#": "0100",
    "$": "0101",
    ".": "0110",
    "*": "0111",
    "+": "1000"
}

if len(sys.argv) < 2:
    print("Please give a file to convert\n\
           Like so: python3 converter.py example.txt")
    sys.exit()

with open(sys.argv[1], "r") as f:
    data = f.readlines()

started = False
lvl_num = 1
lvl = []
lvl_binary = ""

for line in data:
    if line[0] == ";":
        if started:
            for x in lvl:
                for y in x:
                    lvl_binary += Blocks[y]
                lvl_binary += "0000"
            if len(lvl_binary) % 8:
                lvl_binary += "0000"
            to_write = bitstring_to_bytes(lvl_binary)
            filename = str(lvl_num).zfill(2) + ".lvl"
            with open(filename, "w+b") as out:
                out.write(to_write)
            print("Wrote", len(to_write), "bytes to", filename)
            lvl_num += 1
            lvl = []
            lvl_binary = ""
        else:
            started = True
            lvl = []
            lvl_binary = ""
    elif line.rstrip():
        lvl += [line.rstrip()]
if lvl:
    for x in lvl:
        for y in x:
            lvl_binary += Blocks[y]
        lvl_binary += "0000"
    if len(lvl_binary) % 8:
        lvl_binary += "0000"
    to_write = bitstring_to_bytes(lvl_binary)
    filename = str(lvl_num).zfill(2) + ".lvl"
    with open(filename, "w+b") as out:
        out.write(to_write)
    print("Wrote", len(to_write), "bytes to", filename)

print("Done!")
