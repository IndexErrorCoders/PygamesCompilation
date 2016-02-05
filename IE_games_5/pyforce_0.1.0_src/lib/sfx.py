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

class Sfx:
    def __init__(self, ):
        self.bgm = pygame.mixer.Sound(SFX_PATH + BGM)
        self.explosion = pygame.mixer.Sound(SFX_PATH + EXPLOSION)

    def play_bgm(self):
        self.bgm.play(-1)

    def play_explosion(self):
        self.explosion.play()