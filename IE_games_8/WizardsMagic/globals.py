# -*- coding: utf-8 -*-
#Wizards Magic
#Copyright (C) 2011-2014  https://code.google.com/p/wizards-magic/
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
try: 
    import pygame
    yes_pygame = True
except ImportError:
    yes_pygame = False
import os

current_folder = os.path.dirname(os.path.abspath(__file__))
if yes_pygame: 
    pygame.font.init()
    panels = pygame.sprite.Group() #Нижний уровень #Lower Level
    interface = pygame.sprite.Group() #Уровень кнопок #Button Level
    cards_in_deck = pygame.sprite.Group() #Уровень дополнительный #The level of additional
    ccards_1 = pygame.sprite.Group() #  Карты, которые вывел первый игрок #Cards, which brought the first player
    ccards_2 = pygame.sprite.Group() # Карты, которые вывел второй игрок #Cards, which brought the second player
    magic_cards = pygame.sprite.Group() #Использующаяся магия #Magic Cards
    card_info_group = pygame.sprite.Group() #  Группа, которая содержит спрайт, содержащий панель вывода информации о карте
    information_group = pygame.sprite.Group() #Группа, содержащая панель вывода игровой информации
    menu_group = pygame.sprite.Group() # menu items
    #font = pygame.font.Font(current_folder+"/misc/Domestic_Manners.ttf", 15)
    font = pygame.font.Font(current_folder+"/misc/Neocyr.ttf", 15)
    font2 = pygame.font.Font(current_folder+"/misc/Domestic_Manners.ttf", 15)
    #print pygame.font.match_font('Arial')
cards_of_element_shower_element = "water" #какой элемент показывать #Any element to show
selected_card = False #Выбранная карта #Selected Card
selected_elem = None
screen = None
player = None
player1 = None
player2 = None
player_id = 0
players = [[]]  #массив игроки. ID элемента - id игры .Элемент 0 - 1 игрок , элемент 1 - второй игрок
players.append([])
games_cards = [{}] #cards separated for every concurrent game
games_cards.append({})
opponent_disconnect = False
#Каст с выбором цели
cast_focus = False #включен ли режим
cast_focus_wizard = None # ссылка на кастующий объект ( не цель ! )
#cast_focus_filter = None
#Groups for annimations
animations_running = []
cards_attacking = []
#attack_started = False
turn_ended = False
cli = False
stage = 0 # 0=Menu 1=Single player game 2=network game 9=options
question = False # when true disable all events but key stroke
answer = "" #buffer to store key strokes
answer_maxchar = 0 # max number of characters we are waiting for
answer_cmd = "" #function to execute when stoke ENTER
itemfocus = None #input object with focus
running = True #while true, signal to threads that main is still running
server_thread = None #server thread object

#configuration global variables
music = 'Y' #enable background music
sound = 'Y' #enable sound effects
nick = "" #nickname for network game
server = "" # ip server for network game
port = "" # port to connect to/serve network game

def clean():

    panels.empty()
    interface.empty()
    cards_in_deck.empty()
    ccards_1.empty()
    ccards_2.empty()
    magic_cards.empty()
    card_info_group.empty()
    #information_group.empty()
    menu_group.empty()

def playmusic(time=None):
    ''' global function to control music and sounds '''
    ''' time used for fadeout (ms)'''
    if sound=='Y':
        try:
            pygame.mixer.music.play()
            if time != None:
                pygame.mixer.music.fadeout(time)
        except:
            print "Unexpected error: while trying play sound"

def set_element_sound(element):
    if element == 'water':
        try: 
            pygame.mixer.music.load(current_folder+'/misc/sounds/water_elem_click.mp3')
        except:
            print "Unexpected error: while trying load water sound"
    elif element == 'air':
        try: 
            pygame.mixer.music.load(current_folder+'/misc/sounds/air_elem_click.mp3')
        except:
            print "Unexpected error: while trying load air sound"
    elif element == 'fire':
        try: 
            pygame.mixer.music.load(current_folder+'/misc/sounds/fire_elem_click.mp3')
        except:
            print "Unexpected error: while trying load fire sound"
    elif element == 'earth':
        try: 
            pygame.mixer.music.load(current_folder+'/misc/sounds/earth_elem_click.mp3')
        except:
            print "Unexpected error: while trying load earth sound"
    elif element == 'death':
        try: 
            pygame.mixer.music.load(current_folder+'/misc/sounds/death_elem_click.mp3')
        except:
            print "Unexpected error: while trying load death sound"
    elif element == 'life':
        try:
            pygame.mixer.music.load(current_folder+'/misc/sounds/life_elem_click.mp3')
        except:
            print "Unexpected error: while trying load life sound"







