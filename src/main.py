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
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_c:
                    # Ask plant num prompt
                    def ask_plant_num():
                        answer = input("Which plant to cut?: ")
                        if answer.isdigit() and int(answer) < len(plant.ferns)\
                            and not answer.isspace(): return answer
                        else: return ask_plant_num()
                    plant_num = int(ask_plant_num())
                    # Ask cut id prompt. ! Implement check for if branch already cut !
                    def ask_cut_id():
                        answer = input("Which branch to cut?: ")
                        if answer.isdigit(): return ask_cut_id()
                        else: return answer
                    cut_id = ask_cut_id()
                    # Do te cutting
                    plant.ferns[plant_num].blocked_ids.append(cut_id)
                    lines = np.empty(Fern.lines_len(max_order)*2, dtype=tuple)
        clock.tick(1000.0/fps)
        screen.fill((0, 0, 0))
        time = pg.time.get_ticks()
        growth = 1 - 1 / (1 + time / 10000)
        #growth2 = 1 - 1 / (1 + time / 600)
        all_info = [
                {"lines": lines, "id": "", "order": 0, "end": round(max_order), "rot": 0, 
                    "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.02, "origin": origin},
                {"lines": lines, "id": "", "order": 0, "end": round(max_order), "rot": 0, 
                    "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.02, "origin": origin}
        ]
        plant.draw(all_info)
        rendr.draw_lines(screen, lines)
        rendr.render()
    
# Entry point
if __name__ == "__main__":
    main()

# References: 
# https://www.pygame.org/docs/tut/tom_games2.html