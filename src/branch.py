from math import sin, cos
import numpy as np

powers = [1, 5, 25, 125, 625, 3125, 15625, 78125]
scale_dividers = [1, 2.5, 6.25, 15.625, 39.0625, 97.65625, 244.140625, 610.3515625]

class Branch:
    #Store last info
    def __init__(self, attachment_node, scale, rot):
        self.attachment_node = attachment_node
        self.scale = scale
        self.rot = rot

        self.blocked_ids = []
        self.info = []

    # Generate this branch using recursion.
    def generate(self, fracNum, lines, id, order, end, rot, scaleFactor, sway, swayScale, origin, info=None):
        if id == "":
            self.info = {"max_order": end, "rot": rot, "scale_factor": scaleFactor, 
                "sway": sway, "sway_scale": swayScale, "origin": origin}
        
        # Precomputed values
        sinr = sin(rot)
        cosr = cos(rot)
        ox = origin[0]
        oy = origin[1]
        scale = scaleFactor / scale_dividers[order]

        # Calculate offset
        i = 0
        o = 0
        for c in id:
            power = powers[o]
            if c == 'f': i = i + power
            elif c == 'l': i = i + 2*power
            elif c == 'L': i = i + 3*power
            elif c == 'r': i = i + 4*power
            else: i = i + 5*power
            o += 1
        offset = fracNum * Branch.lines_len(end) - 1
        i += offset
        if info is not None:
            info.append([i, id])
        include = True

        # Blocking
        for blocked_id in self.blocked_ids: 
            if(len(blocked_id) > len(id)): continue
            if id[0:len(blocked_id)] == blocked_id:
                include = False
                break
        if include:
            # Add two points forming a line to the lines list
            lines[i] = ([round(ox), round(oy)], [round(ox - sinr * 4 * scale), round(oy - cosr * 4 * scale)])
        
        # Seeds
        if order < end:
            swayOffset = sin(sway) * swayScale
            # Create five brances, f(forward), l(upper left), L (lower left), r (upper right) and R (lower right)
            self.generate(fracNum, lines, id + "f", order+1, end, rot + 0.175 + swayOffset, scaleFactor, sway, swayScale, 
                [round(ox - sinr * 4 * scale), round(oy - cosr * 4 * scale)], info=info)
            self.generate(fracNum, lines, id + "l", order+1, end, rot + 1.257 + swayOffset, scaleFactor * 0.667, sway, swayScale, 
                [round(ox - sinr * 3.5 * scale), round(oy - cosr * 3.5 * scale)], info=info)
            self.generate(fracNum, lines, id + "L", order+1, end, rot + 1.257 + swayOffset, scaleFactor, sway, swayScale, 
                [round(ox - sinr * 2 * scale), round(oy - cosr * 2 * scale)], info=info)
            self.generate(fracNum, lines, id + "r", order+1, end, rot - 0.785 + swayOffset, scaleFactor * 0.667, sway, swayScale, 
                [round(ox - sinr * 3.5 * scale), round(oy - cosr * 3.5 * scale)], info=info)
            self.generate(fracNum, lines, id + "R", order+1, end, rot - 0.785 + swayOffset, scaleFactor, sway, swayScale, 
                [round(ox - sinr * 2 * scale), round(oy - cosr * 2 * scale)], info=info)

    # Regenerate lines based on data from last generation
    def get_lines(self):
        lines = np.zeros(Branch.lines_len(self.info["max_order"]), dtype=tuple)
        lines.fill((None, None))
        info = []
        self.generate(0, lines, "", 0, self.info["max_order"], self.info["rot"], self.info["scale_factor"],
            self.info["sway"], self.info["sway_scale"], self.info["origin"], info=info)
        return lines, info

    # Get length of lines array
    @staticmethod
    def lines_len(max_order):
        sz = 0
        for i in range(max_order + 1):
            sz += 5**i
        return sz
