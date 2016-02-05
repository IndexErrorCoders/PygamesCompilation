#!/usr/bin/env python
#coding=utf-8
# gui
import pygame
import images
import global_access as ga

class Button(pygame.sprite.Sprite):
    def init(self,pos):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
    def update(self, pos):
        if self.rect.collidepoint(pos):
            self.report()
        
class BuildingButton(Button):
    def __init__(self, pos, adjust, bclass, image):
        self.bclass = bclass
        self.image = images.button01.copy()
        self.image.blit(image, adjust)
        self.init(pos)
        
    def report(self):
        ga.station.load_build(self.bclass)
        ga.isoCursor.load_hint(self.bclass)
        
    def add_img(self, image, adjust):
        self.image.blit(image, adjust)