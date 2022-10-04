from fern import Fern

class Fracplant:
    def __init__(self):
        self.ferns = []
        pass

    def add_fern(self, origin, scale, rot):
        self.ferns.append(Fern(origin, scale, rot))

    def draw(self, all_info):
        # For example, Draw a fern from a specific order and with 
        # a certain scale, and then add other fractals
        i = 0
        for fern in self.ferns:
            info = all_info[0]
            fern.draw(i, info["lines"], info["id"], info["order"], info["end"], info["rot"] + fern.rot, 
                info["scale_factor"] * fern.scale, info["sway"], info["sway_scale"], info["origin"])
            i += 1
        pass