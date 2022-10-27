import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame as pg
from math import pi, sin, cos
import multiprocessing as mp
import json

from fracplant import Fracplant, calculate_fracplants
from branch import Branch
from renderer import Renderer
from input_handler import InputHandler
import numpy as np
from constants import *
from config import Config

# Contains the game logic and event loop
class Game:
    def __init__(self):
        self.fracplant = None
        self.input = InputHandler()
        self.renderer = Renderer(1080, 640, NIGHT)
        self.time_offset = 0
        self.cutting = False
        self.changing_name = False
        self.saving = False
        self.save_time = 0
        self.game_time = 0

        self.load_fonts()

    # Runs at program start
    def start(self):
        self.renderer.init()
        pg.display.set_caption("Fractal Garden")

        # UI
        self.cursor = self.cursor_font.render('x', True, RED)
        self.cursor_rect = self.cursor.get_rect()
        self.fracplant_label = self.medium_text_font.render('', True, WHITE)
        self.fracplant_label_rect = self.fracplant_label.get_rect()
        self.key_info = self.small_text_font.render('CUT: [Q],    SET NAME: [N],    SAVE: [S],    RESET: [R]', True, WHITE)
        self.key_info_rect = self.fracplant_label.get_rect(bottom=self.renderer.height+10, left=self.renderer.width-420)

        # Fracplant
        origin = [550, self.renderer.height-100]
        self.fracplant = Fracplant("UNNAMED", origin, 4, WHITE)
        self.fracplant.add_branch(0, 1, 0)
        self.fracplant.add_branch(0, 0.5, pi/20)
        self.fracplant.set_lines(np.empty(Branch.lines_len(self.fracplant.max_order)*2, dtype=tuple))
        self.fracplant.empty_lines()

        # Load save files
        data = ""
        found_data = False
        try:
            with open("saves/recent.json", 'r') as f:
                data = f.read()
        except FileNotFoundError:
            print("No save file found")
        else:
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = []
                print("Couldn't validate save file. Discarded.")
            else:
                try:
                    _ = data["name"]
                    _ = data["time"]
                    _ = data["branches"]
                except KeyError:
                    print("Couldn't validate save file. Discarded.")
                else:
                    found_data = True
        # Apply save file data to fracplant
        if(found_data): # Apply data from save file
            self.fracplant.name = data["name"]
            self.game_time = data["time"]
            for i, branch in enumerate(self.fracplant.branches):
                branch.blocked_ids = data["branches"][i]["blocked_ids"]
        self.start_fracplant_process() # Multiprocessing

        # Main loop
        self.renderer.set_fps(32)
        clock = pg.time.Clock()
        frame_time = pg.time.get_ticks()
        while 1:
            dt = pg.time.get_ticks() - frame_time
            if dt > 1000/self.renderer.fps:
                self.game_time += dt
                frame_time = pg.time.get_ticks()
                self.update()
                clock.tick(self.renderer.fps)

    # Runs every frame
    def update(self):
        # Handle input
        self.input.handle(self)

        # Misc
        if self.changing_name:
            name = self.input.get_recorded_text()
            self.fracplant.set_name(name.upper())
            if not self.input.recording:
                self.input.clear_recorded_text()
                self.changing_name = False

        # Generate visuals
        self.renderer.clear_background_layer()
        self.display_ui()
        self.display_fracplants()

        # Render
        self.renderer.render()

    # Create fonts for different uses based on configs
    def load_fonts(self):
        pg.font.init()
        self.cursor_font = pg.font.Font(Config.cursor_font, Config.cursor_size)
        self.small_text_font = pg.font.Font(Config.small_text_font, Config.small_text_size)
        self.medium_text_font = pg.font.Font(Config.medium_text_font, Config.medium_text_size)
        self.large_text_font = pg.font.Font(Config.large_text_font, Config.large_text_size)

    # Display the UI, including the cursor marker
    def display_ui(self):
        self.renderer.clear_ui_layer()
        mouse_pos = pg.mouse.get_pos()
        self.cursor_rect.center = (mouse_pos[0]+2, mouse_pos[1]-1)
        self.renderer.ui_layer.blit(self.cursor, self.cursor_rect)
        self.fracplant_label = self.medium_text_font.render(self.fracplant.name, True, WHITE)
        self.fracplant_label_rect = self.fracplant_label.get_rect()
        self.fracplant_label_rect.center = (self.renderer.width * 0.5, 50)
        self.renderer.ui_layer.blit(self.fracplant_label, self.fracplant_label_rect)
        if self.changing_name:
            underline_rect = pg.Rect(0, self.fracplant_label_rect.bottom, self.fracplant_label_rect.width + 5, 2)
            if self.fracplant.name == "":
                underline_rect.width = 15 
            underline_rect.centerx = self.fracplant_label_rect.centerx
            pg.draw.rect(self.renderer.ui_layer, WHITE, underline_rect)
        self.renderer.ui_layer.blit(self.key_info, self.key_info_rect)
        if self.saving:
            progress = (pg.time.get_ticks() - self.save_time) / 1000
            text_cutoff_index = max(min(5, round(10*sin(progress * pi))), 0)
            self.saving_text = self.medium_text_font.render('SAVED'[:text_cutoff_index], True, GREEN)
            self.saving_text_rect = self.saving_text.get_rect(center=(self.renderer.width/2, self.renderer.height/2))
            self.renderer.ui_layer.blit(self.saving_text, self.saving_text_rect)
        if pg.time.get_ticks() - self.save_time > 1000:
            self.saving = False

    # Display calculated fracplants
    def display_fracplants(self):
        # Read and act on messages from fracplant process queue
        messages = []
        while not self.fracplant_process_queue.empty():
            messages.append(self.fracplant_process_queue.get())
        for msg in messages:
            if len(msg): # Did we get anything?
                if msg[0] == 0: # This is for me, I'll take it
                    data = msg[1]
                    self.fracplant.set_lines(data[0])
                    for i, branch in enumerate(self.fracplant.branches):
                        branch.info = data[1][i]
                elif msg[0] == 1: # This is not for me, send it back
                    self.fracplant_process_queue.put(msg)
        # Draw
        self.renderer.clear_fractal_layer()
        self.renderer.draw_lines(self.renderer.fractal_layer, self.fracplant.lines, self.fracplant.color)

    # Enable name change of current fracplant
    def set_name_prompt(self):
        self.changing_name = True
        self.input.recorded_text = self.fracplant.name # This feels like cheating
        self.input.start_recording_text()

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
            self.display_ui() # Continue to move the x-cursor
            self.cursor_rect.center = (p1[0]+2, p1[1]-1)
            self.renderer.ui_layer.blit(self.cursor, self.cursor_rect) # Put an x on p1
            pg.draw.line(self.renderer.effect_layer, DARK_GREY, p1, pg.mouse.get_pos(), 1)
            self.renderer.render()
            self.input.handle(self)
        p2 = pg.mouse.get_pos() # p2 placed
        # Perform a cut on <fracplant> from <p1> to <p2>
        fracplant.cut(p1, p2, self.renderer)

        fracplant.lines.fill((None, None))
        end_time = pg.time.get_ticks()
        self.cutting = False 
        self.time_offset -= end_time - start_time # Account for paused time.
        self.update_fracplant_process(self.fracplant) # Send over the cut plant to the calculation process
        self.unpause_fracplant_process()
        self.renderer.clear_effect_layer()
    
    # Save the fracplant to a json file
    def save(self):
        self.saving = True
        self.save_time = pg.time.get_ticks()
        with open("saves/recent.json", 'w') as f:
            data = {
                "name": self.fracplant.name,
                "time": self.game_time + self.time_offset,
                "branches": []
            }
            for branch in self.fracplant.branches:
                branch_data = {
                    "blocked_ids": branch.blocked_ids
                }           
                data["branches"].append(branch_data)
            f.write(json.dumps(data))

    # Reset the fracplant and regrow all branches
    def reset(self):
        for branch in self.fracplant.branches:
            branch.blocked_ids = []
        self.time_offset = 0
        self.game_time = 0
        self.end_fracplant_process()
        self.start_fracplant_process()

    # ---- MULTIPROCESSING ----
    # Start a parallell process to calculate the fracplants
    def start_fracplant_process(self):
        self.fracplant_process_queue = mp.Queue() # Use queue instead to send kill-call
        self.fracplant_process = mp.Process(target=calculate_fracplants, 
            args=(self.fracplant, self.fracplant_process_queue, self.game_time + self.time_offset))
        self.fracplant_process.start()

    # Pause the parallell process calculating the fracplants
    def pause_fracplant_process(self):
        self.fracplant_process_queue.put([1, "pause"]) # Send a message to the fracplant process telling it to pause

    # Unpause the parallell process calculating the fracplants
    def unpause_fracplant_process(self):
        self.fracplant_process_queue.put([1, "unpause"]) # Send a message to the fracplant process telling it to unpause

    # End the parallell process calculating the fracplants
    def end_fracplant_process(self):
        self.fracplant_process_queue.put([1, "die"]) # Send a "kill message" to the other process
        self.fracplant_process.terminate() # Terminate
        self.fracplant_process.join() # Join other process with current process
        self.fracplant_process.close() # Close the other process

    # Sends a new version of <plant> to the fracplant calculation process
    def update_fracplant_process(self, plant):
        self.fracplant_process_queue.put([1, plant])

    # Quit game
    def quit(self):
        self.end_fracplant_process()
        self.fracplant.destroy()