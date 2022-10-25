import pygame as pg
from constants import *

class Renderer:
    def __init__(self, w, h, bg_color):
        self.width = w
        self.height = h
        self.fps = 8
        self.bg_color = bg_color

        # Create screen and layers
        self.screen = pg.display.set_mode((self.width, self.height))
        self.background_layer = pg.Surface(self.screen.get_size(), pg.SRCALPHA) # Intermediate layer
        self.fractal_layer = pg.Surface(self.screen.get_size(), pg.SRCALPHA) # Fracplants are drawn on this layer
        self.ui_layer = pg.Surface(self.screen.get_size(), pg.SRCALPHA) # UI is drawn on this layer
        self.effect_layer = pg.Surface(self.screen.get_size(), pg.SRCALPHA) # Effects are drawn on this layer

    # Initialize renderer and hide mouse
    def init(self):
        pg.init()
        pg.mouse.set_visible(False)

    # Set the frames per second
    def set_fps(self, fps):
        self.fps = fps

    def clear_background_layer(self):
        self.background_layer.fill(self.bg_color)
    
    def clear_fractal_layer(self):
        self.fractal_layer.fill(TRANSPARENT_BLACK)

    def clear_ui_layer(self):
        self.ui_layer.fill(TRANSPARENT_BLACK)

    def clear_effect_layer(self):
        self.effect_layer.fill(TRANSPARENT_BLACK)

    # Apply all layers to the screen and render it
    def render(self):
        self.background_layer.blit(self.fractal_layer, (0, 0))
        self.background_layer.blit(self.effect_layer, (0, 0))
        self.background_layer.blit(self.ui_layer, (0,0))
        self.screen.fill(self.bg_color)
        self.screen.blit(self.background_layer, (0,0))
        pg.display.flip() # Update display

    # Draw lines between nodes
    def draw_lines(self, surface, line_nodes, color):
        # Get information from <surface>
        pixel_array = pg.PixelArray(surface)
        width, height = surface.get_size()
        # Loop through all active pixels
        x = 0
        y = 0
        for line in line_nodes: # Is there a faster way?
            # Confine to screen size
            if line[0] == None or line[1] == None: continue
            p1 = line[0]
            p2 = line[1]
            xdiff = p2[0] - p1[0]
            ydiff = p2[1] - p1[1]
            max_diff = max(abs(xdiff), abs(ydiff))
            if max_diff == 0: 
                x = p1[0]
                x = int(min(width-1, max(0, x)))
                y = p1[1]
                y = int(min(height-1, max(0, y)))
                pixel_array[int(x), int(y)] = (255, 255, 255)
                continue
            # Draw the lines using interpolation
            dx = xdiff / max_diff
            dy = ydiff / max_diff        
            for i in range(max_diff):
                x = p1[0] + dx * i
                x = int(min(width-1, max(0, x)))
                y = p1[1] + dy * i
                y = int(min(height-1, max(0, y)))
                # Color active pixel
                pixel_array[x, y] = color
        # Apply result to <surface>
        pg.pixelcopy.array_to_surface(surface, pixel_array)
        pixel_array.close()

    # Not used
    def draw_pixels(self, surface, pixels):
        pixel_array = pg.PixelArray(surface)
        width, height = surface.get_size()
        # Loop through all active pixels
        for pixel in pixels: # Is there a faster way?
            # Confine to screen size
            x = int(min(width-1, max(0, pixel[0])))
            y = int(min(height-1, max(0, pixel[1])))
            # Color active pixel white
            pixel_array[x, y] = (255, 255, 255)
        pg.pixelcopy.array_to_surface(surface, pixel_array)
        pixel_array.close()