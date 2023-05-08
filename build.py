import pygame
import convert
import level
import os
import subprocess
from copy import deepcopy
from pygame.locals import (
    K_s, K_w, K_a, K_d,
    K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0,
    K_MINUS, K_PLUS, K_EQUALS, K_RETURN, K_BACKSPACE,
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE
)

BlockSprites = {
    "!": None,         # New line
    " ": None,         # Empty
    "@": "player",     # Player
    "#": "rbrick",     # Block
    "$": "crate",      # Crate
    ".": "target",     # Target
    "*": "cratedark",  # Crate on Target
    "+": "player"      # Player on Target
}

default_level = []
grid_size = 8
for x in range(grid_size):
    line = []
    for y in range(grid_size):
        line += [" "]
    default_level += [line]

meta = {
    "title": "Your Levels",
    "description": "Change me!",
    "levels": [deepcopy(default_level)]
}

currlvl = 0

width = 800
height = 480
wconst = (width / 2) - (32 * grid_size / 2)
hconst = (height / 2) - (32 * grid_size / 2)
CAMR = 0
CAMD = 0
FPS = 30
pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("SokoPy Builder")
clock = pygame.time.Clock()

resources = {
    "sprite": {
        "player":       pygame.image.load(f"data/sprites/playerStill2.png").convert_alpha(),
        "rbrick":       pygame.image.load(f"data/sprites/redBrick.png").convert_alpha(),
        "crate":        pygame.image.load(f"data/sprites/crateBrown.png").convert_alpha(),
        "cratedark":    pygame.image.load(f"data/sprites/crateBrownOnTarget.png").convert_alpha(),
        "target":       pygame.image.load(f"data/sprites/target.png").convert_alpha(),
    },
}


def update_grid():
    global grid_size
    global hconst
    global wconst
    grid_size = len(meta["levels"][currlvl])
    wconst = (width / 2) - (32 * grid_size / 2)
    hconst = (height / 2) - (32 * grid_size / 2)


update_grid()


def draw_sprite(sprite, pos):
    screen.blit(resources["sprite"][sprite], pos)


def draw_text(text, color, pos, size=24, center=True, shadow=False):
    text_main = pygame.font.SysFont("Arial", size, bold=True).render(text, True, color)
    if center:
        text_main_pos = text_main.get_rect(center=pos)
    else:
        text_main_pos = pos
    if shadow:
        text_shadow = pygame.font.SysFont("Arial", 24, bold=True).render(text, True, (0, 0, 0))
        if center:
            text_shadow_pos = text_shadow.get_rect(center=(pos[0], pos[1]+3))
        else:
            text_shadow_pos = (pos[0]+3, pos[1]+3)
        screen.blit(text_shadow, text_shadow_pos)
    screen.blit(text_main, text_main_pos)
    return pygame.font.SysFont("Arial", 24, bold=True).size(text)[0]


for s in resources["sprite"].keys():
    resources["sprite"][s] = pygame.transform.scale(resources["sprite"][s], (32, 32))


def load_save(filename):
    fileset = convert.LevelSet(f"data/levels/{filename}")
    global meta
    meta["title"] = fileset.title
    meta["description"] = fileset.description
    filetxt = fileset.get_levels_as_text()
    meta["levels"] = []
    for lvl in filetxt:
        size = len(lvl)
        for row in lvl:
            if len(row) > size:
                size = len(row)
        for row in lvl:
            if len(row) < size:
                for col in range(0, size-len(row)):
                    row += [" "]
        if len(lvl) < size:
            tmp_line = []
            for row in range(0, size):
                tmp_line += [" "]
            for rrow in range(0, size-len(lvl)):
                lvl += [tmp_line]
        tmplvl = []
        for row in range(len(lvl)):
            tmplvl += [[]]
        for row in lvl:
            for index, character in enumerate(row):
                tmplvl[index] += [character]
        meta["levels"] += [tmplvl]


