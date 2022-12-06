import os
import json


def commit_save(savedata: dict) -> None:
    """
    Writes passed savedata to file 'save.json' in working directory.
    """
    # Sort anything sort-able just for my sanity when debugging savefiles
    for i in list(savedata.keys()):
        if isinstance((savedata[i]), list):
            savedata[i].sort()
    with open('save.json', 'w', encoding='utf-8') as f:
        json.dump(savedata, f, ensure_ascii=False, indent=4)
    return


def get_save() -> dict:
    """
    Reads file 'save.json' in working directory to a dictionary,
    then returns the dictionary.
    """
    with open('save.json') as json_file:
        return json.load(json_file)


def init_save() -> bool:
    """
    Checks if 'save.json' exists in working directory,
    and if not, creates it with default settings.
    """
    if os.path.exists('save.json'):
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
