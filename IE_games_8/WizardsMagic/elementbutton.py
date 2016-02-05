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
import pygame
import globals
import os
pygame.font.init()
current_folder = os.path.dirname(os.path.abspath(__file__))

class ElementShower(pygame.sprite.Sprite):
    def __init__(self):
        self.type = 'outer'
        self.init_text = globals.font2.render('',False,(0,0,0))
        pygame.sprite.Sprite.__init__(self)
    def draw(self):
        #self.image = self.surface_backup.copy()
        if not globals.cli:
            text = globals.font2.render(str(globals.player.enemy.mana[self.element]),True,self.color)
        else:
            if not globals.player_id:
                return
            #exec("text = self.font.render(str(globals.player"+str(globals.player_id)+".enemy" + "." + self.element + "_mana),True,"+self.color+")")
            if globals.player_id == 1:
                text = globals.font2.render(str(globals.player2.mana[self.element]),True,self.color)
            else:
                text = globals.font2.render(str(globals.player1.mana[self.element]),True,self.color)
        #self.image.blit(text, (2, 9))
        globals.background.blit(text, self.rect)
    def update(self):
        self.draw()
class WaterElementShower(ElementShower):
    def __init__(self, rect):
        ElementShower.__init__(self)
        self.element = 'water'
        self.color = (255,255,255)
        self.rect = self.init_text.get_rect().move((rect[0], rect[1]))
        globals.interface.add(self)
class FireElementShower(ElementShower):
    def __init__(self, rect):
        ElementShower.__init__(self)
        self.element = 'fire'
        self.color = (255,255,255)
        self.rect = self.init_text.get_rect().move((rect[0], rect[1]))
        ElementShower.__init__(self)
        globals.interface.add(self)
class AirElementShower(ElementShower):
    def __init__(self, rect):
        ElementShower.__init__(self)
        self.element = 'air'
        self.color = (255,255,255)
        self.rect = self.init_text.get_rect().move((rect[0], rect[1]))
        ElementShower.__init__(self)
        globals.interface.add(self)
class EarthElementShower(ElementShower):
    def __init__(self, rect):
        ElementShower.__init__(self)
        self.element = 'earth'
        self.color = (255,255,255)
        self.rect = self.init_text.get_rect().move((rect[0], rect[1]))
        ElementShower.__init__(self)
        globals.interface.add(self)
class LifeElementShower(ElementShower):
    def __init__(self, rect):
        ElementShower.__init__(self)
        self.element = 'life'
        self.color = (255,255,255)
        self.rect = self.init_text.get_rect().move((rect[0], rect[1]))
        ElementShower.__init__(self)
        globals.interface.add(self)
class DeathElementShower(ElementShower):
    def __init__(self, rect):
        ElementShower.__init__(self)
        self.element = 'death'
        self.color = (255,255,255)
        self.rect = self.init_text.get_rect().move((rect[0], rect[1]))
        ElementShower.__init__(self)
        globals.interface.add(self)
class ElementButton(pygame.sprite.Sprite):
    def __init__(self):
        #Это прототип!
        self.type = 'button'
        self.surface_backup = self.image.copy()
        pygame.sprite.Sprite.__init__(self)
    def draw(self):
        self.image = self.surface_backup.copy()
        if not globals.cli:
            #exec("text = self.font.render(str(globals.player" + "." + self.element + "_mana),True,"+self.color+")")
            text = globals.font2.render(str(globals.player.mana[self.element]),True,self.color)
        else:
            if not globals.player_id:
                return
            if globals.player_id == 1:
                text = globals.font2.render(str(globals.player1.mana[self.element]), True, self.color)
            else:
                text = globals.font2.render(str(globals.player2.mana[self.element]), True, self.color)
            #exec("text = self.font.render(str(globals.player"+ str(globals.player_id ) + "." + self.element + "_mana),True,"+self.color+")")
        self.image.blit(text, (12, 17))
        globals.background.blit(self.image, self.rect)
    def update(self):
        self.draw()
    def onmouse(self):
        pass
    def onmouseout(self):
        pass
    def onmousedown(self):
        globals.selected_card = False
        for cardbox in globals.cardboxes:
            cardbox.light = False
        pygame.mixer.music.stop()
        if self.element != globals.selected_elem:
            globals.selected_elem = self.element
            #self.default()
            exec('globals.'+globals.cards_of_element_shower_element+'_element_button.default()')
            globals.cards_in_deck.empty()
            globals.cards_of_element_shower_element = self.element
            self.image = self.image_pressed
            self.surface_backup = self.image.copy()
            #elements sound
            globals.set_element_sound(self.element) 
            globals.playmusic(time=2500);
    def onmouseup(self):
        pass
    def default(self):
        self.image = self.image_normal
        self.surface_backup = self.image.copy()
