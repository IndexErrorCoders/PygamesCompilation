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
import os
import globals
import player
current_folder = os.path.dirname(os.path.abspath(__file__))

class CompleteTheCourseButton(pygame.sprite.Sprite):
    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)
        #self.panel = panel
        self.type = 'button'
        self.image_normal = pygame.image.load(current_folder+'/misc/attack_button_up.gif').convert_alpha()
        self.image_pressed = pygame.image.load(current_folder+'/misc/attack_button_down.gif').convert_alpha()
        self.image = self.image_normal
        self.relative_rect = self.image.get_rect().move((rect[0], rect[1]))
        self.rect = self.relative_rect #.move(self.panel.rect[0], self.panel.rect[1])
        globals.interface.add(self)
    def onmouse(self):
        return
    def onmouseout(self):
        return
    def onmousedown(self):
        self.image = self.image_pressed
        if globals.cli:
            if globals.player_id != globals.player.id:
                return
        for cardbox in globals.cardboxes:
            cardbox.light = False
        player.finish_turn()
    def onmouseup(self):
        self.image = self.image_normal
    def draw(self):
        if globals.cli:
            if globals.player_id != globals.player.id:
                return
        globals.background.blit(self.image, self.relative_rect)
    def update(self):
        self.draw()
