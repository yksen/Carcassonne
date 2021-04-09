import pygame, sys, random, pygame_menu, random, math
from pygame.locals import *
import tileSets as ts

pygame.init()
 
FPS = 144
FramePerSec = pygame.time.Clock()

screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption("Carcassonne")
tileSet = pygame.image.load("tiles.png").convert()

class Game:
    def __init__(self):
        self.hasStarted = 0
    def start(self):
        self.hasStarted = 1
        menu.toggle()
    def drawGame(self):
        if self.hasStarted:
            screen.fill((33, 17, 6))
            if len(placedTiles) > 0:
                for i in range(len(placedTiles)):
                    screen.blit(placedTiles[i].surface, (placedTiles[i].posX, placedTiles[i].posY)) 
    def drawMenu(self):
        if menu.is_enabled():
            menu.draw(screen)
            menu.update(events)
    def draw(self):
        self.drawGame()
        self.drawMenu()
    class PlacedTile():
        def __init__(self, id, posX, posY, rotation):
            self.id = id
            self.txtPosX = self.id.x
            self.txtPosY = self.id.y
            tileTxt = tileSet.subsurface(self.txtPosX, self.txtPosY, 256, 256)
            self.surface = pygame.transform.scale(tileTxt, (128, 128))
            self.posX = math.floor(posX / 128) * 128
            self.posY = math.floor(posY / 128) * 128
            self.rotation = rotation
        def rotateTile(self):
            pass

game = Game()

menu = pygame_menu.Menu('', 1600, 900, theme = pygame_menu.themes.THEME_DARK)
menu.add.button('Play', game.start)
menu.add.button('Quit', pygame_menu.events.EXIT)

placedTiles = []

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()      
        if event.type == pygame.MOUSEBUTTONUP and game.hasStarted:
            placedTiles.append(game.PlacedTile(getattr(ts, 'tile' + str(random.randrange(1, 72))), pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 0))

    game.draw()

    pygame.display.update()
    FramePerSec.tick(FPS)
