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
from pygame.locals import *
import math
from const import *
from bullet import *
from vector import *


# ============== Class for Player Ship
class MyShip:
    def __init__(self, id):
        self.id = id
        self.img = pygame.image.load(IMG_PATH + 'my_ship_%d.png' % \
                                     self.id).convert_alpha()
        self.shadow_img = pygame.image.load(IMG_PATH + 'my_ship_%d_shadow.png'\
                                            % self.id).convert_alpha()
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos_limit = {'left'   : 0,
                          'right'  : RESOLUTION[0] - self.width,
                          'top'    : 0,
                          'bottom' : RESOLUTION[1] - self.height}
        self.pos = [(self.pos_limit['right'] - self.pos_limit['left']) / 2,
                    self.pos_limit['bottom']]
        self.init_pos = self.pos[:]
        self.shadow_pos = [self.pos[0] + SHADOW_OFFSET[0],
                           self.pos[1] + SHADOW_OFFSET[1]]
        self.head_pos = [self.pos[0] + self.width / 2, self.pos[1]]
        self.center_pos = [self.pos[0] + self.width / 2,
                           self.pos[1] + self.height / 2]
        self.collide_radius = MY_SHIP_COLLIDE_RADIUS
        if self.id == 0:
            self.speed = MY_SHIP_0_SPEED
            self.max_hp = MY_SHIP_0_HP
        elif self.id == 1:
            self.speed = MY_SHIP_1_SPEED
            self.max_hp = MY_SHIP_1_HP
        else:
            self.speed = MY_SHIP_2_SPEED
            self.max_hp = MY_SHIP_2_HP
        self.hp = self.max_hp
        self.cooldown = MY_SHIP_COOLDOWN
        self.weapon_cooldown_count = MY_SHIP_COOLDOWN
        self.live = MY_SHIP_LIVE
        self.bomb = INIT_BOMB_NUM
        self.fire_level = 1
        
        if DEBUG: print 'init : myship'

    def weapon_cooldown(self):
        if self.weapon_cooldown_count > 0:
            self.weapon_cooldown_count -= 1

    def move(self, direction):
        if direction == 'LEFT':
            if self.pos[0] > self.pos_limit['left']:
                self.pos[0] -= self.speed
        elif direction == 'RIGHT':
            if self.pos[0] < self.pos_limit['right']:
                self.pos[0] += self.speed
        elif direction == 'UP':
            if self.pos[1] > self.pos_limit['top']:
                self.pos[1] -= self.speed
        elif direction == 'DOWN':
            if self.pos[1] < self.pos_limit['bottom']:
                self.pos[1] += self.speed

    def update(self):
        self.head_pos = [self.pos[0] + self.width / 2, self.pos[1]]
        self.center_pos = [self.pos[0] + self.width / 2,
                           self.pos[1] + self.height / 2]
        self.shadow_pos = [self.pos[0] + SHADOW_OFFSET[0],
                           self.pos[1] + SHADOW_OFFSET[1]]

    def fire(self, my_bullet_list):
        if self.weapon_cooldown_count <= 0:
            if self.fire_level == 1:
                my_bullet_list.append(MY_BULLET[self.id]\
                                      ('none', self.head_pos))
            elif self.fire_level == 2:
                pos = [[self.head_pos[0] - 5, self.head_pos[1]],
                       [self.head_pos[0] + 5, self.head_pos[1]]]
                for x in range(2):
                    my_bullet_list.append(MY_BULLET[self.id]\
                                          ('none', pos[x]))
            elif self.fire_level == 3:
                pos = [[self.head_pos[0] - 10, self.head_pos[1]],
                       [self.head_pos[0], self.head_pos[1]],
                       [self.head_pos[0] + 10, self.head_pos[1]]]
                for x in range(3):
                    my_bullet_list.append(MY_BULLET[self.id]\
                                          ('none', pos[x]))
            else: # >= 4
                pos = [[self.head_pos[0] - 15, self.head_pos[1]],
                       [self.head_pos[0] - 5, self.head_pos[1]],
                       [self.head_pos[0] + 5, self.head_pos[1]],
                       [self.head_pos[0] + 15, self.head_pos[1]]]
                for x in range(4):
                    my_bullet_list.append(MY_BULLET[self.id]\
                                          ('none', pos[x]))
            self.weapon_cooldown_count = self.cooldown



