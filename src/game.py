import numpy as np
from fracplant import Fracplant
from input_handler import InputHandler
from branch import Branch
from renderer import Renderer
import pygame as pg
from math import pi
import threading
import multiprocessing as mp
from time import sleep
from constants import *

class Game:
    def __init__(self):
        self.fracplant = None
        self.input = InputHandler()
        self.renderer = Renderer(1080, 640, NIGHT)
        self.time_offset = 0
        self.cutting = False

        pg.font.init()
        self.pixel_font_small = pg.font.Font('fonts/Pixeled.ttf', 7)
        self.x = self.pixel_font_small.render('x', True, RED)
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
        self.fracplant = Fracplant(origin, 4)
        self.fracplant.add_branch(0, 1, 0)
        self.fracplant.add_branch(0, 0.5, pi/20)
        self.fracplant.set_lines(np.empty(Branch.lines_len(self.fracplant.max_order)*2, dtype=tuple))
        self.fracplant.empty_lines()
        if(found_data):
            i = 0
            for branch in self.fracplant.branches:
                branch_data = data[i].rstrip()
                branch_data = self.remove_multiple(branch_data, ['{', '}', '[', ']', ',', '\'']).split()
                branch.blocked_ids = branch_data
                i += 1
        self.renderer.set_fps(32)
        frame_time = pg.time.get_ticks()
        self.start_fracplant_process() # Multiprocessing
        # Main loop
        while 1:
            # Make time between frames for calculations. Threads?
            if pg.time.get_ticks() - frame_time > 1000/self.renderer.fps:
                frame_time = pg.time.get_ticks()
                self.update()
                clock.tick(self.renderer.fps)

    # Runs every frame
    def update(self):
        # Handle input
        self.input.handle(self)

        # Generate visuals
        self.renderer.clear_background_layer()
        self.generate_ui()
        self.generate_fracplants()

        # Render
        self.renderer.render()

    def generate_ui(self):
        self.renderer.clear_ui_layer()
        mouse_pos = pg.mouse.get_pos()
        self.x_rect.center = (mouse_pos[0]+2, mouse_pos[1]-1)
        self.renderer.ui_layer.blit(self.x, self.x_rect)

    def generate_fracplants(self):
        # Read and act on messages from fracplant process queue
        messages = []
        while not self.fracplant_process_queue.empty():
            messages.append(self.fracplant_process_queue.get())
        for msg in messages:
            if len(msg): # Did we get anything?
                if msg[0] == 0: # This is for me, I'll take it
                    data = msg[1]
                    self.fracplant.set_lines(data[0])
                    i = 0
                    for branch in self.fracplant.branches:
                        branch.info = data[1][i]
                        i+=1
                elif msg[0] == 1: # This is not for me, send it back
                    self.fracplant_process_queue.put(msg)
        # Draw
        self.renderer.clear_fractal_layer()
        self.renderer.draw_lines(self.renderer.fractal_layer, self.fracplant.lines, WHITE)

    # Cut all branches on <fracplant> that intersects a line between two points
    def cut(self, fracplant):
        self.cutting = True
        self.pause_fracplant_process()
        start_time = pg.time.get_ticks()

        # Cut plant from one point (p1) to another point (p2)
        p1 = pg.mouse.get_pos() # p1 placed
        # Pause to place p2
        self.input.pop_key(pg.K_q)
        while not self.input.is_pressed(pg.K_q):
            self.renderer.clear_background_layer()
            self.renderer.clear_effect_layer()
            self.generate_ui() # Continue to move the cross-cursor
            self.x_rect.center = (p1[0]+2, p1[1]-1)
            self.renderer.ui_layer.blit(self.x, self.x_rect) # Put an x on p1

            pg.draw.line(self.renderer.effect_layer, DARK_GREY, p1, pg.mouse.get_pos(), 1)
            self.renderer.render()
            self.input.handle(self)
        p2 = pg.mouse.get_pos() # p2 placed
        # Perform a cut on <fracplant> from <p1> to <p2>
        fracplant.cut(fracplant.selected_branch, p1, p2, self.renderer)

        fracplant.lines.fill((None, None))
        end_time = pg.time.get_ticks()
        self.cutting = False 
        self.time_offset -= end_time - start_time # Account for paused time.
        self.update_fracplant_process(self.fracplant) # Send over the cut plant to the calculation process
        self.unpause_fracplant_process()
        self.renderer.clear_effect_layer()
    
    # Save the fracplant
    def save(self):
        with open("saves/recent.txt", 'w') as f:
            data = ""
            for branch in self.fracplant.branches:
                data += f"{{{str(branch.blocked_ids)}}}\n"
            f.write(data)

    # Reset the fracplant and regrow all branches
    def reset(self):
        for branch in self.fracplant.branches:
            branch.blocked_ids = []
        self.fracplant_process_queue.put([1, self.fracplant])

    # MULTIPROCESSING
    # Start a parallell process to calculate the fracplants
    def start_fracplant_process(self):
        self.fracplant_process_queue = mp.Queue() # Use queue instead to send kill-call
        self.calc_process = mp.Process(target=calculate_fracplants, 
            args=(self.fracplant, self.fracplant_process_queue, self.time_offset))
        self.calc_process.start()

    # Pause the parallell process calculating the fracplants
    def pause_fracplant_process(self):
        self.fracplant_process_queue.put([1, "pause"]) # Send a message to the fracplant process telling it to pause

    # Unpause the parallell process calculating the fracplants
    def unpause_fracplant_process(self):
        self.fracplant_process_queue.put([1, "unpause"]) # Send a message to the fracplant process telling it to unpause

    # End the parallell process calculating the fracplants
    def end_fracplant_process(self):
        self.fracplant_process_queue.put([1, "die"]) # Send a "kill message" to the other process
        self.calc_process.join() # Join other process with current process
        self.calc_process.close() # Close the other process

    # Sends a new version of <plant> to the fracplant calculation process
    def update_fracplant_process(self, plant):
        self.fracplant_process_queue.put([1, plant])

    # MISC
    def remove_multiple(self, str, chars):
        for c in chars:
            str = str.replace(c, '')
        return str

