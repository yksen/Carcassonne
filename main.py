import pygame, sys, random, pygame_menu, random, math, copy
from pygame.locals import *
import tileSets as ts

pygame.init()
 
FPS = 144
FramePerSec = pygame.time.Clock()

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Carcassonne")
tileSet = pygame.image.load("tiles.png").convert()

class App:
    def __init__(self):
        self.mouseLeftClicked = 0
        self.mouseRightClicked = 0
        self.mouseMoving = 0
    class Game:
        def __init__(self):
            self.boardSize = 101
            self.hasStarted = 0        
            self.relativeX = -(math.floor(self.boardSize / 2) * 128) + math.floor((SCREEN_WIDTH / 128 / 2)) * 128
            self.relativeY = -(math.floor(self.boardSize / 2) * 128) + math.floor((SCREEN_HEIGHT / 128 / 2)) * 128
            self.placedTiles = []
            for i in range(self.boardSize):
                self.placedTiles.append([])
                for j in range(self.boardSize):                          
                    self.placedTiles[i].append(None)
            self.availableSpots = []            
            self.tileStack = []
            self.drawNextTile = 1
            self.currentRotation = 0
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
            self.placedTiles[50][50] = self.Tile(ts.tile36, 50, 50)
            self.nextTile = self.Tile(getattr(ts, 'tile' + str(self.tileStack[0])), 0, 0)
            self.checkAvaiableSpots()
        def drawMenu(self):
            if menu.is_enabled():
                menu.draw(screen)
                menu.update(events)
        def drawGame(self):
            if self.hasStarted:
                screen.fill((77, 40, 0))
                for col in self.placedTiles:
                    for tile in col:
                        if tile != None:
                            x = tile.col * 128 + math.floor(self.relativeX)
                            y = tile.row * 128 + math.floor(self.relativeY)
                            tileTxt = tileSet.subsurface(tile.txtPosX, tile.txtPosY, 256, 256)
                            scaledTxt = pygame.transform.scale(tileTxt, (128, 128))
                            screen.blit(pygame.transform.rotate(scaledTxt, -90 * tile.rotation), (x, y))
                for i in range(self.boardSize):
                    for j in range(self.boardSize):
                        if 1 in self.availableSpots[i][j]:
                            x = i * 128 + math.floor(self.relativeX)
                            y = j * 128 + math.floor(self.relativeY)
                            pygame.draw.rect(screen, (179, 89, 0), pygame.Rect(x, y, 128, 128))
                            if self.availableSpots[i][j][self.currentRotation] == True:
                                pygame.draw.rect(screen, (0, 153, 0), pygame.Rect(x, y, 128, 128))                                                  
                if self.drawNextTile:
                    tileTxt = tileSet.subsurface(self.nextTile.txtPosX, self.nextTile.txtPosY, 256, 256)
                    scaledTxt = pygame.transform.scale(tileTxt, (128, 128))
                    screen.blit(pygame.transform.rotate(scaledTxt, -90 * self.nextTile.rotation), (0, 0))
        def drawAll(self):
            self.drawGame()
            self.drawMenu()
        def placeTile(self, mousePos):                     
            if len(self.tileStack) > 0:                         
                posX = mousePos[0] - self.relativeX
                posY = mousePos[1] - self.relativeY
                x = math.floor(posX / 128)
                y = math.floor(posY / 128)      
                if self.availableSpots[x][y][self.currentRotation]:
                    self.placedTiles[x][y] = self.nextTile.rotateTile(self.currentRotation)
                    self.placedTiles[x][y].col = x
                    self.placedTiles[x][y].row = y            
                    self.tileStack.pop(0)
                    self.currentRotation = 0 
                    if len(self.tileStack) > 0:
                        self.nextTile = self.Tile(getattr(ts, 'tile' + str(self.tileStack[0])), 0, 0)
                    else:
                        self.drawNextTile = 0                   
                self.checkAvaiableSpots()                   
        def checkAvaiableSpots(self):
            self.availableSpots.clear()
            for i in range(self.boardSize):
                self.availableSpots.append([])
                for j in range(self.boardSize):
                    self.availableSpots[i].append([0, 0, 0, 0])
            for x in range(1, self.boardSize - 1):
                for y in range(1, self.boardSize - 1):
                    if self.placedTiles[x][y] == None:
                        top = self.getTile(x, y - 1)
                        right = self.getTile(x + 1, y)
                        bot = self.getTile(x, y + 1)
                        left = self.getTile(x - 1, y)
                        
                        for rot in range(4):
                            curr = self.nextTile.rotateTile(rot)
                            if top is None and right is None and bot is None and left is None: 
                                break
                            fits = True
                            for side in ['N', 'E', 'S', 'W']:
                                terrainType = curr.getTerrain(side)
                                if side == 'N': 
                                    fitsTop = top is None or top.getTerrain('S') == terrainType
                                    fits = fits and fitsTop
                                elif side == 'E':
                                    fitsRight = right is None or right.getTerrain('W') == terrainType
                                    fits = fits and fitsRight
                                elif side == 'S':
                                    fitsBot = bot is None or bot.getTerrain('N') == terrainType
                                    fits = fits and fitsBot
                                else:
                                    fitsLeft = left is None or left.getTerrain('E') == terrainType
                                    fits = fits and fitsLeft
                            if fits:
                                self.availableSpots[x][y][rot] = True    
                            
        def getTile(self, x, y):
            return self.placedTiles[x][y]
        class Tile:
            def __init__(self, id, col, row):
                self.id = id
                self.txtPosX = self.id.x
                self.txtPosY = self.id.y
                self.rotation = 0
                self.col = col
                self.row = row
                self.cities = self.id.cities
                self.fields = self.id.fields
                self.roads = self.id.roads
                self.cloister = self.id.cloister
                self.shield = self.id.shield       
            def rotateTileImage(self):
                self.rotation = (self.rotation + 1) % 4
            def rotateTile(self, rotations):
                rotatePattern = ['N', 'E', 'S', 'W']
                rotatePatternExtended = ['NNE', 'ENE', 'ESE', 'SSE', 'SSW', 'WSW', 'WNW', 'NNW']
                rotatedTile = copy.deepcopy(self)
                for i in range(len(rotatedTile.cities)):
                    for j in range(len(rotatedTile.cities[i])):                        
                        rotatedTile.cities[i][j] = rotatePattern[(rotatePattern.index(rotatedTile.cities[i][j]) + rotations) % len(rotatePattern)]
                for i in range(len(rotatedTile.fields)):
                    for j in range(len(rotatedTile.fields[i])):
                        rotatedTile.fields[i][j] = rotatePatternExtended[(rotatePatternExtended.index(rotatedTile.fields[i][j]) + rotations * 2) % len(rotatePatternExtended)]
                for i in range(len(rotatedTile.roads)):
                    for j in range(len(rotatedTile.roads[i])):                        
                        if rotatedTile.roads[i][j] != 'C':
                            rotatedTile.roads[i][j] = rotatePattern[(rotatePattern.index(rotatedTile.roads[i][j]) + rotations) % len(rotatePattern)]
                return rotatedTile   
            def getTerrain(self, side):   
                for i in self.roads:          
                    if side in i:
                        return 'road'
                for i in self.cities:
                    if side in i:
                        return 'city'                
                return 'field'                


app = App()
game = app.Game()

menu = pygame_menu.Menu('', SCREEN_WIDTH, SCREEN_HEIGHT, theme = pygame_menu.themes.THEME_DARK)
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
                game.currentRotation = (game.currentRotation + 1) % 4

        if event.type == pygame.MOUSEMOTION:
            app.mouseMoving = 0            
        if event.type == pygame.MOUSEBUTTONUP: 
            if event.button == 1: app.mouseLeftClicked = 0
            if event.button == 3: app.mouseRightClicked = 0
            mouseMoved = 0

    game.drawAll()
    pygame.display.update()

    FramePerSec.tick(FPS)