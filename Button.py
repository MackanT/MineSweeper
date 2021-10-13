from tkinter import *

class Button:

    def __init__(self, x_pos, y_pos, width, height, text, color, canvas):
        self.canvas = canvas
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.text = text
        self.color = color

        self.buttonArea = canvas.create_rectangle(x_pos, y_pos,x_pos + width, y_pos + height, fill=self.color)
        self.buttonText = canvas.create_text(x_pos + width/2, y_pos + height/2, text=text)

    def get_x(self):
        return self.x_pos

    def get_y(self):
        return self.y_pos

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_name(self):
        return self.text

    def point_in_box(self, x, y):

        x_bool = (x >= self.x_pos) and (x <= self.x_pos + self.width)
        y_bool = (y >= self.y_pos) and (y <= self.y_pos + self.height)

        if x_bool == True and y_bool == True:
            return True