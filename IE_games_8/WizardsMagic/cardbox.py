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
current_folder = os.path.dirname(os.path.abspath(__file__))

class Cardbox(pygame.sprite.Sprite):
    def __init__(self, rect, player, position):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'cardbox'
        self.position = position
        self.animation_tick = 0
        self.location = rect
        self.player = player #ссылка на игрока
        self.opposite = False
        self.image = pygame.image.load(current_folder+'/misc/cardbox_bg.gif').convert_alpha()
        #self.light_image = pygame.image.load(current_folder+'/misc/cardbox-activated.gif').convert_alpha()
        self.animation_point = 0
        self.light_images = []
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac1.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac2.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac3.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac4.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac5.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac6.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac7.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac8.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac9.gif').convert_alpha())
        self.light_images.append(pygame.image.load(current_folder+'/misc/animated_cardbox/ac10.gif').convert_alpha())
        self.surface_backup = self.image.copy()
        self.rect = self.image.get_rect().move((rect[0], rect[1]))
        self.card = self.player
        self.light = False
        globals.panels.add(self)
    def get_opposite_cardbox(self):
        if self.position < 5:
            opposite_position = self.position + 5 #Id - блока, куда атаковать
        else:
            opposite_position = self.position - 5
        return globals.cardboxes[opposite_position]
    def draw(self):
        #self.image = self.surface_backup.copy()
        self.light_image = self.light_images[self.animation_point]
        self.animation_tick += 1
        if not self.animation_tick % 2:
            self.animation_tick = 0
            self.animation_point += 1
        if self.animation_point > len(self.light_images) - 1:
            self.animation_point = 0
        if self.light:
            self.image.blit(self.light_image,(0,0))
            if not self.opposite:
                self.rect = self.normal_rect
            else:
                self.rect = self.opposite_rect
            globals.background.blit(self.image, self.rect)
            self.image = self.surface_backup.copy()
            return
        if not self.opposite:
            self.rect = self.normal_rect
        else:
            self.rect = self.opposite_rect
        globals.background.blit(self.image, self.rect)
    def update(self):
        self.draw()
