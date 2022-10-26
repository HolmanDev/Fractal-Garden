import pygame as pg

# Take care of user input and delegate bound functionality
class InputHandler:
    def __init__(self):
        self.pressed_keys = []

    def handle(self, game):
        for event in pg.event.get():
            # On quit
            if event.type == pg.QUIT:
                print("Tried quitting")
                game.quit()
                pg.quit()
                quit()

            # Key pressed
            if event.type == pg.KEYDOWN:
                if event.key not in self.pressed_keys:
                    self.pressed_keys.append(event.key)
                # Cut
                if not game.cutting and event.key == pg.K_q and game.fracplant.select_branch != -1:
                    game.cut(game.fracplant)
                # Save
                if event.key == pg.K_s:
                    game.save()
                if event.key == pg.K_r:
                    game.reset()
                # Select fracplant
                if event.key == pg.K_0:
                    game.fracplant.select_branch(-1)
                if event.key == pg.K_1:
                    game.fracplant.select_branch(0)
                if event.key == pg.K_2:
                    game.fracplant.select_branch(1)
            
            # Key lifted
            if event.type == pg.KEYUP:
                if event.key in self.pressed_keys:
                    self.pressed_keys.remove(event.key)
    
    # Check if a key is pressed
    def is_pressed(self, key):
        return key in self.pressed_keys

    # Remove a specific key from <pressed_keys>
    def pop_key(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    # Clear <pressed_keys>
    def close(self):
        self.pressed_keys.clear()