# Default imports
import argparse
import time
# Limited default imports
from contextlib import redirect_stdout
from random import randint, seed, choice
# 3rd party imports
with redirect_stdout(None):  # This stops pygame from printing the stupid import message
    import pygame
from pygame.locals import (
    K_SPACE, K_ESCAPE, K_RETURN, KEYDOWN, MOUSEBUTTONDOWN,
    K_BACKSLASH, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_r, K_z
)
# Local imports
import lang
import save
import level as lvl


parser = argparse.ArgumentParser(description="SokoPy - A Python-based Sokoban Clone")
parser.add_argument('-l', '--lang', help="Picks language (from lang.py)", type=str, default="EN-US")
parser.add_argument('-L', '--level', help="Loads directly into the specified level (This doesn't work yet!)",
                    type=str, default="")
args = parser.parse_args()

if args.lang not in lang.languages:
    raise ValueError(f"Language selected ({args.lang}) is not present")

save.init_save()


def load_file(file_name):
    # return os.path.join(os.path.dirname('./'), file_name)
    return file_name


# Initialization
pygame.init()
pygame.display.set_caption('SokoPy')
screen = pygame.display.set_mode([960, 960], pygame.RESIZABLE)
clock = pygame.time.Clock()


resources = {
    "font": {
        "Arial": pygame.font.SysFont("Arial", 36, bold=True),
        "BigArial": pygame.font.SysFont("Arial", 64, bold=True),
    },
    "sprite": {
        "shade":        pygame.image.load(load_file(f"data/sprites/shade.png")).convert_alpha(),
        "vignette":     pygame.image.load(load_file(f"data/sprites/vignette.png")).convert_alpha(),
        "gbrick":       pygame.image.load(load_file(f"data/sprites/grayFloor.png")).convert_alpha(),
        "ggrass":       pygame.image.load(load_file(f"data/sprites/grassFloor.png")).convert_alpha(),
        "rbrick":       pygame.image.load(load_file(f"data/sprites/redBrick.png")).convert_alpha(),
        "rbricksheet":  pygame.image.load(load_file(f"data/sprites/redBrickSheet.png")).convert_alpha(),
        "crate":        pygame.image.load(load_file(f"data/sprites/crateBrown.png")).convert_alpha(),
        "cratedark":    pygame.image.load(load_file(f"data/sprites/crateBrownOnTarget.png")).convert_alpha(),
        "target":       pygame.image.load(load_file(f"data/sprites/target.png")).convert_alpha(),
        # TODO: Spritesheet-ify the player please!
        "player":      [pygame.image.load(load_file(f"data/sprites/playerStill0.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerStill1.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerStill2.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerStill3.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerWalk00.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerWalk10.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerWalk20.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerWalk30.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerWalk01.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerWalk11.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerWalk21.png")).convert_alpha(),
                        pygame.image.load(load_file(f"data/sprites/playerWalk31.png")).convert_alpha()],
        "lvlbutton":    pygame.image.load(load_file(f"data/sprites/levelbutton.png")).convert_alpha(),
        "selbutton":    pygame.image.load(load_file(f"data/sprites/selectedbutton.png")).convert_alpha(),
        "lvlcheck":     pygame.image.load(load_file(f"data/sprites/checkbox.png")).convert_alpha(),
        "lvlchecked":   pygame.image.load(load_file(f"data/sprites/checkedbox.png")).convert_alpha(),
    },
    "sound": {

    },
}

resources["sprite"]["vignette"] = pygame.transform.scale(resources["sprite"]["vignette"], (960, 960))

tiles = ["rbrick", "crate", "target", "cratedark"]

debug_info = {
    "fps": 0
}
debug = False


def debug_show():
    debug_info["fps"] = int(clock.get_fps())
    debug_t = resources["font"]["Arial"].render(str(debug_info), True, pygame.Color("RED"))
    screen.blit(debug_t, (0, 0))


def draw_text(font, text, color, pos, center=False, shadow=False):
    text_main = resources["font"][font].render(text, True, color)
    if center:
        text_main_pos = text_main.get_rect(center=pos)
    else:
        text_main_pos = pos
    if shadow:
        text_shadow = resources["font"][font].render(text, True, (0, 0, 0))
        if center:
            text_shadow_pos = text_shadow.get_rect(center=(pos[0], pos[1]+3))
        else:
            text_shadow_pos = (pos[0]+3, pos[1]+3)
        screen.blit(text_shadow, text_shadow_pos)
    screen.blit(text_main, text_main_pos)
    return resources["font"][font].size(text)[0]


