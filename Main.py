from tkinter import *
from array import *
from enum import Enum
import simpleaudio as sa
import os
import threading
import numpy as np
import random
from Button import Button
from Tile import Tile

### Game Parameters

# Number Colors
number_colors = ['#FFFFFF', '#0000FF', '#007B00', '#FF0000', '#00007B', 
                '#7B0000', '#007B7B', '#7B7B7B', '#000000']
# Background Gray, Button Yellow, Hidden Tile Gray, Visible Tile Gray, Accent Orange
custom_colors = ['#565554', '#f6f193', '#7c7a77', '#cfd0d2', '#fbd083'] 

# Start-up Screen
startup_width = 800
startup_height = 600
startup_color = custom_colors[0]
startup_name = 'The Electric Boogaloo - Minesweeper 2'
startup_button_names = ['New Game', 'Stats', 'Settings', 'Credits', 'Quit']
startup_difficulty_names = ['Easy', 'Medium', 'Hard', 'Back']

game_border = 50
game_tile_width = 40

cwd = os.getcwd()

class Game_state(Enum):
    MENU = 0
    START = 1
    GAME = 2
    LOSS = 3

class Minesweeper():
    
    def __init__(self):

        # Screen Settings
        self.window = Tk()
        self.window.title(startup_name)
        self.canvas = Canvas(self.window, 
                             width = startup_width, 
                             height = startup_height, 
                             bg=startup_color
                            )
        self.window.resizable(False, False)
        self.canvas.pack()

        self.window.bind('<Button-1>', self.left_click)
        self.window.bind('<Button-2>', self.middle_click)
        self.window.bind('<Button-3>', self.right_click)
        self.window.bind('<space>', self.middle_click)

        # Graphical Loading
        self.font_text = ("GOST Common", 12, "bold")
        self.start_up_splash = self.get_image('startup')

        # Global Game Settings
        self.game_state = Game_state.MENU

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
        if self.game_state == Game_state.GAME:
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


### Load Functions

    def get_image(self, filename, folder='images'):
        
        file_name = cwd + '\\' + folder + '\\' + filename + '.png'
        return PhotoImage(file=file_name)

    def load_sound(self, file_name):
        """ loads specified sound file as wave object """
        return sa.WaveObject.from_wave_file(self.cwd 
                        + '\\sound\\' + file_name + '.wav')

    def play_sound(self, file_name):
        """ Plays specified sound file """ 
        if file_name == 'home_button':
            self.sound_home_button.play()
        elif file_name == 'place_tower':
            self.sound_place_tile.play()

### Draw Game Functions
    def leave_startup(self, button_clicked):
        self.int_current_game_rows = self.int_number_game_rows[button_clicked]
        self.int_current_game_columns = self.int_number_game_columns[button_clicked]
        self.int_current_game_mines = self.int_number_game_mines[button_clicked]
        self.int_current_difficulty = button_clicked
        self.game_state = Game_state.START
        self.new_game()

    def menu_difficulty_select(self):
        self.draw_startup_buttons(case=1)
    
    def menu_statistics(self):
        print('menu stats')

    def menu_settings(self):
        print('menu settings')

    def menu_credits(self):
        print('menu credits')
    
    def moved_mouse(self, event):
        """ Fired by mouse movement, calls appropriate function depending on game state """
        if (self.state_game == 0): self.home_button_sound(event)

    def left_click(self, event): 

        # Use buttons on startup screen
        if self.game_state == Game_state.MENU:

            button_clicked = self.startup_button_clicked(event.x, event.y)
            if button_clicked == None: return

            if button_clicked == startup_button_names[0]:
                self.menu_difficulty_select()
            elif button_clicked == startup_button_names[1]:
                self.menu_statistics()
            elif button_clicked == startup_button_names[2]:
                self.menu_settings()
            elif button_clicked == startup_button_names[3]: 
                self.menu_credits()
            elif button_clicked == startup_button_names[4]:
                self.window.destroy()
            elif button_clicked == startup_difficulty_names[0]:
                self.leave_startup(0)
            elif button_clicked == startup_difficulty_names[1]:
                self.leave_startup(1)
            elif button_clicked == startup_difficulty_names[2]:
                self.leave_startup(2)
            elif button_clicked == startup_difficulty_names[3]:
                self.draw_startup_buttons(case=0)

        # New game button from within game
        else:
            if self.new_game_button.point_in_box(event.x, event.y):
                self.new_game()
            else: 
                if self.game_state == Game_state.START:
                    # Restart game until OK start - unoptimal, but works
                    while self.tile_action('num', event) != 0 or self.tile_action('bomb', event):
                        self.new_game()
                    self.game_state = Game_state.GAME
                    self.tile_action('open', event)
                elif self.game_state == Game_state.GAME:
                    self.tile_action('open', event)

    def startup_button_clicked(self, x, y):
        for i, item in enumerate(self.array_startup_buttons): 
            if item.point_in_box(x, y):
                return self.array_startup_buttons[i].get_name()

    def right_click(self, event):
        if self.game_state == (Game_state.GAME or Game_state.START):
           self.tile_action('flag', event)
           self.count_flags()
    
    def middle_click(self, event):
        if self.game_state == (Game_state.GAME or Game_state.START):
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

    def check_victory(self):
        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                if self.array_current_game_board[j][i].get_hidden() == True and self.array_current_game_board[j][i].get_bomb() == False:
                    return
        self.open_remaining_tiles()
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
        self.game_state = Game_state.START
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

        self.draw_startup_buttons(case=0)
        self.canvas.create_image(game_border,startup_height/2, anchor=W, 
                                 image = self.start_up_splash)

    def draw_startup_buttons(self, case=0):
        
        button_list = startup_button_names

        if case == 1:
            button_list = startup_difficulty_names

        button_len = len(button_list)
        button_height = int( (startup_height - 2*game_border) / button_len)

        for i, item in enumerate(self.array_startup_buttons):
            item.delete_button()
        self.array_startup_buttons.clear()

        for i, name in enumerate(button_list):
            self.array_startup_buttons.append(
                    Button(
                        canvas=self.canvas,
                        x_pos=startup_width/2, 
                        y_pos=game_border+i*button_height, 
                        width=startup_width/2-game_border, 
                        height=0.7*button_height, 
                        text=name, 
                        color=custom_colors[1], 
                    )
            )

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