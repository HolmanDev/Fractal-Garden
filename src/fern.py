from math import sin, cos

powers = [1, 5, 25, 125, 625, 3125, 15625, 78125]
scale_dividers = [1, 2.5, 6.25, 15.625, 39.0625, 97.65625, 244.140625, 610.3515625]

class Fern:
    def __init__(self, attachment_node, scale, rot):
        self.attachment_node = attachment_node
        self.scale = scale
        self.rot = rot

        self.blocked_ids = []

    @staticmethod
    def lines_len(max_order):
        sz = 0
        for i in range(max_order + 1):
            sz += 5**i
        return sz

    def path_index(self, id, end, fracNum):
        # This can be done in base 5 instead
        i = 0
        order = 0
        for c in id:
            power = powers[order]
            if c == 'f': i = i + power
            elif c == 'l': i = i + 2*power
            elif c == 'L': i = i + 3*power
            elif c == 'r': i = i + 4*power
            else: i = i + 5*power 
            order += 1
        offset = fracNum * Fern.lines_len(end) - 1
        i += offset
        return i

    def draw(self, fracNum, lines, id, order, end, rot, scaleFactor, sway, swayScale, origin):
        if id in self.blocked_ids: return
        # Precomputed values
        sinr = sin(rot)
        cosr = cos(rot)

        ox = origin[0]
        oy = origin[1]
        scale = scaleFactor / scale_dividers[order]
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
        offset = fracNum * Fern.lines_len(end) - 1
        i += offset
        # Add two points forming a line to the lines list
        lines[i] = ([round(ox), round(oy)], [round(ox - sinr * 4 * scale), round(oy - cosr * 4 * scale)])
        if order < end:
            swayOffset = sin(sway) * swayScale
            # Create five brances, f(forward), l(upper left), L (lower left), r (uppper rigt) and R (lower right)
            self.draw(fracNum, lines, id + "f", order+1, end, rot + 0.175 + swayOffset, scaleFactor, sway, swayScale, 
                [round(ox - sinr * 4 * scale), round(oy - cosr * 4 * scale)])
            self.draw(fracNum, lines, id + "l", order+1, end, rot + 1.257 + swayOffset, scaleFactor * 0.667, sway, swayScale, 
                [round(ox - sinr * 3.5 * scale), round(oy - cosr * 3.5 * scale)])
            self.draw(fracNum, lines, id + "L", order+1, end, rot + 1.257 + swayOffset, scaleFactor, sway, swayScale, 
                [round(ox - sinr * 2 * scale), round(oy - cosr * 2 * scale)])
            self.draw(fracNum, lines, id + "r", order+1, end, rot - 0.785 + swayOffset, scaleFactor * 0.667, sway, swayScale, 
                [round(ox - sinr * 3.5 * scale), round(oy - cosr * 3.5 * scale)])
            self.draw(fracNum, lines, id + "R", order+1, end, rot - 0.785 + swayOffset, scaleFactor, sway, swayScale, 
                [round(ox - sinr * 2 * scale), round(oy - cosr * 2 * scale)])
