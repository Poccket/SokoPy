import os
import json


def commit_save(savedata: dict) -> None:
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
        commit_save({"Completed": []})
        return False


def erase_save() -> None:
    commit_save({"Completed": []})
    return


def add_savedata(levelname: str) -> bool:
    savedata = get_save()
    if levelname not in savedata['Completed']:
        savedata['Completed'] += [levelname]
        commit_save(savedata)
        return True
    else:
        return False


def check_savedata(levelname: str) -> bool:
    savedata = get_save()
    return levelname in savedata['Completed']