def calc_height(xmod, istall, modpos):
    if istall:
        return 608+((xmod-modpos)*64)
    else:
        return modpos+(xmod*64)


def calc_width(ymod, iswide, modpos):
    if iswide:
        return 448+((ymod-modpos)*64)
    else:
        return modpos+(ymod*64)


active = True
focused = True
winState = False
frame = 0
frameup = 0
resUpdated = False

# 0: menu, 1: game
mode = 0
newMode = -1
slides = {
    "display": [0, 0],
    "text": [0, 0],
    "character": [0, 0],
    "crate": [0, 0],
    "shake": 0
}
slideDiv = 0
charSlideMod = 1
setupDone = -2
menuIndex = 0
lvlIndex = 0

lvlpack_list = lvl.get_levelpacks()
menu_items = lvl.menu_packs(lvlpack_list)
filedir = "tutorial.lvl"
erase = ["Erase your save", "Are you sure?", "Save erased"]
erasing = 0
menu_items["set"] = "Settings"
menu_items["tut"] = lang.languages[args.lang][4]
menu_items["quit"] = lang.languages[args.lang][5]
menuLevel = "root"
newMenuLevel = None
kRepeatRate = 20
kHoldDiv = 1
kLast = None
kcd = 0
animStage = 0
animRate = 0
debug_info["lvl"] = "data/levels/tutorial.lvl"
map_content = lvl.decode_lvl("data/levels/tutorial.lvl")
currPos = [-1, -1]
last_state = [map_content, currPos]
settings = {
    "shake": {"title": "Screenshake", "value": 10, "range": [0, 20]},
    "erase": {"title": erase[erasing], "value": None, "range": [None, None]}
}
for setting in list(settings.keys()):
    if settings[setting]["value"] is None:
        save.add_savedata('Settings', [setting, None], categorytype="dict")
    elif setsave := save.check_savedata('Settings', setting):
        if setsave < settings[setting]["range"][0]:
            settings[setting]["value"] = settings[setting]["range"][0]
            save.add_savedata('Settings', [setting, settings[setting]["value"]], categorytype="dict")
        elif setsave > settings[setting]["range"][1]:
            settings[setting]["value"] = settings[setting]["range"][1]
            save.add_savedata('Settings', [setting, settings[setting]["value"]], categorytype="dict")
        else:
            settings[setting]["value"] = setsave
    else:
        save.add_savedata('Settings', [setting, settings[setting]["value"]], categorytype="dict")


def can_press(key):
    global kcd, kLast, kHoldDiv, kRepeatRate
    if kcd < 1 or kLast != key:
        if kLast == key:
            kHoldDiv = min(kHoldDiv + 0.2, 4 if mode == 0 else 2.5)
        else:
            kHoldDiv = 1 if mode == 0 else 1.5
        kLast = key
        kcd = round(kRepeatRate/kHoldDiv)
        return True
    return False


