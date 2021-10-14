from tkinter import *

class Tile:

    def __init__(self, row, col, width, font, canvas):
        self.canvas = canvas
        self.row = row
        self.col = col
        self.width = width
        self.colors = ['#7c7a77', '#cfd0d2', '#fbd083', '#ed2939']
        self.color = None
        self.font = font

        self.is_hidden = True # Hidden / Opened
        self.is_flagged = False
        self.is_bomb = False
        self.num = None
        
        self.tile_area = canvas.create_rectangle(self.get_x(0), self.get_y(0),self.get_x(1), self.get_y(1), fill=self.colors[0])
        self.text_area = canvas.create_text(self.width/2 + self.col * self.width, self.width/2 + self.row * self.width, font=self.font, text="")

        # Idea for flag, not nice.
        #self.flagBase = canvas.create_rectangle(self.get_x(0) + width/3, self.get_y(1) - width/10, self.get_x(1) - width/3, self.get_y(1) - 2*width/10, fill="black")
        #self.flagPole = canvas.create_rectangle(self.get_x(0) + width/2, self.get_y(1) - width/10, self.get_x(1) - width/2, self.get_y(1) - 2*width/3, fill="black")
        #self.flagCloth = canvas.create_polygon([self.get_x(1) - width/2, self.get_y(1) - 2*width/3, self.get_x(1) - width/4, self.get_y(1) - width/2, self.get_x(1) - width/2, self.get_y(1) - width/3], fill='red')

    def get_x(self, col_number):
        return (self.col + col_number)*self.width
    
    def get_y(self, row_number): 
        return (self.row + row_number)*self.width

    def update_tile(self, info):
        if info == 'Flag':
            if self.is_flagged == True:
                self.set_color(2)
            elif self.is_flagged == False:
                self.set_color(0)
        elif info == 'Bomb':
            self.set_color(3)
        elif info == 'Visible':
            self.set_color(1)

    def set_color(self, color_number):
        self.canvas.itemconfig(self.tile_area, fill=self.colors[color_number])

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

    def get_bomb(self):
        return self.is_bomb
    
    def set_bomb(self):
        self.is_bomb = True
        self.num = -1

    def get_flag(self):
        return self.is_flagged

    def set_flag(self):
        if self.is_hidden == True:
            self.is_flagged = not self.is_flagged
            self.update_tile('Flag')

    def force_flag(self):
        self.is_flagged = True
        self.update_tile('Flag')
    
    def get_hidden(self):
        return self.is_hidden

    def open_tile(self):
        if self.is_hidden == True and self.is_flagged == False:
            self.is_hidden = False
            self.update_tile('Visible')
            
            if self.is_bomb == False and self.num != 0:
                self.canvas.itemconfig(self.text_area, text=str(self.num), fill=self.color)
            elif self.is_bomb == True:
                self.set_color(3)

    def get_tile_number(self):
        return self.num

    def set_tile_number(self, num, color):
        self.num = num
        self.color = color
