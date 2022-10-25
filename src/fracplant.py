from fern import Fern
import math
import pygame as pg

class Fracplant:
    def __init__(self, origin, max_order):
        self.ferns = []
        self.lines = []
        self.max_order = max_order
        self.origin = origin
        self.selected_fern = -1

    def set_lines(self, lines):
        self.lines = lines

    def empty_lines(self):
        self.lines.fill((None, None))

    def add_fern(self, origin, scale, rot):
        self.ferns.append(Fern(origin, scale, rot))

    def select_fern(self, index):
        self.selected_fern = index

    def cut(self, fern_num, p1, p2, rendr):
        print(f"Cut {fern_num} from {p1} to {p2}")
        lines, info = self.ferns[fern_num].get_line_nodes() # include id info also
        cut_xdiff = p2[0] - p1[0]
        cut_ydiff = p2[1] - p1[1]
        cut_length = math.sqrt(cut_xdiff*cut_xdiff + cut_ydiff*cut_ydiff)
        cut_dir = (cut_xdiff/cut_length, cut_ydiff/cut_length)
        info.sort(key=lambda x: x[0])
        i = 0
        id = None
        max_length = 0
        max_i = 0
        blocked_ids = []
        blocked_indices = []
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
                t2 = (a1*(y1-y2) - b1*(x1-x2)) / (a1*b2 - a2*b1)
                t1 = (x2-x1+t2*a2)/a1 #a1 = 0?
            elif a1 == 0: # Remove these elifs?
                print("Warning!: ", i)
                t2 = y1 - y2
            elif a1*b2 - a2*b1 == 0:
                print("Warning!: ", i)
                i+=1
                continue

            #intersection = (x1 + a1 * t1, y1 + b1 * t1)

            if t1 > 0 and t1 < cut_length and t2 > 0 and t2 < line_length:
                id = ""
                if i + 1 >= len(info): 
                    id = info[0][1]
                else:
                    id = info[i+1][1]
                blocked_ids.append(id)
                blocked_indices.append(i)
            i += 1
        if id is not None:
            lines_to_draw = [lines[i] for i in blocked_indices]
            for line in lines_to_draw:
                pg.draw.line(rendr.fractal_layer, (255, 50, 100, 255), line[0], line[1], 3)
            self.ferns[fern_num].blocked_ids += blocked_ids
        pg.draw.line(rendr.fractal_layer, (255, 0, 0, 255), p1, p2, 1)
        rendr.render()
        pg.time.delay(1000)

    def draw(self, all_info):
        # For example, Draw a fern from a specific order and with 
        # a certain scale, and then add other fractals
        i = 0
        for fern in self.ferns:
            info = all_info[0]
            fern.draw(i, info["lines"], info["id"], info["order"], info["end"], info["rot"] + fern.rot, 
                info["scale_factor"] * fern.scale, info["sway"], info["sway_scale"], info["origin"])
            i += 1

    # def destroy():