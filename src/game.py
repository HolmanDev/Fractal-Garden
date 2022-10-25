import numpy as np
from fracplant import Fracplant
from input_handler import InputHandler
from fern import Fern
from renderer import Renderer
import pygame as pg
from math import pi
import threading
import multiprocessing as mp
from time import sleep

def yefunc():
    pass

class Game:
    def __init__(self):
        self.plant = None
        self.input = InputHandler()
        self.renderer = Renderer(1080, 640, (0, 0, 0))
        self.time_offset = 0
        self.cutting = False

        pg.font.init()
        self.pixel_font_small = pg.font.Font('fonts/Pixeled.ttf', 7)
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
        self.renderer.set_fps(32)
        frame_time = pg.time.get_ticks()
        self.start_fracplant_calc()
        # Main loop
        while 1:
            # Make time between frames for calculations. Threads?
            if pg.time.get_ticks() - frame_time > 1000/self.renderer.fps:
                frame_time = pg.time.get_ticks()
                self.update()
                clock.tick(self.renderer.fps)

    def start_fracplant_calc(self):
        self.calc_queue = mp.Queue() # Use queue instead to send kill-call
        self.calc_process = mp.Process(target=calculate_fracplants, 
            args=(self.plant, self.calc_queue, self.time_offset + pg.time.get_ticks()))
        self.calc_process.start()

    def end_fracplant_calc(self):
        self.calc_queue.put([1, -1])
        self.calc_process.join()
        self.calc_process.close()

    # Runs every frame
    def update(self):
        # Handle input
        self.input.handle(self)

        # Clear screen
        self.renderer.clear()
        self.renderer.clear_ui()
        # UI
        self.x_rect.center = pg.mouse.get_pos()
        self.renderer.ui_layer.blit(self.x, self.x_rect)
        # Fracplants
        msg = []
        while not self.calc_queue.empty():
            msg = self.calc_queue.get()
        if len(msg):
            if msg[0] == 0:
                data = msg[1]
                self.plant.set_lines(data[0])
                i = 0
                for frn in self.plant.ferns:
                    frn.info = data[1][i]
                    i+=1
            elif msg[0] == 1:
                self.calc_queue.put(msg)
        self.renderer.fractal_layer.fill((0, 0, 0, 0))
        self.renderer.draw_lines(self.renderer.fractal_layer, self.plant.lines, (255, 255, 255))
        # Render
        self.renderer.render()

    def cut(self, plant, rendr):
        self.cutting = True
        self.end_fracplant_calc()
        start_time = pg.time.get_ticks()

        # Cut plant from one point (p1) to another point (p2)
        p1 = pg.mouse.get_pos() # p1 placed
        # Pause to place p2
        self.input.pop_key(pg.K_q)
        while not self.input.is_pressed(pg.K_q): 
            self.renderer.fractal_layer.fill((0, 0, 0))
            self.renderer.draw_lines(self.renderer.fractal_layer, self.plant.lines, (255, 255, 255)) # again, move this to different surface
            pg.draw.line(rendr.fractal_layer, (100, 100, 100), p1, pg.mouse.get_pos(), 1)
            self.renderer.render()
            self.input.handle(self)
        p2 = pg.mouse.get_pos() # p2 placed
        # cut fracplant from p1 to p2
        plant.cut(plant.selected_fern, p1, p2, rendr)

        plant.lines.fill((None, None))
        end_time = pg.time.get_ticks()
        self.cutting = False 
        self.time_offset -= end_time - start_time # Account for paused time.
        self.start_fracplant_calc()
    
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

# Multiprocessing requires this to be outside the class
def calculate_fracplants(plant, calc_queue, time_offset):
    pg.init()
    while 1:
        msg = []
        while not calc_queue.empty():
            msg = calc_queue.get()
        if len(msg):
            if msg[0] == 1:
                if msg[1] == -1:
                    return
        
        time = pg.time.get_ticks() + time_offset
        growth = 1 - 1 / (1 + time / 10000)
        all_info = [
            {"lines": plant.lines, "id": "", "order": 0, "end": round(plant.max_order), "rot": 0, 
                "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.05, "origin": plant.origin},
            {"lines": plant.lines, "id": "", "order": 0, "end": round(plant.max_order), "rot": 0, 
                "scale_factor": 80 * growth, "sway": time / 1000, "sway_scale": 0.02, "origin": plant.origin}
        ]
        plant.draw(all_info)
        calc_queue.put([0, [plant.lines, [frn.info for frn in plant.ferns]]])
        #print((pg.time.get_ticks() + time_offset - time))
        sleep(1/8 - min((pg.time.get_ticks() + time_offset - time)/1000.0, 1/8)) # Only execute every 8th second