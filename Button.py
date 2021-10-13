from tkinter import *

from numpy.lib.function_base import delete

class Button:

    def __init__(self, x_pos=0, y_pos=0, width=10, height=10, text='', color=None, canvas=None):
        
        self.canvas = canvas
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.text = text
        self.color = color

        self.create_button()

    def create_button(self):
        self.button_area = self.canvas.create_rectangle(self.x_pos, self.y_pos, self.x_pos + self.width, self.y_pos + self.height, fill=self.color)
        self.button_text = self.canvas.create_text(self.x_pos + self.width/2, self.y_pos + self.height/2, text=self.text)

    def delete_button(self):
        self.canvas.delete(self.button_area)
        self.canvas.delete(self.button_text)

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