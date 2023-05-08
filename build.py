import pygame
import random
import convert
import level
import os
import subprocess
from copy import deepcopy
from pygame.locals import (
    K_s, K_w, K_a, K_d,
    K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8,
    K_MINUS, K_PLUS, K_EQUALS, K_RETURN, K_BACKSPACE,
    K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE
)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

Blocks = {
    "!": (  0,   0,   0),  # New line
    " ": (  0,   0,   0),  # Empty
    "@": ( 48, 189,  38),  # Player
    "#": (189,  79,  38),  # Block
    "$": (146, 119,  82),  # Crate
    ".": (255, 255, 255),  # Target
    "*": (255, 255, 255),  # Crate on Target
    "+": (255,   0, 255)   # Player on Target
}

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

meta = {
    "title": "Your Levels",
    "description": "Change me!",
    "levels": []
}

deflvl = []
gridsize = 8
for x in range(gridsize):
    line = []
    for y in range(gridsize):
        line += [" "]
    deflvl += [line]

meta["levels"] += [deepcopy(deflvl)]
currlvl = 0

WIDTH = 800
HEIGHT = 480
WCONST = (WIDTH/2) - (32*gridsize/2)
HCONST =(HEIGHT/2) - (32*gridsize/2)
CAMR = 0
CAMD = 0
FPS = 30


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

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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

for s in resources["sprite"].keys():
    resources["sprite"][s] = pygame.transform.scale(resources["sprite"][s], (32, 32))

def loadSave(filename):
    fileset = convert.LevelSet(f"data/levels/{filename}")
    global meta
    meta["title"] = fileset.title
    meta["description"] = fileset.description
    filetxt = fileset.get_levels_as_text()
    meta["levels"] = []
    for lvl in filetxt:
        size = len(lvl)
        for r in lvl:
            if len(r) > size:
                size = len(r)
        for r in lvl:
            if len(r) < size:
                for i in range(0, size-len(r)):
                    r += [" "]
        if len(lvl) < size:
            tmp_line = []
            for i in range(0, size):
                tmp_line += [" "]
            for i in range(0, size-len(lvl)):
                lvl += [tmp_line]
        tmplvl = []
        for i in range(len(lvl)):
            tmplvl += [[]]
        for r in lvl:
            for i, ch in enumerate(r):
                tmplvl[i] += [ch]
        meta["levels"] += [tmplvl]

def commitSave():
    str_lvls = []
    for l in meta["levels"]:
        tmplvl = []
        for i in range(len(l)):
            tmplvl += [""]
        for r in l:
            for i, ch in enumerate(r):
                tmplvl[i] += ch
        str_lvls += [tmplvl]
    with open("temp.txt", 'w') as f:
        for i, l in enumerate(str_lvls):
            f.write(f"; {i+1}\n\n")
            for r in l:
                f.write(f"{r}\n")
    convert.create_packed_levelset(meta["title"], meta["description"], "temp.txt")
    os.remove("temp.txt")

