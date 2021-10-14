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
    DONE = 3

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
        self.game_canvas = Canvas(self.window, 
                             width = 0, 
                             height = 0, 
                             bg=startup_color,
                            )
        self.window.resizable(False, False)
        self.canvas.pack()
        

        # Input listeners
        #self.window.bind('<Motion>', self.moved_mouse)
        self.window.bind('<Button-1>', self.window_click)
        self.game_canvas.bind('<Button-1>', self.left_click)
        self.game_canvas.bind('<Button-2>', self.middle_click)
        self.window.bind('<space>', self.space_click)
        self.game_canvas.bind('<Button-3>', self.right_click)

        # Graphical Loading
        self.font_text = ("GOST Common", 12, "bold")
        self.start_up_splash = self.get_image('startup')

        # Global Game Settings
        self.game_state = Game_state.MENU

        # Highscores
        self.text_save_file_names = ['easy', 'medium', 'hard']
        self.int_number_saved_highscores = 10
        self.array_high_scores = [ [], [], [] ]

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

### Timer Functions

    def start_timer(self):
        threading.Timer(1.0, self.start_timer).start()
        if self.game_state == Game_state.GAME:
            self.int_current_game_time += 1
            self.canvas.itemconfig(self.display_time_marker, 
                                   text=str(self.int_current_game_time)
                                   )

    def reset_timer(self):
        self.int_current_game_time = 0
 

### Highscore Functions

    def load_highscores(self):
        for i in range(len(self.text_save_file_names)):
            highscores_file_name = (cwd + "/highscores/" 
                                    + self.text_save_file_names[i] + '.txt'
                                   )
            highscores_opened_file = open(highscores_file_name)

            for line in highscores_opened_file:
                comma_position = line.find(',')
                self.array_high_scores[i].append(line[0:comma_position])
            highscores_opened_file.close()

    def save_highscores(self):
        highscores_file_name = (cwd + "/highscores/" 
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
                
                if save_score:
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

        self.game_canvas.configure(state='normal',
                        width=game_tile_width*self.int_current_game_columns,
                        height=game_tile_width*self.int_current_game_rows)
        self.game_canvas.place(x=game_border, y=game_border, anchor=NW)
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

    def window_click(self, event):

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
        elif self.new_game_button.point_in_box(event.x, event.y):
            self.new_game()

    def left_click(self, event): 

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
    
    def space_click(self, event):
        self.middle_click(event, space=True)

    def middle_click(self, event, space=False):
        if self.game_state == (Game_state.GAME or Game_state.START):
            work_tile = self.tile_action('tile', event, space)
            if work_tile == None: return

            if work_tile.get_hidden():
               work_tile.set_flag()
               self.count_flags()
            elif not work_tile.is_hidden and not work_tile.get_flag():
                if self.count_nearby_flags(work_tile) == work_tile.get_tile_number():
                    self.open_square(work_tile)

    def tile_action(self, function, event, space=False):

        clicked_col = event.x  / game_tile_width
        clicked_row = event.y  / game_tile_width

        if space:
            clicked_col = (event.x-game_border) / game_tile_width
            clicked_row = (event.y-game_border) / game_tile_width
            if not 0 < clicked_col < self.int_current_game_columns: return
            if not 0 < clicked_row < self.int_current_game_rows: return

        clicked_row = int(clicked_row)
        clicked_col = int(clicked_col)

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
        if tile.get_bomb() and not tile.get_flag():
            self.game_state = Game_state.DONE
            for i in range(self.int_current_game_columns):
                for j in range(self.int_current_game_rows):
                    if self.__is_bomb(j,i):
                        self.__open_tile(j,i)

    def check_victory(self):
        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                is_hidden = self.__is_hidden(j,i)
                is_bomb = self.__is_bomb(j,i)
                if is_hidden and not is_bomb : return

        self.game_state = Game_state.DONE
        self.open_remaining_tiles()
        self.check_highscores()

    def __open_tile(self, i, j):
        self.array_current_game_board[i][j].open_tile()
    
    def __is_hidden(self, i, j):
        return self.array_current_game_board[i][j].get_hidden()

    def __is_bomb(self, i, j):
        return self.array_current_game_board[i][j].get_bomb()
    
    def __is_flag(self, i, j):
        return self.array_current_game_board[i][j].get_flag()

    def __force_flag(self, i, j):
        self.array_current_game_board[i][j].force_flag()

    def open_tile_function(self, tile):
        tile.open_tile()
        self.open_zeros(tile)
        self.check_loss(tile)
        self.check_victory()

    def open_remaining_tiles(self):
        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                if not self.__is_bomb(j,i):
                    self.__open_tile(j,i)
                else:
                    self.__force_flag(j,i)

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
                    if self.__is_flag(k,l) and k >= 0 and l >= 0:
                        number_of_flags += 1
                except: 
                    pass
        return number_of_flags

    def count_flags(self):
        used_flags = 0
        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                if self.__is_flag(j,i):
                    used_flags += 1
        self.canvas.itemconfig(self.display_flag_marker, text=str(used_flags))

    def open_square(self, tile):
        if not tile.get_bomb():
            for k in range(tile.get_row()-1, tile.get_row()+2):
                for l in range(tile.get_col()-1, tile.get_col()+2): 
                    try:
                        if self.__is_hidden(k,l) and k >= 0 and l >= 0 and not self.__is_flag(k,l):
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

        self.array_current_game_board = [[Tile(i, j, game_tile_width, self.game_canvas) for j in range(self.int_current_game_columns)] for i in range(self.int_current_game_rows)]
        
        win_width = self.int_current_game_columns * game_tile_width + 2*game_border
        win_height = self.int_current_game_rows * game_tile_width + 2*game_border

        self.canvas.config(width=win_width,height=win_height)
        self.new_game_button = Button(win_width/2-game_border, 10, 2*game_border , 30, 'New Game', custom_colors[1], self.canvas)
        self.display_flag_marker = self.canvas.create_text(game_tile_width*(self.int_current_game_columns-1/2) + game_border, game_border/2, fill='white', font='arial 20', text='0')
        self.display_time_marker = self.canvas.create_text(game_tile_width/2 + game_border, game_border/2, fill='white', font='arial 20', text='0')

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
                if not tile.get_bomb():
                    for k in range(tile.get_row()-1, tile.get_row()+2):
                        for l in range(tile.get_col()-1, tile.get_col()+2): 
                            try:
                                if self.__is_bomb(k,l) and k >= 0 and l >= 0:
                                    tile_bomb_number += 1
                            except: 
                                tile_bomb_number += 0
                else:
                    tile_bomb_number = 0
                tile.set_tile_number(tile_bomb_number, number_colors[tile_bomb_number])

game_instance = Minesweeper()
game_instance.mainloop()