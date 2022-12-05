import os
import json


def commit_save(savedata: dict) -> None:
    for i in list(savedata.keys()):
        if isinstance((savedata[i]), list):
            savedata[i].sort()
    with open('save.json', 'w', encoding='utf-8') as f:
        json.dump(savedata, f, ensure_ascii=False, indent=4)
    return


def get_save() -> dict:
    with open('save.json') as json_file:
        return json.load(json_file)


def init_save() -> bool:
    if os.path.exists('save.json'):
        return True
    else:
        commit_save({"Completed": [], "Settings": {}})
        return False


def erase_save() -> None:
    commit_save({"Completed": [], "Settings": {}})
    return


def add_savedata(category: str, data: list, categorytype: str = "list") -> bool:
    savedata = get_save()
    if categorytype == "list":
        if data[0] not in savedata[category]:
            savedata[category] += [data[0]]
            commit_save(savedata)
            return True
    elif categorytype == "dict":
        savedata[category][data[0]] = data[1]
        commit_save(savedata)
        return True
    else:
        return False


def check_savedata(category: str, data: str) -> bool:
    savedata = get_save()
    if data in savedata[category]:
        if isinstance(savedata[category], list):
            return True
        elif isinstance(savedata[category], dict):
            return savedata[category][data]
    else:
        return False
