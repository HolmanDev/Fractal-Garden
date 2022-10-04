from fern import Fern

class Fracplant:
    def __init__(self):
        pass

    def add_fern(self):
        self.fern = Fern()

    def draw(self, info):
        # For example, Draw a fern from a specific order and with 
        # a certain scale, and then add other fractals
        self.fern.draw(info["lines"], info["id"], info["order"], info["end"], info["rot"], 
            info["scale_factor"], info["sway"], info["sway_scale"], info["origin"])
        pass