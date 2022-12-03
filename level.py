import os
import json

# blocks:
# new line      , empty space  , walkable  , player
# wall          , movable crate, crate goal, crate on goal
# player on goal, undefined    , undefined , undefined
# undefined     , undefined    , undefined , undefined
visTable = ["\n", "  ", "  ", "=)",
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
            "00", "00", "00", "00", ]


def decode_lvl(filename: str):  # , offset: int = 4): <-- What did this do?
    with open(filename, mode='rb') as f:
        f_content = f.read()
    map_data = [[]]
    # x = 0 ???
    y = 0
    for index in range(len(f_content)):
        f_byte = "{:08b}".format(f_content[index])
        if (nibble := int(f_byte[:4], 2)) == 00:
            y += 1
            map_data.append([])
        else:
            map_data[y].append(nibble)
        if (nibble := int(f_byte[4:], 2)) == 00:
            y += 1
            map_data.append([])
        else:
            map_data[y].append(nibble)
    return map_data


def get_levelpacks():
    levelpack_list = {}
    for dirpath, dirnames, files in os.walk(os.path.abspath(os.curdir + "/data/levels/")):
        if "metadata.json" in files:
            with open(dirpath + "/metadata.json", mode='r') as f:
                f_content = f.read()
            meta = json.loads(f_content)
            levelpack_list[os.path.basename(os.path.normpath(dirpath))] = meta['levelpack']
    return levelpack_list


def menu_packs(lvlpack_list):
    titles = {}
    for i in lvlpack_list:
        titles[i] = lvlpack_list[i]["title"]
    titles = {k: v for k, v in sorted(titles.items(), key=lambda item: item[1])}
    return titles
