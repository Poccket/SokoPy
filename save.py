import os
import json
import lzma


def commit_save(savedata: dict, username) -> None:
    """
    Writes passed savedata to the savefile in working directory.
    """
    # Sort anything sort-able just for my sanity when debugging savefiles
    username = username.lower()
    for i in list(savedata.keys()):
        if isinstance((savedata[i]), list):
            savedata[i].sort()
    json_vers = json.dumps(savedata)
    with lzma.open("data/" + username + '.save', 'wb') as f:
        f.write(json_vers.encode())
    return


def get_save(username) -> dict:
    """
    Reads the savefile in working directory to a dictionary,
    then returns the dictionary.
    """
    username = username.lower()
    with lzma.open("data/" + username + '.save', 'rb') as f:
        return json.loads(f.read().decode())


def list_saves() -> list:
    saves = []
    dir_contents = os.listdir("data")
    for item in dir_contents:
        if item[-5:] == ".save":
            saves += [item[:-5]]
    saves.sort()
    return saves


def init_save(username) -> list:
    """
    Checks if savefile exists in working directory,
    and if not, creates it with default settings.
    """
    if username:
        username = username.lower()
        if os.path.exists("data/" + username + '.save'):
            return []
        else:
            commit_save({"Completed": [], "Settings": {}}, username)
            return []
    else:
        saves = list_saves()
        if saves:
            return saves
        else:
            commit_save({"Completed": [], "Settings": {}}, 'User')
            return ['User']


def rewrite_save(username) -> None:
    """
    Rewrites the save with default settings.
    """
    username = username.lower()
    commit_save({"Completed": [], "Settings": {}}, username)
    return


def erase_save(username) -> None:
    """
    Rewrites the save with default settings.
    """
    username = username.lower()
    os.remove("data/" + username + '.save')
    return


def add_savedata(category: str, data: list, username, categorytype: str = "list") -> bool:
    """
    Adds variable $data to the key of $category in the savedata.
    """
    username = username.lower()
    savedata = get_save(username)               # We need the savedata so we don't overwrite anything
    if categorytype == "list":                  # If we're dealing with a list,
        if data[0] not in savedata[category]:   # >  We can simply check if the given data exists, and if it doesn't:
            savedata[category] += [data[0]]     # >  >  Add it to the list in our savedata variable
            commit_save(savedata, username)     # >  >  Write our new savedata to the system
            return True                         # >  >  And exit out, happy and free!
    elif categorytype == "dict":                # If we have a dictionary,
        savedata[category][data[0]] = data[1]   # >  It doesn't matter if the data exists, we just need to set the value
        commit_save(savedata, username)         # >  Write the new savedata to the system
        return True                             # >  And exit.
    else:                                       # If it's neither a list nor dictionary, something's gone wrong!
        raise ValueError("Save data additions must be in a list or dictionary.")


def check_savedata(category: str, data: str, username) -> bool:
    """
    Checks if $data exists in $category of the savedata
    """
    username = username.lower()
    savedata = get_save(username)
    if data in savedata[category]:
        if isinstance(savedata[category], list):
            return True
        elif isinstance(savedata[category], dict):
            return savedata[category][data]
    else:
        return False


def decompress_save(username) -> None:
    username = username.lower()
    if os.path.exists(savedata):
        with open(username + ".json", 'wt') as f:
            json.dump(get_save(), f, ensure_ascii=False, indent=4)
    else:
        print("No compressed save file to decompress.\nMaybe try playing the game?")


def compress_save(username) -> None:
    username = username.lower()
    if os.path.exists(username + ".json"):
        with open(username + ".json", 'rt') as f:
            commit_save(json.load(f), username)
            jsonSize = os.path.getsize("data/" + username + ".json")
            lzmaSize = os.path.getsize("data/" + username + ".save")
            print(f"Compressed {jsonSize} to {lzmaSize}, saving {round((1-(lzmaSize/jsonSize))*100)}% of the space!")
    else:
        print("No decompressed save file to compress")