def drawGrid():
    blockSize = 32
    for x in range(0, 32*gridsize, blockSize):
        if x < 0:
            continue
        if -32 < (x+WCONST)-CAMR < WIDTH:
            for y in range(0, 32*gridsize, blockSize):
                if -32 < (y+HCONST)-CAMD < HEIGHT:
                    rect = pygame.Rect((x+WCONST)-CAMR, (y+HCONST)-CAMD, blockSize, blockSize)
                    if (x/32+y/32)%2:
                        pygame.draw.rect(screen, (96, 96, 96), rect, 0)
                    else:
                        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
                        rect = pygame.Rect((x+WCONST)-CAMR+2, (y+HCONST)-CAMD+2, blockSize-2, blockSize-2)
                        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
                        rect = pygame.Rect((x+WCONST)-CAMR+2, (y+HCONST)-CAMD+2, blockSize-4, blockSize-4)
                        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
                    if meta["levels"][currlvl][int(x/32)][int(y/32)] == "+":
                        draw_sprite(BlockSprites["."], ((x+WCONST)-CAMR, (y+HCONST)-CAMD))
                        draw_sprite(BlockSprites["@"], ((x+WCONST)-CAMR, (y+HCONST)-CAMD))
                        #draw_text("@", Blocks["@"], ((x+WCONST)-CAMR+16, (y+HCONST)-CAMD+16))
                        #draw_text(".", Blocks["."], ((x+WCONST)-CAMR+16, (y+HCONST)-CAMD+16))
                    else:
                        if (spr := BlockSprites[meta["levels"][currlvl][int(x/32)][int(y/32)]]) is not None:
                            draw_sprite(spr, ((x+WCONST)-CAMR, (y+HCONST)-CAMD))
                        #draw_text(meta["levels"][currlvl][int(x/32)][int(y/32)], Blocks[meta["levels"][currlvl][int(x/32)][int(y/32)]], ((x+WCONST)-CAMR+16, (y+HCONST)-CAMD+16))

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
gridsize = len(meta["levels"][0])
lvlfiles = list(level.get_levelpacks().keys())
lvlfiles.sort()
loadLevels = False
changeTitle = False
changeDesc = False
saved = True
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
                    gridsize += 1 if gridsize < 128 else 0
                    for l in meta["levels"][currlvl]:
                        l += [" "]
                    newl = []
                    for y in range(gridsize):
                        newl += [" "]
                    meta["levels"][currlvl] += [newl]
                    WCONST = (WIDTH/2) - (32*gridsize/2)
                    HCONST = (HEIGHT/2) - (32*gridsize/2)
                elif event.key == K_ESCAPE:
                    menuOpen = False
                    changeLevel = False
                    loadLevels = False
                elif event.key == K_MINUS:
                    gridsize -= 1 if gridsize > 1 else 0
                    for i in range(0, gridsize):
                        meta["levels"][currlvl][i] = meta["levels"][currlvl][i][:-1]
                    meta["levels"][currlvl] = meta["levels"][currlvl][:-1]
                    WCONST = (WIDTH/2) - (32*gridsize/2)
                    HCONST = (HEIGHT/2) - (32*gridsize/2)
                elif event.key == K_RETURN:
                    if changeLevel:
                        if menuSel == len(meta["levels"]):
                            currlvl = len(meta["levels"])
                            meta["levels"] += [deepcopy(deflvl)]
                            gridsize = 8
                            WCONST = (WIDTH/2) - (32*gridsize/2)
                            HCONST = (HEIGHT/2) - (32*gridsize/2)
                        else:
                            currlvl = menuSel
                            gridsize = len(meta["levels"][currlvl])
                            WCONST = (WIDTH/2) - (32*gridsize/2)
                            HCONST = (HEIGHT/2) - (32*gridsize/2)
                        changeLevel = False
                    elif loadLevels:
                        if menuSel == len(lvlfiles):
                            meta = {
                                "title": "Your Levels",
                                "description": "Change me!",
                                "levels": [deepcopy(deflvl)]
                            }
                        else:
                            loadSave(lvlfiles[menuSel])
                        currlvl = 0
                        gridsize = len(meta["levels"][currlvl])
                        WCONST = (WIDTH/2) - (32*gridsize/2)
                        HCONST = (HEIGHT/2) - (32*gridsize/2)
                        loadLevels = False
                    elif menuOpen:
                        if menuSel == 0:
                            menuSel = currlvl
                            changeLevel = True
                        elif menuSel == 1:
                            commitSave()
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
                if gridsize*32 > HEIGHT-96:
                    if event.key == K_w:
                        CAMV = -1
                    elif event.key == K_s:
                        CAMV = 1
                else:
                    CAMD = 0
                if gridsize*32 > WIDTH-96:
                    if event.key == K_d:
                        CAMH = 1
                    elif event.key == K_a:
                        CAMH = -1
                else:
                    CAMR = 0
        elif event.type == pygame.KEYUP:
            if gridsize*32 > HEIGHT-96:
                if event.key == K_w:
                    CAMV = 0
                elif event.key == K_s:
                    CAMV = 0
            if gridsize*32 > WIDTH-96:
                if event.key == K_d:
                    CAMH = 0
                elif event.key == K_a:
                    CAMH = 0
        elif event.type == pygame.QUIT:
            running = False

    if gridsize*32 > HEIGHT-96:
        if CAMV == 1:
            CAMD += 12 if CAMD < 16*gridsize else 0
        elif CAMV == -1:
            CAMD -= 12 if CAMD > -16*gridsize else 0
    if gridsize*32 > WIDTH-96:
        if CAMH == 1:
            CAMR += 12 if CAMR < 16*gridsize else 0
        elif CAMH == -1:
            CAMR -= 12 if CAMR > -16*gridsize else 0

    if PLACE:
        pos = pygame.mouse.get_pos()
        mx, my = int((pos[0]-WCONST+CAMR)/32), int((pos[1]-HCONST+CAMD)/32)
        if 0 <= mx < gridsize and 0 <= my < gridsize:
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

    screen.fill(BLACK)

    drawGrid()

    #rect = pygame.Rect(1, 64, 36, 36*len(SELS))
    #pygame.draw.rect(screen, (64, 64, 64), rect, 0)
    for i, s in enumerate(SELS):
        rect = pygame.Rect(1, (i*40)+64, 40, 40)
        pygame.draw.rect(screen, (96, 96, 96) if i == CURRSEL else (64, 64, 64), rect, 0)
        if s == "+":
            draw_sprite(BlockSprites["@"], (4, (40*i)+68))
            draw_sprite(BlockSprites["."], (4, (40*i)+68))
        else:
            if BlockSprites[s] is not None:
                draw_sprite(BlockSprites[s], (4, (40*i)+68))
        draw_text(str(i+1), (192,192,192), (40, (40*i)+72), 12)

    if menuOpen:
        fakes = ["Return - Select", "Up/Down - Move Selection", "Escape - Cancel"]
        if saved:
            menu[-1] = "Exit"
        else:
            menu[-1] = "Exit   ! Not Saved !"
        rect = pygame.Rect(0, HEIGHT-24-(len(menu)*26), largestMenu+12, (len(menu)*26))
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(2, HEIGHT-22-(len(menu)*26), largestMenu+10, (len(menu)*26)-2)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(2, HEIGHT-22-(len(menu)*26), largestMenu+8, (len(menu)*26)-4)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        for i, m in enumerate(menu):
            if i == menuSel:
                rect = pygame.Rect(0, HEIGHT-24-(len(menu)*26)+(i*26), largestMenu+12, 26)
                pygame.draw.rect(screen, (96, 96, 96), rect, 0)
                rect = pygame.Rect(2, HEIGHT-22-(len(menu)*26)+(i*26), largestMenu+10, 24)
                pygame.draw.rect(screen, (64, 64, 64), rect, 0)
                rect = pygame.Rect(2, HEIGHT-22-(len(menu)*26)+(i*26), largestMenu+8, 22)
                pygame.draw.rect(screen, (72, 72, 72), rect, 0)
            menuS = draw_text(m, (192,192,192), (4, HEIGHT-22-(len(menu)*26)+(i*26)), 18, center=False)
            if menuS > largestMenu:
                largestMenu = menuS
    elif changeLevel:
        fakes = ["Return - Select", "Left/Right - Move Selection", "Escape - Cancel"]
        rect = pygame.Rect(WIDTH/2-150, HEIGHT/2-75, 300, 150)
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(WIDTH/2-148, HEIGHT/2-73, 298, 148)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(WIDTH/2-148, HEIGHT/2-73, 296, 146)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        draw_text("Change level:", (192,192,192),(WIDTH/2, HEIGHT/2-40))
        for i in range(0, len(meta["levels"])+1):
            hpos = WIDTH/2-(95+menuSel*50)+(i*50)
            if hpos < WIDTH/2-150 or hpos > WIDTH/2+150:
                continue
            vpos = HEIGHT/2
            rect = pygame.Rect(hpos, vpos, 40, 40)
            pygame.draw.rect(screen, (96, 96, 96) if i == menuSel else (72, 72, 72), rect, 0)
            if i == currlvl:
                draw_text("↑", (192,192,192), (hpos+20, vpos+50))
            if i >= len(meta["levels"]):
                draw_text("+", (192,192,192), (hpos+20, vpos+17))
            else:
                draw_text(str(i), (192,192,192), (hpos+20, vpos+20))
    elif changeTitle:
        fakes = ["Return - Save", "Escape - Cancel"]
        rect = pygame.Rect(WIDTH/2-250, HEIGHT/2-75, 500, 150)
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(WIDTH/2-248, HEIGHT/2-73, 498, 148)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(WIDTH/2-248, HEIGHT/2-73, 496, 146)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        draw_text("Change Title:", (192,192,192),(WIDTH/2, HEIGHT/2-40))
        rect = pygame.Rect(WIDTH/2-248, HEIGHT/2-15, 496, 30)
        pygame.draw.rect(screen, (96, 96, 96), rect, 0)
        draw_text(tempTitle, (192,192,192),(WIDTH/2, HEIGHT/2))
    elif changeDesc:
        fakes = ["Return - Save", "Escape - Cancel"]
        rect = pygame.Rect(WIDTH/2-250, HEIGHT/2-75, 500, 150)
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(WIDTH/2-248, HEIGHT/2-73, 498, 148)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(WIDTH/2-248, HEIGHT/2-73, 496, 146)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        draw_text("Change Description:", (192,192,192),(WIDTH/2, HEIGHT/2-40))
        rect = pygame.Rect(WIDTH/2-248, HEIGHT/2-15, 496, 30)
        pygame.draw.rect(screen, (96, 96, 96), rect, 0)
        draw_text(tempDesc, (192,192,192),(WIDTH/2, HEIGHT/2))
    elif loadLevels:
        fakes = ["Return - Select", "Up/Down - Move Selection", "Escape - Cancel"]
        rect = pygame.Rect(WIDTH/2-250, HEIGHT/2-75, 500, 150)
        pygame.draw.rect(screen, (64, 64, 64), rect, 0)
        rect = pygame.Rect(WIDTH/2-248, HEIGHT/2-73, 498, 148)
        pygame.draw.rect(screen, (48, 48, 48), rect, 0)
        rect = pygame.Rect(WIDTH/2-248, HEIGHT/2-73, 496, 146)
        pygame.draw.rect(screen, (56, 56, 56), rect, 0)
        for i in range(0, len(lvlfiles)+1):
            hpos = WIDTH/2-250
            vpos = HEIGHT/2-33-(35*menuSel)+(i*35)
            if vpos < HEIGHT/2-70 or vpos > HEIGHT/2+60:
                continue
            rect = pygame.Rect(hpos+2, vpos, 496, 30)
            pygame.draw.rect(screen, (96, 96, 96) if i == menuSel else (72, 72, 72), rect, 0)
            if i >= len(lvlfiles):
                draw_text("New Levels", (192,192,192), (hpos+250, vpos+15))
            else:
                draw_text(lvlfiles[i], (192,192,192), (hpos+250, vpos+15))
    else:
        fakes = ["Return - Open Menu", "Minus/Plus - Change Size"]

    out = ""
    for s in fakes:
        out += s + "  /  "
    out = out[:-4]
    rect = pygame.Rect(0, HEIGHT-24, WIDTH, 24)
    pygame.draw.rect(screen, (64, 64, 64), rect, 0)
    rect = pygame.Rect(2, HEIGHT-22, WIDTH, 24)
    pygame.draw.rect(screen, (48, 48, 48), rect, 0)
    rect = pygame.Rect(2, HEIGHT-22, WIDTH-2, 22)
    pygame.draw.rect(screen, (56, 56, 56), rect, 0)
    draw_text(out, (192,192,192), (8, HEIGHT-20), 18, center=False)
    total_crates = 0
    total_targets = 0
    for l in meta["levels"][currlvl]:
        total_crates += l.count("$") + l.count("*")
        total_targets += l.count(".") + l.count("+") + l.count("*")
    draw_text(f"{total_crates} crates  /  {total_targets} targets", (192,192,192), (710, HEIGHT-10), 18)


    pygame.display.flip()

pygame.quit()
