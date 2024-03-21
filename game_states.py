# Constants
MENU = 10

class GameStateHandler():
    def __init__(self, init_state=MENU):
        self.current_state = init_state
        self.sub_state = ""

    def change_state(self, new_state):
        self.current_state = new_state
        self.sub_state = ""

    def change_sub_state(self, new_state):
        self.sub_state = new_state
