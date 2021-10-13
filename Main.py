from tkinter import *
from array import *
import os
import threading
import numpy as np
import random
from Button import Button
from Tile import Tile

# Design Parameters
gameScreenWidth = 1300
gameOffset = 50
tileWidth = 40
numberColors = ['#FFFFFF', '#0000FF', '#007B00', '#FF0000', '#00007B', '#7B0000', '#007B7B', '#7B7B7B', '#000000']
customColors = ['#565554', '#f6f193', '#7c7a77', '#cfd0d2', '#fbd083'] # Background Gray, Button Yellow, Hidden Tile Gray, Visible Tile Gray, Accent Orange

class Minesweeper():
    
    def __init__(self):

        # Screen Settings
        self.window = Tk()
        self.window.title('The Electric Boogaloo - Minesweeper 2')
        self.canvas = Canvas(self.window, width = gameScreenWidth/2, height = gameScreenWidth/3, bg=customColors[0])
        self.canvas.pack()

        self.window.bind('<Button-1>', self.leftClick)
        self.window.bind('<Button-2>', self.middleClick)
        self.window.bind('<Button-3>', self.rightClick)
        self.window.bind('<space>', self.middleClick)

        # Graphical Settings
        self.font_text = ("GOST Common", 12, "bold")

        # Image Loading
        self.cwd = os.getcwd()
        imageFileName = self.cwd + "\\images\\startup.png"
        self.startUpSplash = PhotoImage(file=imageFileName)

        # Global Game Settings
        self.booleanGameActive = False
        self.booleanStartup = True
        self.booleanFirstClick = True

        # Highscores
        self.saveFiles = ['easy', 'medium', 'hard']
        self.savedHighscores = 10
        self.easyScores = []
        self.mediumScores = []
        self.hardScores = []
        self.highScores = [self.easyScores, self.mediumScores, self.hardScores]

        # Fixed Game Settings
        self.buttonNames     = ['Easy', 'Intermediate', 'Hard', 'Quit']
        self.numberOfRows    = [9, 16, 16]
        self.numberOfColumns = [9, 16, 30]
        self.numberOfMines   = [10, 40, 99]
        self.gameRows = self.gameCols = self.gameMines = 0   

        self.currentTime = self.currentFlagged = 0
        self.currentDifficulty = None
        self.startTimer()

        self.startUpScreenButtons = []
        self.currentBoard = []

        self.drawStartup()
        self.loadHighscores()

    def mainloop(self):
        self.window.mainloop()

    def startTimer(self):
        threading.Timer(1.0, self.startTimer).start()
        if self.booleanGameActive == True:
            self.currentTime += 1
            self.canvas.itemconfig(self.timeMarker, text=str(self.currentTime))

    def resetTimer(self):
        self.currentTime = 0

    def loadHighscores(self):
        for i in range(len(self.saveFiles)):
            fileLocation = self.cwd + "/highscores/" + self.saveFiles[i] + '.txt'
            workingFile = open(fileLocation)

            for line in workingFile:
                commaPos = line.find(',')
                self.highScores[i].append(line[0:commaPos])
            workingFile.close()

    def saveHighscores(self):
        fileLocation = self.cwd + "/highscores/" + self.saveFiles[self.currentDifficulty] + '.txt'
        workingFile = open(fileLocation, 'w')

        for element in self.highScores[self.currentDifficulty]:
            outputText = str(element) + ', M@ckanT \n'
            workingFile.write(outputText)
        workingFile.close()

    def checkHighscores(self):

        print('checking highscores')
        currentGameTime = self.currentTime
        tempList = self.highScores[self.currentDifficulty]
        saveScores = False
        
        for i in range(self.savedHighscores):

            if i >= len(tempList):
                break
            elif currentGameTime < int(tempList[i]):
                saveScores = True
                print('New Highscore! %d seconds time' %(currentGameTime)) 
                if i == 0:
                    tempList = [currentGameTime] + tempList
                else:
                    tempList = tempList[0:i] + [str(currentGameTime)] + tempList[i:]
                    if len(tempList) > self.savedHighscores: tempList = tempList[0:(self.savedHighscores-1)]     
                
                if saveScores == True:
                    self.highScores[self.currentDifficulty] = tempList
                    self.saveHighscores()
                    break

    def leaveStartup(self, buttonClicked):
        self.gameRows = self.numberOfRows[buttonClicked]
        self.gameCols = self.numberOfColumns[buttonClicked]
        self.gameMines = self.numberOfMines[buttonClicked]
        self.currentDifficulty = buttonClicked
        self.booleanStartup = False
        self.newGame()
    
    def leftClick(self, event): 
        # Use buttons on startup screen
        if self.booleanStartup == True:
            buttonClicked = self.startUpScreenButtonClicked(event.x, event.y)
            self.window.destroy() if buttonClicked == 3 else self.leaveStartup(buttonClicked)
        else:
            if self.newGameButton.pointInBox(event.x, event.y) == True:
                self.newGame()
            else: 
                if self.booleanFirstClick == True:
                    # Restart game until OK start - unoptimal, but works
                    while self.tileAction('num', event) != 0 or self.tileAction('bomb', event) == True:
                        self.newGame()
                    self.booleanFirstClick = False
                    self.booleanGameActive = True
                    self.tileAction('open', event)
                elif self.booleanGameActive == True:
                    self.tileAction('open', event)

    def startUpScreenButtonClicked(self, x, y):
        positionIterator = 0
        for item in self.startUpScreenButtons: 
            if self.startUpScreenButtons[positionIterator].pointInBox(x, y) == True:
                return positionIterator
            else:
                positionIterator = positionIterator + 1

    def rightClick(self, event):
        if self.booleanGameActive == True or self.booleanFirstClick == True:
           self.tileAction('flag', event)
           self.countFlags()
    
    def middleClick(self, event):
        if self.booleanGameActive == True or self.booleanFirstClick == True:
            workTile = self.tileAction('tile', event)

            if workTile.getHidden() == True:
               workTile.setFlag()
               self.countFlags()
            elif workTile.isHidden == False and workTile.getFlag() == False:
                if self.countNearbyFlags(workTile) == workTile.getNum():
                    self.openSquare(workTile)
    
    def isTile(self, x, y):
        if x >= 0 and x < self.gameCols and y >= 0 and y < self.gameRows:
            return True
        else:
            return False

    def tileAction(self, function, event):
        clickedCol = (event.x - gameOffset) / tileWidth
        clickedRow = (event.y - gameOffset) / tileWidth
        clickedCol = int(clickedCol) if clickedCol > 0 else -1
        clickedRow = int(clickedRow) if clickedRow > 0 else -1

        if self.isTile(clickedCol, clickedRow) == True:
            tile = self.currentBoard[clickedRow][clickedCol]

            if function == 'num':
                return tile.getNum()
            elif function == 'bomb':
                return tile.getBomb()
            elif function == 'flag':
                tile.setFlag()
            elif function == 'open':
                self.openTileFunction(tile)
            elif function == 'tile':
                return tile

    def checkLoss(self, tile):
        if tile.getBomb() == True and tile.getFlag() == False:
            for i in range(self.gameCols):
                for j in range(self.gameRows):
                    if self.currentBoard[j][i].isBomb == True:
                        self.currentBoard[j][i].openTile()
            self.booleanGameActive = False

    def checkVictory(self):
        for i in range(self.gameCols):
            for j in range(self.gameRows):
                if self.currentBoard[j][i].getHidden() == True and self.currentBoard[j][i].getBomb() == False:
                    return
        self.openRemainingTiles()
        self.booleanGameActive = False
        self.checkHighscores()

    def openTileFunction(self, tile):
        tile.openTile()
        self.openZeros(tile)
        self.checkLoss(tile)
        self.checkVictory()

    def openRemainingTiles(self):
        for i in range(self.gameCols):
            for j in range(self.gameRows):
                if self.currentBoard[j][i].getBomb() == False:
                    self.currentBoard[j][i].openTile()
                else:
                    self.currentBoard[j][i].forceFlag()

    def newGame(self):
        self.booleanFirstClick = True
        self.booleanGameActive = False
        self.numberOfClicks = 0
        self.resetTimer()
        self.canvas.delete("all")
        self.drawBoard()

    def openZeros(self, tile):
        if tile.getNum() == 0:
            self.openSquare(tile)

    def countNearbyFlags(self, tile):

        numberOfFlags = 0
        for k in range(tile.getRow()-1, tile.getRow()+2):
            for l in range(tile.getCol()-1, tile.getCol()+2): 
                try:
                    if self.currentBoard[k][l].getFlag() == True and k >= 0 and l >= 0:
                        numberOfFlags += 1
                except: 
                    pass
        return numberOfFlags

    def countFlags(self):
        usedFlags = 0
        for i in range(self.gameCols):
            for j in range(self.gameRows):
                if self.currentBoard[j][i].getFlag() == True:
                    usedFlags += 1
        self.canvas.itemconfig(self.flagMarker, text=str(usedFlags))

    def openSquare(self, tile):
        if tile.getBomb() == False:
            for k in range(tile.getRow()-1, tile.getRow()+2):
                for l in range(tile.getCol()-1, tile.getCol()+2): 
                    try:
                        if self.currentBoard[k][l].isHidden == True and k >= 0 and l >= 0 and self.currentBoard[k][l].getFlag() == False:
                            self.openTileFunction(self.currentBoard[k][l])
                    except: 
                        1

    def drawStartup(self):
        for i in range(len(self.buttonNames)):
            self.startUpScreenButtons.append(Button(gameScreenWidth/3 - gameOffset, (2+2*i)*tileWidth, gameScreenWidth/6, 1.5*tileWidth, self.buttonNames[i], customColors[1], self.canvas))
        self.canvas.create_image(gameOffset,2*tileWidth, anchor=NW, image = self.startUpSplash)

    def drawBoard(self):

        self.currentBoard = [[Tile(i, j, tileWidth, None, None, gameOffset, self.canvas) for j in range(self.gameCols)] for i in range(self.gameRows)]
        
        winWidth = self.gameCols * tileWidth + 2*gameOffset
        winHeight = self.gameRows * tileWidth + 2*gameOffset

        self.canvas.config(width=winWidth,height=winHeight)
        self.newGameButton = Button(winWidth/2-gameOffset, 10, 2*gameOffset , 30, 'Newgame', customColors[1], self.canvas)
        self.flagMarker = self.canvas.create_text(tileWidth*(self.gameCols-1/2) + gameOffset, gameOffset/2, fill='white', font='arial 20', text='0')
        self.timeMarker = self.canvas.create_text(tileWidth/2 + gameOffset, gameOffset/2, fill='white', font='arial 20', text='0')

        # Set bombs
        tileIndexes = range(self.gameRows*self.gameCols)
        bombIndexes = random.sample(tileIndexes, self.gameMines)
        for index in bombIndexes:
            self.currentBoard[int(index/self.gameCols)][index%self.gameCols].setBomb()

        self.calculateTileNumbers()

    def calculateTileNumbers(self):
        # Calculate adjacent bombs
        for i in range(self.gameRows):
            for j in range(self.gameCols):
                tile = self.currentBoard[i][j]
                tileBombNumber = 0
                if tile.getBomb() == False:
                    for k in range(tile.getRow()-1, tile.getRow()+2):
                        for l in range(tile.getCol()-1, tile.getCol()+2): 
                            try:
                                if self.currentBoard[k][l].getBomb() == True and k >= 0 and l >= 0:
                                    tileBombNumber += 1
                            except: 
                                tileBombNumber += 0
                else:
                    tileBombNumber = 0
                tile.setNum(tileBombNumber, numberColors[tileBombNumber])

game_instance = Minesweeper()
game_instance.mainloop()