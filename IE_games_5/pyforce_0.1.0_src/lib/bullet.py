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
from vector import Vector

class MyBullet:
    def __init__(self,
                 bullet_level,
                 direction,
                 collide_radius,
                 center_offset,
                 damage,
                 ship_head_pos):
        self.bullet_level = bullet_level
        self.img = pygame.image.load(IMG_PATH + 'my_bullet_%d.png' % \
                                     self.bullet_level).convert_alpha()
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos = [ship_head_pos[0] - self.width / 2,
                    ship_head_pos[1] - self.height / 2]
        self.collide_radius = collide_radius
        self.center_offset = center_offset
        self.center_pos = [self.pos[0] + self.center_offset[0],
                           self.pos[1] + self.center_offset[1]]
        if direction == 'left':
            self.speed_x = -MY_BULLET_SPEED_X
        elif direction == 'right':
            self.speed_x = MY_BULLET_SPEED_X
        else:
            self.speed_x = 0
        self.speed_y = MY_BULLET_SPEED_Y
        self.alive = True
        self.damage = damage

    def update(self):
        self.pos[1] -= self.speed_y
        self.pos[0] += self.speed_x
        self.center_pos = [self.pos[0] + self.center_offset[0],
                           self.pos[1] + self.center_offset[1]]
        if self.pos[1] <= 0:
            self.alive = False


class MyBullet0(MyBullet):
    def __init__(self,
                 direction,
                 ship_head_pos):
        MyBullet.__init__(self,
                          0,
                          direction,
                          MY_BULLET_0_COLLIDE_RADIUS,
                          MY_BULLET_0_CENTER_OFFSET,
                          MY_BULLET_0_DAMAGE,
                          ship_head_pos)

class MyBullet1(MyBullet):
    def __init__(self,
                 direction,
                 ship_head_pos):
        MyBullet.__init__(self,
                          1,
                          direction,
                          MY_BULLET_1_COLLIDE_RADIUS,
                          MY_BULLET_1_CENTER_OFFSET,
                          MY_BULLET_1_DAMAGE,
                          ship_head_pos)

class MyBullet2(MyBullet):
    def __init__(self,
                 direction,
                 ship_head_pos):
        MyBullet.__init__(self,
                          2,
                          direction,
                          MY_BULLET_2_COLLIDE_RADIUS,
                          MY_BULLET_2_CENTER_OFFSET,
                          MY_BULLET_2_DAMAGE,
                          ship_head_pos)


MY_BULLET = [MyBullet0, MyBullet1, MyBullet2]


class AimBullet: # bullet moves to myship
    def __init__(self,
                 speed,
                 damage,
                 collide_radius,
                 center_offset,
                 enemy_ship_head_pos,
                 my_ship_pos,
                 anim):
        self.anim = anim
        self.frames = len(anim)
        self.frame = 0
        self.img = self.anim[self.frame]
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos = [enemy_ship_head_pos[0],
                    enemy_ship_head_pos[1]]
        self.center_offset = center_offset
        self.center_pos = [self.pos[0] + self.center_offset[0],
                           self.pos[1] + self.center_offset[1]]
        self.speed = speed
        self.damage = damage
        self.collide_radius = collide_radius
        self.alive = True
        self.cooldown = AIM_BULLET_COOLDOWN
        self.cooldown_count = self.cooldown
        self.vector = Vector(enemy_ship_head_pos, my_ship_pos)
        self.step = self.vector.unit
        self.x_inc = self.step[0] * self.speed
        self.y_inc = self.step[1] * self.speed
        if DEBUG: print '+ Aim Bullet'

    def update(self):
        if self.cooldown_count > 0:
            self.cooldown_count -= 1
        else:
            self.frame = (self.frame + 1) % self.frames
            self.img = self.anim[self.frame]
            self.cooldown_count = self.cooldown
        self.pos[0] += self.x_inc
        self.pos[1] += self.y_inc
        self.center_pos = [self.pos[0] + self.center_offset[0],
                           self.pos[1] + self.center_offset[1]]
        if self.outside_border():
            self.alive = False

    def outside_border(self):
        if self.pos[0] > RESOLUTION[0] or \
            self.pos[0] < -self.width or \
            self.pos[1] > RESOLUTION[1] or \
            self.pos[1] < -self.height:
            return True
        return False

class BulletA(AimBullet):
    def __init__(self,
                 enemy_ship_head_pos,
                 my_ship_pos):
        AimBullet.__init__(self,
                           BULLET_A_SPEED,
                           BULLET_A_DAMAGE,
                           BULLET_A_COLLIDE_RADIUS,
                           BULLET_A_CENTER_OFFSET,
                           enemy_ship_head_pos,
                           my_ship_pos,
                           [pygame.image.load(IMG_PATH + BULLET_A_1_IMG).\
                           convert_alpha(),
                           pygame.image.load(IMG_PATH + BULLET_A_2_IMG).\
                           convert_alpha()])

