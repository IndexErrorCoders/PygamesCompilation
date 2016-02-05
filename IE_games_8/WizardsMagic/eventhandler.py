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
import globals
import pygame
import cards
import sys
import os
import sockets
import socket
import menu
from pygame.locals import *
current_folder = os.path.dirname(os.path.abspath(__file__))

class Point(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(current_folder+'/misc/point_alpha.gif').convert_alpha()
        self.rect = self.image.get_rect()
    def draw(self, rect):
        globals.background.blit(self.image, rect)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(rect)
class Event_handler():
    def __init__(self):
        self.onmouse_element = False
    def event(self, event):
        if event.type == QUIT:
            menu.exit_program()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                if not globals.question:
                    if not 'importantmessage' in globals.__dict__:
                        menu.menu_esc_question()
                    else: #handle ESC key when display importantmessage
                        if globals.cli:
                            if not globals.opponent_disconnect:
                                sockets.query({"action":"bye","player_id":globals.player_id})
                            else:
                                sockets.query({"action":"bbye"})
                        globals.information_group.remove(globals.importantmessage)
                        del globals.importantmessage
                        globals.stage = 0
                        globals.cli = False
                    return
                else:
                    menu.clean_question()
                    return
            if globals.question and (event.key>=K_0 and event.key<=K_9 or event.key>=K_a and event.key<=K_z or event.key==K_PERIOD):
                globals.answer=globals.answer+pygame.key.name(event.key)
            if globals.question and (event.key==K_RETURN or len(globals.answer)>=globals.answer_maxchar):
                exec(globals.answer_cmd)
                menu.clean_question()
                return
            if globals.itemfocus:
                globals.itemfocus.change(event)
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                globals.point.draw(event.pos)
                if globals.stage==0:
                    collided = pygame.sprite.spritecollide(globals.point, globals.menu_group, 0)
                elif globals.stage<=2:
                    collided = pygame.sprite.spritecollide(globals.point, globals.cards_in_deck, 0)
                    if not collided:
                        collided = pygame.sprite.spritecollide(globals.point, globals.interface, 0)
                    if not collided:
                        collided = pygame.sprite.spritecollide(globals.point, globals.panels, 0)
                if not collided:
                    return
                item = collided[len(collided)-1]
                if item.type == "nicknamewindow":
                    return
                if item.type == "healthwindow":
                    return 
                if item.type == 'outer':
                    return
                if item.type == 'button' or item.type == 'txtinput' or item.type == 'checkbox':
                    item.onmousedown()
                    return
                if item.type == "warrior_card": #Карта в колоде! Карта на поле в cardbox
                    #exec('selected_card_0 = cards.' + item.name + '()') #Переменной selected_card_0 присваиваем новый объект
                    globals.selected_card = cards.links_to_cards[item.name]() # из локальной в глобальную
                    if globals.player.id == 1:
                        for cardbox in globals.cardboxes[0:5]:
                            if globals.player.action_points:
                                if cardbox.card.name == "player": #если карты нет
                                    cardbox.light = True
                    else:
                        for cardbox in globals.cardboxes[5:10]:
                            if cardbox.card.name == "player":
                                cardbox.light = True
                    return
                if item.type == "magic_card": #карта магии в колоде
                    if not globals.player.action_points: #если уже ходил
                        globals.gameinformationpanel.display("You've already made a move.")
                        return
                    selected_card = cards.links_to_cards[item.name]()
                    #exec('selected_card = cards.' + item.name + '()') #в переменную selected_card засовываем одну такую карту
                    #exec('available_mana = globals.player.' + selected_card.element + '_mana') # Вычисляем сколько маны у нас есть. Значение помещаем в локальную переменную available_mana
                    available_mana = globals.player.mana[selected_card.element]
                    if available_mana >= selected_card.level:
                        #exec('globals.player.' + selected_card.element + '_mana -= ' + str(selected_card.level)) #Отнимаем ману
                        globals.player.mana[selected_card.element] -= selected_card.level
                        globals.player.action_points = False #ставим запись, что ход сделан
                        selected_card.player = globals.player
                        sockets.query({"action":"card","card":selected_card.name,"type":"magic"})
                        selected_card.cast() #вызываем магию, периодизация делается уже внутри класса, путем добавления в группу globals.magic_cards
                        selected_card.spell_speaker()
                        #Закрываем колоду
                        for cardbox in globals.cardboxes:
                            cardbox.light = False
                    else:
                        globals.gameinformationpanel.display('Not enough mana.')
                    return
                if globals.cast_focus: #выбор цели для каста
                    if item.type == 'cardbox':
                        globals.cast_focus_wizard.focus_cast_action(item.card)
                        sockets.query({"action":"cast","position":globals.cast_focus_wizard.parent.position,"target":item.position,"focus":True})
                if item.player.id != globals.player.id:
                    return
                if globals.cli:
                    if item.player.id != globals.player_id:
                        return
                if item.type == "cardbox": #Если клик на карточный бокс
                    if item.card.name != "player": #Если в этом блоке есть карта
                        if item.card.cast: #если есть каст
                            if not item.card.used_cast: # если еще не кастовали
                                if not item.card.focus_cast:
                                    sockets.query({"action":"cast","position":item.position,"focus":False})
                                item.card.cast_action()
                            else:
                                globals.gameinformationpanel.display("You've already cast.")
                                return
                    if globals.selected_card: #если выбрана карта
                        if item.card.name != 'player':
                            globals.gameinformationpanel.display('This sector is busy.')
                            return
                        if not globals.player.action_points: #если уже ходил
                            globals.gameinformationpanel.display("You've already made a move.")
                            return
                        #отключаем подсветку
                        for cardbox in globals.cardboxes:
                            cardbox.light = False
                        #Выводим карту
                        #exec('available_mana = globals.player.' + globals.selected_card.element + '_mana') # Вычисляем сколько маны у нас есть. Значение помещаем в локальную переменную available_mana
                        available_mana = globals.player.mana[globals.selected_card.element]
                        if available_mana < globals.selected_card.level:
                            globals.gameinformationpanel.display("Not enough mana.")
                            return
                        item.card = globals.selected_card
                        item.card.parent = item
                        sockets.query({"action":"card","card":item.card.name,"position":item.position,"type":"warrior"})
                        #item.card.cardboxes = cardboxes
                        #item.card.playerscards = playerscards
                        item.card.field = True
                        item.card.summon() #функция которая хранит описание действий при выводе карты
                        globals.player.action_points = False
                        #exec('globals.player.' + globals.selected_card.element + '_mana -= ' + str(globals.selected_card.level)) #Отнимаем ману
                        globals.player.mana[globals.selected_card.element] -= globals.selected_card.level
                        #globals.cards_in_deck.empty() #очищаем группу карты в колоде
                        if item.player.id == 1:
                            globals.ccards_1.add(item.card)
                        else:
                            globals.ccards_2.add(item.card)
                        globals.selected_card = 0
            elif event.button == 3: #ПРАВАЯ КНОПКА МЫШИ
                if globals.cast_focus:
                    globals.cast_focus = False
                    for card in globals.ccards_1.sprites()+globals.ccards_2.sprites():
                        card.light_switch(False)
                    return
                globals.point.draw(event.pos)
                collided = pygame.sprite.spritecollide(globals.point, globals.cards_in_deck, 0)
                if not collided:
                    collided = pygame.sprite.spritecollide(globals.point, globals.interface, 0)
                if not collided:
                    collided = pygame.sprite.spritecollide(globals.point, globals.panels, 0)
                if not collided:
                    return
                item = collided[len(collided)-1]
                if item.type == "warrior_card" or item.type == "magic_card" : #по боевой карте
                    globals.card_info_group.add(globals.cardinfo)
                    #globals.cardinfo.text = item.info
                    globals.cardinfo.card = item
                    globals.cardinfo.show = True
                if item.type == "cardbox":
                    if item.card.name != "player":
                        globals.card_info_group.add(globals.cardinfo)
                        #globals.cardinfo.text = item.card.info
                        globals.cardinfo.card = item.card
                        globals.cardinfo.show = True
                if item.type == 'cardsofelementshower':
                    globals.interface.remove(globals.cardsofelementshower1)
                    globals.interface.remove(globals.cardsofelementshower2)
                    globals.cards_in_deck.empty()
                    for cardbox in globals.cardboxes:
                        cardbox.light = False
        elif event.type == MOUSEBUTTONUP: #отпускаем кнопку мыши
            if event.button == 3: #Правую
                if globals.cardinfo.show:
                    globals.cardinfo.show = False
                    globals.card_info_group.empty()
            else: #1
                for elem in globals.interface:
                    if elem.type == 'button':
                        elem.onmouseup()
        elif event.type == MOUSEMOTION:
            globals.point.draw(event.pos)
            if globals.stage==0:
                collided = pygame.sprite.spritecollide(globals.point, globals.menu_group, 0)
            elif globals.stage<=2:
                collided = pygame.sprite.spritecollide(globals.point, globals.interface, 0)
            if not collided:
                if self.onmouse_element:
                    self.onmouse_element.onmouseout()
                    self.onmouse_element = False
                return
            item = collided[len(collided)-1]
            if item.type == 'button':
                if self.onmouse_element != item:
                    item.onmouseout()
                self.onmouse_element = item
                item.onmouse()
#>>>>>>> other