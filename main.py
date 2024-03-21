import os
from contextlib import redirect_stdout
with redirect_stdout(None):  # This stops pygame from printing the import message
    import pygame
from pygame.locals import QUIT
import game_states
import menus

def load_file(filename: str) -> str:
    "Loads a file"
    return os.path.join(os.path.dirname(__file__), filename)

test_dict = {
    "Episode 1": 12,
    "Episode 2": 15,
    "Episode 3": 7
}


def main():
    "Main Game Code"
    pygame.init()
    pygame.display.set_caption('SokoPy')
    screen = pygame.display.set_mode([960, 960], pygame.RESIZABLE)
    clock = pygame.time.Clock()
    states = game_states.GameStateHandler()
    menu = menus.MenuHandler()
    # Event loop
    while True:
        dt = clock.tick(60)
        _ = dt
        screen.fill((20, 20, 50))
        for event in pygame.event.get():
            if event.type == QUIT:
                return
        if states.current_state == game_states.MENU:
            menu.render_level_menu(screen, test_dict)
        pygame.display.flip()

if __name__ == '__main__':
    main()
