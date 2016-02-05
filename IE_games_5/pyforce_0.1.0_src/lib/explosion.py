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


import pygame
from const import *

class Explosion:
    def __init__(self, pos, anim):
        self.pos = pos
        self.anim = anim
        self.frames = len(self.anim)
        self.index = 0
        self.img = self.anim[self.index]
        self.cooldown = EXPLOSION_COOLDOWN
        self.cooldown_count = self.cooldown
        self.alive = True

    def update(self):
        self.cooldown_count -= 1
        if self.cooldown_count <= 0:
            self.index += 1
            if self.index >= self.frames:
                self.alive = False
                return
            self.img = self.anim[self.index]
            self.cooldown_count = self.cooldown


class ExplosionA(Explosion):
    def __init__(self, pos):
        Explosion.__init__(self,
                           pos,
                           [pygame.image.load(IMG_PATH + \
                           'explosion_%d.png' % x)\
                           .convert_alpha() for x in range(16)])

class ExplosionB(Explosion):
    def __init__(self, pos):
        Explosion.__init__(self,
                           pos,
                           [pygame.image.load(IMG_PATH + \
                           'explosion_big_%d.png' % x)\
                           .convert_alpha() for x in range(16)])