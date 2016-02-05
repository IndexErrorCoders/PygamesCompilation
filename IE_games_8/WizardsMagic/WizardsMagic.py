#!/usr/bin/python2
# -*- coding: utf-8 -*-
import pygame.sprite
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

# To change this template, choose Tools | Templates
# and open the template in the editor.
#import pygame.sprite
#Внимание!! Для того, чтоsбы слои не наслаивались, я использую объект surface_backup , который является копией изображения. После этого они заменяются
# Caution! To chtosby layers are layered, I use an object surface_backup, which is a copy of the image. After that, they are replaced
__author__ = "chubakur"
__date__ = "$12.02.2011 12:11:42$"
import pygame
from pygame.locals import *
import sys
import os
import cards
import time
import player
if pygame.version.vernum < (1, 9, 1):
    import copy
import animations
import globals
import elementbutton
import cardinfo
import cardsofelementshower
import completethecoursebutton
import healthwindow
import cardbox
import eventhandler
import gameinformation
import menu
import options
import sockets
import nickname_window
import thread
import important_message
current_folder = os.path.dirname(os.path.abspath(__file__))
globals.current_folder = current_folder
def server_handler():
    handling = True
    while handling:
        gi = sockets.get_package()
        #si = sock.recv(256)
        #print 'si'
        #print si
        #print "RETURN:"
        #print get_package()
        print gi
        if gi['action'] == 'join':
            print("Join to Game with Player_id " + str(gi['id']))
            globals.player_id = gi['id']
            if globals.player_id == 1:
                player.switch_position()
        elif gi['action'] == 'update':
            #Устанавливаем ники
            #globals.player1.nickname = gi['nicknames'][0]
            #globals.player2.nickname = gi['nicknames'][1]
            globals.nickname1.set_nickname(gi['nicknames'][0])
            globals.nickname2.set_nickname(gi['nicknames'][1])
            #TODO: draw nicknames
            #nickname_window.NicknameWindow((200,10), globals.player1)
            #nickname_window.NicknameWindow((200,400), globals.player2)
            #кидаем ману первому игроку
            manas = ["water","fire","air","earth","life","death"]
            for i, element in enumerate(manas):
                globals.player1.mana[element] = gi['mana'][0][i]
                globals.player2.mana[element] = gi['mana'][1][i]
            if globals.player2.cards_generated == 0 and globals.player1.cards_generated == 0:
                print "Выдаем карты"
                globals.player1.get_cards(gi['deck_cards'][0])
                globals.player1.cards_generated = True
                #а теперь второму
                globals.player2.get_cards(gi['deck_cards'][1])
                globals.player2.cards_generated = True
            globals.information_group.remove(globals.importantmessage)
            del globals.importantmessage
            globals.gameinformationpanel.display('Battle started.')
        elif gi['action'] == 'switch_turn':
            player.me_finish_turn()
        elif gi['action'] == 'card':
            #print gi
            #if gi['position'] == 0:
                #cardbox = globals.cardbox0
            if gi['type'] == 'warrior':
                #exec("tmp_card = cards." + gi['card'] + "()")
                tmp_card = cards.links_to_cards[gi['card']]()
                exec("globals.cardbox" + str(gi['position']) + ".card =  tmp_card")
                exec("globals.cardbox" + str(gi['position']) + ".card.parent = globals.cardbox" + str(gi['position']))
                exec("globals.cardbox" + str(gi['position']) + ".card.field = True")
                exec("globals.cardbox" + str(gi['position']) + ".card.summon()")
                globals.player.mana[tmp_card.element] -= tmp_card.level #Отнимаем ману
                exec("globals.ccards_" + str(globals.player.id) + ".add(globals.cardbox" + str(gi['position']) + ".card)")
                #exec("globals.ccards_2.add(globals.cardbox"+str(gi['position'])+".card)")
                #print globals.player.id,tmp_card
            elif gi['type'] == 'magic':
                #exec("tmp_card = cards." + gi['card'] + "()")
                tmp_card = cards.links_to_cards[gi['card']]()
                globals.player.mana[tmp_card.element] -= tmp_card.level #Отнимаем ману
                globals.player.action_points = False #ставим запись, что ход сделан
                tmp_card.player = globals.player
                tmp_card.cast()
                globals.gameinformationpanel.display('Enemy used ' + gi['card'])
        elif gi['action'] == 'cast':
            if not gi['focus']:
                exec('globals.cardbox' + str(gi['position']) + ".card.cast_action()")
            else:#фокус каст
                exec('globals.cardbox' + str(gi['position']) + ".card.focus_cast_action(" + "globals.cardbox" + str(gi['target']) + ".card)")
                    # if not item.card.used_cast: # если еще не кастовали
                                #  item.card.cast_action()
        elif gi['action'] == "opponent_disconnect":
            handling = False
            globals.opponent_disconnect = True
            globals.importantmessage = important_message.MessageWindow('Sorry, your opponent was disconnected from game.')
            time.sleep(3)
            for s in globals.information_group.sprites(): 
                if type(s) == important_message.MessageWindow:
                    globals.information_group.remove(s)
            del globals.importantmessage
            globals.stage = 0
            globals.cli = False
        elif gi['action'] == "server_close":
            handling = False
            globals.importantmessage = important_message.MessageWindow('Sorry, server is closing.')
            time.sleep(3)
            for s in globals.information_group.sprites(): 
                if type(s) == important_message.MessageWindow:
                    globals.information_group.remove(s)
            del globals.importantmessage
            globals.stage = 0
            globals.cli = False
        elif gi['action'] == "value_error":
            handling = False
            globals.importantmessage = important_message.MessageWindow('Socket error. String Null')
            time.sleep(3)
            for s in globals.information_group.sprites(): 
                if type(s) == important_message.MessageWindow:
                    globals.information_group.remove(s)
            del globals.importantmessage
            globals.stage = 0
            globals.cli = False
        elif gi['action'] == "socket_error":
            handling = False
            globals.importantmessage = important_message.MessageWindow('Socket error.')
            time.sleep(3)
            for s in globals.information_group.sprites(): 
                if type(s) == important_message.MessageWindow:
                    globals.information_group.remove(s)
            del globals.importantmessage
            globals.stage = 0
            globals.cli = False
    sockets.sock.close()
