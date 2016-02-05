#!/usr/bin/env python
#coding=utf-8
import random
rnd = random.randint
import pygame

import images
import animation
import global_access as ga
from constants import *
from vectorfunc import *
from utils import Counter


class ShmupObject(pygame.sprite.Sprite):
    ''' class for free moving objects on the "shmup field" '''
    groups = ()
    offset = 0,0
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        
        self.rect = self.image.get_rect()
        tl = ga.shmupGrid.get_tl((-17,pos[1]))
        self.rect.topleft = get_add(tl,self.offset)
        self.floatpos = float(tl[0]),float(tl[1])
        
        self.layer = self.rect.bottom/TY
        self.layerGroup = self.groups[0]
        self.layerGroup.add(self,layer = self.layer)
        self.entering = True
        self.target = pos
        self.isopos = pos
        
        
    def _update(self):
        
        self.isopos = get_sub(self.rect.topleft,self.offset)
        new_layer = self.rect.bottom/TY
        if new_layer != self.layer:
            self.layer = new_layer
            self.layerGroup.change_layer(self, new_layer)
        if self.target == self.isopos:
            self.target = None
        if self.target:
            self.move_towards3(ga.shmupGrid.get_tl(self.target),self.speed)
    
    def move_towards(self, pos, speed):
        target = get_add(pos, self.offset)
        fullmove = get_sub(target, self.rect.topleft)
        if speed >= get_len(fullmove):
            self.rect.topleft = target
        else:
            dir = normalize(fullmove)
            x,y = get_mul(dir,speed)
            self.rect.move_ip(round(x),round(y))
    
    def move_towards2(self, pos, speed):
        full_move = get_sub(pos, self.rect.center)
        full_len = get_len(full_move)
        dir = normalize(full_move)
        xn,yn = get_mul(dir, speed)
        len = get_len((xn,yn/2.0))
        xiso,yiso = get_mul(dir,len)
        if len > full_len:
            self.rect.center = pos
        else:
            self.rect.move_ip(round(xiso), round(yiso))
        
    def move_towards3(self, pos, speed):
        full_move = get_sub(pos, self.rect.topleft)
        full_len = get_len(full_move)
        dir = normalize(full_move)
        xn,yn = get_mul(dir, speed)
        len = get_len((xn,yn/2.0))
        move = get_mul(dir,len)
        if len > full_len:
            self.floatpos = pos
        else:
            self.floatpos = add(self.floatpos,move)
        self.rect.topleft = round(self.floatpos[0]),round(self.floatpos[1])
    
        
    def new_path(self, pos, speed):
        
        fx,fy = get_sub(pos, self.rect.center)
        full_len = get_len((fx,fy))
        parts = full_len//self.speed
        self.moves = [(fx/n,fy/n) for n in range(parts)]
            
            
    def hit(self, projectile):
        self.life -= projectile.get_damage()
        
        
        
        
    
    
class PlayerShip(ShmupObject):
    groups = None
    offset = (10,10)
    def __init__(self, pos, size):
        self.image = images.player_ship
        ShmupObject.__init__(self, pos)
        self.rect = pygame.Rect((0,0), self.image.get_size())
        self.rect.center = pos
        
        self.speed = 12
        self.fire_delay = Counter(10, 4, 0)
        self.is_firing = False
        self.firebuffer = 5
        self.firebuffer_count = 5
        self.reload_delay = Counter(40, 1, 0)
        
    def update(self):
        xiso, yiso = ga.shmup_iso
        self.firebuffer += 0.1
        self.move_towards2(ga.shmupGrid.get_tl((PS_ROW,yiso)), self.speed)
        

        if self.is_firing:
            if self.fire_delay.topped() and self.firebuffer_count:
                self.fire()
                self.fire_delay.reset()
                self.delay_count = 0
                self.firebuffer_count -= 1
            else:
                self.fire_delay.tick()
            
            if not self.reload_delay.topped():
                self.reload_delay.tick()
            if self.reload_delay.topped():
                self.reload_delay.reset()
                self.firebuffer_count = 5
            
            
        
    def fire(self):
        RapidEM(self.rect.topleft, normalize((-2,-1)))
    
    
    
