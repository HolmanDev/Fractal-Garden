import pygame
import numpy as np
import random
from math import cos, sin, sqrt, pi

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
    fps = 16
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
        growth = 1 - 1 / ( 1 + time / 1000)
        origin = (550, height-100)
        pixels = myfern(0, 4, 0, time / 1000, 0.02, origin)
        draw_pixels(background, pixels)
        screen.blit(background, (0,0)) # Display the background, starting at (0,0) and going (+,+)
        pygame.display.flip() # Update display

def myfern(order, end, orientation, sway, swayScale, origin):
    newPixels = []
    ox = origin[0]
    oy = origin[1]
    scale = 20 / (3**order)
    pos = lambda x, y: (
        round(ox + cos(orientation) * x - sin(orientation) * y), 
        round(oy - sin(orientation) * x - cos(orientation) * y)
    )
    for i in range(0, round(5 * scale)):
        newPixels.append(pos(0, i))
    if order < end:
        return(newPixels + 
            myfern(order+0.3, end, orientation + pi/24 + sin(sway) * swayScale, sway, swayScale, pos(0, 5 * scale)) +
            myfern(order+1, end, orientation + pi/2.5 + sin(sway) * swayScale, sway, swayScale, pos(-1, 3 * scale)) +
            myfern(order+1, end, orientation - pi/4 + sin(sway) * swayScale, sway, swayScale, pos(1, 3 * scale))
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
    
def draw_pixels(surface, pixels):
    pixel_array = pygame.PixelArray(surface)
    width, height = surface.get_size()
    # Loop through all active pixels
    for pixel in pixels:
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