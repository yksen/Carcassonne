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
            self.relativeX = 0
            self.relativeY = 0
            self.placedTiles = {}
            self.tileStack = []
        def start(self):
            self.hasStarted = 1
            self.gameSetup()
            menu.toggle()
        def gameSetup(self):
            tileOrder = []
            for i in range(72):
                tileOrder.append(i + 1)
            tileOrder.pop(tileOrder.index(36))
            self.tileStack.clear
            for i in range(71):
                randIndex = random.randint(0, len(tileOrder) - 1)
                self.tileStack.append(tileOrder[randIndex])      
                tileOrder.pop(randIndex)      
            self.placedTiles[768] = {}
            self.placedTiles[768][384] = self.Tile(ts.tile36, 768, 384)
            self.nextTile = self.Tile(getattr(ts, 'tile' + str(self.tileStack[0])), 0, 0)
        def drawMenu(self):
            if menu.is_enabled():
                menu.draw(screen)
                menu.update(events)
        def drawGame(self):
            if self.hasStarted:
                screen.fill((32, 16, 8))
                for i in self.placedTiles.keys():
                    for j in self.placedTiles[i].keys():
                        screen.blit(self.placedTiles[i][j].surface, (self.placedTiles[i][j].posX + self.relativeX, self.placedTiles[i][j].posY + self.relativeY))
                screen.blit(self.nextTile.surface, (0, 0))
        def drawAll(self):
            self.drawGame()
            self.drawMenu()
        def placeTile(self, mousePos):
            if len(self.tileStack) > 0:        
                    x = mousePos[0] - self.relativeX
                    y = mousePos[1] - self.relativeY
                    posX = math.floor(x / 128) * 128
                    posY = math.floor(y / 128) * 128                    
                    keysList = []
                    for i in self.placedTiles.keys():
                        keysList.append(i)
                    if posX in keysList:
                        keysList.clear()
                        for i in self.placedTiles[posX].keys():
                            keysList.append(i)
                        if posY not in keysList:
                            self.placedTiles[posX][posY] = self.nextTile
                            self.placedTiles[posX][posY].posX = posX
                            self.placedTiles[posX][posY].posY = posY
                        else:
                            return
                    else:
                        self.placedTiles[posX] = {}
                        self.placedTiles[posX][posY] = self.nextTile
                        self.placedTiles[posX][posY].posX = posX
                        self.placedTiles[posX][posY].posY = posY
                    self.tileStack.pop(0)
                    if len(self.tileStack) > 0:
                        self.nextTile = self.Tile(getattr(ts, 'tile' + str(self.tileStack[0])), 0, 0)
        def checkAvaiableSpots(self):
            pass
        class Tile:
            def __init__(self, id, posX, posY):
                self.id = id
                self.txtPosX = self.id.x
                self.txtPosY = self.id.y
                tileTxt = tileSet.subsurface(self.txtPosX, self.txtPosY, 256, 256)
                self.surface = pygame.transform.scale(tileTxt, (128, 128))
                self.posX = posX
                self.posY = posY
                self.rotation = 0   
                self.cities = self.id.cities
                self.fields = self.id.fields
                self.roads = self.id.roads
                self.cloister = self.id.cloister
                self.shield = self.id.shield       
            def rotateTileImage(self):
                self.surface = pygame.transform.rotate(self.surface, -90)
                self.rotateTile()
            def rotateTile(self):
                rotatePattern = ['N', 'E', 'S', 'W']
                rotatePatternExtended = ['NNE', 'ENE', 'ESE', 'SSE', 'SSW', 'WSW', 'WNW', 'NNW']


app = App()
game = app.Game()

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
            app.mouseMoving = 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: app.mouseLeftClicked = 1
            if event.button == 3: app.mouseRightClicked = 1

        if game.hasStarted:
            if app.mouseMoving and app.mouseLeftClicked:
                game.relativeX += event.rel[0]
                game.relativeY += event.rel[1]
                mouseMoved = 1
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not app.mouseMoving and not mouseMoved:
                game.placeTile(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3 and not app.mouseMoving and not mouseMoved:
                game.nextTile.rotateTileImage()

        if event.type == pygame.MOUSEMOTION:
            app.mouseMoving = 0            
        if event.type == pygame.MOUSEBUTTONUP: 
            if event.button == 1: app.mouseLeftClicked = 0
            if event.button == 3: app.mouseRightClicked = 0
            mouseMoved = 0

    game.drawAll()
    pygame.display.update()

    FramePerSec.tick(FPS)