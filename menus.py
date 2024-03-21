import text

class MenuHandler():
    def __init__(self):
        self.menu_index = [0, 0]

    def render_level_menu(self, screen, menu_dict):
        for offset, levelpack in enumerate(menu_dict):
            text.draw(screen, levelpack, (15, 20+(45*offset)), bold=True, shadow=True)
