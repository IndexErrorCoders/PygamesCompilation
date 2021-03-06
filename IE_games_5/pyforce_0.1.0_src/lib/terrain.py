#==========================================================================
#    PyForce 0.1.0
#    Copyright (C) 2010 Xueqiao Xu <xueqiaoxu@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==========================================================================


from const import *
import pygame

class Terrain:
    def __init__(self):
        self.img = pygame.image.load(IMG_PATH + TERRAIN_IMG).convert()
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos = [0, -(self.height - RESOLUTION[1])]
        self.speed = TERRAIN_SPEED
        if DEBUG: print 'init : terrain'

    def update(self):
        self.pos[1] += self.speed
        if self.pos[1] >= 0:
            self.pos[1] = -(self.height - RESOLUTION[1]) # scroll back