#!/usr/bin/env python
#coding=utf-8
import pygame
import pygame.sprite as sprite
import os, sys
import math, random

from pygame.locals import *
#-----------------------------------------------------
def load_image(name, colorkey=None):
    fullpath = os.path.join('data',name)
    try:
        loaded_image = pygame.image.load(fullpath)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = pygame.Surface(loaded_image.get_size(),HWSURFACE)
    colorkey = (0,0,0)
    image.fill(colorkey)
    image.blit(loaded_image,(0,0))
    image = image.convert()
    image.set_colorkey(colorkey,RLEACCEL)

    return image
    
#-----------------------------------------------------
def load_sound(name):
    class NoneSound:
        def play(self):pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data',name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound
    
#------------------------------------------------------
def scale_rect(rect,scale):
    rect.top *= scale
    rect.left *= scale
    rect.width *= scale
    rect.Heigh *= scale
    
class Counter(object):
    def __init__(self, max, add, init = 0):
        self.max = max
        self.add = add
        self.value = init
        
    def tick(self):
        if self.value < self.max:
            self.value += self.add
            
    def tick_sub(self):
        self.value -= 1
        
    def reset(self):
        self.value = self.value % self.max
        
    def topped(self):
        return self.value >= self.max