def commit_save():
    str_lvls = []
    for lvl in meta["levels"]:
        tmplvl = []
        for row in range(len(lvl)):
            tmplvl += [""]
        for row in lvl:
            for index, character in enumerate(row):
                tmplvl[index] += character
        str_lvls += [tmplvl]
    with open("temp.txt", 'w') as f:
        for index, lvl in enumerate(str_lvls):
            f.write(f"; {index+1}\n\n")
            for row in lvl:
                f.write(f"{row}\n")
    convert.create_packed_levelset(meta["title"], meta["description"], "temp.txt")
    os.remove("temp.txt")


def draw_grid():
    block_size = 32
    for x in range(0, 32 * grid_size, block_size):
        if x < 0:
            continue
        if -32 < (x + wconst)-CAMR < width:
            for y in range(0, 32 * grid_size, block_size):
                if -32 < (y + hconst)-CAMD < height:
                    rect = pygame.Rect((x + wconst) - CAMR, (y + hconst) - CAMD, block_size, block_size)
                    if (x/32+y/32)%2:
                        pygame.draw.rect(screen, (96, 96, 96), rect, 0)
                    else:
                        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
                        rect = pygame.Rect((x + wconst) - CAMR + 2,
                                           (y + hconst) - CAMD + 2, block_size - 2, block_size - 2)
                        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
                        rect = pygame.Rect((x + wconst) - CAMR + 2,
                                           (y + hconst) - CAMD + 2, block_size - 4, block_size - 4)
                        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
                    if meta["levels"][currlvl][int(x/32)][int(y/32)] == "+":
                        draw_sprite(BlockSprites["."], ((x + wconst) - CAMR, (y + hconst) - CAMD))
                        draw_sprite(BlockSprites["@"], ((x + wconst) - CAMR, (y + hconst) - CAMD))
                    else:
                        if (spr := BlockSprites[meta["levels"][currlvl][int(x/32)][int(y/32)]]) is not None:
                            draw_sprite(spr, ((x + wconst) - CAMR, (y + hconst) - CAMD))


