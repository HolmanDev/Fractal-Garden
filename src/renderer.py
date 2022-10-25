import pygame as pg

# ONE SURFACE FOR PLANT AND ONE FOR OTHER STUFF
# THE PLANT ONE IS SLOW, EVERYTHING ELSE IS FAST

class Renderer:
    def __init__(self, w, h, bg_color):
        self.width = w
        self.height = h
        self.fps = 8
        self.bg_color = bg_color

    def init(self):
        pg.init()
        self.screen = pg.display.set_mode((self.width, self.height))
        self.background = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        self.fractal_layer = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        self.ui_layer = pg.Surface(self.screen.get_size(), pg.SRCALPHA)
        pg.mouse.set_visible(False)

    def set_fps(self, fps):
        self.fps = fps

    def render(self):
        self.background.blit(self.fractal_layer, (0, 0))
        self.background.blit(self.ui_layer, (0,0))
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (0,0))
        pg.display.flip() # Update display
    
    def clear(self):
        self.background.fill(self.bg_color)
    
    def clear_ui(self):
        self.ui_layer.fill((0, 0, 0, 0))

    def draw_lines(self, surface, line_nodes, color):
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
            dx = xdiff / max_diff
            dy = ydiff / max_diff
            
            for i in range(max_diff):
                x = p1[0] + dx * i
                x = int(min(width-1, max(0, x)))
                y = p1[1] + dy * i
                y = int(min(height-1, max(0, y)))
                # Color active pixel
                pixel_array[x, y] = color
        pg.pixelcopy.array_to_surface(surface, pixel_array)
        pixel_array.close()

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