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
__author__="chubakur"
__date__ ="$17.03.2011 16:55:19$"
import pygame
import globals
class MessageWindow(pygame.sprite.Sprite):
    def __init__(self,message):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'informationwindow'
        self.image = pygame.Surface(globals.screen.get_size())
        self.image.fill((0,0,0))
        text = globals.font.render(message,True,(255,255,255))
        self.image.blit(text,(globals.screen.get_size()[0]/2 - text.get_size()[0]/2,globals.screen.get_size()[1]/2))
        globals.information_group.add(self)
    def draw(self):
        globals.background.blit(self.image,(0,0))
    def update(self):
        self.draw()