class WaterElementButton(ElementButton):
    def __init__(self, rect):
        self.element = 'water'
        self.image_normal = pygame.image.load(current_folder+'/misc/water_icon.gif').convert_alpha()
        self.image_pressed = pygame.image.load(current_folder+'/misc/water_icon_selected.gif').convert_alpha()
        self.image = self.image_pressed
        self.color = (255,255,255)
        self.rect = self.image.get_rect().move((rect[0], rect[1]))
        ElementButton.__init__(self)
        globals.interface.add(self)
class FireElementButton(ElementButton):
    def __init__(self, rect):
        self.element = 'fire'
        self.image_normal = pygame.image.load(current_folder+'/misc/fire_icon.gif').convert_alpha()
        self.image_pressed = pygame.image.load(current_folder+'/misc/fire_icon_selected.gif').convert_alpha()
        self.image = self.image_normal
        self.color = (255,255,255)
        self.rect = self.image.get_rect().move((rect[0], rect[1]))
        ElementButton.__init__(self)
        globals.interface.add(self)
class AirElementButton(ElementButton):
    def __init__(self, rect):
        self.element = 'air'
        self.image_normal = pygame.image.load(current_folder+'/misc/air_icon.gif').convert_alpha()
        self.image_pressed = pygame.image.load(current_folder+'/misc/air_icon_selected.gif').convert_alpha()
        self.image = self.image_normal
        self.color = (255,255,255)
        self.rect = self.image.get_rect().move((rect[0], rect[1]))
        ElementButton.__init__(self)
        globals.interface.add(self)
class EarthElementButton(ElementButton):
    def __init__(self, rect):
        self.element = 'earth'
        self.image_normal = pygame.image.load(current_folder+'/misc/earth_icon.gif').convert_alpha()
        self.image_pressed = pygame.image.load(current_folder+'/misc/earth_icon_selected.gif').convert_alpha()
        self.image = self.image_normal
        self.color = (255,255,255)
        self.surface_backup = self.image.copy()
        self.rect = self.image.get_rect().move((rect[0], rect[1]))
        ElementButton.__init__(self)
        globals.interface.add(self)
class LifeElementButton(ElementButton):
    def __init__(self, rect):
        self.element = 'life'
        self.image_normal = pygame.image.load(current_folder+'/misc/life_icon.gif').convert_alpha()
        self.image_pressed = pygame.image.load(current_folder+'/misc/life_icon_selected.gif').convert_alpha()
        self.image = self.image_normal
        self.color = (255,255,255)
        self.rect = self.image.get_rect().move((rect[0], rect[1]))
        ElementButton.__init__(self)
        globals.interface.add(self)
class DeathElementButton(ElementButton):
    def __init__(self, rect):
        self.element = 'death'
        self.image_normal = pygame.image.load(current_folder+'/misc/death_icon.gif').convert_alpha()
        self.image_pressed = pygame.image.load(current_folder+'/misc/death_icon_selected.gif').convert_alpha()
        self.image = self.image_normal
        self.color = (255,255,255)
        self.rect = self.image.get_rect().move((rect[0], rect[1]))
        ElementButton.__init__(self)
        globals.interface.add(self)
