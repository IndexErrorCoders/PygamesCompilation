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
#TODO: cout as globals.player
class NicknameWindow(pygame.sprite.Sprite):
    def __init__(self,rect, nickname):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'nicknamewindow'
        #self.rect = rect
        self.name = nickname
        self.nickname = globals.font2.render(self.name, True, (255,255,255))
        self.rect = self.nickname.get_rect()
        self.rect = self.rect.move(rect)
        globals.interface.add(self)
    def draw(self):
        #return
        globals.background.blit(self.nickname, self.rect)
    def set_nickname(self, nickname):
        self.name = nickname
        self.nickname = globals.font2.render(nickname, True, (255,255,255))
    def update(self):
        self.draw()

