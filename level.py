import os
import json
from math import floor
from random import randint, seed
from copy import deepcopy
from pygame import surface
import pygame
import convert

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


# We offloaded this to the convert script but I'd like to leave it here just in case
def decode_lvl(filename: str):
    with open(filename, mode='rb') as f:
        f_content = f.read()
    map_data = [[]]
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
    for filename in os.listdir("./levels/"):
        if filename == "tutorial.lvl":
            continue
        f = os.path.join("./levels/", filename)
        if os.path.isfile(f):
            if meta := convert.unpack_levelset(f):
                levelpack_list[filename] = {"title": meta['title'], "desc": meta['desc'], "len": meta['length']}
    return levelpack_list


def menu_packs(lvlpack_list):
    titles = {}
    for i in lvlpack_list:
        titles[i] = lvlpack_list[i]["title"]
    titles = {k: v for k, v in sorted(titles.items(), key=lambda item: item[1])}
    return titles


def pre_calc_connections(level: list[list]):
    pre_calced = []
    for x, row in enumerate(level):
        pre_calced += [[]]
        for y, col in enumerate(row):
            if col == 4:
                neighbors = 0
                if x > 0 and y < len(level[x - 1]):
                    neighbors += int(level[x - 1][y] == 4)
                if y > 0:
                    neighbors += int(level[x][y - 1] == 4) * 2
                if y < len(level[x]) - 1:
                    neighbors += int(level[x][y + 1] == 4) * 4
                if x < len(level) and y < len(level[x + 1]):
                    neighbors += int(level[x + 1][y] == 4) * 8
                pre_calced[x] += [((64 * (neighbors % 4), 64 * floor(neighbors / 4)), (64, 64))]
            else:
                pre_calced[x] += [None]
    return pre_calced


def calc_place(modifier, large, modpos, resolution):
    if large:
        return ((resolution/2)-32) + ((modifier - modpos) * 64)
    else:
        return modpos + (modifier * 64)


