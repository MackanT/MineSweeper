from tkinter import *
from array import *
from enum import Enum
from tkinter import font
from PIL import Image, ImageTk
import pygame
import os
import threading
import numpy as np
import random
from Button import Button, Slide_Button, Pop_Button, Slider, Toggle_Switch
from Tile import Tile, TileState

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
stats_button_names = ['Reset', 'Back']
return_button_name = 'Back'
setting_button_name = ['Save', 'Back']
game_button_names = ['X', 'New Game']

sound_effect_names = ['home_button', 'explosion', 'flag', 'win']

game_border = 50
game_tile_width = 40

cwd = os.getcwd()

class Game_state(Enum):
    MENU = 0
    START = 1
    GAME = 2
    DONE = 3
    SETTINGS = 4

class Minesweeper():
    
    def __init__(self):

        # Screen Settings
        self.window = Tk()
        self.window.title(startup_name)
        self.window.config(bg=startup_color)
        self.canvas = Canvas(self.window, 
                             width = 0, 
                             height = 0, 
                             bg=startup_color,
                             borderwidth=0,
                             highlightthickness=0
                            )
        self.game_canvas = Canvas(self.window, 
                             width = 0, 
                             height = 0, 
                             highlightthickness=1
                            )
        self.test_canvas = []
        self.window.resizable(False, False)
        self.canvas.pack()
        

        # Input listeners
        self.canvas.bind('<Motion>', self.moved_mouse)
        self.canvas.bind('<Button-1>', self.canvas_click)
        self.game_canvas.bind('<Button-1>', self.left_click)
        self.game_canvas.bind('<Button-2>', self.middle_click)
        self.window.bind('<space>', self.space_click)
        self.game_canvas.bind('<Button-3>', self.right_click)
        self.canvas.bind('<B1-Motion>', self.mouse_dragged)

        self.change_username = Entry(self.canvas, width=30)
        self.change_username.bind("<Return>", self.update_username)

        # Graphical Loading
        self.font_text = ("GOST Common", 20, "bold")
        self.font_small = ("GOST Common", 12, "bold")
        self.start_up_splash = self.get_image('startup')

        # Sound
        pygame.init()
        self.sound_effects = []
        for sound_name in sound_effect_names:
            self.sound_effects.append(self.load_sound(sound_name))
        self.load_sound('MineSweeper', song=True)
        

        # Highscores
        self.text_save_file_names = ['easy', 'medium', 'hard']
        self.int_number_saved_highscores = 10
        self.check_highscore_file()
        self.load_highscores()

        # Load Game Settings
        self.load_settings()

        self.array_startup_buttons = []
        self.array_game_buttons = [None] * len(game_button_names)
        self.array_current_game_board = []

        self.int_current_difficulty = None
        
        self.set_volume()
        if self.game_settings[0]: pygame.mixer.music.play(-1)

        self.draw_startup()
        self.start_timer()

    def mainloop(self):
        self.window.mainloop()