# =================== Base Class for Enemy Ship
class ShipBase:
    def __init__(self,
                 id,
                 img_name,
                 shadow_img_name,
                 speed,
                 hp,
                 collide_radius,
                 cooldown,
                 cooldown_count,
                 path,
                 bullet_type,
                 powerup):
        self.id = id
        self.img = pygame.image.load(IMG_PATH + img_name).convert_alpha()
        self.shadow_img = pygame.image.load(IMG_PATH + shadow_img_name).\
                   convert_alpha()
        self.shadow_orig_img = self.shadow_img
        self.orig_img = self.img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.powerup = powerup
        self.bullet_type = bullet_type
        if self.bullet_type == 'bullet_c': # bullet_c is rapid fire
            self.bullet_number = BULLET_C_NUMBER
            self.bullet_cooldown = BULLET_C_COOLDOWN
            self.bullet_cooldown_count = self.bullet_cooldown
            self.bullet_count = 0
        self.shot_dead = False
        #===================
        self.center_pos = [path[0][:][0], path[0][:][1]]
        self.pos = [self.center_pos[0] - self.width / 2,
                    self.center_pos[1] - self.height / 2]
        self.head_pos = [self.center_pos[0], self.pos[1] + self.height / 2]
        self.shadow_pos = [self.pos[0] + SHADOW_OFFSET[0],
                           self.pos[1] + SHADOW_OFFSET[1]]
        #===================
        self.in_battle = False
        self.speed = speed
        self.hp = hp
        self.collide_radius = collide_radius
        self.cooldown = cooldown
        self.cooldown_count = cooldown_count
        self.alive = True
        self.path = path[1:]
        self.vector = Vector(self.center_pos, self.path[0])
        self.distance = self.vector.normal
        self.step = self.vector.unit
        self.x_inc = self.step[0] * self.speed
        self.y_inc = self.step[1] * self.speed
        self.inc = math.hypot(self.x_inc, self.y_inc)

    def update(self, my_ship_head_pos):
        if self.hp <= 0:
            self.alive = False
            self.shot_dead = True
            return
        
        if not self.outside_border():
            self.in_battle = True
        else:
            if self.in_battle:
                self.alive = False


        if len(self.path) != 0:
            if self.distance <= self.inc: # can reach next point in one step
                #===================
                self.center_pos = self.path[0]
                self.pos = [self.center_pos[0] - self.width / 2,
                            self.center_pos[1] - self.height / 2]
                self.head_pos = [self.center_pos[0],
                                 self.pos[1] + self.height / 2]
                self.shadow_pos = [self.pos[0] + SHADOW_OFFSET[0],
                                       self.pos[1] + SHADOW_OFFSET[1]]
                #===================
                self.path.pop(0)
                if len(self.path) != 0:
                    self.vector = Vector(self.center_pos, self.path[0])
                    self.distance = self.vector.normal
                    self.step = self.vector.unit
                    self.x_inc = self.step[0] * self.speed
                    self.y_inc = self.step[1] * self.speed
                    self.inc = math.hypot(self.x_inc, self.y_inc)
                    
            else: # can NOT reach next point in one step
                #===================
                self.center_pos[0] += self.x_inc
                self.center_pos[1] += self.y_inc
                self.pos = [self.center_pos[0] - self.width / 2,
                            self.center_pos[1] - self.height / 2]
                self.head_pos = [self.center_pos[0],
                                 self.pos[1] + self.height / 2]
                self.shadow_pos = [self.pos[0] + SHADOW_OFFSET[0],
                                   self.pos[1] + SHADOW_OFFSET[1]]
                #===================
                self.vector = Vector(self.center_pos, self.path[0])
                self.distance = self.vector.normal
                self.step = self.vector.unit
                self.x_inc = self.step[0] * self.speed
                self.y_inc = self.step[1] * self.speed
                self.inc = math.hypot(self.x_inc, self.y_inc)

    def fire(self, enemy_bullet_list, my_ship_head_pos):
        if self.cooldown_count > 0:
            self.cooldown_count -= 1
        else:
            if self.bullet_type in ('bullet_a', 'bullet_b'):
                fire_bullet(self.bullet_type,
                        enemy_bullet_list,
                        self.head_pos,
                        my_ship_head_pos)
                self.cooldown_count = self.cooldown
            else:
                if self.bullet_type == 'bullet_c':
                    if self.bullet_cooldown_count > 0:
                        self.bullet_cooldown_count -= 1
                    else:
                        fire_bullet(self.bullet_type,
                            enemy_bullet_list,
                            self.head_pos,
                            my_ship_head_pos)
                        self.bullet_cooldown_count = self.bullet_cooldown
                        self.bullet_count += 1
                        if self.bullet_count >= self.bullet_number:
                            self.bullet_count = 0
                            self.cooldown_count = self.cooldown
                            
                elif self.bullet_type == 'bullet_d':
                    for x in range(0, 12, 3):
                        fire_bullet(self.bullet_type,
                                    enemy_bullet_list,
                                    self.head_pos,
                                    vector = VECTOR[x])
                    self.cooldown_count = self.cooldown
                elif self.bullet_type == 'bullet_e':
                    for x in range(12):
                        fire_bullet(self.bullet_type,
                                    enemy_bullet_list,
                                    self.head_pos,
                                    vector = VECTOR[x])
                    self.cooldown_count = self.cooldown




        

    def outside_border(self):
        if self.pos[0] + self.width < 0 or \
            self.pos[0] > RESOLUTION[0] or \
            self.pos[1] + self.height < 0 or \
            self.pos[1] > RESOLUTION[1]:
            return True
        return False

