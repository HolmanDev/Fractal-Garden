import pygame
import numpy as np
from math import sin

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
        time = pygame.time.get_ticks()
        pixels = fractal(1, int(time/100), (int(width/2), int(height/2)))
        draw_pixels(background, pixels)
        screen.blit(background, (0,0)) # Display the background, starting at (0,0) and going (+,+)
        pygame.display.flip() # Update display

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