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
class HealthWindow(pygame.sprite.Sprite):
    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'healthwindow'
        globals.interface.add(self)
        self.font = pygame.font.Font(None, 22)
        text = self.font.render('1', True, (1,1,1))
        self.rect = text.get_rect().move(rect)
    def draw(self):
        #cb3b3a
        if not globals.cli:
            text = self.font.render(str(globals.player.health), True, (203, 59, 58))
        else:
            if globals.player_id == 1:
                text = self.font.render(str(globals.player1.health), True, (203, 59, 58))
            else:
                text = self.font.render(str(globals.player2.health), True, (203, 59, 58))
        globals.background.blit(text, self.rect)
    def update(self):
        self.draw()
class HealthWindowEnemy(pygame.sprite.Sprite):
    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'healthwindow'
        globals.interface.add(self)
        self.font = pygame.font.Font(None, 22)
        text = self.font.render('1', True, (1,1,1))
        self.rect = text.get_rect().move(rect)
    def draw(self):
        #cb3b3a
        if not globals.cli:
            text = self.font.render(str(globals.player.enemy.health), True, (203, 59, 58))
        else:
            if globals.player_id == 1:
                text = self.font.render(str(globals.player2.health), True, (203, 59, 58))
            else:
                text = self.font.render(str(globals.player1.health), True, (203, 59, 58))
        globals.background.blit(text, self.rect)
    def update(self):
        self.draw()