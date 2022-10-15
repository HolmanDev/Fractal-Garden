import pygame as pg

class InputHandler:
    def __input__(self):
        pass

    def handle(self, game):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN:
                # Cut
                if event.key == pg.K_q and game.plant.select_fern is not -1:
                    start_time = pg.time.get_ticks()
                    game.cut(game.plant, game.renderer)
                    end_time = pg.time.get_ticks()
                    game.time_offset = game.time_offset - (end_time - start_time) # Account for paused time.
                # Select fracplant
                if event.key == pg.K_0:
                    game.plant.select_fern(-1)
                if event.key == pg.K_1:
                    game.plant.select_fern(0)
                if event.key == pg.K_2:
                    game.plant.select_fern(1)