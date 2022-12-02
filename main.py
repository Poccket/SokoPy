# Imports
import pygame
import os
import argparse
import lang
import level as lvl
import json
from random import randint, seed, choice
from math import floor
import time
from copy import deepcopy
from pygame.locals import (
    K_SPACE,
    K_ESCAPE,
    K_RETURN,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    K_BACKSLASH,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_r,
    K_z
)

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


parser = argparse.ArgumentParser(description="SokoPy - A Python-based Sokoban Clone")
parser.add_argument('-l', '--lang', help="Picks language (from lang.py)", type=str, default="EN-US")
parser.add_argument('-v', '--verbose', help="Uses more verbose language in the log for debugging",
                    action='store_true')
parser.add_argument('-m', '--menusize', help="The amount of items to be displayed at once on a menu",
                    type=int, default=15)
parser.add_argument('-L', '--level', help="Loads directly into the specified level",
                    type=str, default="")
args = parser.parse_args()


def commit_save(savedata):
    with open('save.json', 'w', encoding='utf-8') as f:
        json.dump(savedata, f, ensure_ascii=False, indent=4)


def get_save():
    with open('save.json') as json_file:
        return json.load(json_file)


if os.path.exists('save.json'):
    saveData = get_save()
else:
    saveData = {"Completed": []}
    commit_save(saveData)


def load_file(file_name):
    #return os.path.join(os.path.dirname('./'), file_name)
    return file_name


# Initialization
pygame.init()
pygame.display.set_caption('SokoPy')
_sm = 2
screen = pygame.display.set_mode([640*_sm, 480*_sm])
clock = pygame.time.Clock()

spriteSize = "x64"

resources = {
    "font": {
        "Arial": pygame.font.SysFont("Arial", 18*_sm, bold=True),
        "BigArial": pygame.font.SysFont("Arial", 32*_sm, bold=True),
        "Andy": pygame.font.Font(load_file(f"data/andy.ttf"), 48*_sm)
    },
    "sprite": {
        "shade":        pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/shade.png")).convert_alpha(),
        "vignette":     pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/vignette.png")).convert_alpha(),
        "gbrick":       pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/grayFloor.png")).convert_alpha(),
        "bbrick":       pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/grayFloorBad.png")).convert_alpha(),
        "rbrick":       pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/redBrick.png")).convert_alpha(),
        "rbricksheet":       pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/redBrickSheet.png")).convert_alpha(),
        "crate":        pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/crateBrown.png")).convert_alpha(),
        "cratedark":    pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/crateBrownOnTarget.png")).convert_alpha(),
        "target":       pygame.image.load(
                            load_file(f"data/sprites/{spriteSize}/target.png")).convert_alpha(),
        "player":       [pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerStill0.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerStill1.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerStill2.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerStill3.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerWalk00.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerWalk10.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerWalk20.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerWalk30.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerWalk01.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerWalk11.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerWalk21.png")).convert_alpha(),
                         pygame.image.load(
                             load_file(f"data/sprites/{spriteSize}/playerWalk31.png")).convert_alpha()],
        "lvlbutton":     pygame.image.load(
                             load_file(f"data/sprites/levelbutton.png")).convert_alpha(),
        "selbutton":     pygame.image.load(
                             load_file(f"data/sprites/selectedbutton.png")).convert_alpha(),
        "lvlcheck":      pygame.image.load(
                             load_file(f"data/sprites/checkbox.png")).convert_alpha(),
        "lvlchecked":    pygame.image.load(
                             load_file(f"data/sprites/checkedbox.png")).convert_alpha(),
    },
    "sound": {

    },
}

tiles = ["rbrick", "crate", "target", "cratedark"]

debug_info = {
    "fps": None
}
debug = True


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
paused = False
winState = False
frame = 0
frameup = 0

# 0: menu, 1: game
mode = 0
newMode = -1
slideOffset = [0, 0]
slideDiv = 0
textSlide = [0, 0]
charSlide = [0, 0]
charSlideMod = 1
setupDone = 1
menuIndex = 0
lvlIndex = 0
screenShake = 0
vignette = True

