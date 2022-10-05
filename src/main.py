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
    lines.fill((None, None))
    origin = [550, rendr.height-100]
    fps = 8
    time_offset = 0
    # Main loop
    frame_time = pg.time.get_ticks()
    while 1:
        if pg.time.get_ticks() - frame_time > 1000/fps:
            frame_time = pg.time.get_ticks()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN:
                    # Cutting
                    if event.key == pg.K_q:
                        cut = False
                        start_time = pg.time.get_ticks()
                        p1 = pg.mouse.get_pos() #p1 placed
                        # Pause to place p2
                        while not cut:
                            # Poll for second Q-press
                            es = pg.event.get()
                            for e in es:
                                if e.type == pg.KEYDOWN:
                                    if e.key == pg.K_q:
                                        p2 = pg.mouse.get_pos() #p2 placed
                                        plant.cut(0, p1, p2, rendr) # cut fracplant from p1 to p2
                                        cut = True
                                        end_time = pg.time.get_ticks()
                                        time_offset -= end_time - start_time # Account for paused time
                                        lines.fill((None, None))
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
            clock.tick(fps)
            screen.fill((0, 0, 0))
            #pg.draw.circle(screen, (255, 0, 0), pg.mouse.get_pos(), 4)
            time = pg.time.get_ticks() + time_offset
            growth = 1 - 1 / (1 + time / 10000)
            #growth2 = 1 - 1 / (1 + time / 600)
            all_info = [
                    {"lines": lines, "id": "", "order": 0, "end": round(max_order), "rot": 0, 
                        "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.05, "origin": origin},
                    {"lines": lines, "id": "", "order": 0, "end": round(max_order), "rot": 0, 
                        "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.02, "origin": origin}
            ]
            plant.draw(all_info)
            rendr.draw_lines(screen, lines, (255, 255, 255))
            rendr.render()
    
# Entry point
if __name__ == "__main__":
    main()

# References: 
# https://www.pygame.org/docs/tut/tom_games2.html