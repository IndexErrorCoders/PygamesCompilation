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

class Orb:
    def __init__(self, pos):
        self.pos = pos
        self.anim = [pygame.image.load(IMG_PATH + 'orb_%d.png' % x)\
                     .convert_alpha() for x in range(18)]
        self.index = 0
        self.img = self.anim[self.index]
        self.width = self.img.get_width() # may in const later
        self.height = self.img.get_height()
        self.spin_speed = ORB_SPIN_SPEED
        self.degree = 0
        
        
    def update(self, pos):
        self.pos = pos
        self.degree -= self.spin_speed
        self.degree %= 180
        if self.degree % 10 == 0:
            self.index += 1
            self.index %= 18
            self.img = self.anim[self.index]


class PowerUp:
    def __init__(self, pos, powerup, range_x):
        self.orb = Orb(pos)
        self.pos = pos
        self.powerup = powerup
        if self.powerup == 'fire':
            self.img = pygame.image.load(IMG_PATH + FIRE_UP).convert_alpha()
            self.img_pos = [self.pos[0] + FIRE_UP_OFFSET[0],
                            self.pos[1] + FIRE_UP_OFFSET[1]]
        elif self.powerup == 'shield':
            self.img = pygame.image.load(IMG_PATH + SHIELD).convert_alpha()
            self.img_pos = [self.pos[0] + FIRE_UP_OFFSET[0],
                            self.pos[1] + FIRE_UP_OFFSET[1]]
        self.width = self.orb.width
        self.height = self.orb.height

        self.center_pos = [self.pos[0] + self.width / 2,
                           self.pos[1] + self.height / 2]

        self.alive = True
        self.speed = POWERUP_SPEED
        # scatter
        self.scatter_speed_y = POWERUP_SCATTER_SPEED_Y
        self.scatter_range_y = POWERUP_SCATTER_RANGE_Y
        self.scatter_range_x = range_x
        self.scatter_speed_x = float(self.scatter_range_x) / \
                               (float(self.scatter_range_y) / \
                               self.scatter_speed_y)
        self.scatter_count = 0
        self.scatter = True
        # offset
        self.offset_speed = POWERUP_OFFSET_SPEED
        self.offset_range = POWERUP_OFFSET_RANGE
        self.offset_count = 0
        self.direction = 0
        self.collide_radius = POWERUP_COLLIDE_RADIUS

    def update(self):
        if self.outside_border():
            self.alive = False
            return

        if self.scatter:
            self.pos[0] += self.scatter_speed_x
            self.pos[1] -= self.scatter_speed_y
            self.scatter_count += self.scatter_speed_y
            if self.scatter_count >= self.scatter_range_y:
                self.scatter = False
        else:
            if self.direction == 0:
                self.pos[0] -= self.offset_speed
            elif self.direction == 1:
                self.pos[1] -= self.offset_speed
            elif self.direction == 2:
                self.pos[0] += self.offset_speed
            else:
                self.pos[1] += self.offset_speed

            self.offset_count += self.offset_speed
            if self.offset_count >= self.offset_range:
                self.offset_count = 0
                self.direction = (self.direction + 1) % 4
                
            self.pos[1] += self.speed
            
        self.center_pos = [self.pos[0] + self.width / 2,
                           self.pos[1] + self.height / 2]
        self.img_pos = [self.pos[0] + FIRE_UP_OFFSET[0],
                        self.pos[1] + FIRE_UP_OFFSET[1]]
            
        self.orb.update(self.pos)

    def outside_border(self):
        if self.pos[0] > RESOLUTION[0] or \
            self.pos[0] < -self.width or \
            self.pos[1] > RESOLUTION[1] or \
            self.pos[1] < -self.height:
            return True
        return False