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
    lines = np.empty(5**(max_order + 1) + 1, dtype=tuple) # rename to lines
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        clock.tick(1000.0/fps)
        background.fill((0, 0, 0))
        #pixels = fractal(1, int(time/100), origin)
        #pixels = fern(origin, growth)
        #pixels = myfern(0, 10, pi / 2, origin)
        time = pygame.time.get_ticks()
        growth = 1 - 1 / (1 + time / 10000)
        #growth = 1
        origin = (550, height-100)
        #pixels = fern(origin, growth)
        #pixels = myfern(0, round(5 * growth * 3)/3, 0, 25 * growth, time / 1000, 0.02, origin)
        #draw_pixels(background, pixels)
        #order = round(max_order * growth * 3)/3
        lightfern(lines, "", 0, max_order, 0, 100 * growth, time / 1000, 0.02, [550, height-100])
        #print(i)
        draw_line_points(background, lines)
        screen.blit(background, (0,0)) # Display the background, starting at (0,0) and going (+,+)
        pygame.display.flip() # Update display

def pos(x, y, x0, y0, rot):
    return [round(x0 + cos(rot) * x - sin(rot) * y), 
        round(y0 - sin(rot) * x - cos(rot) * y)]

def path_index(path):
    i = 0
    order = 0
    for c in path:
        power = 5**order
        if c == 'f': i = i + power 
        elif c == 'l': i = i + 2*power 
        elif c == 'L': i = i + 3*power 
        elif c == 'r': i = i + 4*power
        else: i = i + 5*power
        order += 1
    return i

def lightfern(lines, id, order, end, rot, scaleFactor, sway, swayScale, origin):
    ox = origin[0]
    oy = origin[1]
    scale = scaleFactor / (2.5**order)
    index = path_index(id)
    if(id == ""):
        index = 0
    lines[index] = (pos(0, 0, ox, oy, rot), pos(0, 4*scale, ox, oy, rot))
    if order < end:
        swayOffset = sin(sway) * swayScale
        lightfern(lines, id + "f", order+1, end, rot + pi/18 + swayOffset, scaleFactor, sway, swayScale, pos(0, 4 * scale,ox,oy,rot))
        lightfern(lines, id + "l", order+1, end, rot + pi/2.5 + swayOffset, scaleFactor*2/3, sway, swayScale, pos(-1, 3.5 * scale,ox,oy,rot))
        lightfern(lines, id + "L", order+1, end, rot + pi/2.5 + swayOffset, scaleFactor, sway, swayScale, pos(-1, 2 * scale,ox,oy,rot))
        lightfern(lines, id + "r", order+1, end, rot - pi/4 + swayOffset, scaleFactor*2/3, sway, swayScale, pos(1, 3.5 * scale,ox,oy,rot))
        lightfern(lines, id + "R", order+1, end, rot - pi/4 + swayOffset, scaleFactor, sway, swayScale, pos(1, 2 * scale,ox,oy,rot))

"""
def myfern(order, end, orientation, scaleFactor, sway, swayScale, origin):
    newPixels = [] # Switch to numpy array. Create one outside the function
    ox = origin[0]
    oy = origin[1]
    scale = scaleFactor / (3**order)
    pos = lambda x, y: (
        round(ox + cos(orientation) * x - sin(orientation) * y), 
        round(oy - sin(orientation) * x - cos(orientation) * y)
    )
    for i in range(0, round(5 * scale)):
        newPixels.append(pos(0, i))
    if order < end:
        swayOffset = sin(sway) * swayScale
        return(newPixels + 
            myfern(order+1/3, end, orientation + pi/24 + swayOffset, scaleFactor, sway, swayScale, pos(0, 5 * scale)) +
            myfern(order+1, end, orientation + pi/2.5 + swayOffset, scaleFactor, sway, swayScale, pos(-1, 3 * scale)) +
            myfern(order+1, end, orientation - pi/4 + swayOffset, scaleFactor, sway, swayScale, pos(1, 3 * scale))
        )
    else:
        return newPixels

def fern(origin, growth):
    pixels = []
    x = 0
    y = 0
    for n in range(11000):
        r = random.random()
        if r < 0.01:
            x, y =  0.00 * x + 0.00 * y,  0.00 * x + 0.16 * y + 0.00
        elif r < 0.86:
            x, y =  0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.60
        elif r < 0.93:
            x, y =  0.20 * x - 0.26 * y,  0.23 * x + 0.22 * y + 1.60
        else:
            x, y = -0.15 * x + 0.28 * y,  0.26 * x + 0.24 * y + 0.44
        pixels.append((x * 65 * growth**2 + origin[0], growth * y * -37 + origin[1]))
    return pixels

# Spiral fractal
def fractal(order, end, origin):
    newPixels = []
    for i in range(10*order):
        n = order % 4
        if n == 0:
            newPixels.append((origin[0], origin[1] + i))
        elif n == 1:
            newPixels.append((origin[0] + i, origin[1]))
        elif n == 2:
            newPixels.append((origin[0], origin[1] - i))
        else:
            newPixels.append((origin[0] - i, origin[1]))
    if order < end:
        startPos = newPixels[-1]
        return(newPixels + fractal(order+1, end, startPos))
    else:
        return newPixels
"""

def draw_line_points(surface, lines):
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