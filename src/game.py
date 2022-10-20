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
        self.cutting = False
        pg.font.init()
        self.pixel_font_small = pg.font.Font('fonts/Pixeled.ttf', 5)
        self.x = self.pixel_font_small.render('x', True, (255, 0, 0))
        self.x_rect = self.x.get_rect()

    # Runs at program start
    def start(self):
        self.renderer.init()
        pg.display.set_caption("Fractal Garden")
        
        # Load files
        data = []
        found_data = False
        try:
            with open("saves/recent.txt", 'r') as f:
                data = f.readlines()
        except FileNotFoundError:
            print("No save file found")
        else:
            found_data = True
        
        clock = pg.time.Clock()
        origin = [550, self.renderer.height-100]
        self.plant = Fracplant(origin, 4)
        self.plant.add_fern(0, 1, 0)
        self.plant.add_fern(0, 0.5, pi/20)
        self.plant.set_lines(np.empty(Fern.lines_len(self.plant.max_order)*2, dtype=tuple))
        self.plant.empty_lines()
        if(found_data):
            i = 0
            for fern in self.plant.ferns:
                fern_data = data[i].rstrip()
                fern_data = self.remove_multiple(fern_data, ['{', '}', '[', ']', ',', '\'']).split()
                fern.blocked_ids = fern_data
                i += 1
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
        #pg.draw.circle(self.renderer.screen, (255, 0, 0), pg.mouse.get_pos(), 4)
        self.x_rect.center = pg.mouse.get_pos()
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
        self.renderer.screen.blit(self.x, self.x_rect)
        self.renderer.render()

    def cut(self, plant, rendr):
        self.cutting = True
        start_time = pg.time.get_ticks()

        # Cut plant from one point (p1) to another point (p2)
        p1 = pg.mouse.get_pos() # p1 placed
        # Pause to place p2
        self.input.pop_key(pg.K_q)
        while not self.input.is_pressed(pg.K_q): 
            self.renderer.screen.fill((0, 0, 0))
            self.renderer.draw_lines(self.renderer.screen, self.plant.lines, (255, 255, 255)) # again, move this to different surface
            pg.draw.line(rendr.screen, (100, 100, 100), p1, pg.mouse.get_pos(), 1)
            self.renderer.render()
            self.input.handle(self)
        p2 = pg.mouse.get_pos() # p2 placed
        # cut fracplant from p1 to p2
        plant.cut(plant.selected_fern, p1, p2, rendr)

        plant.lines.fill((None, None))
        end_time = pg.time.get_ticks()
        self.cutting = False 
        self.time_offset -= end_time - start_time # Account for paused time.
    
    def save(self):
        with open("saves/recent.txt", 'w') as f:
            data = ""
            for fern in self.plant.ferns:
                data += f"{{{str(fern.blocked_ids)}}}\n"
            f.write(data)

    def reset(self):
        for fern in self.plant.ferns:
            fern.blocked_ids = []

    def remove_multiple(self, str, chars):
        for c in chars:
            str = str.replace(c, '')
        return str