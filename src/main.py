import numpy as np
from fracplant import Fracplant
from fern import Fern
from renderer import Renderer
import pygame as pg
from math import pi

def main():
    print("Fractal Garden")
    pg.init()
    pg.display.set_caption("Fractal Garden")

    rendr = Renderer(1080, 640)
    clock = pg.time.Clock()
    screen = rendr.screen
    plant = Fracplant()
    plant.add_fern(0, 1, 0)
    plant.add_fern(0, 0.5, pi/20)
    max_order = 4
    lines = np.empty(Fern.lines_len(max_order)*2, dtype=tuple)
    origin = [550, rendr.height-100]
    fps = 8
    while 1:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        clock.tick(1000.0/fps)
        screen.fill((0, 0, 0))
        time = pg.time.get_ticks()
        growth = 1 - 1 / (1 + time / 10000)
        #growth2 = 1 - 1 / (1 + time / 600)
        info = {"lines": lines, "id": "", "order": 0, "end": round(max_order), "rot": 0, 
            "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.02, "origin": origin}
        plant.draw(info)
        rendr.draw_lines(screen, lines)
        rendr.render()
    
# Entry point
if __name__ == "__main__":
    main()

# References: 
# https://www.pygame.org/docs/tut/tom_games2.html