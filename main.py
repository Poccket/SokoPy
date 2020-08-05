import curses
import time

import level as lvl


def main(stdscr):
    curses.curs_set(0)

    curses.init_pair(1, curses.COLOR_RED    , curses.COLOR_BLACK )
    curses.init_pair(2, curses.COLOR_GREEN  , curses.COLOR_BLACK )
    curses.init_pair(3, curses.COLOR_BLUE   , curses.COLOR_BLACK )
    curses.init_color(20, 750, 750, 0)
    curses.init_pair(4, curses.COLOR_BLACK  , 20                 )
    curses.init_pair(5, curses.COLOR_YELLOW , curses.COLOR_BLACK )
    curses.init_color(21, 0, 250, 0)
    curses.init_pair(6, 21                  , curses.COLOR_BLACK )
    curses.init_pair(7, 20                  , curses.COLOR_BLACK )

    inp = ""
    lvlpack_list = lvl.get_levelpacks()
    lvlpack_list["tut"] = {"title": "Tutorial"}
    lvlpack_list["quit"] = {"title": "Exit game"}
    select = 0
    running = True


    def load_lvl(filedir: str):
        mapContent = lvl.decode_lvl("levels/" + filedir)
        playerLoc = [-1, -1]
        gameRunning = True
        clip = True
        while gameRunning:
            stdscr.clear()
            height = 1
            length = 4
            goal_visible = False
            stdscr.addstr(1, 4, "Arrow keys to move, R to restart, Enter to exit", curses.A_REVERSE)
            stdscr.addstr(2, 4, "Get the boxes [] to the goal <> to win!", curses.A_REVERSE)
            for y, row in enumerate(mapContent):
                if not goal_visible:
                    goal_visible = 6 in row
                for x, item in enumerate(row):
                    if item == 3:
                        playerLoc = [y, x]
                        mapContent[y][x] = 2
                    if [y, x] == playerLoc:
                        stdscr.addstr(4+y, 4+x*2, lvl.visTable[3], curses.color_pair(4))
                    elif item == 2:
                        stdscr.addstr(4+y, 4+x*2, lvl.visTable[item], curses.color_pair(6))
                    elif item == 5:
                        stdscr.addstr(4+y, 4+x*2, lvl.visTable[item], curses.color_pair(5))
                    elif item == 7:
                        stdscr.addstr(4+y, 4+x*2, lvl.visTable[item], curses.color_pair(7))
                    else:
                        stdscr.addstr(4+y, 4+x*2, lvl.visTable[item])
            stdscr.refresh()
            if not goal_visible:
                stdscr.addstr(2+round(len(mapContent)/2), 4, "(:        GOOD JOB! YOU WON!       :)", curses.A_REVERSE)
                stdscr.addstr(3+round(len(mapContent)/2), 4, "(:  PRESS ENTER TO RETURN TO MENU  :)", curses.A_REVERSE)
            inp = stdscr.getkey()
            if inp == "KEY_DOWN":
                if (not clip) or (lvl.atrTable[mapContent[playerLoc[0]+1][playerLoc[1]]][0] == "1"):
                    playerLoc[0] += 1
                elif lvl.atrTable[mapContent[playerLoc[0]+1][playerLoc[1]]][1] == "1":
                    if lvl.atrTable[mapContent[playerLoc[0]+2][playerLoc[1]]][0] == "1":
                        playerLoc[0] += 1
                        if mapContent[playerLoc[0]+1][playerLoc[1]] == 6:
                            mapContent[playerLoc[0]+1][playerLoc[1]] = 7
                        else:
                            mapContent[playerLoc[0]+1][playerLoc[1]] = 5
                        if mapContent[playerLoc[0]][playerLoc[1]] == 7:
                            mapContent[playerLoc[0]][playerLoc[1]] = 6
                        else:
                            mapContent[playerLoc[0]][playerLoc[1]] = 2
            elif inp == "KEY_UP":
                if (not clip) or (lvl.atrTable[mapContent[playerLoc[0]-1][playerLoc[1]]][0] == "1"):
                    playerLoc[0] -= 1
                elif lvl.atrTable[mapContent[playerLoc[0]-1][playerLoc[1]]][1] == "1":
                    if lvl.atrTable[mapContent[playerLoc[0]-2][playerLoc[1]]][0] == "1":
                        playerLoc[0] -= 1
                        if mapContent[playerLoc[0]-1][playerLoc[1]] == 6:
                            mapContent[playerLoc[0]-1][playerLoc[1]] = 7
                        else:
                            mapContent[playerLoc[0]-1][playerLoc[1]] = 5
                        if mapContent[playerLoc[0]][playerLoc[1]] == 7:
                            mapContent[playerLoc[0]][playerLoc[1]] = 6
                        else:
                            mapContent[playerLoc[0]][playerLoc[1]] = 2
            elif inp == "KEY_RIGHT":
                if (not clip) or (lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]+1]][0] == "1"):
                    playerLoc[1] += 1
                elif lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]+1]][1] == "1":
                    if lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]+2]][0] == "1":
                        playerLoc[1] += 1
                        if mapContent[playerLoc[0]][playerLoc[1]+1] == 6:
                            mapContent[playerLoc[0]][playerLoc[1]+1] = 7
                        else:
                            mapContent[playerLoc[0]][playerLoc[1]+1] = 5
                        if mapContent[playerLoc[0]][playerLoc[1]] == 7:
                            mapContent[playerLoc[0]][playerLoc[1]] = 6
                        else:
                            mapContent[playerLoc[0]][playerLoc[1]] = 2
            elif inp == "KEY_LEFT":
                if (not clip) or (lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]-1]][0] == "1"):
                    playerLoc[1] -= 1
                elif lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]-1]][1] == "1":
                    if lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]-2]][0] == "1":
                        playerLoc[1] -= 1
                        if mapContent[playerLoc[0]][playerLoc[1]-1] == 6:
                            mapContent[playerLoc[0]][playerLoc[1]-1] = 7
                        else:
                            mapContent[playerLoc[0]][playerLoc[1]-1] = 5
                        if mapContent[playerLoc[0]][playerLoc[1]] == 7:
                            mapContent[playerLoc[0]][playerLoc[1]] = 6
                        else:
                            mapContent[playerLoc[0]][playerLoc[1]] = 2
            elif inp == "r":
                mapContent = lvl.decode_lvl("levels/" + filedir)
                playerLoc = [-1, -1]
            elif inp == "p":
                clip = False
            elif inp == "\n":
                gameRunning = not gameRunning


    def load_pack(lvlpack):
        packdata = lvlpack_list[lvlpack]
        packdata['lvls']['Back to menu'] = None
        ThirdVariable = True
        sbelect = 0
        while ThirdVariable:
            stdscr.clear()
            for index, pack in zip(range(len(packdata['lvls'])), packdata['lvls']):
                stdscr.addstr(index+4, 2, "> " if index == sbelect else "- ", curses.color_pair(2))
                stdscr.addstr(index+4, 4, pack, curses.color_pair(1))
            stdscr.addstr(1, 4, packdata['title'], curses.A_REVERSE)
            stdscr.addstr(2, 4, packdata['desc'], curses.A_REVERSE)
            stdscr.refresh()
            inp = stdscr.getkey()
            if inp == "KEY_DOWN":
                sbelect = (0 if sbelect >= len(packdata['lvls'])-1 else sbelect+1)
            elif inp == "KEY_UP":
                sbelect = (len(packdata['lvls'])-1 if sbelect <= 0 else sbelect-1)
            elif inp == "\n":
                if sbelect == len(packdata['lvls'])-1:
                    ThirdVariable = not ThirdVariable
                else:
                    load_lvl(lvlpack + "/" + list(packdata['lvls'].values())[select])


    while running:
        stdscr.clear()
        for index, pack in zip(range(len(lvlpack_list)), lvlpack_list):
            stdscr.addstr(index+4, 2, "> " if index == select else "- ", curses.color_pair(2))
            stdscr.addstr(index+4, 4, lvlpack_list[pack]['title'], curses.color_pair(1))
        stdscr.addstr(1, 4, "SokoPy v0.1", curses.A_REVERSE)
        stdscr.addstr(2, 4, "A Sokoban clone made in Python", curses.A_REVERSE)
        stdscr.refresh()

        inp = stdscr.getkey()
        if inp == "KEY_DOWN":
            select = (0 if select >= len(lvlpack_list)-1 else select+1)
        elif inp == "KEY_UP":
            select = (len(lvlpack_list)-1 if select <= 0 else select-1)
        elif inp == "\n":
            if select == len(lvlpack_list)-1:
                running = not running
            elif select == len(lvlpack_list)-2:
                load_lvl("tutorial.lvl")
                select = 0
            else:
                load_pack(list(lvlpack_list.keys())[select], )


curses.wrapper(main)
