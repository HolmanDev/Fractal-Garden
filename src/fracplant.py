import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "True"
import pygame as pg
import math
from time import sleep

from branch import Branch
from constants import *

# A plant made of fractals. Can be grown and cut to desired shape
class Fracplant:
    def __init__(self, name, origin, max_order, color):
        self.name = name
        self.origin = origin
        self.max_order = max_order
        self.color = color

        self.branches = []
        self.lines = []

    # Set lines (used for preallocation)
    def set_lines(self, lines):
        self.lines = lines

    # Fill lines with filler elements (None, None)
    def empty_lines(self):
        self.lines.fill((None, None))

    def set_name(self, name):
        self.name = name

    def default_name(self):
        self.name = "UNNAMED"

    # Add a branch to the fracplant
    def add_branch(self, origin, scale, rot):
        self.branches.append(Branch(origin, scale, rot))

    # Generate this fracplant by generating all its branches
    def generate(self, all_info):
        for i, branch in enumerate(self.branches):
            info = all_info[0]
            branch.generate(i, info["lines"], info["id"], info["order"], info["end"], info["rot"] + branch.rot, 
                info["scale_factor"] * branch.scale, info["sway"], info["sway_scale"], info["origin"])

    # Cut the branch with index <branch_num> from <p1> to <p2>
    def cut(self, p1, p2, renderer):
        for branch in self.branches:
            lines, info = branch.get_lines()
            cut_xdiff = p2[0] - p1[0]
            cut_ydiff = p2[1] - p1[1]
            cut_length = math.sqrt(cut_xdiff*cut_xdiff + cut_ydiff*cut_ydiff)
            if cut_length == 0: return
            cut_dir = (cut_xdiff/cut_length, cut_ydiff/cut_length)
            info.sort(key=lambda x: x[0])
            i = 0
            id = None
            blocked_ids = []
            blocked_indices = []
            # Below is just a bunch of math. It works.
            for line in lines:
                if line[0] == None or line[1] == None:
                    i += 1
                    continue
                l1 = line[0]
                l2 = line[1]
                t1 = 0
                t2 = 0

                x1 = p1[0]
                y1 = p1[1]
                a1 = cut_dir[0]
                b1 = cut_dir[1]

                x2 = l1[0]
                y2 = l1[1]
                a2 = l2[0] - l1[0]
                b2 = l2[1] - l1[1]
                line_length = math.sqrt(a2*a2 + b2*b2)
                if(line_length == 0) : 
                    i += 1
                    continue
                a2 /= line_length
                b2 /= line_length

                if a1*b2 - a2*b1 != 0 and a1 != 0:
                    # Use linear algebra to calculate the intersection
                    t2 = (a1*(y1-y2) - b1*(x1-x2)) / (a1*b2 - a2*b1)
                    t1 = (x2-x1+t2*a2)/a1
                elif a1 == 0:
                    print("Warning!: ", i)
                    t2 = y1 - y2
                elif a1*b2 - a2*b1 == 0:
                    print("Warning!: ", i)
                    i+=1
                    continue

                if t1 > 0 and t1 < cut_length and t2 > 0 and t2 < line_length:
                    id = ""
                    if i + 1 >= len(info): 
                        id = info[0][1]
                    else:
                        id = info[i+1][1]
                    blocked_ids.append(id)
                    blocked_indices.append(i)
                i += 1
            # If a branch was intersected
            if id is not None:
                lines_to_draw = [lines[i] for i in blocked_indices]
                for line in lines_to_draw:
                    pg.draw.line(renderer.fractal_layer, HOT_PINK, line[0], line[1], 3)
                branch.blocked_ids += blocked_ids
        pg.draw.line(renderer.fractal_layer, RED, p1, p2, 1)
        renderer.render()
        pg.time.delay(1000)

    # Destroy this fracplant
    def destroy(self):
        pass
        #print("Destroyed a fracplant")

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
            growth = 1 - 1 / (1 + start_time / 20000) # Arbitrary growth equation
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