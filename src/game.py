import numpy as np
from fracplant import Fracplant
from input_handler import InputHandler
from fern import Fern
from renderer import Renderer
import pygame as pg
from math import pi

class Game:
    def __init__(self):
        self.plant = None
        self.input = InputHandler()
        self.renderer = Renderer(1080, 640)
        self.time_offset = 0

    # Runs at program start
    def start(self):
        self.renderer.init()
        pg.display.set_caption("Fractal Garden")

        clock = pg.time.Clock()
        origin = [550, self.renderer.height-100]
        self.plant = Fracplant(origin, 4)
        self.plant.add_fern(0, 1, 0)
        self.plant.add_fern(0, 0.5, pi/20)
        self.plant.set_lines(np.empty(Fern.lines_len(self.plant.max_order)*2, dtype=tuple))
        self.plant.empty_lines()
        self.renderer.set_fps(8)
        frame_time = pg.time.get_ticks()
        # Main loop
        while 1:
            # Make time between frames for calculations. Threads?
            if pg.time.get_ticks() - frame_time > 1000/self.renderer.fps:
                frame_time = pg.time.get_ticks()
                self.update()
                clock.tick(self.renderer.fps)

    # Runs every frame
    def update(self):
        # Break into keyhandling function
        self.input.handle(self)
        self.renderer.screen.fill((0, 0, 0))
        #pg.draw.circle(screen, (255, 0, 0), pg.mouse.get_pos(), 4)
        time = pg.time.get_ticks() + self.time_offset
        growth = 1 - 1 / (1 + time / 10000)
        all_info = [
                {"lines": self.plant.lines, "id": "", "order": 0, "end": round(self.plant.max_order), "rot": 0, 
                    "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.05, "origin": self.plant.origin},
                {"lines": self.plant.lines, "id": "", "order": 0, "end": round(self.plant.max_order), "rot": 0, 
                    "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.02, "origin": self.plant.origin}
        ]
        self.plant.draw(all_info)
        self.renderer.draw_lines(self.renderer.screen, self.plant.lines, (255, 255, 255))
        self.renderer.render()

    def cut(self, plant, rendr):
        cut = False
        p1 = pg.mouse.get_pos() #p1 placed
        # Pause to place p2
        while not cut:
            # Poll for second Q-press
            # BREAK THIS INTO INPUT HANDLER SOMEHOW. Send trigger info pipeline to while loop?
            es = pg.event.get()
            for e in es:
                if e.type == pg.KEYDOWN:
                    if e.key == pg.K_q:
                        p2 = pg.mouse.get_pos() #p2 placed
                        plant.cut(plant.selected_fern, p1, p2, rendr) # cut fracplant from p1 to p2
                        cut = True                   
                        plant.lines.fill((None, None))