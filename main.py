import curses
import time
import logging
import argparse
import sys
import level as lvl
import lang

parser = argparse.ArgumentParser(description="SokoPy - A Python-based Sokoban Clone")
parser.add_argument('-l', '--lang', help="Picks language (from lang.py)", type=str, default="EN-US")
parser.add_argument('-v', '--verbose', help="Uses more verbose language in the log for debugging",
                    action='store_true')
parser.add_argument('-m', '--menusize', help="The amount of items to be displayed at once on a menu",
                    type=int, default=15)
parser.add_argument('-L', '--level', help="Loads directly into the specified level",
                    type=str, default="")
args = parser.parse_args()

logging.basicConfig(filename=('logs/sokopy'+str(int(time.time()))+'.log'),
                    level=(logging.DEBUG if args.verbose else logging.WARNING))
logging.info("Level module seemingly loaded OK!")


def main(stdscr):
    logging.info("Entered curses screen")
    curses.curs_set(0)

    curses.init_color(21, 0,   250, 0)
    curses.init_color(20, 750, 750, 0)
    curses.init_pair(1, curses.COLOR_RED,     curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN,   curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE,    curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW,  curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLACK,   20)
    curses.init_pair(6, 21,                   curses.COLOR_BLACK)
    curses.init_pair(7, 20,                   curses.COLOR_BLACK)

    lvlpack_list = lvl.get_levelpacks()
    if len(lvlpack_list) > 0:
        logging.info("Level packs seemingly loaded OK!")
    menu_items = lvl.menu_packs(lvlpack_list)
    menu_items["tut"] = lang.languages[args.lang][4]
    menu_items["quit"] = lang.languages[args.lang][5]
    select = 0
    running = True
    is_tut = False
    menu_limit = args.menusize
    modd = menu_limit % 2

    total_count = 0
    pack_count = 0
    logging.info("List of levelpacks and their level counts:")
    for pack in lvlpack_list:
        packcount = len(lvlpack_list[pack]["lvls"])
        logging.info(" - " + lvlpack_list[pack]["title"] + " | " + str(packcount) + " levels")
        total_count += packcount
        pack_count += 1
    logging.info("Total packs: " + str(pack_count) + " | Total Levels: " + str(total_count))

    def load_lvl(filedir: str):
        logging.info("Level load requested: " + str(filedir))
        map_content = lvl.decode_lvl("levels/" + filedir)
        player_loc = [-1, -1]
        player_last_dir = -1
        player_was_push = False
        game_stats = {
            "moves": 0,
            "pushes": 0,
            "b_lines": 0,
            "p_lines": 0
        }
        final_stats = None
        finished = False
        game_running = True
        clip = True
        logging.info("Level seemingly loaded OK!")
        while game_running:
            stdscr.clear()
            goal_visible = False
            stdscr.addstr(1, 4, lang.languages[args.lang][7].center(50), curses.A_REVERSE)
            if is_tut:
                stdscr.addstr(2, 4, "Get the boxes to the goal to win!".center(50), curses.A_REVERSE)
                #stdscr.addstr(2, 18, lvl.visTable[5], curses.color_pair(5))
                #stdscr.addstr(2, 33, lvl.visTable[6], curses.color_pair(2))
            stdscr.addstr((4 if is_tut else 2), 4,
                          (lang.languages[args.lang][8] + ": " + str(game_stats["pushes"]).ljust(4) + " | " + lang.languages[args.lang][9] + ": " + str(game_stats["moves"]).ljust(4)).center(50), curses.A_REVERSE)
            bl_width = lvl.visWidth
            bl_height = lvl.visHeight
            margin = 6 if is_tut else 4
            for y, row in enumerate(map_content):
                if not goal_visible:
                    goal_visible = (6 in row) or (8 in row)
                for x, item in enumerate(row):
                    if item == 3:
                        player_loc = [y, x]
                        map_content[y][x] = 2
                    elif item == 8:
                        player_loc = [y, x]
                        map_content[y][x] = 6
                    if [y, x] == player_loc:
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
                    final_stats = game_stats.copy()
                    logging.info("Player completed the level! Moves: " + str(final_stats["moves"]) +
                                 " | Pushes: " + str(final_stats["pushes"]))
                stdscr.addstr((margin-3)+round(len(map_content)/2), 4,
                              "!!" + lang.languages[args.lang][10].center(46) + "!!", curses.A_REVERSE)
                stdscr.addstr((margin+2)+round(len(map_content)/2), 4,
                              lang.languages[args.lang][15].center(50), curses.A_REVERSE)
                
                stdscr.addstr((margin-1)+round(len(map_content)/2), 4,
                              (" " + lang.languages[args.lang][11] + ": " + str(final_stats["pushes"]).ljust(6) +
                              (" " + lang.languages[args.lang][12] + ": " + str(final_stats["moves"]).ljust(6))).center(50), curses.A_REVERSE)
                stdscr.addstr((margin)+round(len(map_content)/2), 4,
                              (" " + lang.languages[args.lang][13] + ": " + str(final_stats["b_lines"]).ljust(6) +
                              (" " + lang.languages[args.lang][14] + ": " + str(final_stats["p_lines"]).ljust(6))).center(50), curses.A_REVERSE)
            inpup = stdscr.getkey()
            if inpup == "KEY_DOWN":
                if (not clip) or (lvl.atrTable[map_content[player_loc[0]+1][player_loc[1]]][0] == "1"):
                    player_loc[0] += 1
                    game_stats["moves"] += 1
                    if player_last_dir != 2:
                        game_stats["p_lines"] += 1
                    player_last_dir = 2
                    player_was_push = False
                elif lvl.atrTable[map_content[player_loc[0]+1][player_loc[1]]][1] == "1":
                    if lvl.atrTable[map_content[player_loc[0]+2][player_loc[1]]][0] == "1":
                        player_loc[0] += 1
                        game_stats["moves"] += 1
                        if player_last_dir != 2:
                            game_stats["p_lines"] += 1
                            if player_was_push:
                                game_stats["b_lines"] += 1
                        player_last_dir = 2
                        game_stats["pushes"] += 1
                        if not player_was_push:
                            player_was_push = True
                            game_stats["b_lines"] += 1
                        if map_content[player_loc[0]+1][player_loc[1]] == 6:
                            map_content[player_loc[0]+1][player_loc[1]] = 7
                        else:
                            map_content[player_loc[0]+1][player_loc[1]] = 5
                        if map_content[player_loc[0]][player_loc[1]] == 7:
                            map_content[player_loc[0]][player_loc[1]] = 6
                        else:
                            map_content[player_loc[0]][player_loc[1]] = 2
            elif inpup == "KEY_UP":
                if (not clip) or (lvl.atrTable[map_content[player_loc[0]-1][player_loc[1]]][0] == "1"):
                    player_loc[0] -= 1
                    game_stats["moves"] += 1
                    if player_last_dir != 0:
                        game_stats["p_lines"] += 1
                    player_last_dir = 0
                    player_was_push = False
                elif lvl.atrTable[map_content[player_loc[0]-1][player_loc[1]]][1] == "1":
                    if lvl.atrTable[map_content[player_loc[0]-2][player_loc[1]]][0] == "1":
                        player_loc[0] -= 1
                        game_stats["moves"] += 1
                        if player_last_dir != 0:
                            game_stats["p_lines"] += 1
                            if player_was_push:
                                game_stats["b_lines"] += 1
                        player_last_dir = 0
                        game_stats["pushes"] += 1
                        if not player_was_push:
                            player_was_push = True
                            game_stats["b_lines"] += 1
                        if map_content[player_loc[0]-1][player_loc[1]] == 6:
                            map_content[player_loc[0]-1][player_loc[1]] = 7
                        else:
                            map_content[player_loc[0]-1][player_loc[1]] = 5
                        if map_content[player_loc[0]][player_loc[1]] == 7:
                            map_content[player_loc[0]][player_loc[1]] = 6
                        else:
                            map_content[player_loc[0]][player_loc[1]] = 2
            elif inpup == "KEY_RIGHT":
                if (not clip) or (lvl.atrTable[map_content[player_loc[0]][player_loc[1]+1]][0] == "1"):
                    player_loc[1] += 1
                    game_stats["moves"] += 1
                    if player_last_dir != 1:
                        game_stats["p_lines"] += 1
                    player_last_dir = 1
                    player_was_push = False
                elif lvl.atrTable[map_content[player_loc[0]][player_loc[1]+1]][1] == "1":
                    if lvl.atrTable[map_content[player_loc[0]][player_loc[1]+2]][0] == "1":
                        player_loc[1] += 1
                        game_stats["moves"] += 1
                        if player_last_dir != 1:
                            game_stats["p_lines"] += 1
                            if player_was_push:
                                game_stats["b_lines"] += 1
                        player_last_dir = 1
                        game_stats["pushes"] += 1
                        if not player_was_push:
                            player_was_push = True
                            game_stats["b_lines"] += 1
                        if map_content[player_loc[0]][player_loc[1]+1] == 6:
                            map_content[player_loc[0]][player_loc[1]+1] = 7
                        else:
                            map_content[player_loc[0]][player_loc[1]+1] = 5
                        if map_content[player_loc[0]][player_loc[1]] == 7:
                            map_content[player_loc[0]][player_loc[1]] = 6
                        else:
                            map_content[player_loc[0]][player_loc[1]] = 2
            elif inpup == "KEY_LEFT":
                if (not clip) or (lvl.atrTable[map_content[player_loc[0]][player_loc[1]-1]][0] == "1"):
                    player_loc[1] -= 1
                    game_stats["moves"] += 1
                    if player_last_dir != 3:
                        game_stats["p_lines"] += 1
                    player_last_dir = 3
                    player_was_push = False
                elif lvl.atrTable[map_content[player_loc[0]][player_loc[1]-1]][1] == "1":
                    if lvl.atrTable[map_content[player_loc[0]][player_loc[1]-2]][0] == "1":
                        player_loc[1] -= 1
                        game_stats["moves"] += 1
                        if player_last_dir != 3:
                            game_stats["p_lines"] += 1
                            if player_was_push:
                                game_stats["b_lines"] += 1
                        player_last_dir = 3
                        game_stats["pushes"] += 1
                        if not player_was_push:
                            player_was_push = True
                            game_stats["b_lines"] += 1
                        if map_content[player_loc[0]][player_loc[1]-1] == 6:
                            map_content[player_loc[0]][player_loc[1]-1] = 7
                        else:
                            map_content[player_loc[0]][player_loc[1]-1] = 5
                        if map_content[player_loc[0]][player_loc[1]] == 7:
                            map_content[player_loc[0]][player_loc[1]] = 6
                        else:
                            map_content[player_loc[0]][player_loc[1]] = 2
            elif inpup == "r":
                map_content = lvl.decode_lvl("levels/" + filedir)
                player_loc = [-1, -1]
                game_stats["moves"] = 0
                game_stats["pushes"] = 0
                clip = True
            elif inpup == "p":
                if clip:
                    logging.info("Somebody's cheating!")
                    clip = False
                    game_stats["moves"] = 9000
                    game_stats["pushes"] = 1337
                else:
                    map_content = lvl.decode_lvl("levels/" + filedir)
                    player_loc = [-1, -1]
                    game_stats["moves"] = 0
                    game_stats["pushes"] = 0
                    clip = True
            elif inpup == "\n":
                logging.info("Returning to menu...")
                game_running = not game_running

    def load_pack(lvlpack):
        logging.info("Level pack load requested: " + str(lvlpack))
        packdata = lvlpack_list[lvlpack]
        third_variable = True
        sbelect = 0
        while third_variable:
            stdscr.clear()
            pack_content = list(packdata['lvls'].keys()) + [lang.languages[args.lang][6], ""]
            for indux in range(menu_limit):
                packitem = pack_content[(round(sbelect - ((menu_limit - modd) / 2)) + indux + 4) % len(pack_content)]
                if packitem == "":
                    continue
                else:
                    stdscr.addstr(indux+4, 2, "> " if indux == ((menu_limit-modd)/2)-4 else "- ", curses.color_pair(2))
                    stdscr.addstr(indux+4, 4, packitem, curses.color_pair(3 if indux == ((menu_limit-modd)/2)-4 else 1))
            stdscr.addstr(1, 4, packdata['title'], curses.A_REVERSE)
            stdscr.addstr(2, 4, packdata['desc'], curses.A_REVERSE)
            stdscr.addstr(menu_limit+5, 4, lang.languages[args.lang][3], curses.A_REVERSE)
            stdscr.refresh()
            imput = stdscr.getkey()
            if imput == "KEY_DOWN":
                sbelect = (0 if sbelect >= len(packdata['lvls']) else sbelect+1)
            elif imput == "KEY_UP":
                sbelect = (len(packdata['lvls']) if sbelect <= 0 else sbelect-1)
            elif imput == "\n":
                if sbelect == len(packdata['lvls']):
                    third_variable = False
                else:
                    load_lvl(lvlpack + "/" + list(packdata['lvls'].values())[sbelect])
            elif imput == "r":
                third_variable = False

    logging.info("Secondary definitions seemingly completed OK!")

    if args.level:
        logging.info("Level specified in command line...")
        load_lvl(args.level)
        sys.exit()

    logging.info("Giving user control... Stay back, this may go wrong.")

    while running:
        is_tut = False
        stdscr.clear()
        real_menu_items = list(menu_items.values()) + [""]
        for index in range(menu_limit):
            itemname = real_menu_items[(round(select-((menu_limit-modd)/2))+index+4) % (len(real_menu_items))]
            if itemname == "":
                continue
            else:
                stdscr.addstr(index+4, 2, "> " if index == ((menu_limit-modd)/2)-4 else "- ", curses.color_pair(2))
                stdscr.addstr(index+4, 4, itemname, curses.color_pair(3 if index == ((menu_limit-modd)/2)-4 else 1))
        stdscr.addstr(1, 4, lang.languages[args.lang][0] + "  -  " + lang.languages[args.lang][1] +": " + str(total_count), curses.A_REVERSE)
        stdscr.addstr(2, 4, lang.languages[args.lang][2], curses.A_REVERSE)
        stdscr.addstr(menu_limit+5, 4, lang.languages[args.lang][3], curses.A_REVERSE)
        stdscr.refresh()

        inp = stdscr.getkey()
        if inp == "KEY_DOWN":
            select = (0 if select >= len(menu_items)-1 else select+1)
        elif inp == "KEY_UP":
            select = (len(menu_items)-1 if select <= 0 else select-1)
        elif inp == "\n":
            if select == len(menu_items)-1:
                running = not running
            elif select == len(menu_items)-2:
                is_tut = True
                load_lvl("tutorial.lvl")
                select = 0
            else:
                load_pack(list(menu_items.keys())[select], )
        elif inp == "r":
            running = not running


logging.info("Primary definitions seemingly completed OK!")
curses.wrapper(main)
logging.info("Exiting out...")
