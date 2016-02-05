#!/usr/bin/env python
#coding=utf-8
import pygame
from nested2d import Nested2d
import images
import global_access as ga
from vectorfunc import *

class RoadNet(object):
    def __init__(self, (x,y)):
        self.map = Nested2d(x,y, False)
        
    def set(self, (xi, yi)):
        self.map[xi][yi] = True
    
    def unset(self, (xi, yi)):
        self.map[xi][yi] = False
    
    def get_roads(self,(xi,yi)):
        return (
        self.map[xi]   [yi-1],
        self.map[xi+1] [yi],
        self.map[xi]   [yi+1],
        self.map[xi-1] [yi])
        
class Walker(pygame.sprite.Sprite):
    offset = (0,0)
    
    def __init__(self,pos):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = get_add(ga.stationGrid.get_bl(pos),self.offset)
        self.is_moving = True
        self.goal = None
        
    def _update(self):
        self.xi, self.yi = ga.stationGrid.get_bl(self.rect.topleft)
    
    def random_walk(self):
        if self.goal:
            self.move_towards(self.goal)
            
    def move_towards(self,goal):
        newpos = ga.stationGrid.get_bl(goal)
        vector = get_sub(newpos, self.rect.topleft)
        self.rect.topleft
        
        
class  RepairDrone(Walker):
    offset = (3,-2)
    def __init__(self,pos):
        self.image = images.repairdrone_01[0]
        Walker.__init__(self, pos)
    
    def update(self):
        if self.is_moving:
            self.random_walk()
            
        self._update()
        
def walk_api_mockup():
    if self.walk_random:
        if self.is_at_node:
            self.dir = self.get_dir(node)
            self.move_next
        else:
            self.move_next