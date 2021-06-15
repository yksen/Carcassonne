import pygame, sys, random, pygame_menu, math, copy
from pygame.locals import *
import tileSets as ts

pygame.init()

FPS = 144
FramePerSec = pygame.time.Clock()

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Carcassonne")

tileSet = pygame.image.load("textures/tiles.png").convert()
blueMeeple = pygame.image.load("textures/blue-meeple.png").convert_alpha()
greenMeeple = pygame.image.load("textures/green-meeple.png").convert_alpha()
redMeeple = pygame.image.load("textures/red-meeple.png").convert_alpha()
yellowMeeple = pygame.image.load("textures/yellow-meeple.png").convert_alpha()

font = pygame.font.SysFont('calibri', 24)

class App:
    def __init__(self):
        self.mouseLeftClicked = 0
        self.mouseRightClicked = 0
        self.mouseMoving = 0
    class Game:
        def __init__(self):
            self.boardSize = 71
            self.hasStarted = 0
            self.gameStateMenuWidth = 300
            self.relativeX = -(math.floor(self.boardSize / 2) * 128) + math.floor(((SCREEN_WIDTH - self.gameStateMenuWidth) / 128 / 2)) * 128
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
            #####
            self.playerTurn = 0
            self.playerCount = 2
            self.playerNames = []
            self.playerColors = (blueMeeple, greenMeeple, redMeeple, yellowMeeple)
            self.playerMeeples = [7, 7, 7, 7]
            self.playerPoints = [0, 10, 110, 0]
        def start(self):
            self.hasStarted = 1
            self.setPlayerNames()
            self.gameSetup()
        def launchSettingsMenu(self):
            menu.toggle()
            settingsMenu.toggle()
        def setPlayerCount(self, x, value):
            self.playerCount = value
            for n, widget in enumerate(settingsMenu.get_widgets()):
                if n != 0 and n != 1:
                    settingsMenu.remove_widget(widget)
            for i in range(self.playerCount):
                settingsMenu.add.text_input("", default = "Player " + str(i + 1) + " name", repeat_keys_interval_ms=10, maxchar=20)
            settingsMenu.add.button('Play', game.start)
        def setPlayerNames(self):
            for i in range(self.playerCount):
                self.playerNames.append(settingsMenu.get_widgets()[2 + i].get_value())
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
            halfBoardSize = math.floor(self.boardSize / 2)   
            self.placedTiles[halfBoardSize][halfBoardSize] = self.Tile(ts.tile36, halfBoardSize, halfBoardSize)
            self.nextTile = self.Tile(getattr(ts, 'tile' + str(self.tileStack[0])), 0, 0)
            self.checkAvaiableSpots()
        def drawSettingsMenu(self):
            settingsMenu.draw(screen)
            settingsMenu.update(events)
        def drawMenu(self):            
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
                            pygame.draw.rect(screen, (128, 64, 0), pygame.Rect(x, y, 128, 128))
                            if self.availableSpots[i][j][self.currentRotation] == True:
                                pygame.draw.rect(screen, (0, 153, 0), pygame.Rect(x, y, 128, 128))                                                                  
        def drawGameState(self):
            pygame.draw.rect(screen, (200, 115, 24), pygame.Rect(SCREEN_WIDTH - self.gameStateMenuWidth, 0, self.gameStateMenuWidth, SCREEN_HEIGHT))
            pygame.draw.rect(screen, (77, 40, 0), pygame.Rect(SCREEN_WIDTH - 128 - ((self.gameStateMenuWidth - 128) / 2) - 4, 64 - 4, 128 + 2 * 4, 128 + 2 * 4))
            text = font.render('Next tile:', True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH - self.gameStateMenuWidth / 2, 32)))
            text = font.render(str(self.playerNames[self.playerTurn]) + "'s turn", True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH - self.gameStateMenuWidth / 2, SCREEN_HEIGHT - 32)))
            if self.drawNextTile:
                tileTxt = tileSet.subsurface(self.nextTile.txtPosX, self.nextTile.txtPosY, 256, 256)
                scaledTxt = pygame.transform.scale(tileTxt, (128, 128))
                screen.blit(pygame.transform.rotate(scaledTxt, -90 * self.nextTile.rotation), (SCREEN_WIDTH - 128 - ((self.gameStateMenuWidth - 128) / 2), 64))
            for n, name in enumerate(self.playerNames):
                infoX = SCREEN_WIDTH - self.gameStateMenuWidth + 16
                infoY = 320 + n * 80
                infoWidth = self.gameStateMenuWidth - 32
                infoHeight = 64
                pygame.draw.rect(screen, (252, 177, 3), pygame.Rect(infoX, infoY, infoWidth, infoHeight))
                text = font.render(name, True, (0, 0, 0))
                screen.blit(text, text.get_rect(center=(SCREEN_WIDTH - self.gameStateMenuWidth / 2 - 26, infoY + 18)))
                text = font.render(str(self.playerPoints[n]), True, (0, 0, 0))
                screen.blit(text, text.get_rect(center=(SCREEN_WIDTH - 44, infoY + infoHeight / 2 + 2)))
                scaledTxt = pygame.transform.scale(self.playerColors[n], (24, 24))
                for i in range(self.playerMeeples[n]):
                    screen.blit(scaledTxt, (infoX + 12 + i * 28, infoY + infoHeight - 28))            
        def drawAll(self):            
            if menu.is_enabled():
                self.drawMenu()
            if settingsMenu.is_enabled():
                self.drawSettingsMenu()
            if self.hasStarted:
                self.drawGame()
                self.drawGameState()
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
menu.add.button('Play', game.launchSettingsMenu)
menu.add.button('Quit', pygame_menu.events.EXIT)

settingsMenu = pygame_menu.Menu('', SCREEN_WIDTH, SCREEN_HEIGHT, theme = pygame_menu.themes.THEME_DARK)
settingsMenu.toggle()
settingsMenu.add.selector('Player count: ', [('2', 2), ('3', 3), ('4', 4)], default = game.playerCount - 2, onchange = game.setPlayerCount)
settingsMenu.add.label('Player names:')
settingsMenu.add.button('Play', game.start)
game.setPlayerCount('', 2)

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