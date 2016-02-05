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
import os
import pygame
#globals.cards_of_element_shower_element содержит стихию
class CardsOfElementShower(pygame.sprite.Sprite):
    #Не прототип!
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.player = player
        self.type = 'cardsofelementshower'
        #self.rect = self.image.get_rect().move((rect[0], rect[1]))
        self.cards = 0
        self.shift = 2
        #self.first_part = True #True - shows 1,2,3 from list, False shows 2,3,4 elements
    def draw(self):
        pass
        #globals.background.blit(self.image, self.rect)
    def update(self):
        #print self.type, 'update'
        globals.cards_in_deck.empty()
        if globals.cli:
            if globals.player_id != globals.player.id:
                return
        if not globals.cli or  globals.player.cards_generated: 
            for card in globals.player.cards[globals.cards_of_element_shower_element]:
                #exec("globals.cards_in_deck.add(globals.player." + card.lower() + ")")
                globals.cards_in_deck.add(globals.player.cards[globals.cards_of_element_shower_element][card])
