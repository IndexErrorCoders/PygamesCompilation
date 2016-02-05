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


from battlefield import BattleField
from const import *
from fps import FPS
import pygame
from pygame.locals import *
from sfx import Sfx
from random import Random

class PyForce:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(RESOLUTION)
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.sfx = Sfx()
        self.rand = Random()
        self.battlefield = BattleField(self.screen, self.sfx, self.rand)
        if FPS_ENABLED:
            self.fps = FPS(self.screen, self.clock)
        self.status = 'game'
        if DEBUG:
            print 'init : main'
            import sys
            print sys.version[:6]

    def run(self):
        while self.status != 'quit':
            # check quit
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.status = 'quit'
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.status = 'quit'

            # select status
            if self.status == 'intro':
                self.intro()
            elif self.status == 'game':
                self.game()
            elif self.status == 'win':
                img = pygame.image.load('res/img/end.png').convert()
                self.screen.blit(img, (0, 0))

            pygame.display.update()
            self.clock.tick(FPS_LIMIT)
        else:
            if DEBUG: print 'user prompt quit'
            

    def game(self):
        self.battlefield.update()
        if self.battlefield.status == 'win':
            self.status = 'win'
        if FPS_ENABLED:
            self.fps.update()
