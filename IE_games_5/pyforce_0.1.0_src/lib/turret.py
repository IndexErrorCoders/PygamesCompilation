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
from bullet import fire_bullet
from vector import Vector
from const import *

class Barrel:
    def __init__(self,
                 center_pos,
                 img):
        self.orig_img = img
        self.img = img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.center_pos = center_pos
        self.pos = [self.center_pos[0] - self.width / 2,
                    self.center_pos[1] - self.height / 2]

    def update(self, center_pos, my_ship_head_pos):
        self.vector = Vector(center_pos, my_ship_head_pos)
        self.degree = self.vector.degree
        self.img = pygame.transform.rotate(self.orig_img, self.degree)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.center_pos = center_pos
        self.pos = [self.center_pos[0] - self.width / 2,
                    self.center_pos[1] - self.height / 2]


class Turret:
    def __init__(self,
                 id,
                 base_img,
                 barrel_img,
                 hp,
                 collide_radius,
                 cooldown,
                 cooldown_count,
                 pos,
                 bullet_type,
                 powerup):
        self.id = id
        self.pos = pos
        self.img = base_img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.hp = hp
        self.collide_radius = collide_radius
        self.cooldown = cooldown
        self.cooldown_count = cooldown_count
        self.head_pos = [self.pos[0] + self.width / 2,
                         self.pos[1] + self.height / 2]
        self.center_pos = self.head_pos
        self.barrel = Barrel(self.center_pos, barrel_img)
        self.bullet_type = bullet_type
        self.powerup = powerup
        self.alive = True

    def update(self, my_ship_head_pos):
        if self.hp <= 0:
            self.alive = False
            self.shot_dead = True
            return

        self.pos[1] += TERRAIN_SPEED
        self.head_pos = [self.pos[0] + self.width / 2,
                         self.pos[1] + self.height / 2]
        self.center_pos = self.head_pos
        self.barrel.update(self.center_pos, my_ship_head_pos)
        
        
    def fire(self, enemy_bullet_list, my_ship_head_pos):
        if self.cooldown_count > 0:
            self.cooldown_count -= 1
        else:
            fire_bullet(self.bullet_type,
                        enemy_bullet_list,
                        self.head_pos,
                        my_ship_head_pos)
            self.cooldown_count = self.cooldown


class TurretA(Turret):
    def __init__(self,
                 id,
                 pos,
                 bullet_type,
                 powerup):
        Turret.__init__(self,
                        id,
                        pygame.image.load(IMG_PATH + TURRET_A_BASE_IMG),
                        pygame.image.load(IMG_PATH + TURRET_A_BARREL_IMG),
                        TURRET_A_HP,
                        TURRET_A_COLLIDE_RADIUS,
                        TURRET_A_COOLDOWN,
                        TURRET_A_COOLDOWN_COUNT,
                        pos,
                        bullet_type,
                        powerup)

TURRET = {
    'turret_a': TurretA

}