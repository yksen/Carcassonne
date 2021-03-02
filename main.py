import pygame, sys, random
from pygame.locals import *

pygame.init()
 
HEIGHT = 900
WIDTH = 1600
FPS = 60
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Carcassonne")

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    displaysurface.fill((0, 0, 0))
 
    pygame.display.update()
    FramePerSec.tick(FPS)