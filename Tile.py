from tkinter import *

class Tile:

    def __init__(self, row, col, width, isBomb, num, gameOffset, canvas):
        self.canvas = canvas
        self.row = row
        self.col = col
        self.width = width
        self.gameOffset = gameOffset
        self.colors = ['#7c7a77', '#cfd0d2', '#fbd083', '#ed2939']
        self.color = None

        self.isHidden = True # Hidden / Opened
        self.isFlagged = False
        self.isBomb = False
        self.num = num
        
        self.tileArea = canvas.create_rectangle(self.getX(0), self.getY(0),self.getX(1), self.getY(1), fill=self.colors[0])
        self.textArea = canvas.create_text(self.gameOffset + self.width/2 + self.col * self.width,self.gameOffset + self.width/2 + self.row * self.width, font="arial 20", text="")

        # Idea for flag, not nice.
        #self.flagBase = canvas.create_rectangle(self.getX(0) + width/3, self.getY(1) - width/10, self.getX(1) - width/3, self.getY(1) - 2*width/10, fill="black")
        #self.flagPole = canvas.create_rectangle(self.getX(0) + width/2, self.getY(1) - width/10, self.getX(1) - width/2, self.getY(1) - 2*width/3, fill="black")
        #self.flagCloth = canvas.create_polygon([self.getX(1) - width/2, self.getY(1) - 2*width/3, self.getX(1) - width/4, self.getY(1) - width/2, self.getX(1) - width/2, self.getY(1) - width/3], fill='red')

    def getX(self, colNumber):
        return (self.col + colNumber)*self.width + self.gameOffset
    
    def getY(self, rowNumber): 
        return (self.row + rowNumber)*self.width + self.gameOffset

    def updateTile(self, info):
        if info == 'Flag':
            if self.isFlagged == True:
                self.setColor(2)
            elif self.isFlagged == False:
                self.setColor(0)
        elif info == 'Bomb':
            self.setColor(3)
        elif info == 'Visible':
            self.setColor(1)

    def setColor(self, colorNumber):
        self.canvas.itemconfig(self.tileArea, fill=self.colors[colorNumber])

    def getRow(self):
        return self.row

    def getCol(self):
        return self.col

    def getBomb(self):
        return self.isBomb
    
    def setBomb(self):
        self.isBomb = True
        self.num = -1

    def getFlag(self):
        return self.isFlagged

    def setFlag(self):
        if self.isHidden == True:
            self.isFlagged = not self.isFlagged
            self.updateTile('Flag')

    def forceFlag(self):
        self.isFlagged = True
        self.updateTile('Flag')
    
    def getHidden(self):
        return self.isHidden

    def openTile(self):
        if self.isHidden == True and self.isFlagged == False:
            self.isHidden = False
            self.updateTile('Visible')
            
            if self.isBomb == False and self.num != 0:
                self.canvas.itemconfig(self.textArea, text=str(self.num), fill=self.color)
            elif self.isBomb == True:
                self.setColor(3)

    def getNum(self):
        return self.num

    def setNum(self, num, color):
        self.num = num
        self.color = color
