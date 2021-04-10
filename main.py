import pygame, sys, random, pygame_menu, random, math
from pygame.locals import *
import tileSets as ts

pygame.init()
 
FPS = 144
FramePerSec = pygame.time.Clock()

screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption("Carcassonne")
tileSet = pygame.image.load("tiles.png").convert()

class App:
    def __init__(self):
        self.mouseLeftClicked = 0
        self.mouseRightClicked = 0
        self.mouseMoving = 0
    class Game:
        def __init__(self):
            self.hasStarted = 0
            self.placedTiles = []
            self.relativeX = 0
            self.relativeY = 0
        def start(self):
            self.hasStarted = 1
            menu.toggle()
        def drawMenu(self):
            if menu.is_enabled():
                menu.draw(screen)
                menu.update(events)
        def drawGame(self):
            if self.hasStarted:
                screen.fill((33, 17, 6))
                if len(self.placedTiles) > 0:
                    for i in range(len(self.placedTiles)):
                        screen.blit(self.placedTiles[i].surface, (self.placedTiles[i].posX + self.relativeX, self.placedTiles[i].posY + self.relativeY)) 
        def drawAll(self):
            self.drawGame()
            self.drawMenu()
        class PlacedTile:
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

carcassonne = App()
game = carcassonne.Game()

menu = pygame_menu.Menu('', 1600, 900, theme = pygame_menu.themes.THEME_DARK)
menu.add.button('Play', game.start)
menu.add.button('Quit', pygame_menu.events.EXIT)



while True:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            sys.exit()   
        if event.type == pygame.MOUSEMOTION:
            carcassonne.mouseMoving = 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: carcassonne.mouseLeftClicked = 1
            if event.button == 3: carcassonne.mouseRightClicked = 1

        if game.hasStarted:
            if carcassonne.mouseMoving and carcassonne.mouseLeftClicked:
                game.relativeX += event.rel[0]
                game.relativeY += event.rel[1]
                mouseMoved = 1
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not carcassonne.mouseMoving and not mouseMoved:            
                game.placedTiles.append(game.PlacedTile(getattr(ts, 'tile' + str(random.randrange(1, 72))), pygame.mouse.get_pos()[0] - game.relativeX, pygame.mouse.get_pos()[1] - game.relativeY, 0))
        
        if event.type == pygame.MOUSEMOTION:
            carcassonne.mouseMoving = 0            
        if event.type == pygame.MOUSEBUTTONUP: 
            if event.button == 1: carcassonne.mouseLeftClicked = 0
            if event.button == 3: carcassonne.mouseRightClicked = 0
            mouseMoved = 0

    game.drawAll()
    pygame.display.update()

    FramePerSec.tick(FPS)
