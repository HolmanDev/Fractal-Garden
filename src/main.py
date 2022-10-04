from re import I
import pygame
import numpy as np
import random
from math import cos, sin, sqrt, pi, ceil

i = 0

def main():
    print("Fractal Garden")

    pygame.init()
    width = 1080
    height = 640
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Fractal Garden")

    background = pygame.Surface(screen.get_size())
    background = background.convert() # Converts to single pixel format, speeding up rendering times
    clock = pygame.time.Clock()
    fps = 8
    max_order = 4
    sz = 0
    for i in range(max_order + 1):
        sz += 5**i
    lines = np.empty(sz, dtype=tuple) # rename to lines
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        clock.tick(1000.0/fps)
        background.fill((0, 0, 0))
        time = pygame.time.get_ticks()
        growth = 1 - 1 / (1 + time / 10000)
        growth2 = 1 - 1 / (1 + time / 600)
        origin = [550, height-100]
        lightfern(lines, "", 0, round(max_order), 0, 100 * growth, time / 1000, 0.02, origin)
        draw_lines(background, lines)
        screen.blit(background, (0,0)) # Display the background, starting at (0,0) and going (+,+)
        pygame.display.flip() # Update display

def pos(x, y, x0, y0, rot):
    return [round(x0 + cos(rot) * x - sin(rot) * y), 
        round(y0 - sin(rot) * x - cos(rot) * y)]

powers = [1, 5, 25, 125, 625, 3125, 15625, 78125]
scale_dividers = [1, 2.5, 6.25, 15.625, 39.0625, 97.65625, 244.140625, 610.3515625]

def path_index(path):
    # This can be done in base 5 instead
    i = 0
    order = 0
    for c in path:
        power = powers[order]
        if c == 'f': i = i + power 
        elif c == 'l': i = i + 2*power
        elif c == 'L': i = i + 3*power
        elif c == 'r': i = i + 4*power
        else: i = i + 5*power
        order += 1
    return i

# My own optimized fern code. In the future, avoid recursion
def lightfern(lines, id, order, end, rot, scaleFactor, sway, swayScale, origin):
    # Precomputed values
    sinr = sin(rot)
    cosr = cos(rot)

    ox = origin[0]
    oy = origin[1]
    scale = scaleFactor / scale_dividers[order]
    index = path_index(id)
    if(id == ""): # Fix index of stem
        index = 0
    # Add two points forming a line to the lines list
    lines[index] = ([round(ox), round(oy)], [round(ox - sinr * 4 * scale), round(oy - cosr * 4 * scale)])
    if order < end:
        swayOffset = sin(sway) * swayScale
        # Create five brances, f(forward), l(upper left), L (lower left), r (uppper rigt) and R (lower right)
        lightfern(lines, id + "f", order+1, end, rot + 0.175 + swayOffset, scaleFactor, sway, swayScale, 
            [round(ox - sinr * 4 * scale), round(oy - cosr * 4 * scale)])
        lightfern(lines, id + "l", order+1, end, rot + 1.257 + swayOffset, scaleFactor * 0.667, sway, swayScale, 
            [round(ox - sinr * 3.5 * scale), round(oy - cosr * 3.5 * scale)])
        lightfern(lines, id + "L", order+1, end, rot + 1.257 + swayOffset, scaleFactor, sway, swayScale, 
            [round(ox - sinr * 2 * scale), round(oy - cosr * 2 * scale)])
        lightfern(lines, id + "r", order+1, end, rot - 0.785 + swayOffset, scaleFactor * 0.667, sway, swayScale, 
            [round(ox - sinr * 3.5 * scale), round(oy - cosr * 3.5 * scale)])
        lightfern(lines, id + "R", order+1, end, rot - 0.785 + swayOffset, scaleFactor, sway, swayScale, 
            [round(ox - sinr * 2 * scale), round(oy - cosr * 2 * scale)])

def draw_lines(surface, lines):
    pixel_array = pygame.PixelArray(surface)
    width, height = surface.get_size()
    # Loop through all active pixels
    x = 0
    y = 0
    for line in lines: # Is there a faster way?
        # Confine to screen size
        if(line == None): continue
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
            # Color active pixel white
            pixel_array[x, y] = (255, 255, 255)
    pygame.pixelcopy.array_to_surface(surface, pixel_array)
    pixel_array.close()

def draw_pixels(surface, pixels):
    pixel_array = pygame.PixelArray(surface)
    width, height = surface.get_size()
    # Loop through all active pixels
    for pixel in pixels: # Is there a faster way?
        # Confine to screen size
        x = int(min(width-1, max(0, pixel[0])))
        y = int(min(height-1, max(0, pixel[1])))
        # Color active pixel white
        pixel_array[x, y] = (255, 255, 255)
    pygame.pixelcopy.array_to_surface(surface, pixel_array)
    pixel_array.close()
    
# Entry point
if __name__ == "__main__":
    main()

# References: 
# https://www.pygame.org/docs/tut/tom_games2.html