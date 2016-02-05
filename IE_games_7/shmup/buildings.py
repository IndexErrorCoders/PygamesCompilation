#!/usr/bin/env python
#coding=utf-8
import random
import pygame

import images
import roadlib
import shmupobjects
from vectorfunc import *
from constants import *
from isospace import IsoGrid
import global_access as ga

def make_indexes((x,y), (xsize,ysize)): # returns a list of indexes from topindex and size
        return [[x+nx, y + ny] for nx in range(xsize) for ny in range(ysize)]

def standard_check_free(pos,bc): # Building Class
    indexes = make_indexes(pos, bc.size)
    for (x,y) in indexes:
        if 0 <= x < ga.station.free_tiles.x_len and 0 <= y < ga.station.free_tiles.y_len:
            if isinstance(ga.station.buildings[x][y],Road):
                return False            
            if ga.station.free_tiles[x][y]:
                continue
            else:
                return False
        else:
            return False
    return True
    
def cannon_check_free((x,y),cc):
    print x,y
    if x == -1:
        if 0 <= x+1 < ga.station.free_tiles.x_len and 0 <= y < ga.station.free_tiles.y_len:
            if ga.station.free_tiles[x+1][y]:
                return True
    return False
        
    
    
class Building(pygame.sprite.Sprite):
    anchor = 0,0 # standard anchor point is top tile
    check_free = (standard_check_free,)
    
    def __init__(self, pos):
        self.top_index = pos[0] - self.anchor[0], pos[1] - self.anchor[1]
        indexes = make_indexes(self.top_index, self.size)
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.xlen, self.ylen = self.size
        
        self.make_geometry()
        self.sprites = []
        x,y = ga.stationGrid.get_tl(self.top_index)
        self.ig = IsoGrid((TX,TY),
            (ga.stationGrid.get_mt(self.top_index)))
            
        self.mark_tiles(indexes)
        self.make_sidetiles()
        BuildingPiece(self.imageset[0], self.ig.get_bl((self.xlen-1, self.ylen-1)),self)
        for n in range(self.xlen-1):
            l, b = self.ig.get_bl((n, self.ylen-1))
            BuildingPiece(self.imageset[n+1], (l,b),self)
        for n in range(self.ylen-1):
            l, b = self.ig.get_mb((self.xlen-1,n))
            BuildingPiece(self.imageset[n+self.xlen], (l-1, b),self)
            
    def mark_tiles(self,indexes):
        for x,y in indexes:
            ga.station.free_tiles[x][y] = False
            ga.station.buildings[x][y] = self
        
    
    def get_piecepos(self, x,y):
        xpos = self.rect.left + self.topx + x * TX - y * TX
        ypos = self.rect.top + x * TY + y * TY
        return xpos, ypos + TH
        
    def make_geometry(self):
        w = (self.xlen + self.ylen) * TX
        h = (self.xlen + self.ylen) * TY
        left, top = ga.stationGrid.get_tl(self.top_index)
        self.topx = (self.ylen-1)*TX
        left = left - self.topx
        self.rect = pygame.Rect((left,top),(w,h))
        
    def make_sidetiles(self):
        self.sidetiles = []
        xi, yi = self.top_index
        self.sidetiles.extend((xi +x, yi -1) for x in range(self.xlen))
        self.sidetiles.extend((xi + self.xlen, yi + y) for y in range(self.ylen))
        self.sidetiles.extend((xi +x, yi + self.ylen) for x in range(self.xlen))
        self.sidetiles.extend((xi -1, yi + y) for y in range(self.ylen))
        
    def destroy(self):
        for s in self.sprites:
            s.kill()
        for x,y in make_indexes(self.top_index, self.size):
            ga.station.free_tiles[x][y] = True
            ga.station.buildings[x][y] = None
        self.kill()
    
    def get_roadentry(self):
        for i in self.sidetiles:
            b = ga.station.buildings[i[0]][i[1]]
            if isinstance(b, Road):
                return i
            
class BuildingPiece(pygame.sprite.Sprite):
    def __init__(self, image,pos,parent = None):
        self.layer = pos[1]/TY
        pygame.sprite.Sprite.__init__(self)
        self.groups[0].add(self,layer = self.layer)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        if parent:
            parent.sprites.append(self)
        
class Barrack(Building):
    size = 2,2
    def __init__(self, pos):
        Building.__init__(self, pos)

class Barrier(Building):
    size = 1,1
    def __init__(self, pos):
        Building.__init__(self, pos)
        
class Barrier2(Building):
    size = 2,1
    anchor = 1,0
    def __init__(self, pos):
        Building.__init__(self, pos)
        

class PowerGen(Building):
    size = 2,2
    def __init__(self, pos):
        Building.__init__(self, pos)
    
    def update(self):
        pass
            
class CommandCenter(Building):
    size = 3,3
    def __init__(self, pos):
        Building.__init__(self, pos)
        
    def update(self):
        self.road_entry = self.get_roadentry()
        self.release_repairdrone()
        
    def release_repairdrone(self):
        if not random.randint(0,30) and self.road_entry:
            roadlib.RepairDrone(self.road_entry)
            
class Cannon(Building):
    size = 2,1
    anchor = 1,0
    check_free = (cannon_check_free,)
    def __init__(self, pos):
        Building.__init__(self, pos)
        self.firepos = get_add(self.rect.topleft,(0,-2))
        self.firemark = ga.count
        self.firerate = 20
        
    def update(self):
        
        if ga.count == self.firemark + self.firerate:
            self.firemark = ga.count
            self.fire()
            
    def fire(self):
        shmupobjects.DefaultBeam(self.firepos, normalize((-2,-1)))
        
    def mark_tiles(self, indexes):
        x,y = self.top_index
        ga.station.free_tiles[x+1][y] = False
        ga.station.buildings[x+1][y] = self        

class Road(Building):
    size = 1,1
    def __init__(self,pos):
        Building.__init__(self, pos)
        
    def mark_tiles(self,indexes):
        for x,y in indexes:
            ga.station.buildings[x][y] = self        

class Destroy(Road):
    pass
