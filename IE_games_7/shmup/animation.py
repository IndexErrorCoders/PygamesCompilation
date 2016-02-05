#!/usr/bin/env python
#coding=utf-8
# animation
import pygame
from pygame.locals import *
import utils
import images


class Animation(object):
    def __init__(self, images, speed):
        self.images = images
        self.amount = len(images)
        self.speed = speed
        self.framev = 60/float(speed)
        self.count = 0
        
    def start(self,frame = 0):
        self.count = int(frame*self.framev)
        return self
    
    def has_finished(self):
        if self.count > self.framev*self.amount:
            return True
        else:
            return False
    
    def get(self):
        v = self.count//self.framev
        self.frame = int(v % self.amount)
        self.count += 1
        return self.images[self.frame]
    
    def get_rect(self):
        return self.images[0].get_rect()
        
    
    
class Animation1(object):
    def __init__(self, img_list, speed, loop_point = None):
        self.images = img_list
        self.frames = len(img_list)
        self.count = 0
        self.speed = speed
        self.loop_point = loop_point
        self.current_frame = 0
        
    def get(self):
        self.count += 1
        return self.images[int(self.count/self.speed%self.frames)]

        
class Animation2(object):
    def __init__(self, images, speed, mode = 1, loopfrom = 0):
        self.speed = speed
        self.framev = 30/float(speed)
        self.mode = mode # 0 =fwd, 1 =fwd/bwd, 2 =fwd_loopfrom, 3 =fwd/bwd_loopfrom
        self.forward = True
        self.images = images
        self.len = len(images)
        self.loopfrom = loopfrom
        self.at_frame = 0
        self.current = self.images[0]
        
    def get(self, count):
        if count/self.framev > self.at_frame:
            self.current = self.get_next()
            return self.current
        else:
            return self.current
            
    def get_next(self):
        if self.mode == 0:
            self.at_frame = (self.at_frame +1)%self.len
            return self.images[self.at_frame]
        elif self.mode == 1:
            self.at_frame = (self.at_frame +1)%(self.len*2)
            return self.images[self.at_frame-(self.at_frame%self.len)]
        elif self.mode == 2:
            self.at_frame
        
        
        
def test():
    game = gamebase.GameBase((400,400),30)
    count = 0
    img = utils.load_image("explosion_01.png")
    imgs = images.cut_sheet(img,(26,26))
    anim = Animation(imgs, 2)
    anim2 = Animation(imgs, 4)
    while True:
        game.clock.tick(60)
        events = game.get_events()
        game.screen.blit(anim.get(),(0,0))
        game.screen.blit(anim2.get(),(30,0))
        if anim2.has_finished():
            anim.start(2)
        pygame.display.flip()
        game.screen.fill((0,0,0))
        count += 1
if __name__ == "__main__":
    test()