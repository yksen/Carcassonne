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

tileset = pygame.image.load("textures/tiles.png").convert()
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
            self.turnState = "tile"
            self.gameStateMenuWidth = 300
            self.relativeX = -(math.floor(self.boardSize / 2) * 128) + math.floor(((SCREEN_WIDTH - self.gameStateMenuWidth) / 128 / 2)) * 128
            self.relativeY = -(math.floor(self.boardSize / 2) * 128) + math.floor((SCREEN_HEIGHT / 128 / 2)) * 128
            self.placedTile = None
            self.placedTiles = []            
            for i in range(self.boardSize):
                self.placedTiles.append([])
                for j in range(self.boardSize):                          
                    self.placedTiles[i].append(None)
            self.availableSpots = [] 
            self.meepleSpots = []     
            self.tileStack = []
            self.drawNextTile = 1
            self.currentRotation = 0            
            self.playerTurn = 0
            self.playerCount = 2
            self.playerNames = []
            self.playerColors = (blueMeeple, greenMeeple, redMeeple, yellowMeeple)
            self.playerMeeples = [7, 7, 7, 7]
            self.meeplePositions = [[] ,[] ,[] ,[]]
            self.playerPoints = [0, 0, 0, 0]
        def start(self):
            self.hasStarted = 1
            self.setPlayerNames()
            self.gamesetup()
            settingsMenu.remove_widget(settingsMenu.get_widgets()[-1])
        def launchsettingsMenu(self):
            menu.toggle()
            settingsMenu.toggle()
        def setPlayerCount(self, x, value):
            self.playerCount = value
            for n, widget in enumerate(settingsMenu.get_widgets()):
                if n != 0 and n != 1 and n != 2:
                    settingsMenu.remove_widget(widget)
            for i in range(self.playerCount):
                settingsMenu.add.text_input("", default = "Player " + str(i + 1) + " name", repeat_keys_interval_ms=10, maxchar=20)
            settingsMenu.add.label('')
            settingsMenu.add.button('Play', game.start)
        def setPlayerNames(self):
            for i in range(self.playerCount):
                self.playerNames.append(settingsMenu.get_widgets()[3 + i].get_value())
        def gamesetup(self):
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
        def drawsettingsMenu(self):
            settingsMenu.draw(screen)
            settingsMenu.update(events)
        def drawMenu(self):            
            menu.draw(screen)
            menu.update(events)
        def getSidePos(self, side, size):        
            if side == 'N': return (64 - size / 2, 10)
            if side == 'S': return (64 - size / 2, 118 - size)
            if side == 'E': return (118 - size, 64 - size / 2)
            if side == 'W': return (10, 64 - size / 2)
            if side == 'C': return (64 - size / 2, 64 - size / 2)
        def drawGame(self):
            if self.hasStarted:
                screen.fill((77, 40, 0))
                for col in self.placedTiles:
                    for tile in col:
                        if tile != None:
                            x = tile.col * 128 + math.floor(self.relativeX)
                            y = tile.row * 128 + math.floor(self.relativeY)
                            tileTxt = tileset.subsurface(tile.txtPosX, tile.txtPosY, 256, 256)
                            scaledTxt = pygame.transform.scale(tileTxt, (128, 128))
                            screen.blit(pygame.transform.rotate(scaledTxt, -90 * tile.rotation), (x, y))
                for n, player in enumerate(self.meeplePositions):
                    for meeple in player:
                        scaledTxt = pygame.transform.scale(self.playerColors[n], (40, 40))       
                        side = self.getSidePos(meeple[2], 40)
                        x = meeple[0] * 128 + math.floor(self.relativeX) + side[0]
                        y = meeple[1] * 128 + math.floor(self.relativeY) + side[1]           
                        screen.blit(scaledTxt, (x, y))
                if self.turnState == 'meeple':
                    for spot in self.meepleSpots:
                        side = self.getSidePos(spot[2], 20)
                        x = spot[0] * 128 + math.floor(self.relativeX) + side[0]
                        y = spot[1] * 128 + math.floor(self.relativeY) + side[1]  
                        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x, y, 20, 20))
                if self.turnState == 'tile':
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
            text = font.render('Tiles left: ' + str(len(self.tileStack) - 1), True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH - self.gameStateMenuWidth / 2, 230)))
            if self.playerTurn < len(self.playerNames):
                text = font.render(str(self.playerNames[self.playerTurn]) + "'s turn", True, (0, 0, 0))
            screen.blit(text, text.get_rect(center=(SCREEN_WIDTH - self.gameStateMenuWidth / 2, SCREEN_HEIGHT - 32)))
            if self.drawNextTile:
                tileTxt = tileset.subsurface(self.nextTile.txtPosX, self.nextTile.txtPosY, 256, 256)
                scaledTxt = pygame.transform.scale(tileTxt, (128, 128))
                screen.blit(pygame.transform.rotate(scaledTxt, -90 * self.nextTile.rotation), (SCREEN_WIDTH - 128 - ((self.gameStateMenuWidth - 128) / 2), 64))
            for n, name in enumerate(self.playerNames):
                infoX = SCREEN_WIDTH - self.gameStateMenuWidth + 16
                infoY = 320 + n * 80
                infoWidth = self.gameStateMenuWidth - 32
                infoHeight = 64
                pygame.draw.rect(screen, (77, 40, 0), pygame.Rect(infoX - 4, infoY - 4, infoWidth + 8, infoHeight + 8))
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
                self.drawsettingsMenu()
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
                    self.placedTile = self.placedTiles[x][y]

                    self.tileStack.pop(0)
                    self.currentRotation = 0 
                    if len(self.tileStack) > 0:
                        self.nextTile = self.Tile(getattr(ts, 'tile' + str(self.tileStack[0])), 0, 0)
                    else:
                        self.drawNextTile = 0
                    self.checkMeepleSpots()   
                    if len(self.meepleSpots) > 0:
                        self.turnState = 'meeple'      
                    else:
                        self.scoreCloisters(self.placedTile)
                        self.scoreRoads(self.placedTile)
                        self.playerTurn = 0 if self.playerTurn + 1 > self.playerCount - 1 else self.playerTurn + 1
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

        def placeMeeple(self, mousePos):
            posX = mousePos[0]
            posY = mousePos[1]

            if self.playerMeeples[self.playerTurn] > 0:
                for spot in self.meepleSpots:
                    side = self.getSidePos(spot[2], 20)
                    x = spot[0] * 128 + math.floor(self.relativeX) + side[0]
                    y = spot[1] * 128 + math.floor(self.relativeY) + side[1]  
                    if pygame.Rect.collidepoint(pygame.Rect(x, y, 20, 20), (posX, posY)):
                        self.meeplePositions[self.playerTurn].append([self.placedTile.col, self.placedTile.row, spot[2]])            
                        self.scoreCloisters(self.placedTile)
                        self.scoreRoads(self.placedTile)
                        self.playerMeeples[self.playerTurn] -= 1
                        self.playerTurn = 0 if self.playerTurn + 1 > self.playerCount - 1 else self.playerTurn + 1
                        self.turnState = 'tile' 
            else:
                self.scoreCloisters(self.placedTile)
                self.scoreRoads(self.placedTile)
                self.playerTurn = 0 if self.playerTurn + 1 > self.playerCount - 1 else self.playerTurn + 1
                self.turnState = 'tile'
        def checkMeepleSpots(self):
            self.meepleSpots.clear()
    
            self.checkCloisters(self.placedTile)
            self.checkRoads(self.placedTile)
            # self.checkCities(self.placedTile)

        def checkCloisters(self, tile):
            if tile.cloister:
                self.meepleSpots.append((tile.col, tile.row, 'C'))
        def scoreCloisters(self, tile):
            tilesAround = []
            for i in range(3):
                for j in range(3):
                    tilesAround.append(self.placedTiles[tile.col - 1 + i][tile.row - 1 + j])
            for tile2 in tilesAround:
                if tile2 != None and tile2.cloister:
                    cloisterCompleted = 1
                    for i in range(3):
                        for j in range(3):    
                            if self.placedTiles[tile2.col - 1 + i][tile2.row - 1 + j] == None:
                                cloisterCompleted = 0
                                break
                    if cloisterCompleted:                  
                        pos = [tile2.col, tile2.row, 'C']
                        for n, player in enumerate(self.meeplePositions):
                            if pos in player:
                                self.playerPoints[n] += 9
                                self.playerMeeples[n] += 1
                                player.remove(pos)
        def checkRoads(self, tile):
            x = tile.col
            y = tile.row

            for road in tile.roads:
                isAvailable = 1
                for side in road:
                    if side != 'C':
                        startingPos = [x, y, side]
                        pos = [x, y, side]
                        pos2 = [x, y, 0]
                        for i in road:
                            if side in i:
                                tmp = road.copy()
                                tmp.remove(side)
                                pos2[2] = tmp[0]
                        roadNotEnded = 1
                        while roadNotEnded and isAvailable:
                            for i in range(self.playerCount):
                                if pos in self.meeplePositions[i] or pos2 in self.meeplePositions[i]:
                                    isAvailable = 0
                                    break
                            opp = self.getOppositeSide(pos[2])
                            if self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]] is not None: 
                                if len(self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]].roads) > 0:
                                    for road2 in self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]].roads:
                                        if opp[2] in road2:
                                            if 'C' in road2: 
                                                roadNotEnded = 0
                                                pos2 = [pos[0] + opp[0], pos[1] + opp[1], opp[2]]
                                                for i in range(self.playerCount):
                                                    if pos2 in self.meeplePositions[i]:
                                                        isAvailable = 0
                                                break
                                            else:
                                                pos2 = [pos[0] + opp[0], pos[1] + opp[1], opp[2]]
                                                tmp = road2.copy()
                                                tmp.remove(opp[2])
                                                pos = [pos[0] + opp[0], pos[1] + opp[1], tmp[0]]
                            else:
                                roadNotEnded = 0
                                break
                if isAvailable:
                    self.meepleSpots.append(startingPos)
        def scoreRoads(self, tile):
            x = tile.col
            y = tile.row
            
            for road in tile.roads:
                roadLength = 1
                roadEndsCount = 0
                meeplesCount = [0, 0, 0, 0]
                meeplesToRemove = []
                for side in road:
                    if side == 'C':
                            roadEndsCount += 1
                    else:
                        pos = [x, y, side]
                        pos2 = [x, y, 0]
                        for i in road:
                            if side in i:
                                tmp = road.copy()
                                tmp.remove(side)
                                pos2[2] = tmp[0]                        
                        roadNotEnded = 1
                        while roadNotEnded:
                            roadLength += 1
                            for i in range(self.playerCount):
                                if pos in self.meeplePositions[i]: 
                                    meeplesToRemove.append(pos)
                                    meeplesCount[i] += 1
                                if pos2 in self.meeplePositions[i]:
                                    meeplesToRemove.append(pos2)
                                    meeplesCount[i] += 1
                            opp = self.getOppositeSide(pos[2])
                            if self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]] is not None: 
                                if len(self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]].roads) > 0:
                                    for road2 in self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]].roads:
                                        if opp[2] in road2:
                                            if 'C' in road2:
                                                roadEndsCount += 1
                                                roadNotEnded = 0
                                                pos2 = [pos[0] + opp[0], pos[1] + opp[1], opp[2]]
                                                for i in range(self.playerCount):
                                                    if pos2 in self.meeplePositions[i]:
                                                        meeplesToRemove.append(pos2)
                                                        meeplesCount[i] += 1
                                                break
                                            else:
                                                pos2 = [pos[0] + opp[0], pos[1] + opp[1], opp[2]]
                                                tmp = road2.copy()
                                                tmp.remove(opp[2])
                                                pos = [pos[0] + opp[0], pos[1] + opp[1], tmp[0]]
                            else:
                                roadNotEnded = 0
                                break
                if roadEndsCount == 2:
                    high = max(meeplesCount)
                    for n, i in enumerate(meeplesCount):
                        if i == high:
                            self.playerPoints[n] += roadLength
                    for meeple in meeplesToRemove:
                        for player in self.meeplePositions:
                            if meeple in player:
                                player.remove(meeple)
        def checkCities(self, tile):
            x = tile.col
            y = tile.row

            for city in tile.cities:
                isAvailable = 1
                for side in city:
                    startingPos = [x, y, side]
                    pos = [x, y, side]
                    pos2 = [x, y, 0]
                    for i in city:
                        if side in i:
                            tmp = city.copy()
                            tmp.remove(side)
                            pos2[2] = tmp[0]
                    cityNotEnded = 1
                    while cityNotEnded and isAvailable:
                        for i in range(self.playerCount):
                            if pos in self.meeplePositions[i] or pos2 in self.meeplePositions[i]:
                                isAvailable = 0
                                break
                        opp = self.getOppositeSide(pos[2])
                        if self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]] is not None: 
                            if len(self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]].cities) > 0:
                                for city2 in self.placedTiles[pos[0] + opp[0]][pos[1] + opp[1]].cities:
                                    if opp[2] in city2:
                                        if 'C' in city2: 
                                            cityNotEnded = 0
                                            pos2 = [pos[0] + opp[0], pos[1] + opp[1], opp[2]]
                                            for i in range(self.playerCount):
                                                if pos2 in self.meeplePositions[i]:
                                                    isAvailable = 0
                                            break
                                        else:
                                            pos2 = [pos[0] + opp[0], pos[1] + opp[1], opp[2]]
                                            tmp = city2.copy()
                                            tmp.remove(opp[2])
                                            pos = [pos[0] + opp[0], pos[1] + opp[1], tmp[0]]
                        else:
                            cityNotEnded = 0
                            break
                if isAvailable:
                    self.meepleSpots.append(startingPos)
        def getOppositeSide(self, side):
            if side == 'N': return [0, -1, 'S']
            if side == 'S': return [0, 1, 'N']
            if side == 'E': return [1, 0, 'W']
            if side == 'W': return [-1, 0, 'E']
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
menu.add.button('Play', game.launchsettingsMenu)
menu.add.button('Quit', pygame_menu.events.EXIT)

settingsMenu = pygame_menu.Menu('', SCREEN_WIDTH, SCREEN_HEIGHT, theme = pygame_menu.themes.THEME_DARK)
settingsMenu.toggle()
settingsMenu.add.selector('Player count: ', [('2', 2), ('3', 3), ('4', 4)], default = game.playerCount - 2, onchange = game.setPlayerCount)
settingsMenu.add.label('')
settingsMenu.add.label('Enter player names:')
settingsMenu.add.label('')
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
                if game.turnState == 'tile':
                    game.placeTile(pygame.mouse.get_pos())                
                elif game.turnState == 'meeple':
                    game.placeMeeple(pygame.mouse.get_pos())
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