while active:
    if focused:
        dt = clock.tick(60)
        seed(time.time())
        settings["erase"]["title"] = erase[erasing]
        kcd -= 1
        for event in pygame.event.get():
            if event.type == pygame.ACTIVEEVENT:
                try:
                    event.state
                except AttributeError:
                    continue
                if event.state & 1 == 1:
                    focused = event.gain
            elif event.type == pygame.QUIT:
                active = False
            elif event.type == MOUSEBUTTONDOWN:
                continue
            if event.type == pygame.VIDEORESIZE:
                resources["sprite"]["vignette"] = \
                    pygame.image.load(load_file(f"data/sprites/vignette.png")).convert_alpha()
                resources["sprite"]["vignette"] = \
                    pygame.transform.scale(resources["sprite"]["vignette"], (event.w, event.h))
                resources["sprite"]["shade"] = \
                    pygame.image.load(load_file(f"data/sprites/shade.png")).convert_alpha()
                resources["sprite"]["shade"] = \
                    pygame.transform.scale(resources["sprite"]["shade"], (event.w, event.h))
                resUpdated = True
            elif event.type == KEYDOWN and newMode == -1:
                if event.key == K_BACKSLASH:
                    debug = not debug
                if mode == 0 and setupDone == 0:
                    if event.key == K_RETURN or event.key == K_SPACE:
                        if menuLevel == "root":
                            if menuIndex < len(menu_items)-3:
                                newMenuLevel = list(menu_items.keys())[menuIndex]
                            elif menuIndex == len(menu_items)-3:
                                newMenuLevel = "settings"
                            elif menuIndex == len(menu_items)-1:
                                active = False
                            elif menuIndex == len(menu_items)-2:
                                newMode = 1
                                filedir = "tutorial.lvl"
                        elif menuLevel == "settings":
                            if menuIndex == len(settings.keys())-1:
                                if erasing == 1:
                                    erasing = 2
                                    save.erase_save()
                                    slides["shake"] = 60
                                else:
                                    slides["shake"] = 30
                                    erasing = 1
                            else:
                                setting = list(settings.keys())[menuIndex]
                                if settings[setting]["value"] is not None:
                                    if settings[setting]["value"] >= settings[setting]["range"][1]:
                                        settings[setting]["value"] = settings[setting]["range"][0]
                                    else:
                                        settings[setting]["value"] += 1
                                    save.add_savedata('Settings', [setting, settings[setting]["value"]],
                                                      categorytype="dict")
                        else:
                            newMode = 1
                            filedir = menuLevel + '/' + list(lvlpack_list[menuLevel]['lvls'].values())[lvlIndex]
                    elif event.key == K_ESCAPE and menuLevel != "root":
                        newMenuLevel = "root"
                    elif event.key == K_r:
                        setupDone = -1
                elif mode == 1 and setupDone == 1:
                    if event.key == K_r:
                        newMode = 1
                    elif event.key == K_ESCAPE:
                        newMode = 0
                    elif event.key == K_z:
                        if len(map_content.history):
                            map_content.rewind()
                        else:
                            slides["shake"] = 5
        keys = pygame.key.get_pressed()
        if newMode == -1:
            if mode == 0:
                if keys[K_UP]:
                    if can_press(K_UP):
                        if menuLevel == "root":
                            erasing = 0
                            oldMenuIndex = menuIndex
                            menuIndex = menuIndex-1 if menuIndex > 0 else menuMax
                            slides["display"][0] += (oldMenuIndex-menuIndex)*50
                        elif menuLevel == "settings":
                            erasing = 0
                            oldMenuIndex = menuIndex
                            menuIndex = menuIndex + 1 if menuIndex < len(settings)-1 else 0
                            slides["display"][0] += (oldMenuIndex - menuIndex) * 50
                        else:
                            if lvlIndex >= lvls_can_fit:
                                lvlIndex -= lvls_can_fit
                                slides["display"][0] += 160
                elif keys[K_DOWN]:
                    if can_press(K_DOWN):
                        if menuLevel == "root":
                            erasing = 0
                            oldMenuIndex = menuIndex
                            menuIndex = menuIndex+1 if menuIndex < menuMax else 0
                            slides["display"][0] += (oldMenuIndex-menuIndex)*50
                        elif menuLevel == "settings":
                            erasing = 0
                            oldMenuIndex = menuIndex
                            menuIndex = menuIndex+1 if menuIndex < len(settings)-1 else 0
                            slides["display"][0] += (oldMenuIndex-menuIndex)*50
                        else:
                            if lvlIndex <= menuMax-lvls_can_fit:
                                lvlIndex += lvls_can_fit
                                slides["display"][0] -= 160
                elif keys[K_RIGHT]:
                    if can_press(K_RIGHT):
                        if menuLevel == "settings":
                            setting = list(settings.keys())[menuIndex]
                            if settings[setting]["value"] is not None:
                                if settings[setting]["value"] >= settings[setting]["range"][1]:
                                    settings[setting]["value"] = settings[setting]["range"][1]
                                else:
                                    settings[setting]["value"] += 1
                                save.add_savedata('Settings', [setting, settings[setting]["value"]],
                                                  categorytype="dict")
                        elif menuLevel != "root":
                            if lvlIndex < menuMax:
                                lvlIndex += 1
                                if lvlIndex % lvls_can_fit == 0:
                                    slides["display"][0] -= 160
                elif keys[K_LEFT]:
                    if can_press(K_LEFT):
                        if menuLevel == "settings":
                            setting = list(settings.keys())[menuIndex]
                            if settings[setting]["value"] is not None:
                                if settings[setting]["value"] <= settings[setting]["range"][0]:
                                    settings[setting]["value"] = settings[setting]["range"][0]
                                else:
                                    settings[setting]["value"] -= 1
                                save.add_savedata('Settings', [setting, settings[setting]["value"]],
                                                  categorytype="dict")
                        elif menuLevel != "root":
                            if lvlIndex > 0:
                                lvlIndex -= 1
                                if lvlIndex % lvls_can_fit == lvls_can_fit-1:
                                    slides["display"][0] += 160
                else:
                    kHoldDiv = 1
                    kLast = None
            if mode == 1:
                if keys[K_UP]:
                    if can_press(K_UP):
                        map_content.move_player([-1, 0], slides)
                elif keys[K_DOWN]:
                    if can_press(K_DOWN):
                        map_content.move_player([1, 0], slides)
                elif keys[K_LEFT]:
                    if can_press(K_LEFT):
                        map_content.move_player([0, -1], slides)
                elif keys[K_RIGHT]:
                    if can_press(K_RIGHT):
                        map_content.move_player([0, 1], slides)
                else:
                    kHoldDiv = 1
                    kLast = None
        if newMode != -1:
            if slides["display"][0] < 2000:
                slides["display"][0] += max(1+abs(slides["display"][0]/10), 1)
            else:
                mode = newMode
                newMode = -1
                setupDone = -1
                slides["display"][0] = -2000
        elif newMenuLevel:
            if slides["display"][0] < 20000:
                slides["display"][0] += max(1+abs(slides["display"][0]/10), 1)
            else:
                menuLevel = newMenuLevel
                newMenuLevel = None
                menuIndex = 0
                slides["display"][0] = -2000
        else:
            for vector in list(slides.keys()):
                if vector == "shake":
                    if slides["shake"]:
                        slides["shake"] -= 1
                        slides["display"][0] += randint(round(-(settings["shake"]["value"]*10) * (slides["shake"] / 10)),
                                                        round((settings["shake"]["value"]*10) * (slides["shake"] / 10)))
                        slides["display"][1] += randint(round(-(settings["shake"]["value"]*10) * (slides["shake"] / 10)),
                                                        round((settings["shake"]["value"]*10) * (slides["shake"] / 10)))
                    continue
                if slides[vector][0] < 0:
                    slides[vector][0] = min(slides[vector][0] - (slides[vector][0] / slideDiv), -0.04)
                elif slides[vector][0]:
                    slides[vector][0] = max(slides[vector][0] - (slides[vector][0] / slideDiv), 0.04)
                if slides[vector][1] < 0:
                    slides[vector][1] = min(slides[vector][1] - (slides[vector][1] / slideDiv), -0.04)
                elif slides[vector][1]:
                    slides[vector][1] = max(slides[vector][1] - (slides[vector][1] / slideDiv), 0.04)
                slides[vector][0] = round(slides[vector][0], 1)
                slides[vector][1] = round(slides[vector][1], 1)
    else:
        dt = clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.ACTIVEEVENT:
                try:
                    event.state
                except AttributeError:
                    continue
                if event.state & 1 == 1:
                    focused = event.gain
            elif event.type == pygame.QUIT:
                active = False
    screen.fill((10, 10, 32))
    if mode == 1:
        res = pygame.display.Info()
        res = [res.current_w, res.current_h]
        if setupDone != 1:
            last_state = []
            debug_info["lvl"] = f"data/levels/{filedir}"
            map_content = lvl.Level(f"data/levels/{filedir}", res)
            setupDone = 1
            charSlideMod = 100
            slides["character"][0] = 3000
            modPos = [0, 0]
            slideDiv = 5
            winState = False
            winText = True
            lastMoved = [-1, -1]
        else:
            if resUpdated:
                map_content.update_res(res)
                resUpdated = False
            if newMode != -1:
                charSlideMod = 1
            else:
                winState = map_content.check_win()
                if winState and winText:
                    slides["text"][1] = -2000
                    winText = False
                if 0 < slides["crate"][0] < 0.2 and 0 < slides["crate"][1] < 0.2:
                    lastMoved = [-1, -1]
                elif -0.2 < slides["crate"][0] < 0 and -0.2 < slides["crate"][1] < 0:
                    lastMoved = [-1, -1]
        map_content.render(res, slides, screen, resources, tiles, dt)
        if winState:
            if menuLevel != "root":
                levelTitle = menuLevel + '/' + list(lvlpack_list[menuLevel]['lvls'].values())[lvlIndex]
                save.add_savedata('Completed', [levelTitle])
            draw_text("BigArial", "You Won!", (192, 192, 255),
                      ((res[0]/2)-slides["text"][0], ((res[1]/2)-80)-slides["text"][1]), center=True, shadow=True)
            draw_text("Arial", "Press R to restart or", (192, 192, 255),
                      ((res[0]/2)-slides["text"][0], (res[1]/2)-slides["text"][1]), center=True, shadow=True)
            draw_text("Arial", "Press ESC to leave", (192, 192, 255),
                      ((res[0]/2)-slides["text"][0], ((res[1]/2)+50)-slides["text"][1]), center=True, shadow=True)
    elif mode == 0:
        if setupDone != 0:
            res = pygame.display.Info()
            res = [res.current_w, res.current_h]
            setupDone = 0
            newMenuLevel = None
            walking = False
            menuBackLevelPack = choice(list(menu_items.keys())[:-3])
            menuBackLevel = choice(list(lvlpack_list[menuBackLevelPack]['lvls'].values()))
            debug_info["lvl"] = f"data/levels/{menuBackLevelPack}/{menuBackLevel}"
            map_content = lvl.Level(f"data/levels/{menuBackLevelPack}/{menuBackLevel}", res)
            parallaxMulti = 2
            slideDiv = 7
        elif resUpdated:
            res = pygame.display.Info()
            res = [res.current_w, res.current_h]
            map_content.update_res(res)
            resUpdated = False
        if menuLevel == "root":
            lvlIndex = 0
            menuMax = len(menu_items)-1
            map_content.render(res, slides, screen, resources, tiles, dt, mod=menuIndex, parallax=3, player=False, modsize=50)
            screen.blit(resources["sprite"]["shade"], (0, 0))
            for i, item in enumerate(menu_items.values()):
                draw_text("Arial", item,
                          (192, 192, 255) if i == menuIndex else (128, 128, 196),
                          (50-slides["display"][1], 240+((50*(i-menuIndex))-slides["display"][0])), shadow=True)
            titleWidth = draw_text("BigArial", lang.languages[args.lang][0], (192, 192, 255),
                                   (20-slides["display"][1], 90+((50*(-menuIndex))-slides["display"][0])), shadow=True)
            screen.blit(resources["sprite"]["player"][2], (128-slides["display"][1], 90+((50*(-menuIndex))-slides["display"][0])))
            draw_text("Arial", lang.languages[args.lang][16], (128, 128, 196),
                      (45+titleWidth-slides["display"][1], 120+((50*(-menuIndex))-slides["display"][0])), shadow=True)
            draw_text("Arial", lang.languages[args.lang][2], (128, 128, 196),
                      (40-slides["display"][1], 150+((50*(-menuIndex))-slides["display"][0])), shadow=True)
        elif menuLevel == "settings":
            lvlIndex = 0
            menuMax = len(menu_items)-1
            map_content.render(res, slides, screen, resources, tiles, dt, mod=menuIndex, parallax=3, player=False, modsize=50)
            screen.blit(resources["sprite"]["shade"], (0, 0))
            for i, item in enumerate(settings.values()):
                draw_text("Arial", item["title"],
                          (192, 192, 255) if i == menuIndex else (128, 128, 196),
                          (50-slides["display"][1], 240+((50*(i-menuIndex))-slides["display"][0])), shadow=True)
                if item["value"] is not None:
                    draw_text("Arial", str(item["value"]),
                              (192, 192, 255) if i == menuIndex else (128, 128, 196),
                              (500-slides["display"][1], 240+((50*(i-menuIndex))-slides["display"][0])), shadow=True)
            titleWidth = draw_text("BigArial", lang.languages[args.lang][0], (192, 192, 255),
                                   (20-slides["display"][1], 90+((50*(-menuIndex))-slides["display"][0])), shadow=True)
            screen.blit(resources["sprite"]["player"][2], (128-slides["display"][1], 90+((50*(-menuIndex))-slides["display"][0])))
            draw_text("Arial", lang.languages[args.lang][16], (128, 128, 196),
                      (45+titleWidth-slides["display"][1], 120+((50*(-menuIndex))-slides["display"][0])), shadow=True)
            draw_text("Arial", lang.languages[args.lang][2], (128, 128, 196),
                      (40-slides["display"][1], 150+((50*(-menuIndex))-slides["display"][0])), shadow=True)
        else:
            titles = lvlpack_list[menuLevel]['title'].partition('(')
            levelList = list(lvlpack_list[menuLevel]['lvls'].keys())
            menuMax = len(levelList)-1
            lvlIndex = max(0, min(menuMax, lvlIndex))
            lvls_can_fit = int(res[0]/165)
            for i in range(len(levelList)):
                if (290-((lvlIndex//lvls_can_fit)*160)-slides["display"][0]+(160*((i-lvls_can_fit)//lvls_can_fit))) > res[0]:
                    continue
                if i == lvlIndex:
                    screen.blit(resources["sprite"]["selbutton"],
                                (15+(160*(i % lvls_can_fit))-slides["display"][1], 250-((lvlIndex//lvls_can_fit)*160)-slides["display"][0]+(160*(i//lvls_can_fit))))
                    draw_text("BigArial", str(i+1), (192, 192, 255),
                              (50+(160*(i % lvls_can_fit))-slides["display"][1],
                               290-((lvlIndex//lvls_can_fit)*160)-slides["display"][0]+(160*(i//lvls_can_fit))), shadow=True, center=True)
                else:
                    screen.blit(resources["sprite"]["lvlbutton"],
                                (15+(160*(i % lvls_can_fit))-slides["display"][1], 250-((lvlIndex// lvls_can_fit)*160)-slides["display"][0]+(160*(i// lvls_can_fit))))
                    draw_text("BigArial", str(i+1), (128, 128, 196),
                              (50+(160*(i % lvls_can_fit))-slides["display"][1],
                               290-((lvlIndex// lvls_can_fit)*160)-slides["display"][0]+(160*(i// lvls_can_fit))), shadow=True, center=True)
                if save.check_savedata('Completed', menuLevel + '/' + list(lvlpack_list[menuLevel]['lvls'].values())[i]):
                    screen.blit(resources["sprite"]["lvlchecked"],
                                (80 + (160 * (i % lvls_can_fit)) - slides["display"][1],
                                 300 - ((lvlIndex // lvls_can_fit) * 160) - slides["display"][0] + (160 * (i // lvls_can_fit))))
                else:
                    screen.blit(resources["sprite"]["lvlcheck"],
                                (80 + (160 * (i % lvls_can_fit)) - slides["display"][1],
                                 300 - ((lvlIndex // lvls_can_fit) * 160) - slides["display"][0] + (160 * (i // lvls_can_fit))))
            titleWidth = draw_text("BigArial", titles[0], (192, 192, 255),
                                   (20-slides["display"][1],
                                    90+((160*(-(lvlIndex // lvls_can_fit)))-slides["display"][0])), shadow=True)
            draw_text("Arial", titles[2][:-1], (128, 128, 196),
                      (35+titleWidth-slides["display"][1],
                       120+((160*(-(lvlIndex // lvls_can_fit)))-slides["display"][0])), shadow=True)
            draw_text("Arial", lvlpack_list[menuLevel]['desc'], (128, 128, 196),
                      (40-slides["display"][1],
                       150+((160*(-(lvlIndex // lvls_can_fit)))-slides["display"][0])), shadow=True)
    if debug:
        debug_show()
        #lineRes = pygame.display.Info()
        #for i in range(1, int(lineRes.current_h/64)):
        #    pygame.draw.line(screen, (255, 255, 255), (0, 64*i), (lineRes.current_w, 64*i))
        #for i in range(1, int(lineRes.current_w/64)):
        #    pygame.draw.line(screen, (255, 255, 255), (64*i, 0), (64*i, lineRes.current_h))
    screen.blit(resources["sprite"]["vignette"], (0, 0))
    pygame.display.flip()
pygame.quit()
