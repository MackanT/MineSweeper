from tkinter import *
from array import *
import os
import threading
import numpy as np
import random
from Button import Button
from Tile import Tile

# Design Parameters
game_screen_width = 1300
game_offset = 50
game_tile_width = 40

# Number Colors
number_colors = ['#FFFFFF', '#0000FF', '#007B00', '#FF0000', '#00007B', 
                '#7B0000', '#007B7B', '#7B7B7B', '#000000']

# Background Gray, Button Yellow, Hidden Tile Gray, Visible Tile Gray, Accent Orange
custom_colors = ['#565554', '#f6f193', '#7c7a77', '#cfd0d2', '#fbd083'] 

class Minesweeper():
    
    def __init__(self):

        # Screen Settings
        self.window = Tk()
        self.window.title('The Electric Boogaloo - Minesweeper 2')
        self.canvas = Canvas(self.window, 
                             width = game_screen_width/2, 
                             height = game_screen_width/3, 
                             bg=custom_colors[0]
                            )
        self.canvas.pack()

        self.window.bind('<Button-1>', self.left_click)
        self.window.bind('<Button-2>', self.middle_click)
        self.window.bind('<Button-3>', self.right_click)
        self.window.bind('<space>', self.middle_click)

        # Graphical Settings
        self.font_text = ("GOST Common", 12, "bold")

        # Image Loading
        self.cwd = os.getcwd()
        image_file_name_startup = self.cwd + "\\images\\startup.png"
        self.startUpSplash = PhotoImage(file=image_file_name_startup)

        # Global Game Settings
        self.boolean_game_active = False
        self.boolean_startup = True
        self.boolean_first_click = True

        # Highscores
        self.text_save_file_names = ['easy', 'medium', 'hard']
        self.int_number_saved_highscores = 10
        self.array_easy_scores = []
        self.array_medium_scores = []
        self.array_hard_scores = []
        self.array_high_scores = [self.array_easy_scores, 
                                  self.array_medium_scores, 
                                  self.array_hard_scores
                                 ]

        # Fixed Game Settings
        self.text_startup_button_names = ['Easy', 'Intermediate', 
                                          'Hard', 'Quit']
        self.int_number_game_rows    = [9, 16, 16]
        self.int_number_game_columns = [9, 16, 30]
        self.int_number_game_mines   = [10, 40, 99]
        self.int_current_game_rows = self.int_current_game_columns = 0 
        self.int_current_game_mines = 0
        self.int_current_game_time = self.int_current_flag_count = 0

        self.int_current_difficulty = None
        self.start_timer()

        self.array_startup_buttons = []
        self.array_current_game_board = []

        self.draw_startup()
        self.load_highscores()

    def mainloop(self):
        self.window.mainloop()

    def start_timer(self):
        threading.Timer(1.0, self.start_timer).start()
        if self.boolean_game_active == True:
            self.int_current_game_time += 1
            self.canvas.itemconfig(self.display_time_marker, 
                                   text=str(self.int_current_game_time)
                                   )

    def reset_timer(self):
        self.int_current_game_time = 0

    def load_highscores(self):
        for i in range(len(self.text_save_file_names)):
            highscores_file_name = (self.cwd + "/highscores/" 
                                    + self.text_save_file_names[i] + '.txt'
                                   )
            highscores_opened_file = open(highscores_file_name)

            for line in highscores_opened_file:
                comma_position = line.find(',')
                self.array_high_scores[i].append(line[0:comma_position])
            highscores_opened_file.close()

    def save_highscores(self):
        highscores_file_name = (self.cwd + "/highscores/" 
                    + self.text_save_file_names[self.int_current_difficulty] 
                    + '.txt')
        highscores_opened_file = open(highscores_file_name, 'w')

        ##### Add code for chanign username!
        for element in self.array_high_scores[self.int_current_difficulty]:
            output_text = str(element) + ', M@ckanT \n'
            highscores_opened_file.write(output_text)
        highscores_opened_file.close()

    def check_highscores(self):

        print('checking highscores')
        current_game_time = self.int_current_game_time
        temp_list = self.array_high_scores[self.int_current_difficulty]
        save_score = False
        
        for i in range(self.int_number_saved_highscores):

            if i >= len(temp_list):
                break
            elif current_game_time < int(temp_list[i]):
                save_score = True
                print('New Highscore! %d seconds time' %(current_game_time)) 
                if i == 0:
                    temp_list = [current_game_time] + temp_list
                else:
                    temp_list = (temp_list[0:i] + [str(current_game_time)] 
                                 + temp_list[i:])
                    if len(temp_list) > self.int_number_saved_highscores: 
                        temp_list = temp_list[0:(self.int_number_saved_highscores-1)]     
                
                if save_score == True:
                    self.array_high_scores[self.int_current_difficulty] = temp_list
                    self.save_highscores()
                    break

    def leave_startup(self, button_clicked):
        self.int_current_game_rows = self.int_number_game_rows[button_clicked]
        self.int_current_game_columns = self.int_number_game_columns[button_clicked]
        self.int_current_game_mines = self.int_number_game_mines[button_clicked]
        self.int_current_difficulty = button_clicked
        self.boolean_startup = False
        self.new_game()
    
    def left_click(self, event): 
        # Use buttons on startup screen
        if self.boolean_startup == True:
            button_clicked = self.startup_button_clicked(event.x, event.y)
            self.window.destroy() if button_clicked == 3 else self.leave_startup(button_clicked)
        else:
            if self.new_game_button.point_in_box(event.x, event.y) == True:
                self.new_game()
            else: 
                if self.boolean_first_click == True:
                    # Restart game until OK start - unoptimal, but works
                    while self.tile_action('num', event) != 0 or self.tile_action('bomb', event) == True:
                        self.new_game()
                    self.boolean_first_click = False
                    self.boolean_game_active = True
                    self.tile_action('open', event)
                elif self.boolean_game_active == True:
                    self.tile_action('open', event)

    def startup_button_clicked(self, x, y):
        position_iterator = 0
        for item in self.array_startup_buttons: 
            if self.array_startup_buttons[position_iterator].point_in_box(x, y) == True:
                return position_iterator
            else:
                position_iterator = position_iterator + 1

    def right_click(self, event):
        if self.boolean_game_active == True or self.boolean_first_click == True:
           self.tile_action('flag', event)
           self.count_flags()
    
    def middle_click(self, event):
        if self.boolean_game_active == True or self.boolean_first_click == True:
            work_tile = self.tile_action('tile', event)

            if work_tile.get_hidden() == True:
               work_tile.set_flag()
               self.count_flags()
            elif work_tile.is_hidden == False and work_tile.get_flag() == False:
                if self.count_nearby_flags(work_tile) == work_tile.get_tile_number():
                    self.open_square(work_tile)
    
    def is_tile(self, x, y):
        if x >= 0 and x < self.int_current_game_columns and y >= 0 and y < self.int_current_game_rows:
            return True
        else:
            return False

    def tile_action(self, function, event):
        clicked_col = (event.x - game_offset) / game_tile_width
        clicked_row = (event.y - game_offset) / game_tile_width
        clicked_col = int(clicked_col) if clicked_col > 0 else -1
        clicked_row = int(clicked_row) if clicked_row > 0 else -1

        if self.is_tile(clicked_col, clicked_row) == True:
            tile = self.array_current_game_board[clicked_row][clicked_col]

            if function == 'num':
                return tile.get_tile_number()
            elif function == 'bomb':
                return tile.get_bomb()
            elif function == 'flag':
                tile.set_flag()
            elif function == 'open':
                self.open_tile_function(tile)
            elif function == 'tile':
                return tile

    def check_loss(self, tile):
        if tile.get_bomb() == True and tile.get_flag() == False:
            for i in range(self.int_current_game_columns):
                for j in range(self.int_current_game_rows):
                    if self.array_current_game_board[j][i].is_bomb == True:
                        self.array_current_game_board[j][i].open_tile()
            self.boolean_game_active = False

    def check_victory(self):
        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                if self.array_current_game_board[j][i].get_hidden() == True and self.array_current_game_board[j][i].get_bomb() == False:
                    return
        self.open_remaining_tiles()
        self.boolean_game_active = False
        self.check_highscores()

    def open_tile_function(self, tile):
        tile.open_tile()
        self.open_zeros(tile)
        self.check_loss(tile)
        self.check_victory()

    def open_remaining_tiles(self):
        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                if self.array_current_game_board[j][i].get_bomb() == False:
                    self.array_current_game_board[j][i].open_tile()
                else:
                    self.array_current_game_board[j][i].force_flag()

    def new_game(self):
        self.boolean_first_click = True
        self.boolean_game_active = False
        self.numberOfClicks = 0
        self.reset_timer()
        self.canvas.delete("all")
        self.draw_board()

    def open_zeros(self, tile):
        if tile.get_tile_number() == 0:
            self.open_square(tile)

    def count_nearby_flags(self, tile):

        number_of_flags = 0
        for k in range(tile.get_row()-1, tile.get_row()+2):
            for l in range(tile.get_col()-1, tile.get_col()+2): 
                try:
                    if self.array_current_game_board[k][l].get_flag() == True and k >= 0 and l >= 0:
                        number_of_flags += 1
                except: 
                    pass
        return number_of_flags

    def count_flags(self):
        used_flags = 0
        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                if self.array_current_game_board[j][i].get_flag() == True:
                    used_flags += 1
        self.canvas.itemconfig(self.display_flag_marker, text=str(used_flags))

    def open_square(self, tile):
        if tile.get_bomb() == False:
            for k in range(tile.get_row()-1, tile.get_row()+2):
                for l in range(tile.get_col()-1, tile.get_col()+2): 
                    try:
                        if self.array_current_game_board[k][l].is_hidden == True and k >= 0 and l >= 0 and self.array_current_game_board[k][l].get_flag() == False:
                            self.open_tile_function(self.array_current_game_board[k][l])
                    except: 
                        1

    def draw_startup(self):
        for i in range(len(self.text_startup_button_names)):
            self.array_startup_buttons.append(Button(game_screen_width/3 - game_offset, (2+2*i)*game_tile_width, game_screen_width/6, 1.5*game_tile_width, self.text_startup_button_names[i], custom_colors[1], self.canvas))
        self.canvas.create_image(game_offset,2*game_tile_width, anchor=NW, image = self.startUpSplash)

    def draw_board(self):

        self.array_current_game_board = [[Tile(i, j, game_tile_width, None, None, game_offset, self.canvas) for j in range(self.int_current_game_columns)] for i in range(self.int_current_game_rows)]
        
        win_width = self.int_current_game_columns * game_tile_width + 2*game_offset
        win_height = self.int_current_game_rows * game_tile_width + 2*game_offset

        self.canvas.config(width=win_width,height=win_height)
        self.new_game_button = Button(win_width/2-game_offset, 10, 2*game_offset , 30, 'New Game', custom_colors[1], self.canvas)
        self.display_flag_marker = self.canvas.create_text(game_tile_width*(self.int_current_game_columns-1/2) + game_offset, game_offset/2, fill='white', font='arial 20', text='0')
        self.display_time_marker = self.canvas.create_text(game_tile_width/2 + game_offset, game_offset/2, fill='white', font='arial 20', text='0')

        # Set bombs
        tile_indexes = range(self.int_current_game_rows*self.int_current_game_columns)
        bomb_indexes = random.sample(tile_indexes, self.int_current_game_mines)
        for index in bomb_indexes:
            self.array_current_game_board[int(index/self.int_current_game_columns)][index%self.int_current_game_columns].set_bomb()

        self.calculate_tile_numbers()

    def calculate_tile_numbers(self):
        # Calculate adjacent bombs
        for i in range(self.int_current_game_rows):
            for j in range(self.int_current_game_columns):
                tile = self.array_current_game_board[i][j]
                tile_bomb_number = 0
                if tile.get_bomb() == False:
                    for k in range(tile.get_row()-1, tile.get_row()+2):
                        for l in range(tile.get_col()-1, tile.get_col()+2): 
                            try:
                                if self.array_current_game_board[k][l].get_bomb() == True and k >= 0 and l >= 0:
                                    tile_bomb_number += 1
                            except: 
                                tile_bomb_number += 0
                else:
                    tile_bomb_number = 0
                tile.set_tile_number(tile_bomb_number, number_colors[tile_bomb_number])

game_instance = Minesweeper()
game_instance.mainloop()