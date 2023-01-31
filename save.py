import os
import json
import lzma


savefile = "sokopy.save"


def commit_save(savedata: dict) -> None:
    """
    Writes passed savedata to the savefile in working directory.
    """
    # Sort anything sort-able just for my sanity when debugging savefiles
    for i in list(savedata.keys()):
        if isinstance((savedata[i]), list):
            savedata[i].sort()
    json_vers = json.dumps(savedata, ensure_ascii=False, indent=4)
    with lzma.open(savefile, 'wb') as f:
        f.write(json_vers.encode())
    return


def get_save() -> dict:
    """
    Reads the savefile in working directory to a dictionary,
    then returns the dictionary.
    """
    with lzma.open(savefile, 'rb') as f:
        return json.loads(f.read().decode())


def init_save() -> bool:
    """
    Checks if savefile exists in working directory,
    and if not, creates it with default settings.
    """
    if os.path.exists(savefile):
        return True
    else:
        commit_save({"Completed": [], "Settings": {}})
        return False


def erase_save() -> None:
    """
    Rewrites the save with default settings.
    """
    commit_save({"Completed": [], "Settings": {}})
    return


def add_savedata(category: str, data: list, categorytype: str = "list") -> bool:
    """
    Adds variable $data to the key of $category in the savedata.
    """
    savedata = get_save()                       # We need the savedata so we don't overwrite anything
    if categorytype == "list":                  # If we're dealing with a list,
        if data[0] not in savedata[category]:   # >  We can simply check if the given data exists, and if it doesn't:
            savedata[category] += [data[0]]     # >  >  Add it to the list in our savedata variable
            commit_save(savedata)               # >  >  Write our new savedata to the system
            return True                         # >  >  And exit out, happy and free!
    elif categorytype == "dict":                # If we have a dictionary,
        savedata[category][data[0]] = data[1]   # >  It doesn't matter if the data exists, we just need to set the value
        commit_save(savedata)                   # >  Write the new savedata to the system
        return True                             # >  And exit.
    else:                                       # If it's neither a list nor dictionary, something's gone wrong!
        raise ValueError("Save data additions must be in a list or dictionary.")


def check_savedata(category: str, data: str) -> bool:
    """
    Checks if $data exists in $category of the savedata
    """
    savedata = get_save()
    if data in savedata[category]:
        if isinstance(savedata[category], list):
            return True
        elif isinstance(savedata[category], dict):
            return savedata[category][data]
    else:
        return False