class Projectile(pygame.sprite.Sprite):
    speed = 0
    
    def __init__(self, pos, dir):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.floatpos = float(pos[0]),float(pos[1])
        self.pos = pos
        self.dir = dir
        self.rect.topleft = pos
        self.hit = False
        
    def _update(self):
        self.oldpos = self.rect.topleft
        #self.rect.move_ip(*get_mul(self.dir, self.speed))
        move = get_mul(self.dir, self.speed)
        self.floatpos = add(self.floatpos,move)
        self.rect.topleft = self.floatpos
        self.newpos = self.rect.topleft
        
    def check_outside(self):
        if self.rect.colliderect(pygame.Rect((0,0),SCREENSIZE)):
            return False
        else:
            return True
    
class DefaultBeam(Projectile):
    speed = 10
    def __init__(self, pos, dir):
        self.image = images.beam01
        self.end_anim = images.beam01_end
        self.rect = self.image.get_rect()
        Projectile.__init__(self, pos, dir)
    
    def update(self):
        self._update()
        if self.hit or self.check_outside():
            self.kill()
            
        for s in ga.shmupObjects.sprites():
            if isinstance(s,ShmupObject) and not isinstance(s,PlayerShip):
                if intersect(self.oldpos, self.newpos, *s.col):
                    self.hit = True
                    s.kill()
                    Explosion(s.rect.topleft)
                    DyingAnim(self.rect.topleft, self.end_anim, 60)
                    

        
class RapidEM(Projectile):
    speed = 10
    def __init__(self,pos, dir):
        self.images = images.beam02
        self.animation = animation.Animation(self.images,60)
        self.image = self.images[0]
        self.rect = self.images[0].get_rect()
        Projectile.__init__(self, pos, dir)
        
    def update(self):
        self._update()
        self.image = self.animation.get()
        if self.hit or self.check_outside():
            self.kill()
            
        for s in ga.shmupObjects.sprites():
            if isinstance(s,ShmupObject) and not isinstance(s,PlayerShip):
                if intersect(self.oldpos, self.newpos, *s.col):
                    self.hit = True
                    s.kill()
                    Explosion(s.rect.topleft)
                    
        
    
class LaserDrone(ShmupObject):
    offset = -4,-2
    a= 27,10
    b= 18,14 # endpoints of the front collision line
    lcolor = (255,200,100)
    enterspeed = 9
    speed = 9
    
    def __init__(self,pos):
        self.image = images.ship_05
        ShmupObject.__init__(self,pos)
        self.actionqueue = []
        self.col =(add(self.a,self.rect.topleft),add(self.b,self.rect.topleft))
        self.energy = 3
        self.cooldown = 5
        self.recharge = 1.0/20
        self.do_fire = False
        
    def update(self):
        self._update()
        if self.isopos == self.target:
            target = None
        self.col =(add(self.a,self.rect.topleft),add(self.b,self.rect.topleft))
        ga.lm.reg(self.col,self.lcolor)
        
        if not rnd(0,20):
            self.fire()
        
        if len(self.actionqueue):
            action = self.actionqueue.pop(0)
            action(self)
        
    def new_actions(self):
        actionqueue.append(rnd(0,1))
        
    def fire(self):
        DefaultBeam(self.rect.bottomright, normalize((2,1)))
    
        
class AttackerManager(object):
    def __init__(self):
        self.register = {}
        
    def reg_unit(self,time, cls, args):
        if self.register.get(time):
            self.register[time] = self.register[time] + ((cls,args),)
        else:
            self.register[time] = ((cls,args),)
        
    def update(self, time):
        units = self.register.get(time)
        if units:
            for i in units:
                i[0](*i[1]) # is[0] is class, i[1] is args
            
class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.animation = animation.Animation(images.explosion_01, 60)
        self.rect = self.animation.get_rect()
        self.rect.topleft = pos
        self.image = self.animation.images[0]
        
    def update(self):
        self.image = self.animation.get()
        if self.animation.has_finished():
            self.kill()

class DyingAnim(pygame.sprite.Sprite):
    def __init__(self, pos, imgs, speed):
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.animation = animation.Animation(imgs, speed)
        self.rect = self.animation.get_rect()
        self.rect.topleft = pos
        self.image = self.animation.images[0]
        
    def update(self):
        self.image = self.animation.get()
        if self.animation.has_finished():
            self.kill()
