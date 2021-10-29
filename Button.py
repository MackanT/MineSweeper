from tkinter import *
from tkinter import font

class Button:

    def __init__(self, x_pos=0, y_pos=0, width=10, height=10, text='', font=None, color=None, canvas=None):
        
        self.canvas = canvas
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.font = font
        self.mouse_in_box = False

        self.create_button()

    def create_button(self):
        self.button_area = self.canvas.create_rectangle(self.x_pos, self.y_pos, self.x_pos + self.width, self.y_pos + self.height, fill=self.color)
        self.button_text = self.canvas.create_text(self.x_pos + self.width/2, self.y_pos + self.height/2, text=self.text, font=self.font)

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

        if x_bool and y_bool: return True
        else: return False
    
    def set_button_highlighted(self, state):
        self.mouse_in_box = state

    def get_button_highlighted(self):
        return self.mouse_in_box

class Slide_Button(Button):

    def __init__(self, x_pos=0, y_pos=0, width=10, height=10, text='', font=None, color=None, canvas=None, x_anim=0, y_anim=0):
        
        super().__init__(x_pos, y_pos, width, height, text, font, color, canvas)

        self.x_anim = x_anim
        self.y_anim = y_anim
    
    def is_selected(self, state):
        if state:
            self.canvas.move(self.button_area, self.x_anim, self.y_anim)
            self.canvas.move(self.button_text, self.x_anim, self.y_anim)
        else:
            self.canvas.move(self.button_area, -self.x_anim, -self.y_anim)
            self.canvas.move(self.button_text, -self.x_anim, -self.y_anim)

class Pop_Button(Button):

    def __init__(self, x_pos=0, y_pos=0, width=10, height=10, text='', font=None, color=None, canvas=None, x_anim=0, y_anim=0):
        
        super().__init__(x_pos, y_pos, width, height, text, font, color, canvas)

        self.x_anim = x_anim
        self.y_anim = y_anim
    
    def is_selected(self, state):
        
        x0, y0, x1, y1 = self.canvas.coords(self.button_area)

        if state:
            self.canvas.coords(self.button_area, x0-self.x_anim, y0-self.y_anim, x1+self.x_anim, y1+self.y_anim)
        else:
            self.canvas.coords(self.button_area, x0+self.x_anim, y0+self.y_anim, x1-self.x_anim, y1-self.y_anim)