class Level:
    def __init__(self, level, screen_dimensions: list[int]):
        self.data = level
        self.precalculated_connections = pre_calc_connections(self.data)
        self.dimensions = {
            "height": len(self.data) - 1,
            "width": max([len(i) for i in self.data])
        }
        self.widest = [len(i[:i.index(1) if 1 in i else -1])+1 for i in self.data].index(self.dimensions["width"])
        self.large = {
            "tall": self.dimensions["height"] > (screen_dimensions[1]/64),
            "wide": self.dimensions["width"] > (screen_dimensions[0]/64)
        }
        self.edge = {
            "horizontal": round((screen_dimensions[1]/64)/2)-2,
            "vertical": round((screen_dimensions[0]/64)/2)-2
        }
        self.notEdge = [self.large["tall"], self.large["wide"]]
        self.corner = {
            "top": (screen_dimensions[1]/2) - ((self.dimensions["height"]/2)*64),
            "left": (screen_dimensions[0]/2) - ((self.dimensions["width"]/2)*64)
        }
        self.distances = {
            "height": int(screen_dimensions[1]/128) + 1,
            "width": int(screen_dimensions[0]/128) + 1,
        }
        self.shakeDelay = 2
        for x, row in enumerate(self.data):
            for y, col in enumerate(row):
                if col == 3:
                    self.player = [x, y]
                    self.data[x][y] = 2
                    break
                elif col == 8:
                    self.player = [x, y]
                    self.data[x][y] = 6
                    break
        self.player += [2]
        self.last_crate_moved = [-1, -1]
        self.history = []
        self.animation = {
            "ticks": 0,
            "frame": 0
        }
        self.background = None
        self.inside = None

    def update_res(self, screen_dimensions) -> None:
        self.large = {
            "tall": self.dimensions["height"] > (screen_dimensions[1] / 64),
            "wide": self.dimensions["width"] > (screen_dimensions[0] / 64)
        }
        self.corner = {
            "top": (screen_dimensions[1] / 2) - ((self.dimensions["height"] / 2) * 64),
            "left": (screen_dimensions[0] / 2) - ((self.dimensions["width"] / 2) * 64)
        }
        self.distances = {
            "height": int(screen_dimensions[1]/128) + 1,
            "width": int(screen_dimensions[0]/128) + 1,
        }
        self.edge = {
            "horizontal": round((screen_dimensions[1]/64)/2)-2,
            "vertical": round((screen_dimensions[0]/64)/2)-2
        }
        self.notEdge = [self.large["tall"], self.large["wide"]]

    def capture(self) -> None:
        if len(self.history) > 100:
            self.history.pop(0)
        self.history += [{
            "data": deepcopy(self.data),
            "player": deepcopy(self.player),
        }]

    def rewind(self) -> None:
        self.data = self.history[-1]["data"]
        self.player = self.history[-1]["player"]
        self.history.pop(-1)

    def check_win(self) -> int:
        targets = 0
        for x in self.data:
            for y in x:
                if y == 5:
                    targets += 1
        return targets

    def move_player(self, direction: list[int], slides):
        self.player[2] = (0 if direction[0] == -1 else 2) if direction[0] else (3 if direction[1] == -1 else 1)
        if atrTable[self.data[self.player[0] + direction[0]][self.player[1] + direction[1]]][0] == "1":
            self.shakeDelay = 2
            self.capture()
            self.player[0] += direction[0]
            self.player[1] += direction[1]
            if self.notEdge[0]:
                slides["display"][0] -= 64*direction[0]
            else:
                slides["character"][0] += 64*direction[0]
            if self.notEdge[1]:
                slides["display"][1] -= 64*direction[1]
            else:
                slides["character"][1] += 64*direction[1]
        elif atrTable[self.data[self.player[0] + direction[0]][self.player[1] + direction[1]]][1] == "1":
            if atrTable[self.data[self.player[0] + (direction[0]*2)][self.player[1] + (direction[1]*2)]][0] == "1":
                self.shakeDelay = 2
                self.capture()
                if self.data[self.player[0] + direction[0]][self.player[1] + direction[1]] == 5:
                    self.data[self.player[0] + (direction[0]*2)][self.player[1] + (direction[1]*2)] = 5 if \
                        self.data[self.player[0] + (direction[0]*2)][self.player[1] + (direction[1]*2)] == 2 else 7
                    self.data[self.player[0] + direction[0]][self.player[1] + direction[1]] = 2
                if self.data[self.player[0] + direction[0]][self.player[1] + direction[1]] == 7:
                    self.data[self.player[0] + (direction[0]*2)][self.player[1] + (direction[1]*2)] = 5 if \
                        self.data[self.player[0] + (direction[0]*2)][self.player[1] + (direction[1]*2)] == 2 else 7
                    self.data[self.player[0] + direction[0]][self.player[1] + direction[1]] = 6
                self.last_crate_moved = [self.player[0] + (direction[0]*2), self.player[1] + (direction[1]*2)]
                slides["crate"][0] += 64*direction[0]
                slides["crate"][1] += 64*direction[1]
                self.player[0] += direction[0]
                self.player[1] += direction[1]
                if self.notEdge[0]:
                    slides["display"][0] -= 64*direction[0]
                else:
                    slides["character"][0] += 64*direction[0]
                if self.notEdge[1]:
                    slides["display"][1] -= 64*direction[1]
                else:
                    slides["character"][1] += 64*direction[1]
            else:
                if self.shakeDelay == 0:
                    slides["shake"] = 3
                else:
                    self.shakeDelay -= 1
        else:
            if self.shakeDelay == 0:
                slides["shake"] = 3
            else:
                self.shakeDelay -= 1

    def render(self, screen_dimensions: list[int], slides: dict, screen, resources, tiles,
               dt, mod=0, modw=0, parallax=1, player=True, modsize=0):  # TODO: Too many goddamn variables
        if not self.background:
            if not self.inside:
                self.inside = []
                for x in range(-12, self.dimensions["height"] + 12):
                    self.inside += [[0 for _ in range(-12, self.dimensions["width"] + 12)]]
                self.inside[self.player[0]][self.player[1]] = 1
                processing = True
                while processing:
                    processing = False
                    for x, row in enumerate(self.inside):
                        for y, col in enumerate(row):
                            if col == 1:
                                if x > 0:
                                    if self.data[x - 1][y] != 4:
                                        if self.inside[x - 1][y] != -1:
                                            self.inside[x - 1][y] = 1
                                            processing = True
                                    else:
                                        self.inside[x - 1][y] = -2
                                if y > 0 and self.data[x][y - 1] != 4:
                                    if self.inside[x][y - 1] != -1:
                                        self.inside[x][y - 1] = 1
                                        processing = True
                                else:
                                    self.inside[x][y - 1] = -2
                                if self.data[x][y] != 4:
                                    if self.inside[x][y] != -1:
                                        self.inside[x][y] = 1
                                        processing = True
                                else:
                                    self.inside[x][y] = -2
                                if y < len(self.data[x]) - 1 and self.data[x][y + 1] != 4:
                                    if self.inside[x][y + 1] != -1:
                                        self.inside[x][y + 1] = 1
                                        processing = True
                                else:
                                    self.inside[x][y + 1] = -2
                                if x < len(self.data):
                                    if self.data[x + 1][y] != 4:
                                        if self.inside[x + 1][y] != -1:
                                            self.inside[x + 1][y] = 1
                                            processing = True
                                    else:
                                        self.inside[x + 1][y] = -2
                                self.inside[x][y] = -1
            self.background = surface.Surface(((self.dimensions["width"]*64)+1536, (self.dimensions["height"]*64)+1536))
            self.background.fill((10, 10, 32))
            for x in range(-12, self.dimensions["height"]+12):
                for y in range(-12, self.dimensions["width"]+12):
                    seed(sum(self.data[0]) + sum(self.data[-1]) + x + y)
                    draw_floor = False
                    if -1 <= x <= self.dimensions["height"]:
                        if -1 <= y <= self.dimensions["width"]:
                            if x < len(self.data):
                                if y < len(self.data[x])-1:
                                    if self.data[x][y+1] == 4:
                                        draw_floor = True
                                if 0 < y < len(self.data[x])+1:
                                    if self.data[x][y-1] == 4:
                                        draw_floor = True
                                if -1 <= x < len(self.data)-1:
                                    if y < len(self.data[x + 1]) - 1:
                                        if self.data[x + 1][y + 1] == 4:
                                            draw_floor = True
                                    if 0 < y < len(self.data[x + 1]) + 1:
                                        if self.data[x + 1][y - 1] == 4:
                                            draw_floor = True
                                if 1 <= x < len(self.data):
                                    if y < len(self.data[x - 1]) - 1:
                                        if self.data[x - 1][y + 1] == 4:
                                            draw_floor = True
                                    if 0 < y < len(self.data[x - 1]) + 1:
                                        if self.data[x - 1][y - 1] == 4:
                                            draw_floor = True
                            if 0 <= x <= self.dimensions["height"]:
                                if 0 <= y < len(self.data[x]):
                                    if self.data[x][y] == 4:
                                        continue
                                    elif self.inside[x][y]:
                                        self.background.blit(resources["sprite"]["gbrick"],
                                                             ((y + 11) * 64, (x + 11) * 64))
                                        continue
                        else:
                            if y < 0:
                                draw_floor = randint(0, abs(y)) < 1
                            elif y > len(self.data[x]):
                                draw_floor = randint(0, abs(y - len(self.data[x]))) < 1
                    else:
                        if 0 <= y <= self.dimensions["width"] + 1:
                            if x < 0:
                                draw_floor = randint(0, abs(x)) < 1
                            elif x > self.dimensions["height"] + 1:
                                draw_floor = randint(0, abs(x - self.dimensions["height"])) < 1
                    if draw_floor:
                        self.background.blit(resources["sprite"]["ggrass"], ((y+11)*64, (x+11)*64))
            for x, row in enumerate(self.data):
                for y, col in enumerate(row):
                    if 4 <= col <= 7:
                        if col == 4:
                            self.background.blit(resources["sprite"]["rbricksheet"],
                                                 ((y + 12) * 64, (x + 12) * 64),
                                                 area=self.precalculated_connections[x][y])
                        elif col == 7:
                            self.background.blit(resources["sprite"]["target"],
                                                 ((y + 12) * 64, (x + 12) * 64))
                        elif col != 5:
                            self.background.blit(resources["sprite"][tiles[col - 4]],
                                                 ((y + 12) * 64, (x + 12) * 64))
        modpos = [0, 0]
        observpos = [0, 0]
        if self.large["wide"]:
            modpos[1] = min(max(self.edge["vertical"], self.player[1]), self.dimensions["width"]-self.edge["vertical"])
            observpos[1] = self.player[1]-modpos[1]
            if self.notEdge[1]:
                self.notEdge[1] = self.edge["vertical"] < self.player[1] < self.dimensions["width"] - self.edge["vertical"]
            else:
                self.notEdge[1] = self.edge["vertical"] < self.player[1] < self.dimensions["width"] - self.edge["vertical"]
                if self.notEdge[1]:
                    slides["display"][1] += 64*(self.player[2]-2)
                    slides["character"][1] += 64*(self.player[2]-2)
        else:
            modpos[1] = self.corner["left"]
        if self.large["tall"]:
            modpos[0] = min(max(self.edge["horizontal"], self.player[0]), self.dimensions["height"]-self.edge["horizontal"])
            observpos[0] = self.player[0]-modpos[0]
            if self.notEdge[0]:
                self.notEdge[0] = self.edge["horizontal"] < self.player[0] < self.dimensions["height"] - self.edge["horizontal"]
            else:
                self.notEdge[0] = self.edge["horizontal"] < self.player[0] < self.dimensions["height"] - self.edge["horizontal"]
                if self.notEdge[0]:
                    slides["display"][0] -= 64*(self.player[2]-1)
                    slides["character"][0] -= 64*(self.player[2]-1)
        else:
            modpos[0] = self.corner["top"]
        screen.blit(self.background,
                    ((((screen_dimensions[0]/2)-32)-((modpos[1]*64)+768))
                     - ((slides["display"][1]) / parallax) - ((modsize / parallax) * modw)
                        if self.large["wide"] else
                     (modpos[1]-768) - (slides["display"][1] / parallax) - ((modsize / parallax) * modw),

                     (((screen_dimensions[1]/2)-32)-((modpos[0]*64)+768))
                     - (slides["display"][0] / parallax) - ((modsize / parallax) * mod)
                        if self.large["tall"] else
                     (modpos[0]-768) - (slides["display"][0] / parallax) - ((modsize / parallax) * mod)))
        for x, row in enumerate(self.data):
            for y, col in enumerate(row):
                if col in [5, 7]:
                    crateslide = slides["crate"] if self.last_crate_moved == [x, y] else [0, 0]
                    screen.blit(resources["sprite"][tiles[col - 4]],
                                (calc_place(y, self.large["wide"], modpos[1], screen_dimensions[0]) - crateslide[1]
                                 - (slides["display"][1] / parallax) - ((modsize / parallax) * modw),
                                 calc_place(x, self.large["tall"], modpos[0], screen_dimensions[1]) - crateslide[0]
                                 - (slides["display"][0] / parallax) - ((modsize / parallax) * mod)))
        if self.animation["ticks"] > 100:
            self.animation["ticks"] = 0
            self.animation["frame"] = 0 if self.animation["frame"] == 2 else self.animation["frame"]+1
        else:
            self.animation["ticks"] += dt
        if player:
            walkingframe = 4 * self.animation["frame"]\
                           if int((sum(slides["display"]) + sum(slides["character"])) / 10)\
                           else 0
            screen.blit(resources["sprite"]["player"][self.player[2] + walkingframe],
                        (((screen_dimensions[0]/2)-32 - (slides["display"][1] / 100) + (observpos[1] * 64) - (slides["character"][1]))
                        if self.large["wide"] else
                         (self.corner["left"] - slides["character"][1] - slides["display"][1] + self.player[1] * 64),

                         ((screen_dimensions[1]/2)-32 - (slides["display"][0] / 100) + (observpos[0] * 64) - (slides["character"][0]))
                        if self.large["tall"] else
                         (self.corner["top"] - slides["display"][0] - slides["character"][0] + self.player[0] * 64)))
        return