lvlpack_list = lvl.get_levelpacks()
menu_items = lvl.menu_packs(lvlpack_list)
filedir = ""
erase = ["Erase your save", "Are you sure?", "Save erased"]
erasing = 0
menu_items["shake"] = erase[erasing]
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
map_content = lvl.decode_lvl("data/levels/tutorial.lvl")
currPos = [-1, -1]
last_state = [map_content, currPos]


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
    if not paused:
        dt = clock.tick(60)
        if animRate > 100:
            animRate = 0
            animStage = 0 if animStage == 2 else animStage+1
        else:
            animRate += dt
        menu_items["shake"] = erase[erasing]
        if screenShake:
            screenShake -= 1
            slideOffset[0] += randint(round(-100*(screenShake/10)), round(100*(screenShake/10)))
            slideOffset[1] += randint(round(-100*(screenShake/10)), round(100*(screenShake/10)))
        kcd -= 1
        for event in pygame.event.get():
            if event.type == pygame.ACTIVEEVENT:
                try:
                    event.state
                except AttributeError:
                    continue
                if event.state & 1 == 1:
                    paused = not event.gain
            elif event.type == pygame.QUIT:
                active = False
            elif event.type == MOUSEBUTTONDOWN:
                continue
            elif event.type == KEYDOWN and newMode == -1:
                if event.key == K_BACKSLASH:
                    vignette = not vignette
                if mode == 0 and setupDone == 0:
                    if event.key == K_RETURN or event.key == K_SPACE:
                        if menuLevel == "root":
                            if menuIndex < len(menu_items)-3:
                                newMenuLevel = list(menu_items.keys())[menuIndex]
                            elif menuIndex == len(menu_items)-3:
                                if erasing == 1:
                                    erasing = 2
                                    saveData = {"Completed": []}
                                    commit_save(saveData)
                                    screenShake = 60
                                else:
                                    screenShake = 30
                                    erasing = 1
                            elif menuIndex == len(menu_items)-1:
                                active = False
                            elif menuIndex == len(menu_items)-2:
                                newMode = 1
                                filedir = "tutorial.lvl"
                        else:
                            newMode = 1
                            filedir = menuLevel + '/' + list(lvlpack_list[menuLevel]['lvls'].values())[lvlIndex]
                    elif event.key == K_ESCAPE:
                        newMenuLevel = "root"
                elif mode == 1 and setupDone == 1:
                    if event.key == K_r:
                        newMode = 1
                    elif event.key == K_ESCAPE:
                        newMode = 0
                    elif event.key == K_z:
                        if len(last_state):
                            map_content = last_state[-1][0]
                            currPos = last_state[-1][1]
                            currDir = last_state[-1][2]
                            last_state.pop(-1)
                        else:
                            screenShake = 5
        keys = pygame.key.get_pressed()
        if newMode == -1:
            if mode == 0:
                if keys[K_UP]:
                    if can_press(K_UP):
                        if menuLevel == "root":
                            erasing = 0
                            oldMenuIndex = menuIndex
                            menuIndex = menuIndex-1 if menuIndex > 0 else menuMax
                            slideOffset[0] += (oldMenuIndex-menuIndex)*50
                        else:
                            if lvlIndex >= 8:
                                lvlIndex -= 8
                                slideOffset[0] += 160
                elif keys[K_DOWN]:
                    if can_press(K_DOWN):
                        if menuLevel == "root":
                            erasing = 0
                            oldMenuIndex = menuIndex
                            menuIndex = menuIndex+1 if menuIndex < menuMax else 0
                            slideOffset[0] += (oldMenuIndex-menuIndex)*50
                        else:
                            if lvlIndex <= menuMax-8:
                                lvlIndex += 8
                                slideOffset[0] -= 160
                elif keys[K_RIGHT]:
                    if can_press(K_RIGHT):
                        if menuLevel != "root":
                            if lvlIndex < menuMax:
                                lvlIndex += 1
                                if lvlIndex % 8 == 0:
                                    slideOffset[0] -= 160
                elif keys[K_LEFT]:
                    if can_press(K_LEFT):
                        if menuLevel != "root":
                            if lvlIndex > 0:
                                lvlIndex -= 1
                                if lvlIndex % 8 == 7:
                                    slideOffset[0] += 160
                else:
                    kHoldDiv = 1
                    kLast = None
            if mode == 1:
                if keys[K_UP]:
                    if can_press(K_UP):
                        lastDir = currDir
                        currDir = 0
                        if lvl.atrTable[map_content[currPos[0]-1][currPos[1]]][0] == "1":
                            last_state += [[deepcopy(map_content), deepcopy(currPos), lastDir]]
                            currPos[0] -= 1
                            if mapTall:
                                slideOffset[0] += 64
                            else:
                                charSlide[0] -= 64
                        elif lvl.atrTable[map_content[currPos[0]-1][currPos[1]]][1] == "1" and not winState:
                            if lvl.atrTable[map_content[currPos[0]-2][currPos[1]]][0] == "1":
                                last_state += [[deepcopy(map_content), deepcopy(currPos), lastDir]]
                                if map_content[currPos[0]-1][currPos[1]] == 5:
                                    map_content[currPos[0]-2][currPos[1]] = 5 if \
                                        map_content[currPos[0]-2][currPos[1]] == 2 else 7
                                    map_content[currPos[0]-1][currPos[1]] = 2
                                if map_content[currPos[0]-1][currPos[1]] == 7:
                                    map_content[currPos[0]-2][currPos[1]] = 5 if \
                                        map_content[currPos[0]-2][currPos[1]] == 2 else 7
                                    map_content[currPos[0]-1][currPos[1]] = 6
                                lastMoved = [currPos[0]-2, currPos[1]]
                                crateSlide[0] -= 64
                                currPos[0] -= 1
                                if mapTall:
                                    slideOffset[0] += 64
                                else:
                                    charSlide[0] -= 64
                            else:
                                screenShake = 3
                        else:
                            screenShake = 3
                elif keys[K_DOWN]:
                    if can_press(K_DOWN):
                        lastDir = currDir
                        currDir = 2
                        if lvl.atrTable[map_content[currPos[0]+1][currPos[1]]][0] == "1":
                            last_state += [[deepcopy(map_content), deepcopy(currPos), lastDir]]
                            currPos[0] += 1
                            if mapTall:
                                slideOffset[0] -= 64
                            else:
                                charSlide[0] += 64
                        elif lvl.atrTable[map_content[currPos[0]+1][currPos[1]]][1] == "1" and not winState:
                            if lvl.atrTable[map_content[currPos[0]+2][currPos[1]]][0] == "1":
                                last_state += [[deepcopy(map_content), deepcopy(currPos), lastDir]]
                                if map_content[currPos[0]+1][currPos[1]] == 5:
                                    map_content[currPos[0]+2][currPos[1]] = 5 if \
                                        map_content[currPos[0]+2][currPos[1]] == 2 else 7
                                    map_content[currPos[0]+1][currPos[1]] = 2
                                if map_content[currPos[0]+1][currPos[1]] == 7:
                                    map_content[currPos[0]+2][currPos[1]] = 5 if \
                                        map_content[currPos[0]+2][currPos[1]] == 2 else 7
                                    map_content[currPos[0]+1][currPos[1]] = 6
                                lastMoved = [currPos[0]+2, currPos[1]]
                                crateSlide[0] += 64
                                currPos[0] += 1
                                if mapTall:
                                    slideOffset[0] -= 64
                                else:
                                    charSlide[0] += 64
                            else:
                                screenShake = 3
                        else:
                            screenShake = 3
                elif keys[K_LEFT]:
                    if can_press(K_LEFT):
                        lastDir = currDir
                        currDir = 3
                        if lvl.atrTable[map_content[currPos[0]][currPos[1]-1]][0] == "1":
                            last_state += [[deepcopy(map_content), deepcopy(currPos), lastDir]]
                            currPos[1] -= 1
                            if mapWide:
                                slideOffset[1] += 64
                            else:
                                charSlide[1] -= 64
                        elif lvl.atrTable[map_content[currPos[0]][currPos[1]-1]][1] == "1" and not winState:
                            if lvl.atrTable[map_content[currPos[0]][currPos[1]-2]][0] == "1":
                                last_state += [[deepcopy(map_content), deepcopy(currPos), lastDir]]
                                if map_content[currPos[0]][currPos[1]-1] == 5:
                                    map_content[currPos[0]][currPos[1]-2] = 5 if \
                                        map_content[currPos[0]][currPos[1]-2] == 2 else 7
                                    map_content[currPos[0]][currPos[1]-1] = 2
                                if map_content[currPos[0]][currPos[1]-1] == 7:
                                    map_content[currPos[0]][currPos[1]-2] = 5 if \
                                        map_content[currPos[0]][currPos[1]-2] == 2 else 7
                                    map_content[currPos[0]][currPos[1]-1] = 6
                                lastMoved = [currPos[0], currPos[1]-2]
                                crateSlide[1] -= 64
                                currPos[1] -= 1
                                if mapWide:
                                    slideOffset[1] += 64
                                else:
                                    charSlide[1] -= 64
                            else:
                                screenShake = 3
                        else:
                            screenShake = 3
                elif keys[K_RIGHT]:
                    if can_press(K_RIGHT):
                        lastDir = currDir
                        currDir = 1
                        if lvl.atrTable[map_content[currPos[0]][currPos[1]+1]][0] == "1":
                            last_state += [[deepcopy(map_content), deepcopy(currPos), lastDir]]
                            currPos[1] += 1
                            if mapWide:
                                slideOffset[1] -= 64
                            else:
                                charSlide[1] += 64
                        elif lvl.atrTable[map_content[currPos[0]][currPos[1]+1]][1] == "1" and not winState:
                            if lvl.atrTable[map_content[currPos[0]][currPos[1]+2]][0] == "1":
                                last_state += [[deepcopy(map_content), deepcopy(currPos), lastDir]]
                                if map_content[currPos[0]][currPos[1]+1] == 5:
                                    map_content[currPos[0]][currPos[1]+2] = 5 if \
                                        map_content[currPos[0]][currPos[1]+2] == 2 else 7
                                    map_content[currPos[0]][currPos[1]+1] = 2
                                if map_content[currPos[0]][currPos[1]+1] == 7:
                                    map_content[currPos[0]][currPos[1]+2] = 5 if \
                                        map_content[currPos[0]][currPos[1]+2] == 2 else 7
                                    map_content[currPos[0]][currPos[1]+1] = 6
                                lastMoved = [currPos[0], currPos[1]+2]
                                crateSlide[1] += 64
                                currPos[1] += 1
                                if mapWide:
                                    slideOffset[1] -= 64
                                else:
                                    charSlide[1] += 64
                            else:
                                screenShake = 3
                        else:
                            screenShake = 3
                else:
                    kHoldDiv = 1
                    kLast = None
        if newMode != -1:
            if slideOffset[0] < 2000:
                slideOffset[0] += max(1+abs(slideOffset[0]/10), 1)
            else:
                mode = newMode
                newMode = -1
                setupDone = -1
                slideOffset[0] = -2000
        elif newMenuLevel:
            if slideOffset[0] < 20000:
                slideOffset[0] += max(1+abs(slideOffset[0]/10), 1)
            else:
                menuLevel = newMenuLevel
                newMenuLevel = None
                menuIndex = 0
                slideOffset[0] = -2000
        else:
            if slideOffset[0] < 0:
                slideOffset[0] = min(slideOffset[0] - (slideOffset[0] / slideDiv), -0.04)
            elif slideOffset[0]:
                slideOffset[0] = max(slideOffset[0] - (slideOffset[0] / slideDiv), 0.04)
            if slideOffset[1] < 0:
                slideOffset[1] = min(slideOffset[1] - (slideOffset[1] / slideDiv), -0.04)
            elif slideOffset[1]:
                slideOffset[1] = max(slideOffset[1] - (slideOffset[1] / slideDiv), 0.04)
        slideOffset[0] = round(slideOffset[0], 1)
        slideOffset[1] = round(slideOffset[1], 1)
    else:
        dt = clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.ACTIVEEVENT:
                try:
                    event.state
                except AttributeError:
                    continue
                if event.state & 1 == 1:
                    paused = not event.gain
            elif event.type == pygame.QUIT:
                active = False
    screen.fill((10, 10, 32))
    if mode == 1:
        if setupDone != 1:
            last_state = []
            map_content = lvl.decode_lvl("data/levels/" + filedir)
            for x, row in enumerate(map_content):
                for y, col in enumerate(row):
                    if col == 3:
                        currPos = [x, y]
                        map_content[x][y] = 2
                        currDir = 2
                        break
                    elif col == 8:
                        currPos = [x, y]
                        map_content[x][y] = 6
                        currDir = 2
                        break
            mapHeight = len(map_content)-1
            mapWidth = max([len(i) for i in map_content])
            mapTall = mapHeight > 15
            mapWide = mapWidth > 18
            top = 480 - ((mapHeight/2)*64)
            left = 640 - ((mapWidth/2)*64)
            setupDone = 1
            charSlideMod = 100
            charSlide[0] = 3000
            crateSlide = [-1, -1]
            modPos = [0, 0]
            slideDiv = 5
            winState = False
            textSlide[1] = -2000
            lastMoved = [-1, -1]
        else:
            if newMode != -1:
                charSlideMod = 1
            else:
                for x in map_content:
                    winState = True
                    for y in x:
                        if y == 5:
                            winState = False
                            break
                    if not winState:
                        break
                if charSlide[0] < 0:
                    charSlide[0] = min(charSlide[0]-(charSlide[0]/slideDiv), -0.04)
                else:
                    charSlide[0] = max(charSlide[0]-(charSlide[0]/slideDiv), 0.04)
                if charSlide[1] < 0:
                    charSlide[1] = min(charSlide[1]-(charSlide[1]/slideDiv), -0.04)
                else:
                    charSlide[1] = max(charSlide[1]-(charSlide[1]/slideDiv), 0.04)
                if crateSlide[0] < 0:
                    crateSlide[0] = min(crateSlide[0]-(crateSlide[0]/(slideDiv/2)), -0.04)
                else:
                    crateSlide[0] = max(crateSlide[0]-(crateSlide[0]/(slideDiv/2)), 0.04)
                if crateSlide[1] < 0:
                    crateSlide[1] = min(crateSlide[1]-(crateSlide[1]/(slideDiv/2)), -0.04)
                else:
                    crateSlide[1] = max(crateSlide[1]-(crateSlide[1]/(slideDiv/2)), 0.04)
                crateSlide = [round(crateSlide[0], 1), round(crateSlide[1], 1)]
                if 0 < crateSlide[0] < 0.2 and 0 < crateSlide[1] < 0.2:
                    lastMoved = [-1, -1]
                elif -0.2 < crateSlide[0] < 0 and -0.2 < crateSlide[1] < 0:
                    lastMoved = [-1, -1]
                if winState:
                    if textSlide[0] < 0:
                        textSlide[0] = min(textSlide[0]-(textSlide[0]/10), -0.04)
                    elif textSlide[0]:
                        textSlide[0] = max(textSlide[0]-(textSlide[0]/10), 0.04)
                    if textSlide[1] < 0:
                        textSlide[1] = min(textSlide[1]-(textSlide[1]/10), -0.04)
                    elif textSlide[1]:
                        textSlide[1] = max(textSlide[1]-(textSlide[1]/10), 0.04)
        modPos[0] = currPos[0] if mapTall else top
        modPos[1] = currPos[1] if mapWide else left
        for x in range(currPos[0]-8, currPos[0]+9) if mapTall else range(-8, mapHeight+8):
            for y in range(currPos[1]-11, currPos[1]+11) if mapWide else range(-8, mapWidth+8):
                drawFloor = False
                seed(sum(map_content[0]) + sum(map_content[-1]) + x + y)
                if -1 <= x <= mapHeight:
                    if -1 <= y <= mapWidth:
                        drawFloor = True
                    else:
                        if y < 0:
                            drawFloor = randint(0, abs(y)) < 1
                        elif y > len(map_content[x]):
                            drawFloor = randint(0, abs(y-len(map_content[x]))) < 1
                else:
                    if 0 <= y <= mapWidth+1:
                        if x < 0:
                            drawFloor = randint(0, abs(x)) < 1
                        elif x > mapHeight+1:
                            drawFloor = randint(0, abs(x-mapHeight)) < 1
                if drawFloor:
                    screen.blit(resources["sprite"]["gbrick"], (-64 + calc_height(y, mapWide, modPos[1]) - slideOffset[1],
                                                                -64 + calc_width(x, mapTall, modPos[0]) - slideOffset[0]))
        for x, row in enumerate(map_content):
            if mapTall and (x < currPos[0]-8 or x > currPos[0]+8):
                continue
            for y, col in enumerate(row):
                if mapWide and (y < currPos[1]-11 or y > currPos[1]+11):
                    continue
                if 4 <= col <= 7:
                    if [x, y] == lastMoved:
                        if col == 7:
                            screen.blit(resources["sprite"]["target"],
                                        (calc_height(y, mapWide, modPos[1]) - slideOffset[1],
                                         calc_width(x, mapTall, modPos[0]) - slideOffset[0]))
                        screen.blit(resources["sprite"][tiles[col - 4]],
                                    (calc_height(y, mapWide, modPos[1]) - slideOffset[1] - crateSlide[1],
                                     calc_width(x, mapTall, modPos[0]) - slideOffset[0] - crateSlide[0]))
                    elif col == 4 and vignette:
                        neighborNum = 0
                        if x > 0 and y < len(map_content[x - 1]):
                            neighborNum += int(map_content[x - 1][y] == 4)
                        if y > 0:
                            neighborNum += int(map_content[x][y - 1] == 4) * 2
                        if y < len(map_content[x]) - 1:
                            neighborNum += int(map_content[x][y + 1] == 4) * 4
                        if x < len(map_content) and y < len(map_content[x + 1]):
                            neighborNum += int(map_content[x + 1][y] == 4) * 8
                        screen.blit(resources["sprite"]["rbricksheet"],
                                    (calc_height(y, mapWide, modPos[1]) - slideOffset[1],
                                     calc_width(x, mapTall, modPos[0]) - slideOffset[0]),
                                    area=pygame.Rect((64 * (neighborNum % 4), 64 * floor(neighborNum / 4)), (64, 64)))

                    else:
                        screen.blit(resources["sprite"][tiles[col - 4]],
                                    (calc_height(y, mapWide, modPos[1]) - slideOffset[1],
                                     calc_width(x, mapTall, modPos[0]) - slideOffset[0]))
        walkingAnim = 4*animStage if int((sum(slideOffset) + sum(charSlide))/10) else 0
        screen.blit(resources["sprite"]["player"][currDir+walkingAnim],
                    ((608-(slideOffset[1]/charSlideMod)) if mapWide else
                     (left-charSlide[1]-slideOffset[1]+currPos[1]*64),
                     (446-(slideOffset[0]/charSlideMod)) if mapTall else
                     (top-slideOffset[0]-charSlide[0]+currPos[0]*64)))
        if winState:
            if menuLevel != "root":
                levelTitle = menuLevel + '/' + list(lvlpack_list[menuLevel]['lvls'].values())[lvlIndex]
                if levelTitle not in saveData['Completed']:
                    saveData['Completed'] += [levelTitle]
                    commit_save(saveData)
            draw_text("BigArial", "You Won!", (192, 192, 255),
                      (640-textSlide[0], 400-textSlide[1]), center=True, shadow=True)
            draw_text("Arial", "Press R to restart or", (192, 192, 255),
                      (640-textSlide[0], 480-textSlide[1]), center=True, shadow=True)
            draw_text("Arial", "Press ESC to leave", (192, 192, 255),
                      (640-textSlide[0], 520-textSlide[1]), center=True, shadow=True)
    elif mode == 0:
        if setupDone != 0:
            setupDone = 0
            newMenuLevel = None
            walking = False
            seed(time.time())
            menuBackLevelPack = choice(list(menu_items.keys())[:-3])
            menuBackLevel = choice(list(lvlpack_list[menuBackLevelPack]['lvls'].values()))
            map_content = lvl.decode_lvl(f"data/levels/{menuBackLevelPack}/{menuBackLevel}")
            mapHeight = len(map_content)-1
            mapWidth = max([len(i) for i in map_content])
            parallaxMulti = 2
            slideDiv = 7
        if menuLevel == "root":
            lvlIndex = 0
            menuMax = len(menu_items)-1
            for x in range(-3, min(mapHeight + 8, 20)):
                for y in range(-8, min(mapHeight + 5, 9)):
                    drawFloor = False
                    drawTile = None
                    seed(sum(map_content[0]) + sum(map_content[-1]) + x + y)
                    if -1 <= x <= mapHeight:
                        if -1 <= y <= mapWidth:
                            drawFloor = True
                        else:
                            if y < 0:
                                drawFloor = randint(0, abs(y)) < 1
                            elif y > len(map_content[x]):
                                drawFloor = randint(0, abs(y - mapWidth)) < 1
                    else:
                        if 0 <= y <= mapWidth + 1:
                            if x < 0:
                                drawFloor = randint(0, abs(x)) < 1
                            elif x > mapHeight + 1:
                                drawFloor = randint(0, abs(x - mapHeight)) < 1
                    if drawFloor:
                        screen.blit(resources["sprite"]["gbrick"], (-64 + calc_height(y, False, 750) - (slideOffset[1]/parallaxMulti),
                                                                    -64 + calc_width(x, False, 100) - (slideOffset[0]/parallaxMulti) - ((50/parallaxMulti)*menuIndex)))
            for x, row in enumerate(map_content):
                if x > 20:
                    continue
                for y, col in enumerate(row):
                    if y > 8:
                        continue
                    if 4 <= col <= 7:
                        if col == 4:
                            neighborNum = 0
                            if x > 0 and y < len(map_content[x - 1]):
                                neighborNum += int(map_content[x - 1][y] == 4)
                            if y > 0:
                                neighborNum += int(map_content[x][y - 1] == 4) * 2
                            if y < len(map_content[x]) - 1:
                                neighborNum += int(map_content[x][y + 1] == 4) * 4
                            if x < len(map_content) and y < len(map_content[x + 1]):
                                neighborNum += int(map_content[x + 1][y] == 4) * 8
                            screen.blit(resources["sprite"]["rbricksheet"],
                                        (calc_height(y, False, 750) - (slideOffset[1] / parallaxMulti),
                                         calc_width(x, False, 100) - (slideOffset[0] / parallaxMulti) - (
                                                 (50 / parallaxMulti) * menuIndex)),
                                        area=pygame.Rect((64 * (neighborNum % 4), 64 * floor(neighborNum / 4)),
                                                         (64, 64)))
                        else:
                            screen.blit(resources["sprite"][tiles[col - 4]],
                                        (calc_height(y, False, 750) - (slideOffset[1] / parallaxMulti),
                                         calc_width(x, False, 100) - (slideOffset[0] / parallaxMulti) - (
                                                     (50 / parallaxMulti) * menuIndex)))
            screen.blit(resources["sprite"]["shade"], (0, 0))
            for i, item in enumerate(menu_items.values()):
                draw_text("Arial", item,
                          (192, 192, 255) if i == menuIndex else (128, 128, 196),
                          (50-slideOffset[1], 240+((50*(i-menuIndex))-slideOffset[0])), shadow=True)
            titleWidth = draw_text("BigArial", lang.languages[args.lang][0], (192, 192, 255),
                                   (20-slideOffset[1], 90+((50*(-menuIndex))-slideOffset[0])), shadow=True)
            screen.blit(resources["sprite"]["player"][2], (128-slideOffset[1], 90+((50*(-menuIndex))-slideOffset[0])))
            draw_text("Arial", lang.languages[args.lang][16], (128, 128, 196),
                      (45+titleWidth-slideOffset[1], 120+((50*(-menuIndex))-slideOffset[0])), shadow=True)
            draw_text("Arial", lang.languages[args.lang][2], (128, 128, 196),
                      (40-slideOffset[1], 150+((50*(-menuIndex))-slideOffset[0])), shadow=True)
        else:
            titles = lvlpack_list[menuLevel]['title'].partition('(')
            levelList = list(lvlpack_list[menuLevel]['lvls'].keys())
            menuMax = len(levelList)-1
            lvlIndex = max(0, min(menuMax, lvlIndex))
            for i in range(len(levelList)):
                if i == lvlIndex:
                    screen.blit(resources["sprite"]["selbutton"],
                                (15+(160*(i % 8))-slideOffset[1], 250-((lvlIndex//8)*160)-slideOffset[0]+(160*(i//8))))
                    if menuLevel + '/' + list(lvlpack_list[menuLevel]['lvls'].values())[i] in saveData['Completed']:
                        screen.blit(resources["sprite"]["lvlchecked"],
                                    (80+(160*(i % 8))-slideOffset[1],
                                     300-((lvlIndex//8)*160)-slideOffset[0]+(160*(i//8))))
                    else:
                        screen.blit(resources["sprite"]["lvlcheck"],
                                    (80+(160*(i % 8))-slideOffset[1],
                                     300-((lvlIndex//8)*160)-slideOffset[0]+(160*(i//8))))
                    draw_text("BigArial", str(i+1), (192, 192, 255),
                              (50+(160*(i % 8))-slideOffset[1],
                               290-((lvlIndex//8)*160)-slideOffset[0]+(160*(i//8))), shadow=True, center=True)
                else:
                    screen.blit(resources["sprite"]["lvlbutton"],
                                (15+(160*(i % 8))-slideOffset[1], 250-((lvlIndex//8)*160)-slideOffset[0]+(160*(i//8))))
                    if menuLevel + '/' + list(lvlpack_list[menuLevel]['lvls'].values())[i] in saveData['Completed']:
                        screen.blit(resources["sprite"]["lvlchecked"],
                                    (80+(160*(i % 8))-slideOffset[1],
                                     300-((lvlIndex//8)*160)-slideOffset[0]+(160*(i//8))))
                    else:
                        screen.blit(resources["sprite"]["lvlcheck"],
                                    (80+(160*(i % 8))-slideOffset[1],
                                     300-((lvlIndex//8)*160)-slideOffset[0]+(160*(i//8))))
                    draw_text("BigArial", str(i+1), (128, 128, 196),
                              (50+(160*(i % 8))-slideOffset[1],
                               290-((lvlIndex//8)*160)-slideOffset[0]+(160*(i//8))), shadow=True, center=True)
            titleWidth = draw_text("BigArial", titles[0], (192, 192, 255),
                                   (20-slideOffset[1], 90+((160*(-(lvlIndex//8)))-slideOffset[0])), shadow=True)
            draw_text("Arial", titles[2][:-1], (128, 128, 196),
                      (35+titleWidth-slideOffset[1], 120+((160*(-(lvlIndex//8)))-slideOffset[0])), shadow=True)
            draw_text("Arial", lvlpack_list[menuLevel]['desc'], (128, 128, 196),
                      (40-slideOffset[1], 150+((160*(-(lvlIndex//8)))-slideOffset[0])), shadow=True)
    if debug:
        debug_show()
    if paused:
        draw_text("Arial", "Focus Lost!", (255, 255, 255), (500, 20))
    screen.blit(resources["sprite"]["vignette"], (0, 0))
    pygame.display.flip()
saveData['Completed'].sort()
commit_save(saveData)
pygame.quit()
