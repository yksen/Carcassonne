import pygame, sys, random
from pygame.locals import *
import tileSets as ts

pygame.init()
 
FPS = 60

FramePerSec = pygame.time.Clock()
 
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption("Carcassonne")

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))

    pygame.display.update()
    FramePerSec.tick(FPS)