class BulletB(AimBullet):
    def __init__(self,
                 enemy_ship_head_pos,
                 my_ship_pos):
        AimBullet.__init__(self,
                            BULLET_B_SPEED,
                            BULLET_B_DAMAGE,
                            BULLET_B_COLLIDE_RADIUS,
                            BULLET_B_CENTER_OFFSET,
                            enemy_ship_head_pos,
                            my_ship_pos,
                            [pygame.image.load(IMG_PATH + BULLET_B_1_IMG).\
                            convert_alpha(),
                            pygame.image.load(IMG_PATH + BULLET_B_2_IMG).\
                            convert_alpha()])

                            
class BulletC(AimBullet):
    def __init__(self,
                 enemy_ship_head_pos,
                 my_ship_pos):
        AimBullet.__init__(self,
                            BULLET_C_SPEED,
                            BULLET_C_DAMAGE,
                            BULLET_C_COLLIDE_RADIUS,
                            BULLET_C_CENTER_OFFSET,
                            enemy_ship_head_pos,
                            my_ship_pos,
                            [pygame.image.load(IMG_PATH + BULLET_C_1_IMG).\
                            convert_alpha(),
                            pygame.image.load(IMG_PATH + BULLET_C_2_IMG).\
                            convert_alpha()])



class SimpleBullet: # bullet moves in a specified direction
                    # relative to the terrain
    def __init__(self,
                 speed,
                 damage,
                 collide_radius,
                 center_offset,
                 enemy_ship_head_pos,
                 vector,
                 anim):
        self.anim = anim
        self.frames = len(anim)
        self.frame = 0
        self.img = self.anim[self.frame]
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.pos = [enemy_ship_head_pos[0],
                    enemy_ship_head_pos[1]]
        self.center_offset = center_offset
        self.center_pos = [self.pos[0] + self.center_offset[0],
                           self.pos[1] + self.center_offset[1]]
        self.speed = speed
        self.damage = damage
        self.collide_radius = collide_radius
        self.alive = True
        self.cooldown = AIM_BULLET_COOLDOWN
        self.cooldown_count = self.cooldown
        self.vector = vector
        self.step = self.vector.unit
        self.x_inc = self.step[0] * self.speed
        self.y_inc = self.step[1] * self.speed + TERRAIN_SPEED # <---
        if DEBUG: print '+ Simple Bullet'

    def update(self):
        if self.cooldown_count > 0:
            self.cooldown_count -= 1
        else:
            self.frame = (self.frame + 1) % self.frames
            self.img = self.anim[self.frame]
            self.cooldown_count = self.cooldown
        self.pos[0] += self.x_inc
        self.pos[1] += self.y_inc
        self.center_pos = [self.pos[0] + self.center_offset[0],
                           self.pos[1] + self.center_offset[1]]
        if self.outside_border():
            self.alive = False

    def outside_border(self):
        if self.pos[0] > RESOLUTION[0] or \
            self.pos[0] < -self.width or \
            self.pos[1] > RESOLUTION[1] or \
            self.pos[1] < -self.height:
            return True
        return False

class BulletD(SimpleBullet):
    def __init__(self, enemy_ship_head_pos, vector):
        SimpleBullet.__init__(self,
                              BULLET_D_SPEED,
                              BULLET_D_DAMAGE,
                              BULLET_D_COLLIDE_RADIUS,
                              BULLET_D_CENTER_OFFSET,
                              enemy_ship_head_pos,
                              vector,
                              [pygame.image.load(IMG_PATH + BULLET_D_1_IMG)\
                               .convert_alpha(),
                               pygame.image.load(IMG_PATH + BULLET_D_2_IMG)\
                               .convert_alpha(),])


def fire_bullet(bullet_type,
                enemy_bullet_list,
                enemy_ship_head_pos,
                my_ship_head_pos = (0, 0),
                vector = Vector((0, 0), (0, 0))):
    if bullet_type == 'none':
        return
    elif bullet_type == 'bullet_a':
        bullet = BulletA(enemy_ship_head_pos, my_ship_head_pos)
        enemy_bullet_list.append(bullet)
    elif bullet_type == 'bullet_b':
        bullet = BulletB(enemy_ship_head_pos, my_ship_head_pos)
        enemy_bullet_list.append(bullet)
    elif bullet_type == 'bullet_c':
        bullet = BulletC(enemy_ship_head_pos, my_ship_head_pos)
        enemy_bullet_list.append(bullet)
    elif bullet_type == 'bullet_d':
        bullet = BulletD(enemy_ship_head_pos, vector)
        enemy_bullet_list.append(bullet)
    elif bullet_type == 'bullet_e':
        bullet = BulletD(enemy_ship_head_pos, vector)
        enemy_bullet_list.append(bullet)