def load_and_start_bg_music():
    globals.bg_sound = pygame.mixer.Sound(current_folder+'/misc/sounds/11_the_march_of_the_goblins__tobias_steinmann.ogg')
    globals.bg_sound.play(-1)
def start_game(cli=False,ai=False):
    globals.attack_started = [True]
    globals.background = pygame.image.load(current_folder+'/misc/bg_sample.gif')
    #globals.background = globals.background.convert()
    #globals.background = pygame.Surface(globals.screen.get_size())
    globals.background = globals.background.convert_alpha()
    globals.cards_of_element_shower_element = "water"
    #globals.background.fill((0, 0, 0))
    background_backup = globals.background.copy()
    #font.set_bold(0)
    globals.games_cards[0]['water'] = cards.water_cards_deck[:]
    globals.games_cards[0]['fire'] = cards.fire_cards_deck[:]
    globals.games_cards[0]['air'] = cards.air_cards_deck[:]
    globals.games_cards[0]['earth'] = cards.earth_cards_deck[:]
    globals.games_cards[0]['life'] = cards.life_cards_deck[:] 
    globals.games_cards[0]['death'] = cards.death_cards_deck[:]
    if globals.player1: 
        globals.player1.enemy = None
        globals.player2.enemy = None
    globals.player1 = player.Player1()
    globals.player2 = player.Player2()
    globals.player1.enemy = globals.player2
    globals.player2.enemy = globals.player1
    globals.player = globals.player1
    # 0 1 2 3 4   //Расположение
    # 5 6 7 8 9
    globals.cardbox0 = cardbox.Cardbox((22, 46), globals.player1, 0) #0 место на поле
    globals.cardbox1 = cardbox.Cardbox((172, 46), globals.player1, 1) #1 место на поле
    globals.cardbox2 = cardbox.Cardbox((322, 46), globals.player1, 2) #2 место на поле
    globals.cardbox3 = cardbox.Cardbox((472, 46), globals.player1, 3) #3 место на поле
    globals.cardbox4 = cardbox.Cardbox((622, 46), globals.player1, 4) #4 место на поле
    globals.cardbox5 = cardbox.Cardbox((22, 238), globals.player2, 5) #5 место на поле
    globals.cardbox6 = cardbox.Cardbox((172, 238), globals.player2, 6) #6 место на поле
    globals.cardbox7 = cardbox.Cardbox((322, 238), globals.player2, 7) #7 место на поле
    globals.cardbox8 = cardbox.Cardbox((472, 238), globals.player2, 8) #8 место на поле
    globals.cardbox9 = cardbox.Cardbox((622, 238), globals.player2, 9) #9 место на поле
    globals.cardboxes = [globals.cardbox0, globals.cardbox1, globals.cardbox2, globals.cardbox3, globals.cardbox4, globals.cardbox5, globals.cardbox6, globals.cardbox7, globals.cardbox8, globals.cardbox9] #Ссылки на объекты

    for tcardbox in globals.cardboxes:
        if pygame.version.vernum < (1, 9, 1):
            tcardbox.normal_rect = copy.deepcopy(tcardbox.rect)
            tcardbox.opposite_rect = copy.deepcopy(tcardbox.get_opposite_cardbox().rect)
        else:
            tcardbox.normal_rect = tcardbox.rect.copy()
            tcardbox.opposite_rect = tcardbox.get_opposite_cardbox().rect.copy()
    globals.castlabel = cards.CastLabel()
    healthwindow.HealthWindowEnemy((175, 10)) #Окошко здоровья верхнего игрока
    healthwindow.HealthWindow((167, 557)) #Окошко здоровья нижнего игрока
    # Кнопки колод стихий первого игрока
    elementbutton.WaterElementShower((246, 2))
    elementbutton.FireElementShower((337, 2))
    elementbutton.AirElementShower((419, 2))
    elementbutton.EarthElementShower((509, 2))
    elementbutton.LifeElementShower((590, 2))
    elementbutton.DeathElementShower((668, 2))
    # Кнопки колод стихий второго игрока
    globals.water_element_button = elementbutton.WaterElementButton((11, 427))
    globals.fire_element_button = elementbutton.FireElementButton((56, 427))
    globals.air_element_button = elementbutton.AirElementButton((101, 427))
    globals.earth_element_button = elementbutton.EarthElementButton((146, 427))
    globals.life_element_button = elementbutton.LifeElementButton((191, 427))
    globals.death_element_button = elementbutton.DeathElementButton((236, 427))
    #Кнопки завершения хода первого и второго игрока.
    completethecoursebutton.CompleteTheCourseButton((758, 378))
    #Окна выбора карты стихии
    globals.cardofelementsshower = cardsofelementshower.CardsOfElementShower()
    globals.nickname2 = nickname_window.NicknameWindow((142, 530), 'Guest')
    globals.nickname1 = nickname_window.NicknameWindow((22, 0), globals.nick)
    if ai:
        globals.player2.ai = True
        globals.nickname2.set_nickname('Computer')
    #стрелочки для сдвига карт в колоде
    #globals.leftarrow = cardsofelementshower.LeftArrow((356, 489))
    #globals.rightarrow = cardsofelementshower.RightArrow((739, 491))
    if not cli:
        globals.gameinformationpanel.display('Battle Started')
        globals.cli = False
        sockets.query = lambda x: x
    else:
        val = sockets.connect()
        if not val:
            globals.gameinformationpanel.display('Cant connect to server.')
            menu.menu_main()
            globals.stage = False
            return 0
        else:
            globals.importantmessage = important_message.MessageWindow('We are waiting for another player')
        sockets.query = sockets.query_
        globals.cli = True
        thread.start_new_thread(server_handler, ())
    if not globals.cli:
        player.switch_position()
    #********************************************************************************
    globals.screen.blit(globals.background, (0, 0))
    globals.panels.update()
    globals.interface.update()
    pygame.display.flip()
    sockets.query({"action":"join", "nickname":globals.nick}) #входим в игру
    while globals.stage == 1:
        #if globals.turn_ended and len(cards_attacking) = 0:
        #    for cardbox in globals.cardboxes:
        #        cardbox.opposite = not cardbox.opposite
        for event in pygame.event.get():
            globals.event_handler.event(event)
        globals.panels.update()
        globals.interface.update()
        globals.ccards_1.update()
        globals.ccards_2.update()
        globals.cardofelementsshower.update()
        globals.cards_in_deck.update()
        globals.card_info_group.update()
        globals.information_group.update()
        #interface_up_layer.update()
        globals.screen.blit(globals.background, (0, 0))
        #globals.background.fill((0,0,0))
        globals.background = background_backup.copy()
        if globals.animation == "N":
            for item in animations.animations_running + animations.cards_attacking + animations.cards_dying:
                del item
            animations.animations_running = []
            animations.cards_attacking = []
            animations.cards_dying = []
        if len(animations.animations_running) == False and len(globals.attack_started):
            if not globals.cli:
                player.switch_position()
        for animation_running in animations.animations_running:
            animation_running.run()
            if len(globals.attack_started) and len(globals.cards_attacking) == False:
                if not globals.cli:
                    player.switch_position()
        pygame.display.flip()
        clock.tick(50)



pygame.init()
globals.screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Wizards Magic')
clock = pygame.time.Clock()

#read configuration file
options.read_configuration()
if globals.music == "Y":
    thread.start_new_thread(load_and_start_bg_music,())
menu.menu_main()

globals.event_handler = eventhandler.Event_handler()
globals.point = eventhandler.Point()
globals.gameinformationpanel = gameinformation.GameInformationPanel()
globals.cardinfo = cardinfo.CardInfo()

globals.screen.blit(globals.background, (0, 0))

pygame.display.flip()
# noinspection PyPackageRequirements
while 1:
    for event in pygame.event.get():
        globals.event_handler.event(event)
    if globals.stage == 1:
        if globals.cli: 
            start_game(1)
        else:
            start_game(ai=globals.ai)
            #start_game(ai=(globals.ai == 'Y'))
        globals.clean()
        menu.menu_main()

    globals.menu_group.update()
    globals.information_group.update()
    globals.screen.blit(globals.background, (0, 0))
    globals.background = globals.background_backup.copy()
    pygame.display.flip()
    clock.tick(50)    
