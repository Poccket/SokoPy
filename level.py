import os
import json

# blocks:
# new line      , empty space  , walkable  , player
# wall          , movable crate, crate goal, crate on goal
# player on goal, undefined    , undefined , undefined
# undefined     , undefined    , undefined , undefined
visTable = ["\n", "  ", "::", "=)",
            "▓▒", "▓█", "╳╳", "▓█",
            "  ", "  ", "  ", "  ",
            "  ", "  ", "  ", "  "]
visHeight = 1
visWidth = 2
# index 0: canClip
#   1 = player can stand here
#   0 = player cannot stand here
# index 1: canMove
#   1 = player can push this
#   0 = player cannot push this
atrTable = ["00", "00", "10", "10",
            "00", "01", "10", "01",
            "10", "00", "00", "00",
            "00", "00", "00", "00",]

def decode_lvl(filename: str, offset: int = 4):
    with open(filename, mode='rb') as f:
        fContent = f.read()
    mapData = [[]]
    x = 0
    y = 0
    for index in range(len(fContent)):
        fByte = "{:08b}".format(fContent[index])
        if (nibble := int(fByte[:4], 2)) == 00:
            x  = 0
            y += 1
            mapData.append([])
        else:
            mapData[y].append(nibble)
        if (nibble := int(fByte[4:], 2)) == 00:
            x  = 0
            y += 1
            mapData.append([])
        else:
            mapData[y].append(nibble)
    return mapData

def get_levelpacks():
    levelpack_list = {}
    for dirpath, dirnames, files in os.walk(os.path.abspath(os.curdir + "/levels/")):
        if "metadata.json" in files:
            with open(dirpath + "/metadata.json", mode='r') as f:
                fContent = f.read()
            meta = json.loads(fContent)
            levelpack_list[os.path.basename(os.path.normpath(dirpath))] = meta['levelpack']
    return levelpack_list

#print(get_levelpacks())
