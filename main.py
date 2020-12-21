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
    is_tut = False

    def load_lvl(filedir: str):
        mapContent = lvl.decode_lvl("levels/" + filedir)
        playerLoc = [-1, -1]
        moves = 0
        pushes = 0
        finished = False
        gameRunning = True
        clip = True
        while gameRunning:
            stdscr.clear()
            height = 1
            length = 4
            goal_visible = False
            stdscr.addstr(1, 4, "Arrow keys to move, R to restart, Enter to exit", curses.A_REVERSE)
            if is_tut:
                stdscr.addstr(2, 4, "Get the boxes    to the goal    to win!", curses.A_REVERSE)
                stdscr.addstr(2, 18, lvl.visTable[5], curses.color_pair(5))
                stdscr.addstr(2, 33, lvl.visTable[6], curses.color_pair(2))
            stdscr.addstr((4 if is_tut else 2), 4, ("Moves: " + str(moves).ljust(6) + " | Pushes: " + str(pushes).ljust(6)), curses.A_REVERSE)

            bl_width = lvl.visWidth
            bl_height = lvl.visHeight
            margin = 6 if is_tut else 4
            for y, row in enumerate(mapContent):
                if not goal_visible:
                    goal_visible = 6 in row
                for x, item in enumerate(row):
                    if item == 3:
                        playerLoc = [y, x]
                        mapContent[y][x] = 2
                    elif item == 8:
                        playerLoc = [y, x]
                        mapContent[y][x] = 6
                    if [y, x] == playerLoc:
                        stdscr.addstr(margin+y*bl_height, 4+x*bl_width, lvl.visTable[3], curses.color_pair(4))
                    elif item == 2:
                        stdscr.addstr(margin+y*bl_height, 4+x*bl_width, lvl.visTable[item], curses.color_pair(6))

                    elif item == 5:
                        stdscr.addstr(margin+y*bl_height, 4+x*bl_width, lvl.visTable[item], curses.color_pair(5))
                    elif item == 6:
                        stdscr.addstr(margin+y*bl_height, 4+x*bl_width, lvl.visTable[item], curses.color_pair(2))
                    elif item == 7:
                        stdscr.addstr(margin+y*bl_height, 4+x*bl_width, lvl.visTable[item], curses.color_pair(7))
                    else:
                        stdscr.addstr(margin+y*bl_height, 4+x*bl_width, lvl.visTable[item])
            stdscr.refresh()
            if not goal_visible:
                if not finished:
                    finished = True
                    final_score = [moves, pushes]

                stdscr.addstr((margin-2)+round(len(mapContent)/2), 4, "!!        GOOD JOB! YOU WON!       !!", curses.A_REVERSE)
                stdscr.addstr((margin-1)+round(len(mapContent)/2), 4, (" TOTAL PUSHES: " + str(final_score[1]).ljust(4) + ("TOTAL MOVES: " + str(final_score[0])).rjust(17) + " "), curses.A_REVERSE)
                stdscr.addstr((margin+1)+round(len(mapContent)/2), 4, "    PRESS ENTER TO RETURN TO MENU    ", curses.A_REVERSE)
            inp = stdscr.getkey()
            if inp == "KEY_DOWN":
                if (not clip) or (lvl.atrTable[mapContent[playerLoc[0]+1][playerLoc[1]]][0] == "1"):
                    playerLoc[0] += 1
                    moves += 1
                elif lvl.atrTable[mapContent[playerLoc[0]+1][playerLoc[1]]][1] == "1":
                    if lvl.atrTable[mapContent[playerLoc[0]+2][playerLoc[1]]][0] == "1":
                        playerLoc[0] += 1
                        moves += 1
                        pushes += 1
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
                    moves += 1
                elif lvl.atrTable[mapContent[playerLoc[0]-1][playerLoc[1]]][1] == "1":
                    if lvl.atrTable[mapContent[playerLoc[0]-2][playerLoc[1]]][0] == "1":
                        playerLoc[0] -= 1
                        moves += 1
                        pushes += 1
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
                    moves += 1
                elif lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]+1]][1] == "1":
                    if lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]+2]][0] == "1":
                        playerLoc[1] += 1
                        moves += 1
                        pushes += 1
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
                    moves += 1
                elif lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]-1]][1] == "1":
                    if lvl.atrTable[mapContent[playerLoc[0]][playerLoc[1]-2]][0] == "1":
                        playerLoc[1] -= 1
                        moves += 1
                        pushes += 1
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
                moves = 0
                pushes = 0
                clip = True
            elif inp == "p":
                if clip:
                    clip = False
                    moves = 9000
                    pushes = 1337
                else:
                    mapContent = lvl.decode_lvl("levels/" + filedir)
                    playerLoc = [-1, -1]
                    moves = 0
                    pushes = 0
                    clip = True
            elif inp == "\n":
                gameRunning = not gameRunning


    def load_pack(lvlpack):
        packdata = lvlpack_list[lvlpack]
        ThirdVariable = True
        sbelect = 0
        while ThirdVariable:
            stdscr.clear()
            entriesBritten = 0
            for index, pack in zip(range(len(packdata['lvls'])+1), ["Back to menu..."] + list(packdata['lvls'].keys())):
                if len(packdata['lvls'])+1 > 7:
                    if index < (sbelect-3):
                        if (sbelect+3) < len(packdata['lvls'])+1:
                            continue
                        elif index < (len(packdata['lvls'])-6):
                            continue
                    if entriesBritten >= 7:
                        break
                entriesBritten += 1
                stdscr.addstr(entriesBritten+3, 2, "> " if index == sbelect else "- ", curses.color_pair(2))
                stdscr.addstr(entriesBritten+3, 4, pack, curses.color_pair(3 if index == sbelect else 1))
            stdscr.addstr(1, 4, packdata['title'], curses.A_REVERSE)
            stdscr.addstr(2, 4, packdata['desc'], curses.A_REVERSE)
            stdscr.addstr(12, 4, "Up/Down to move the cursor, Enter to select", curses.A_REVERSE)
            stdscr.refresh()
            inp = stdscr.getkey()
            if inp == "KEY_DOWN":
                sbelect = (0 if sbelect >= len(packdata['lvls']) else sbelect+1)
            elif inp == "KEY_UP":
                sbelect = (len(packdata['lvls']) if sbelect <= 0 else sbelect-1)
            elif inp == "\n":
                if sbelect == 0:
                    ThirdVariable = False
                else:
                    load_lvl(lvlpack + "/" + list(packdata['lvls'].values())[sbelect-1])
            elif inp == "r":
                ThirdVariable = False


    while running:
        is_tut = False
        stdscr.clear()
        entriesWritten = 0
        for index, pack in zip(range(len(lvlpack_list)), lvlpack_list):
            if len(lvlpack_list) > 7:
                if index < (select-3):
                    if (sbelect+3) < len(lvlpack_list):
                        continue
                    elif index < (len(lvlpack_list)-7):
                        continue
                if entriesWritten > 7:
                    break
            entriesWritten += 1
            stdscr.addstr(entriesWritten+3, 2, "> " if index == select else "- ", curses.color_pair(2))
            stdscr.addstr(entriesWritten+3, 4, lvlpack_list[pack]['title'], curses.color_pair(3 if index == select else 1))
        stdscr.addstr(1, 4, "SokoPy v1.0", curses.A_REVERSE)
        stdscr.addstr(2, 4, "A Sokoban clone made in Python", curses.A_REVERSE)
        stdscr.addstr(12, 4, "Up/Down to move the cursor, Enter to select", curses.A_REVERSE)
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
                is_tut = True
                load_lvl("tutorial.lvl")
                select = 0
            else:
                load_pack(list(lvlpack_list.keys())[select], )


curses.wrapper(main)