### Settings

    def load_settings(self):
        # Fixed Game Settings
        self.int_number_game_rows    = [9, 16, 16]
        self.int_number_game_columns = [9, 16, 30]
        self.int_number_game_mines   = [10, 40, 99]
        self.int_current_game_rows = self.int_current_game_columns = 0 
        self.int_current_game_mines = self.int_current_flags = 0
        self.int_current_game_time = 0

        self.game_settings = [0, 0, 0, 0]

        path = cwd + '/settings.txt'
        with open(path, 'r') as f:
            lines = (line.rstrip() for line in f) 
            for i, line in enumerate(lines):
                comma_position = line.find(' ') + 1
                self.game_settings[i] = line[comma_position:]
        
    def save_settings(self):

        self.game_settings[0] = self.audio_toggle.state
        self.game_settings[1] = self.audio_slider.value
        self.game_settings[2] = self.bgm_slider.value

        if self.game_settings[0]: pygame.mixer.music.play(-1)
        else: pygame.mixer.music.stop()
        self.set_volume()

        path = cwd + '/settings.txt'
        data = []
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:  
                data.append(line)

        with open(path, 'w') as f:
            for i, line in enumerate(data):
                comma_position = line.find(' ')
                if i == 3:
                    f.write('{:s} {}\n'.format(data[i][0:comma_position], self.game_settings[i]))
                else:
                    f.write('{:s} {}\n'.format(data[i][0:comma_position], int(self.game_settings[i])))
            

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

    def check_highscore_file(self):
        file = cwd + "/highscores/"
        if not os.path.exists(file): os.mkdir(file)

        for name in self.text_save_file_names:
            with open(file + name + '.txt', 'a+') as f: f.read()

    def load_highscores(self):

        self.array_high_scores = [ [], [], [] ]
        self.array_high_scores_names = [ [], [], [] ]

        for i, name in enumerate(self.text_save_file_names):
            path = cwd + '/highscores/' + name + '.txt'

            with open(path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    comma_position = line.find(',')
                    self.array_high_scores[i].append(line[0:comma_position])
                    self.array_high_scores_names[i].append(line[comma_position+2:])

    def save_highscores(self):
        highscores_file_name = (cwd + "/highscores/" 
                    + self.text_save_file_names[self.int_current_difficulty] 
                    + '.txt')
        highscores_opened_file = open(highscores_file_name, 'w')

        ##### Add code for chanign username!
        for element in self.array_high_scores[self.int_current_difficulty]:
            output_text = str(element) + ', {} \n'.format(self.game_settings[3])
            highscores_opened_file.write(output_text)
        highscores_opened_file.close()

    def check_highscores(self):

        time = self.int_current_game_time
        temp_list = self.array_high_scores[self.int_current_difficulty]
        save_game = False

        for i, list_time in enumerate(temp_list):
            if time < int(list_time):
                temp_list.insert(i, time)
                save_game = True
                break

        if len(temp_list) < self.int_number_saved_highscores and not save_game:
            temp_list.append(time)
            save_game = True
        else:
            temp_list = temp_list[0:self.int_number_saved_highscores]

        if save_game: 
            self.array_high_scores[self.int_current_difficulty] = temp_list
            # have to send index i to save highsscore for correct naming to times
            self.save_highscores()
            return True

        return False
    
    def reset_highscores(self):
        file = cwd + "/highscores/"
        for name in self.text_save_file_names:
            with open(file + name + '.txt', 'w+') as f: f.read()
        self.menu_statistics()


### Images

    def get_image(self, filename, folder='images'):
        
        file_name = cwd + '\\' + folder + '\\' + filename + '.png'
        return PhotoImage(file=file_name)


### Sound 

    def load_sound(self, file_name, song=False):
        """ loads specified sound file as wave object """
        if song: pygame.mixer.music.load(cwd + '\\sound\\' + file_name + '.wav')
        return pygame.mixer.Sound(cwd + '\\sound\\' + file_name + '.wav')
        

    def play_sound(self, file_name):
        """ Plays specified sound file """ 
        for i, name in enumerate(sound_effect_names):
            if name == file_name:
                self.sound_effects[i].play()
                return

    def set_volume(self):
        pygame.mixer.music.set_volume(int(self.game_settings[1])/100)
        for sound in self.sound_effects:
            sound.set_volume(int(self.game_settings[2])/100)

### User Input

    def left_click(self, event): 
        if self.game_state == Game_state.START:
            x, y = self.get_tile(event)
            no_bomb_on_int = x*self.int_current_game_columns + y
            self.add_bombs(no_bomb_on_int)
            self.game_state = Game_state.GAME
        
        if self.game_state == Game_state.DONE: return
        self.tile_action('open', event)

    def right_click(self, event):
        if self.game_state == (Game_state.GAME or Game_state.START):
           self.tile_action('flag', event)
    
    def space_click(self, event):
        self.middle_click(event, space=True)

    def middle_click(self, event, space=False):
        if self.game_state == (Game_state.GAME or Game_state.START):
            work_tile = self.tile_action('tile', event, space)
            if work_tile == None: return

            if work_tile.get_state() == TileState.VISIBLE:
                if self.count_nearby_flags(work_tile) == work_tile.get_tile_number():
                    self.open_square(work_tile)
            else:
                self.tile_action('flag', event, space)
    
    def moved_mouse(self, event):
        """ Fired by mouse movement, calls appropriate function depending on game state """
        if (self.game_state == Game_state.MENU or self.game_state == Game_state.SETTINGS): 
            
            x, y = event.x, event.y

            for button in self.array_startup_buttons:
                if button.point_in_box(x, y): 
                    # First highlighted
                    if not button.get_button_highlighted():
                        self.play_sound('home_button')
                        button.set_button_highlighted(True)
                        button.is_selected(True)
                    # Mouse remains on button
                    else: 
                        button.set_button_highlighted(True)
                else: 
                    # Mouse leaves button
                    if button.get_button_highlighted():
                        button.is_selected(False)
                    # Mouse is outside of button
                    button.set_button_highlighted(False)

    def mouse_dragged(self, event):

        if self.game_state == Game_state.SETTINGS:

            if self.audio_slider.point_in_box(event.x, event.y):
                self.audio_slider.move_slider(event.x)
            elif self.bgm_slider.point_in_box(event.x, event.y):
                self.bgm_slider.move_slider(event.x)

    def canvas_click(self, event):
        # Use buttons on startup screen

        if self.game_state == Game_state.SETTINGS:
            if self.audio_toggle.point_in_box(event.x, event.y):
                self.audio_toggle.toggle_switch()
            button_clicked = self.find_clicked_button(event.x, event.y, self.array_startup_buttons)
            if button_clicked == None: return
            
            if button_clicked == startup_difficulty_names[3]:
                self.draw_startup()
            elif button_clicked == setting_button_name[0]:
                self.save_settings()
        
        elif self.game_state == Game_state.MENU:
            button_clicked = self.find_clicked_button(event.x, event.y, self.array_startup_buttons)
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
                self.draw_startup()
            elif button_clicked == stats_button_names[0]:
                self.reset_highscores()
            elif button_clicked == setting_button_name[0]:
                self.save_settings()

        # New game button from within game 
        else:
            
            button_clicked = self.find_clicked_button(event.x, event.y, self.array_game_buttons)
            if button_clicked == None: return
            
            if button_clicked == game_button_names[0]:
                self.draw_startup()
            elif button_clicked == game_button_names[1]:
                self.new_game()
            

### Draw Game

    def draw_startup(self):
        
        self.game_state = Game_state.MENU
        self.canvas.delete('all')
        self.change_username.place_forget()
        self.game_canvas.place_forget()

        self.canvas.config(width=startup_width,height=startup_height)
        self.window.geometry('%dx%d'%(startup_width, startup_height))

        self.draw_startup_buttons(x=startup_width/2, y=0, x_move=-50, button=Slide_Button)
        self.canvas.create_image(game_border,startup_height/2, anchor=W, 
                                image = self.start_up_splash)
    
    def draw_board(self):

        self.array_current_game_board = [[Tile(i, j, game_tile_width, self.font_text, self.game_canvas) for j in range(self.int_current_game_columns)] for i in range(self.int_current_game_rows)]
        
        win_width = self.int_current_game_columns * game_tile_width + 2*game_border
        win_height = self.int_current_game_rows * game_tile_width + 2*game_border

        self.canvas.config(width=win_width,height=game_border)
        self.window.geometry('%dx%d'%(win_width, win_height))

        self.array_game_buttons[0] = Button(x_pos = game_border/2, 
                                      y_pos = 10, 
                                      width = game_border, 
                                      height = 30, 
                                      text = game_button_names[0], 
                                      font = self.font_small,
                                      color = custom_colors[1], 
                                      canvas = self.canvas
                                      )

        self.array_game_buttons[1] = Button(x_pos = win_width/2-game_border, 
                                      y_pos = 10, 
                                      width = 2*game_border, 
                                      height = 30, 
                                      text = game_button_names[1], 
                                      font = self.font_small,
                                      color = custom_colors[1], 
                                      canvas = self.canvas
                                      )
        
        flag_x = game_tile_width*(self.int_current_game_columns-1/2) + game_border
        flag_y = game_border/2
        time_x = game_tile_width/2 + 2*game_border
        time_y = game_border/2

        self.display_flag_marker = self.canvas.create_text(flag_x, flag_y, 
                                        fill='white', font=self.font_text, 
                                        text=str(self.int_current_game_mines))
        self.display_time_marker = self.canvas.create_text(time_x, time_y, 
                                        fill='white', font=self.font_text, 
                                        text='0')

    def draw_startup_buttons(self, x, y, border=10, list=startup_button_names, vertical=True, button=Button, x_move=0, y_move=0):

        button_len = len(list)

        for item in self.array_startup_buttons: item.delete_button()
        self.array_startup_buttons.clear()

        dx = 0 if vertical else 1
        dy = 1 if vertical else 0
    
        width = dy*(startup_width - x - 2*border) + dx*int(((startup_width-x)-(button_len+1)*border)/button_len)
        height = dx*(startup_height - y - 2*border) + dy*int(((startup_height-y)-(button_len+1)*border)/button_len)

        for i, name in enumerate(list):

            x_pos = x + i*dx*(width) + dx*(i+1)*border
            y_pos = y + i*dy*(height) + dy*(i+1)*border
            self.array_startup_buttons.append(
                    button(
                        canvas=self.canvas,
                        x_pos=x_pos,
                        y_pos=y_pos,
                        width=width,
                        height=height,
                        text=name, 
                        color=custom_colors[1],
                        font=self.font_text,
                        x_anim=x_move,
                        y_anim=y_move
                    )
            )

    def draw_win_screen(self):

        dx = int(self.game_canvas.winfo_width()/2)
        dy = int(self.game_canvas.winfo_height()/2)

        self.draw_rectangle(dx - 3*game_border, dy - game_border, dx + 3*game_border, dy + game_border, fill='#fbd083', alpha=.6)
        self.game_canvas.create_text(dx, dy-5, anchor=S, text='Congratulations!', font=self.font_text)
        if self.check_highscores():
            win_text = '-- New high score --  \n {0} seconds!'.format(self.int_current_game_time)
        else:
            win_text = 'You completed the \n game in {0} seconds!'.format(self.int_current_game_time)

        self.game_canvas.create_text(dx, dy+5, anchor=N, text=win_text, font=self.font_small, justify=CENTER)    
        
    def draw_lose_screen(self):

        dx = int(self.game_canvas.winfo_width()/2)
        dy = int(self.game_canvas.winfo_height()/2)

        self.draw_rectangle(dx - 3*game_border, dy - game_border, dx + 3*game_border, dy + game_border, fill='#ed2939', alpha=.8)
        self.game_canvas.create_text(dx, dy-5, anchor=S, text='Failure!', font=self.font_text)
        self.game_canvas.create_text(dx, dy+5, anchor=N, text='You failed in securing the mines!', font=self.font_small, justify=CENTER)

    def draw_rectangle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = (int(fill[1:3],16),int(fill[3:5],16),int(fill[5:7],16),alpha)
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            self.test_canvas.append(ImageTk.PhotoImage(image))
            self.game_canvas.create_image(x1, y1, image=self.test_canvas[-1], anchor='nw')
        self.game_canvas.create_rectangle(x1, y1, x2, y2, **kwargs)
        

### Button Reseults

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
        self.draw_startup_buttons(list=startup_difficulty_names, x=startup_width/2, y=0, x_move=-50, button=Slide_Button)
    
    def menu_statistics(self):
        self.load_highscores()
        self.canvas.delete("all")
        for i in range(3):
            
            this_x = 150 + 250*i
            this_y = 30
            
            self.canvas.create_text(this_x, this_y,  anchor=N, text='~ {0} ~'.format(startup_difficulty_names[i]), fill='#ffffff', font=self.font_text)
            self.canvas.create_rectangle(this_x - 110, this_y + game_border, this_x + 110, this_y + 370, fill=custom_colors[1])
            if not self.array_high_scores[i]:
                pass
            else:
                for j, time in enumerate(self.array_high_scores[i]):
                    self.canvas.create_text(this_x - 80, this_y + 30*(j+2),  anchor=N, text=time, font=self.font_text)
                    self.canvas.create_text(this_x + 20, this_y + 30*(j+2),  anchor=N, text=' - {0}'.format(self.array_high_scores_names[i][j]), font=self.font_text)

        self.draw_startup_buttons(list=stats_button_names, x=0, y=startup_height-100, vertical=False, x_move=5, y_move=5, button=Pop_Button)

    def menu_settings(self):
        self.game_state = Game_state.SETTINGS
        self.canvas.delete("all")

        white = '#ffffff'

        self.canvas.create_text(game_border, game_border, anchor=NW, font=self.font_text, fill=white, text="Settings")
        self.canvas.create_line(game_border, 90, game_border + 450, 90, fill=white)

        self.canvas.create_text(game_border, 100, anchor=NW, font=self.font_text, fill=white, text="Audio")
        self.audio_toggle = Toggle_Switch(350, 100, height=35, canvas=self.canvas, state=int(self.game_settings[0]), font=self.font_small)
        
        self.canvas.create_text(game_border, 150, anchor=NW, font=self.font_small, fill=white, text="Audio Level")
        self.audio_slider = Slider(100, 170, height=30, canvas=self.canvas, font=self.font_text, value=int(self.game_settings[1]), fill=white) 
        
        self.canvas.create_text(game_border, 200, anchor=NW, font=self.font_small, fill=white, text="Music Level")
        self.bgm_slider = Slider(100, 220, height=30, canvas=self.canvas, font=self.font_text, value=int(self.game_settings[2]), fill=white) 

        self.canvas.create_text(game_border, 300, anchor=NW, font=self.font_text, fill=white, text="Username:")
        self.change_username.place(x=220, y=310)
        self.change_username.delete(0, END)
        self.change_username.insert(0, self.game_settings[3])

        self.draw_startup_buttons(x=0,y=startup_height-100, vertical=False, list=setting_button_name, x_move=5, y_move=5, button=Pop_Button)

    def update_username(self, event):
        self.game_settings[3] = self.change_username.get()

    def menu_credits(self):
        self.canvas.delete("all")
        self.canvas.create_text(10, game_border,  anchor=NW, text='Thanks for playing! \n I should really fill this area out with better text at some time', fill='#ffffff', font=self.font_text)
        self.draw_startup_buttons(x=0,y=startup_height-100, vertical=False, list=[return_button_name], x_move=5, y_move=5, button=Pop_Button)
        

    def new_game(self):
        self.int_current_flags = 0
        self.game_state = Game_state.START
        self.reset_timer()
        self.canvas.delete("all")
        self.draw_board()
    

### Logic

    def check_loss(self, tile):
        if tile.get_bomb() and tile.get_state() == TileState.VISIBLE:
            self.game_state = Game_state.DONE
            self.play_sound('explosion')
            self.draw_lose_screen()
            for i in range(self.int_current_game_columns):
                for j in range(self.int_current_game_rows):
                    if self.__is_bomb(j,i):
                        self.__open_tile(j,i)
            return True
        return False

    def check_victory(self):

        if self.int_current_flags > self.int_current_game_mines: return

        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                tile = self.array_current_game_board[j][i]
                not_bomb = not tile.get_bomb()
                if tile.get_state() == TileState.HIDDEN and not_bomb : return

        self.game_state = Game_state.DONE
        self.play_sound('win')
        self.open_remaining_tiles()
        self.draw_win_screen()
    
    def add_bombs(self, no_bomb):

        # Set bombs
        max_tiles = self.int_current_game_rows*self.int_current_game_columns
        tile_indexes = [i for i in range(max_tiles) if i != no_bomb]
        bomb_indexes = random.sample(tile_indexes, self.int_current_game_mines)
        for index in bomb_indexes:
            row = int(index/self.int_current_game_columns)
            col = index%self.int_current_game_columns
            self.array_current_game_board[row][col].set_bomb()

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

    def count_nearby_flags(self, tile):
        number_of_flags = 0
        for k in [tile.get_row()-1 + i for i in range(3)]:
            for l in [tile.get_col()-1 + i for i in range(3)]:
                
                ok_k = (0 <= k < self.int_current_game_rows)
                ok_l = (0 <= l < self.int_current_game_columns)

                if ok_k and ok_l:
                    new_tile = self.array_current_game_board[k][l]
                    if new_tile.get_state() == TileState.FLAGGED:
                        number_of_flags += 1

        return number_of_flags

    def find_clicked_button(self, x, y, button_list):
        for i, item in enumerate(button_list): 
            if item.point_in_box(x, y):
                return button_list[i].get_name()


### Tile Actions

    def get_tile(self, event, space=False):

        delta = game_border if space else 0
            
        col = (event.x-delta) / game_tile_width
        row = (event.y-delta) / game_tile_width
        if not 0 < col <= self.int_current_game_columns: return -1, -1
        if not 0 < row <= self.int_current_game_rows: return -1, -1

        return int(row), int(col)

    def tile_action(self, function, event, space=False):
        
        row, col = self.get_tile(event, space)
        if (row or col) == -1: return
        tile = self.array_current_game_board[row][col]
        
        if function == 'flag':
            self.int_current_flags += tile.toggle_flag()
            self.__update_flags()
            self.play_sound('flag')
        elif function == 'open':
            self.open_tile_function(tile)
        elif function == 'tile':
            return tile

    def open_tile_function(self, tile):
        tile.open_tile()
        if tile.get_tile_number() == 0: self.open_square(tile)
        if self.check_loss(tile): return
        self.check_victory()

    def open_remaining_tiles(self):
        for i in range(self.int_current_game_columns):
            for j in range(self.int_current_game_rows):
                if not self.__is_bomb(j,i):
                    self.__open_tile(j,i)
                else:
                    self.__force_flag(j,i)

    def open_square(self, tile):
        if not tile.get_bomb():
            for k in [tile.get_row()-1 + i for i in range(3)]:
                for l in [tile.get_col()-1 + i for i in range(3)]: 
                    
                    ok_k = (0 <= k < self.int_current_game_rows)
                    ok_l = (0 <= l < self.int_current_game_columns)
                    
                    if ok_k and ok_l:
                        new_tile = self.array_current_game_board[k][l]
                        if new_tile.get_state() == TileState.HIDDEN:
                            self.open_tile_function(new_tile)

    def __open_tile(self, i, j):
        self.array_current_game_board[i][j].open_tile()

    def __is_bomb(self, i, j):
        return self.array_current_game_board[i][j].get_bomb()

    def __force_flag(self, i, j):
        self.array_current_game_board[i][j].force_flag()


### Update Graphics

    def __update_flags(self):
        n_flags = self.int_current_game_mines-self.int_current_flags
        self.canvas.itemconfig(self.display_flag_marker, text=str(n_flags))

game_instance = Minesweeper()
game_instance.mainloop()