#============== Enemy Ship A
class ShipA(ShipBase):
    def __init__(self,
                 id,
                 path,
                 bullet_type,
                 powerup,
                 img):
        ShipBase.__init__(self,
                          id,
                          img,
                          SHIP_A_SHADOW,
                          SHIP_A_SPEED,
                          SHIP_A_HP,
                          SHIP_A_COLLIDE_RADIUS,
                          SHIP_A_COOLDOWN,
                          SHIP_A_COOLDOWN_COUNT,
                          path,
                          bullet_type,
                          powerup)

    def update(self, my_ship_head_pos):
        ShipBase.update(self, my_ship_head_pos)
        #=================
        self.img = pygame.transform.rotate(self.orig_img, self.vector.degree)
        self.shadow_img = pygame.transform.rotate(self.shadow_orig_img,
                          self.vector.degree)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos = [self.center_pos[0] - self.width / 2,
                    self.center_pos[1] - self.height / 2]
        self.head_pos = [self.center_pos[0],
                         self.pos[1] + self.height / 2]



#================= Enemy Ship B
class ShipB(ShipBase):
    def __init__(self,
                 id,
                 path,
                 bullet_type,
                 powerup,
                 img):
        ShipBase.__init__(self,
                          id,
                          img,
                          SHIP_B_SHADOW,
                          SHIP_B_SPEED,
                          SHIP_B_HP,
                          SHIP_B_COLLIDE_RADIUS,
                          SHIP_B_COOLDOWN,
                          SHIP_B_COOLDOWN_COUNT,
                          path,
                          bullet_type,
                          powerup)

    def update(self, my_ship_head_pos):
        ShipBase.update(self, my_ship_head_pos)
        #=================
        self.img = pygame.transform.rotate(self.orig_img, self.vector.degree)
        self.shadow_img = pygame.transform.rotate(self.shadow_orig_img,
                                                  self.vector.degree)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos = [self.center_pos[0] - self.width / 2,
                    self.center_pos[1] - self.height / 2]
        self.head_pos = [self.center_pos[0],
                         self.pos[1] + self.height / 2]
                        


class Blade:
    def __init__(self, pos):
        self.pos = pos
        self.anim = [pygame.image.load(IMG_PATH + 'blade_%d.png' % x)\
                     .convert_alpha() for x in range(6)]
        self.shadow_anim = [pygame.image.load(IMG_PATH + \
                            'blade_shadow_%d.png' % x)\
                            .convert_alpha() for x in range(6)]
        self.index = 0
        self.img = self.anim[self.index]
        self.shadow_img = self.shadow_anim[self.index]
        self.shadow_pos = [self.pos[0] + SHADOW_OFFSET[0],
                           self.pos[1] + SHADOW_OFFSET[1]]
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.spin_speed = BLADE_SPIN_SPEED
        self.degree = 0

    def update(self, pos):
        self.pos = pos
        self.shadow_pos = [self.pos[0] + SHADOW_OFFSET[0],
                           self.pos[1] + SHADOW_OFFSET[1]]
        self.degree -= self.spin_speed
        self.degree %= 90
        if self.degree % 15 == 0:
            self.index += 1
            self.index %= 6
            self.img = self.anim[self.index]
            self.shadow_img = self.shadow_anim[self.index]


#================= ShipC
class ShipC(ShipBase):
    def __init__(self,
                 id,
                 path,
                 bullet_type,
                 powerup, 
                 img):
        ShipBase.__init__(self,
                          id,
                          img,
                          SHIP_C_SHADOW,
                          SHIP_C_SPEED,
                          SHIP_C_HP,
                          SHIP_C_COLLIDE_RADIUS,
                          SHIP_C_COOLDOWN,
                          SHIP_C_COOLDOWN_COUNT,
                          path,
                          bullet_type,
                          powerup)
        self.blade_pos = [self.center_pos[0] + BLADE_OFFSET[0],
                          self.center_pos[1] + BLADE_OFFSET[1]]
        self.blade = Blade(self.blade_pos)

    def update(self, my_ship_head_pos):
        ShipBase.update(self, my_ship_head_pos)
        #=================
        self.img = pygame.transform.rotate(self.orig_img, self.vector.degree)
        self.shadow_img = pygame.transform.rotate(self.shadow_orig_img,
                                                  self.vector.degree)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos = [self.center_pos[0] - self.width / 2,
                    self.center_pos[1] - self.height / 2]
        self.head_pos = [self.center_pos[0],
                         self.pos[1] + self.height / 2]
        self.blade_pos = [self.center_pos[0] + BLADE_OFFSET[0],
                          self.center_pos[1] + BLADE_OFFSET[1]]
        self.blade.update(self.blade_pos)


    