running = True
CAMV = 0
CAMH = 0
PLACE = 0
SELNUMS = [K_1, K_2, K_3, K_4, K_5]
SELS = [" ", "@", "#", "$", "."]
fakes = ["Return - Open Menu", "Minus/Plus - Change Size"]
menu = ["Change Level", "Save Levels", "Load Levels", "Run SokoPy", "Change Title", "Change Description", "Exit"]
menuOpen = False
changeLevel = False
menuSel = 0
largestMenu = 0
CURRSEL = 3
PLAYER = None
lvlfiles = list(level.get_levelpacks().keys())
lvlfiles.sort()
loadLevels = False
changeTitle = False
changeDesc = False
saved = True
tempTitle = meta["title"]
tempDesc = meta["description"]
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            PLACE = 1
            saved = False
        elif event.type == pygame.MOUSEBUTTONUP:
            PLACE = 0
        elif event.type == pygame.KEYDOWN:
            if changeTitle or changeDesc:
                if changeTitle:
                    if event.key == K_RETURN:
                        meta["title"] = tempTitle
                        changeTitle = False
                    elif event.key == K_BACKSPACE:
                        tempTitle = tempTitle[:-1]
                    elif event.key == K_ESCAPE:
                        changeTitle = False
                    else:
                        tempTitle += event.unicode
                else:
                    if event.key == K_RETURN:
                        meta["description"] = tempDesc
                        changeDesc = False
                    elif event.key == K_BACKSPACE:
                        tempDesc = tempDesc[:-1]
                    elif event.key == K_ESCAPE:
                        changeDesc = False
                    else:
                        tempDesc += event.unicode

            else:
                tempTitle = meta["title"]
                tempDesc = meta["description"]
                if event.key in SELNUMS:
                    CURRSEL = SELNUMS.index(event.key)
                elif event.key in [K_PLUS, K_EQUALS]:
                    grid_size += 1 if grid_size < 128 else 0
                    for lvl in meta["levels"][currlvl]:
                        lvl += [" "]
                    newl = []
                    for y in range(grid_size):
                        newl += [" "]
                    meta["levels"][currlvl] += [newl]
                    wconst = (width / 2) - (32 * grid_size / 2)
                    hconst = (height / 2) - (32 * grid_size / 2)
                elif event.key == K_ESCAPE:
                    menuOpen = False
                    changeLevel = False
                    loadLevels = False
                elif event.key == K_MINUS:
                    grid_size -= 1 if grid_size > 1 else 0
                    for i in range(0, grid_size):
                        meta["levels"][currlvl][i] = meta["levels"][currlvl][i][:-1]
                    meta["levels"][currlvl] = meta["levels"][currlvl][:-1]
                    wconst = (width / 2) - (32 * grid_size / 2)
                    hconst = (height / 2) - (32 * grid_size / 2)
                elif event.key == K_RETURN:
                    if changeLevel:
                        if menuSel == len(meta["levels"]):
                            currlvl = len(meta["levels"])
                            meta["levels"] += [deepcopy(default_level)]
                        else:
                            currlvl = menuSel
                        update_grid()
                        changeLevel = False
                    elif loadLevels:
                        if menuSel == len(lvlfiles):
                            meta = {
                                "title": "Your Levels",
                                "description": "Change me!",
                                "levels": [deepcopy(default_level)]
                            }
                        else:
                            load_save(lvlfiles[menuSel])
                        currlvl = 0
                        update_grid()
                        loadLevels = False
                    elif menuOpen:
                        if menuSel == 0:
                            menuSel = currlvl
                            changeLevel = True
                        elif menuSel == 1:
                            commit_save()
                            saved = True
                        elif menuSel == 2:
                            menuSel = 0
                            loadLevels = True
                        elif menuSel == 3:
                            subprocess.run(["python3", "main.py"])
                        elif menuSel == 4:
                            changeTitle = True
                        elif menuSel == 5:
                            changeDesc = True
                        elif menuSel == 6:
                            running = False
                        menuOpen = False
                    else:
                        menuSel = 0
                        menuOpen = True
                elif menuOpen and event.key == K_UP:
                    menuSel = menuSel-1 if menuSel > 0 else len(menu)-1
                elif menuOpen and event.key == K_DOWN:
                    menuSel = menuSel+1 if menuSel < len(menu)-1 else 0
                elif loadLevels and event.key == K_UP:
                    menuSel = menuSel-1 if menuSel > 0 else len(lvlfiles)
                elif loadLevels and event.key == K_DOWN:
                    menuSel = menuSel+1 if menuSel < len(lvlfiles) else 0
                elif changeLevel and event.key == K_LEFT:
                    menuSel = menuSel-1 if menuSel > 0 else len(meta["levels"])
                elif changeLevel and event.key == K_RIGHT:
                    menuSel = menuSel+1 if menuSel < len(meta["levels"]) else 0
                if grid_size*32 > height-96:
                    if event.key == K_w:
                        CAMV = -1
                    elif event.key == K_s:
                        CAMV = 1
                else:
                    CAMD = 0
                if grid_size*32 > width-96:
                    if event.key == K_d:
                        CAMH = 1
                    elif event.key == K_a:
                        CAMH = -1
                else:
                    CAMR = 0
        elif event.type == pygame.KEYUP:
            if grid_size*32 > height-96:
                if event.key == K_w:
                    CAMV = 0
                elif event.key == K_s:
                    CAMV = 0
            if grid_size*32 > width-96:
                if event.key == K_d:
                    CAMH = 0
                elif event.key == K_a:
                    CAMH = 0
        elif event.type == pygame.QUIT:
            running = False
    if grid_size*32 > height-96:
        if CAMV == 1:
            CAMD += 12 if CAMD < 16 * grid_size else 0
        elif CAMV == -1:
            CAMD -= 12 if CAMD > -16 * grid_size else 0
    if grid_size*32 > width-96:
        if CAMH == 1:
            CAMR += 12 if CAMR < 16 * grid_size else 0
        elif CAMH == -1:
            CAMR -= 12 if CAMR > -16 * grid_size else 0
    if PLACE:
        mpos = pygame.mouse.get_pos()
        mx, my = int((mpos[0] - wconst + CAMR) / 32), int((mpos[1] - hconst + CAMD) / 32)
        if 0 <= mx < grid_size and 0 <= my < grid_size:
            if CURRSEL == 1:
                if PLAYER is not None:
                    if meta["levels"][currlvl][PLAYER[0]][PLAYER[1]] == "+":
                        meta["levels"][currlvl][PLAYER[0]][PLAYER[1]] = "."
                    elif meta["levels"][currlvl][PLAYER[0]][PLAYER[1]] == "@":
                        meta["levels"][currlvl][PLAYER[0]][PLAYER[1]] = " "
                if meta["levels"][currlvl][mx][my] in [".", "*", "+"]:
                    meta["levels"][currlvl][mx][my] = "+"
                else:
                    meta["levels"][currlvl][mx][my] = SELS[CURRSEL]
                PLAYER = [mx, my]
            elif CURRSEL == 3:
                if meta["levels"][currlvl][mx][my] in [".", "*", "+"]:
                    meta["levels"][currlvl][mx][my] = "*"
                else:
                    meta["levels"][currlvl][mx][my] = SELS[CURRSEL]
            elif CURRSEL == 4:
                if meta["levels"][currlvl][mx][my] in ["$", "*"]:
                    meta["levels"][currlvl][mx][my] = "*"
                elif meta["levels"][currlvl][mx][my] in ["@", "+"]:
                    meta["levels"][currlvl][mx][my] = "+"
                else:
                    meta["levels"][currlvl][mx][my] = SELS[CURRSEL]
            else:
                meta["levels"][currlvl][mx][my] = SELS[CURRSEL]
    screen.fill((0, 0, 0))
    draw_grid()
    for i, s in enumerate(SELS):
        rect = pygame.Rect(1, (i*40)+64, 40, 40)
        pygame.draw.rect(screen, (96, 96, 96) if i == CURRSEL else (64, 64, 64), rect, 0)
        if s == "+":
            draw_sprite(BlockSprites["@"], (4, (40*i)+68))
            draw_sprite(BlockSprites["."], (4, (40*i)+68))
        else:
            if BlockSprites[s] is not None:
                draw_sprite(BlockSprites[s], (4, (40*i)+68))
        draw_text(str(i+1), (192, 192, 192), (40, (40*i)+72), 12)

    if menuOpen:
        fakes = ["Return - Select", "Up/Down - Move Selection", "Escape - Cancel"]
        if saved:
            menu[-1] = "Exit"
        else:
            menu[-1] = "Exit   ! Not Saved !"
        rect = pygame.Rect(0, height - 24 - (len(menu) * 26), largestMenu + 12, (len(menu) * 26))
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(2, height - 22 - (len(menu) * 26), largestMenu + 10, (len(menu) * 26) - 2)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(2, height - 22 - (len(menu) * 26), largestMenu + 8, (len(menu) * 26) - 4)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        for i, m in enumerate(menu):
            if i == menuSel:
                rect = pygame.Rect(0, height - 24 - (len(menu) * 26) + (i * 26), largestMenu + 12, 26)
                pygame.draw.rect(screen, (96, 96, 96), rect, 0)
                rect = pygame.Rect(2, height - 22 - (len(menu) * 26) + (i * 26), largestMenu + 10, 24)
                pygame.draw.rect(screen, (64, 64, 64), rect, 0)
                rect = pygame.Rect(2, height - 22 - (len(menu) * 26) + (i * 26), largestMenu + 8, 22)
                pygame.draw.rect(screen, (72, 72, 72), rect, 0)
            menuS = draw_text(m, (192, 192, 192), (4, height - 22 - (len(menu) * 26) + (i * 26)), 18, center=False)
            if menuS > largestMenu:
                largestMenu = menuS
    elif changeLevel:
        fakes = ["Return - Select", "Left/Right - Move Selection", "Escape - Cancel"]
        rect = pygame.Rect(width / 2 - 150, height / 2 - 75, 300, 150)
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(width / 2 - 148, height / 2 - 73, 298, 148)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(width / 2 - 148, height / 2 - 73, 296, 146)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        draw_text("Change level:", (192, 192, 192), (width / 2, height / 2 - 40))
        for i in range(0, len(meta["levels"])+1):
            hpos = width / 2 - (95 + menuSel * 50) + (i * 50)
            if hpos < width/2-150 or hpos > width/2+150:
                continue
            vpos = height / 2
            rect = pygame.Rect(hpos, vpos, 40, 40)
            pygame.draw.rect(screen, (96, 96, 96) if i == menuSel else (72, 72, 72), rect, 0)
            if i == currlvl:
                draw_text("↑", (192, 192, 192), (hpos+20, vpos+50))
            if i >= len(meta["levels"]):
                draw_text("+", (192, 192, 192), (hpos+20, vpos+17))
            else:
                draw_text(str(i), (192, 192, 192), (hpos+20, vpos+20))
    elif changeTitle:
        fakes = ["Return - Save", "Escape - Cancel"]
        rect = pygame.Rect(width / 2 - 250, height / 2 - 75, 500, 150)
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(width / 2 - 248, height / 2 - 73, 498, 148)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(width / 2 - 248, height / 2 - 73, 496, 146)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        draw_text("Change Title:", (192, 192, 192), (width / 2, height / 2 - 40))
        rect = pygame.Rect(width / 2 - 248, height / 2 - 15, 496, 30)
        pygame.draw.rect(screen, (96, 96, 96), rect, 0)
        draw_text(tempTitle, (192, 192, 192), (width / 2, height / 2))
    elif changeDesc:
        fakes = ["Return - Save", "Escape - Cancel"]
        rect = pygame.Rect(width / 2 - 250, height / 2 - 75, 500, 150)
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(width / 2 - 248, height / 2 - 73, 498, 148)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(width / 2 - 248, height / 2 - 73, 496, 146)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        draw_text("Change Description:", (192, 192, 192), (width / 2, height / 2 - 40))
        rect = pygame.Rect(width / 2 - 248, height / 2 - 15, 496, 30)
        pygame.draw.rect(screen, (96, 96, 96), rect, 0)
        draw_text(tempDesc, (192, 192, 192), (width / 2, height / 2))
    elif loadLevels:
        fakes = ["Return - Select", "Up/Down - Move Selection", "Escape - Cancel"]
        rect = pygame.Rect(width / 2 - 250, height / 2 - 75, 500, 150)
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(width / 2 - 248, height / 2 - 73, 498, 148)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(width / 2 - 248, height / 2 - 73, 496, 146)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        for i in range(0, len(lvlfiles)+1):
            hpos = width / 2 - 250
            vpos = height / 2 - 33 - (35 * menuSel) + (i * 35)
            if vpos < height/2-70 or vpos > height/2+60:
                continue
            rect = pygame.Rect(hpos+2, vpos, 496, 30)
            pygame.draw.rect(screen, (96, 96, 96) if i == menuSel else (72, 72, 72), rect, 0)
            if i >= len(lvlfiles):
                draw_text("New Levels", (192, 192, 192), (hpos+250, vpos+15))
            else:
                draw_text(lvlfiles[i], (192, 192, 192), (hpos+250, vpos+15))
    else:
        fakes = ["Return - Open Menu", "Minus/Plus - Change Size"]

    out = ""
    for s in fakes:
        out += s + "  /  "
    out = out[:-4]
    rect = pygame.Rect(0, height - 24, width, 24)
    pygame.draw.rect(screen, (64, 64, 64), rect, 0)
    rect = pygame.Rect(2, height - 22, width, 24)
    pygame.draw.rect(screen, (48, 48, 48), rect, 0)
    rect = pygame.Rect(2, height - 22, width - 2, 22)
    pygame.draw.rect(screen, (56, 56, 56), rect, 0)
    draw_text(out, (192, 192, 192), (8, height - 20), 18, center=False)
    total_crates = 0
    total_targets = 0
    for l in meta["levels"][currlvl]:
        total_crates += l.count("$") + l.count("*")
        total_targets += l.count(".") + l.count("+") + l.count("*")
    draw_text(f"{total_crates} crates  /  {total_targets} targets", (192, 192, 192), (710, height - 10), 18)

    pygame.display.flip()

pygame.quit()
