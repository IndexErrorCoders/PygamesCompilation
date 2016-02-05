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
from path import FLY_PATH
import pygame
from pygame.locals import *
from ship import MyShip, SHIP
from turret import TURRET
from terrain import Terrain
from powerup import PowerUp
from explosion import ExplosionA, ExplosionB
from vector import Vector


class BattleField:
    def __init__(self, screen, sfx, rand):
        self.level = 1
        self.ship_type = 1 # 0, 1, 2
        self.screen = screen
        self.sfx = sfx
        self.terrain = Terrain()
        self.myship = MyShip(self.ship_type)
        self.enemy_list = []
        self.my_bullet_list = []
        self.enemy_bullet_list = []
        self.powerup_list = []
        self.explosion_list = []
        self.milage = RESOLUTION[1]
        self.rand = rand
        
        self.level_dat_path = LEVEL_PATH + '%02d.dat' % self.level
        self.level_dat = open(self.level_dat_path).readlines()
        self.next_pos = int(self.level_dat[0].split()[0])

        self.status = 'game'

        sfx.play_bgm()
        
        if DEBUG: print 'init : battlefield'


    def update(self):
        if self.milage == 3500:
            self.status = 'win'

        self.spawn_enemy()
        self.update_terrain()
        self.update_myship()
        self.update_my_bullet()
        self.update_enemy()
        self.update_enemy_bullet()
        self.update_powerup()
        self.update_explosion()

        # be cautious about the blit order
        # blit terrain
        self.screen.blit(self.terrain.img, self.terrain.pos)
        # blit shadow
        self.screen.blit(self.myship.shadow_img, self.myship.shadow_pos)
        for enemy in self.enemy_list:
            if enemy.id[:4] == 'ship':
                self.screen.blit(enemy.shadow_img, enemy.shadow_pos)
                if enemy.id[5] == 'c': # heli
                    self.screen.blit(enemy.blade.shadow_img,
                                     enemy.blade.shadow_pos)

        # blit enemy
        for enemy in self.enemy_list:
            self.screen.blit(enemy.img, enemy.pos)
            if enemy.id[:6] == 'ship_c': # is helicopter
                self.screen.blit(enemy.blade.img,
                                 enemy.blade.pos)
            elif enemy.id[:6] == 'turret': # is turret
                self.screen.blit(enemy.barrel.img,
                                 enemy.barrel.pos)

        self.screen.blit(self.myship.img, self.myship.pos)
        # blit bullet
        for bullet in self.my_bullet_list:
            self.screen.blit(bullet.img, bullet.pos)
        for bullet in self.enemy_bullet_list:
            self.screen.blit(bullet.img, bullet.pos)
        # blit explosion
        for explosion in self.explosion_list:
            self.screen.blit(explosion.img, explosion.pos  )
        # blit powerup
        for powerup in self.powerup_list:
            self.screen.blit(powerup.img, powerup.img_pos)
            self.screen.blit(powerup.orb.img, powerup.pos)


    def update_terrain(self):
        self.terrain.update()
        self.milage += TERRAIN_SPEED


    def update_myship(self):
        if self.myship.hp < 0:
            explosion = ExplosionB(self.myship.pos)
            self.explosion_list.append(explosion)
            for x in range(self.myship.fire_level - 1):
                powerup = PowerUp(self.myship.pos[:],
                                  'fire',
                                  self.rand.randint(\
                                  -POWERUP_SCATTER_RANGE_X,
                                  POWERUP_SCATTER_RANGE_X))
                self.powerup_list.append(powerup)
            self.myship.live -= 1
            self.myship.hp = self.myship.max_hp
            self.myship.pos = self.myship.init_pos[:]
            self.myship.fire_level = 1
            if self.myship.live <= 0:
                self.status = 'lose'

        self.myship.weapon_cooldown()
        key = pygame.key.get_pressed()
        if key[K_UP]:
            self.myship.move('UP')
        if key[K_DOWN]:
            self.myship.move('DOWN')
        if key[K_LEFT]:
            self.myship.move('LEFT')
        if key[K_RIGHT]:
            self.myship.move('RIGHT')
        if key[K_SPACE]:
            self.myship.fire(self.my_bullet_list)
        self.myship.update()


    def update_enemy(self):
        for enemy in self.enemy_list:
            enemy.update(self.myship.head_pos[:])
            if not enemy.alive:
                self.enemy_list.remove(enemy)
                # add sound and power ups
                if enemy.shot_dead:
                    explosion = ExplosionB(enemy.pos[:])
                    self.explosion_list.append(explosion)
                    self.sfx.play_explosion()
                    if not enemy.powerup == 'none':
                        powerup = PowerUp(enemy.pos[:],
                                          enemy.powerup,
                                          self.rand.randint(\
                                          -POWERUP_SCATTER_RANGE_X,
                                          POWERUP_SCATTER_RANGE_X))
                        self.powerup_list.append(powerup)
            else:
                enemy.fire(self.enemy_bullet_list, self.myship.head_pos[:])
                if self.check_collision(enemy, self.myship):
                    enemy.hp -= COLLISION_DAMAGE
                    self.myship.hp -= COLLISION_DAMAGE
                    if DEBUG: print 'myship hp : ', self.myship.hp


    def update_my_bullet(self):
        for bullet in self.my_bullet_list:
            bullet.update()
            for enemy in self.enemy_list:
                if self.check_collision(bullet, enemy):
                    bullet.alive = False
                    enemy.hp -= bullet.damage
                    explosion = ExplosionA(bullet.pos[:])
                    self.explosion_list.append(explosion)
                    break
            if bullet.alive == False:
                self.my_bullet_list.remove(bullet)


    def update_enemy_bullet(self):
        for bullet in self.enemy_bullet_list:
            bullet.update()
            if self.check_collision(bullet, self.myship):
                bullet.alive = False
                self.myship.hp -= bullet.damage
                explosion = ExplosionA(bullet.pos[:])
                self.explosion_list.append(explosion)
                if DEBUG: print 'myship hp : ', self.myship.hp
            if bullet.alive == False:
                self.enemy_bullet_list.remove(bullet)


    def spawn_enemy(self):
        if len(self.level_dat) != 0:
            if self.milage >= self.next_pos:
                line = self.level_dat[0].split()
                enemy_type = line[1]
                path = line[2]
                bullet = line[3]
                powerup = line[4]
                if enemy_type[:4] == 'ship':
                    enemy = SHIP[enemy_type](enemy_type,
                                             FLY_PATH[path],
                                             bullet,
                                             powerup)
                elif enemy_type[:6] == 'turret':
                    enemy = TURRET[enemy_type](enemy_type,
                                               [int(path[6:]), -50],
                                               bullet,
                                               powerup)
                if DEBUG: print 'spawn', enemy_type, path, bullet, powerup
                self.enemy_list.append(enemy)
                self.level_dat.pop(0)
                if len(self.level_dat) != 0:
                    self.next_pos = int(self.level_dat[0].split()[0])

    def update_powerup(self):
        for powerup in self.powerup_list:
            powerup.update()
            if not powerup.alive:
                self.powerup_list.remove(powerup)
            else:
                if self.check_collision(self.myship, powerup):
                    if powerup.powerup == 'fire':
                        self.myship.fire_level += 1
                    elif powerup.powerup == 'shield':
                        self.myship.hp += SHIELD_HP
                    self.powerup_list.remove(powerup)


    def update_explosion(self):
        for explosion in self.explosion_list:
            if not explosion.alive:
                self.explosion_list.remove(explosion)
            else:
                explosion.update()
                
    
    def check_collision(self, obj1, obj2):
        vector = Vector(obj1.center_pos[:], obj2.center_pos[:])
        distance = vector.normal
        if obj1.collide_radius + obj2.collide_radius >= distance:
            return True
        else:
            return False
