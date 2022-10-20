import pygame as pg

class InputHandler:
    def __init__(self):
        self.pressed_keys = []

    def handle(self, game):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key not in self.pressed_keys:
                    self.pressed_keys.append(event.key)
                # Cut
                if not game.cutting and event.key == pg.K_q and game.plant.select_fern is not -1:
                    game.cut(game.plant, game.renderer)
                # Save
                if event.key == pg.K_s:
                    game.save()
                if event.key == pg.K_r:
                    game.reset()
                # Select fracplant
                if event.key == pg.K_0:
                    game.plant.select_fern(-1)
                if event.key == pg.K_1:
                    game.plant.select_fern(0)
                if event.key == pg.K_2:
                    game.plant.select_fern(1)
            if event.type == pg.KEYUP:
                if event.key in self.pressed_keys:           
                    self.pressed_keys.remove(event.key)
    
    def is_pressed(self, key):
        return key in self.pressed_keys

    def pop_key(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def close(self):
        self.pressed_keys.clear()