#====================

class ShipA1(ShipA):
    def __init__(self, id, path, bullet_type, powerup):
        ShipA.__init__(self, id, path, bullet_type, powerup, SHIP_A_1_IMG)

class ShipA2(ShipA):
    def __init__(self, id, path, bullet_type, powerup):
        ShipA.__init__(self, id, path, bullet_type, powerup, SHIP_A_2_IMG)

class ShipA3(ShipA):
    def __init__(self, id, path, bullet_type, powerup):
        ShipA.__init__(self, id, path, bullet_type, powerup, SHIP_A_3_IMG)

class ShipA4(ShipA):
    def __init__(self, id, path, bullet_type, powerup):
        ShipA.__init__(self, id, path, bullet_type, powerup, SHIP_A_4_IMG)

class ShipA5(ShipA):
    def __init__(self, id, path, bullet_type, powerup):
        ShipA.__init__(self, id, path, bullet_type, powerup, SHIP_A_5_IMG)

class ShipA6(ShipA):
    def __init__(self, id, path, bullet_type, powerup):
        ShipA.__init__(self, id, path, bullet_type, powerup, SHIP_A_6_IMG)


class ShipB1(ShipB):
    def __init__(self, id, path, bullet_type, powerup):
        ShipB.__init__(self, id, path, bullet_type, powerup, SHIP_B_1_IMG)

class ShipB2(ShipB):
    def __init__(self, id, path, bullet_type, powerup):
        ShipB.__init__(self, id, path, bullet_type, powerup, SHIP_B_2_IMG)

class ShipB3(ShipB):
    def __init__(self, id, path, bullet_type, powerup):
        ShipB.__init__(self, id, path, bullet_type, powerup, SHIP_B_3_IMG)

class ShipB4(ShipB):
    def __init__(self, id, path, bullet_type, powerup):
        ShipB.__init__(self, id, path, bullet_type, powerup, SHIP_B_4_IMG)

class ShipB5(ShipB):
    def __init__(self, id, path, bullet_type, powerup):
        ShipB.__init__(self, id, path, bullet_type, powerup, SHIP_B_5_IMG)

class ShipB6(ShipB):
    def __init__(self, id, path, bullet_type, powerup):
        ShipB.__init__(self, id, path, bullet_type, powerup, SHIP_B_6_IMG)


class ShipC1(ShipC):
    def __init__(self, id, path, bullet_type, powerup):
        ShipC.__init__(self, id, path, bullet_type, powerup, SHIP_C_1_IMG)

class ShipC2(ShipC):
    def __init__(self, id, path, bullet_type, powerup):
        ShipC.__init__(self, id, path, bullet_type, powerup, SHIP_C_2_IMG)

class ShipC3(ShipC):
    def __init__(self, id, path, bullet_type, powerup):
        ShipC.__init__(self, id, path, bullet_type, powerup, SHIP_C_3_IMG)

class ShipC4(ShipC):
    def __init__(self, id, path, bullet_type, powerup):
        ShipC.__init__(self, id, path, bullet_type, powerup, SHIP_C_4_IMG)

class ShipC5(ShipC):
    def __init__(self, id, path, bullet_type, powerup):
        ShipC.__init__(self, id, path, bullet_type, powerup, SHIP_C_5_IMG)

class ShipC6(ShipC):
    def __init__(self, id, path, bullet_type, powerup):
        ShipC.__init__(self, id, path, bullet_type, powerup, SHIP_C_6_IMG)


SHIP = {
    'ship_a_1': ShipA1,
    'ship_a_2': ShipA2,
    'ship_a_3': ShipA3,
    'ship_a_4': ShipA4,
    'ship_a_5': ShipA5,
    'ship_a_6': ShipA6,

    'ship_b_1': ShipB1,
    'ship_b_2': ShipB2,
    'ship_b_3': ShipB3,
    'ship_b_4': ShipB4,
    'ship_b_5': ShipB5,
    'ship_b_6': ShipB6,

    'ship_c_1': ShipC1,
    'ship_c_2': ShipC2,
    'ship_c_3': ShipC3,
    'ship_c_4': ShipC4,
    'ship_c_5': ShipC5,
    'ship_c_6': ShipC6
}