# Calculates the points and lines constituting the fracplants. Multiprocessing requires this to be outside all classes
def calculate_fracplants(fracplant, queue, time_offset):
    pg.init()
    on = True
    start_time = pg.time.get_ticks() + time_offset
    while 1:
        # Read and act on messages on the fracplant calculation queue
        messages = []
        while not queue.empty():
            messages.append(queue.get())
        for msg in messages:
            if len(msg): # Did we get anything?
                if msg[0] == 1: # This is for me, I'll take it
                    data = msg[1]
                    if data == "die":
                        return
                    elif data == "pause":
                        on = False
                        continue
                    elif data == "unpause":
                        time_offset -= pg.time.get_ticks() + time_offset - start_time
                        on = True
                    else:
                        fracplant = data
                elif msg[0] == 0: # This is not for me, send it back
                    queue.put(msg)
        
        # Calculate the nodes and lines of <fracplant>
        if on:
            start_time = pg.time.get_ticks() + time_offset # Time before calculation
            growth = 1 - 1 / (1 + start_time / 10000) # Arbitrary growth equation
            all_info = [
                {"lines": fracplant.lines, "id": "", "order": 0, "end": round(fracplant.max_order), "rot": 0, 
                    "scale_factor": 80 * growth, "sway": start_time / 1000, "sway_scale": 0.05, "origin": fracplant.origin},
                {"lines": fracplant.lines, "id": "", "order": 0, "end": round(fracplant.max_order), "rot": 0, 
                    "scale_factor": 80 * growth, "sway": start_time / 1000, "sway_scale": 0.02, "origin": fracplant.origin}
            ]
            fracplant.generate(all_info)
            queue.put([0, [fracplant.lines, [branch.info for branch in fracplant.branches]]])
            end_time = pg.time.get_ticks() + time_offset # Time after calculation
            sleep(1/8 - min((end_time - start_time)/1000.0, 1/8)) # Only execute every 8th second