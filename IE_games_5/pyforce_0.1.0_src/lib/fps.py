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
from pygame import Color
from pygame.locals import *

class FPS:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.font_size = FPS_FONT_SIZE
        self.font = pygame.font.SysFont('Arial', self.font_size, bold = True)
        self.text = '%.2f' % self.clock.get_fps()
        self.img = self.font.render(self.text, 0, Color('white'))
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos = (0, RESOLUTION[1] - self.height)
        self.alpha = FPS_ALPHA
        self.cooldown = FPS_COOLDOWN
        self.cooldown_count = FPS_COOLDOWN
        if DEBUG: print 'init : fps'

    def update(self):
        if self.cooldown_count > 0:
            self.cooldown_count -= 1
        else:
            self.text = '%.2f' % self.clock.get_fps()
            self.img = self.font.render(self.text, 0, Color('white'))
            self.img.set_alpha(self.alpha, RLEACCEL)# <-------- blend option
            self.cooldown_count = self.cooldown
        self.screen.blit(self.img, self.pos)

        # ===========  debug ============
        a = pygame.mouse.get_pressed()
        if a[0]:
            print pygame.mouse.get_pos()