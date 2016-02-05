#!/usr/bin/env python
#coding=utf-8
import pygame
from nested2d import Nested2d

def from_nested2d(n2d, offset, pos):
    isoSpace = IsoSpace((n2d.xlen, n2d.ylen), offset, pos)
    for i in n2d.loop_all():
        i,x,y = i
        isoSpace.array[x][y] = i

class IsoSpace(object):
    def __init__(self, (x,y), (cellw,cellh), (xoffset, yoffset), pos):
        self.xlen = x
        self.ylen = y
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.cell_width = cellw
        self.cell_height = cellh
        
        self.top_point = (self.ylen-1)* self.xoffset
        w = self.xlen * self.xoffset + self.ylen * self.xoffset -2
        h = self.xlen * self.yoffset + self.ylen * self.yoffset
        self.rect = pygame.Rect(pos, (w,h)) # bounding rect for the area
        
        if self.xlen%2:
            self.yfix = self.xoffset
        else:
            self.yfix = 0
        if self.ylen%2:
            self.xfix = self.xoffset
        else:
            self.xfix = 0
            
        
        self.array = Nested2d(self.xlen, self.ylen, None)
        
    def fill(self, v):
        for x,c in enumerate(self.array):
            for y, i in enumerate(c):
                self.array[x][y] = v
    
    def fill_callable(self, callable, *args):
        for x,c in enumerate(self.array):
            for y, i in enumerate(c):
                self.array[x][y] = callable(*args)
    
        
        
    def get_iso(self, pos):

            x,y = pos[0] - self.rect.left, pos[1] - self.rect.top
            xiso = (x+2*y)/ (self.xoffset*2) - self.ylen/2
            yiso = (self.rect.width-x+2*y)/ (self.xoffset*2) -self.xlen/2            

            return self.array[xiso][yiso]
    
    def get_iso_pos(self, pos):
        x,y = pos[0] - self.rect.left, pos[1] - self.rect.top
        xiso = (x+2*y-self.xfix+2)/ (self.xoffset*2) - self.ylen/2
        yiso = (self.rect.width-x-self.yfix+2*y+1)/ (self.xoffset*2) - self.xlen/2
            
        return xiso, yiso

    
    def get_pos(self,(x,y),center = False, cropped = False):
        if cropped:
            x = max(min(x,self.xlen-1), 0)
            y = max(min(y,self.ylen-1), 0)
        xpos = self.rect.left + self.top_point + x * self.xoffset - y * self.xoffset
        ypos = self.rect.top + x * self.yoffset + y * self.yoffset
        return xpos, ypos
    
    def get_center(self,(x,y)):
        xpos = self.rect.left + self.top_point + x * self.xoffset - y * self.xoffset + self.xoffset-2
        ypos = self.rect.top + x * self.yoffset + y * self.yoffset + self.yoffset-1
        return xpos, ypos
    
    def get_snap(self,pos):
         return self.get_pos(self.get_iso_pos(pos))
    
    def get_snap_center(self,pos):
         return self.get_center(self.get_iso_pos(pos))
    
    def get_rect(self):
        return self.rect
    
class IsoGrid(object):
    def __init__(self, (x,y), (xoffs, yoffs), tl = (0,0)):
        self.xlen = x
        self.ylen = y
        self.xoffset = xoffs
        self.yoffset = yoffs
        self.rect = pygame.Rect(tl, ((x+y)*xoffs,(x+y)*yoffs))
        self.topx = (self.ylen-1)* self.xoffset
        
        if self.xlen%2:
            self.yfix = self.xoffset
        else:
            self.yfix = 0
        if self.ylen%2:
            self.xfix = self.xoffset
        else:
            self.xfix = 0
        

        
    def part_rect(self, (x,y),w):
        xpos = self.rect.left + self.topx + x * self.xoffset - y * self.xoffset
        ypos = self.rect.top + x * self.yoffset + y * self.yoffset
        rect = pygame.Rect((xpos,0),(w,self.rect.height))
        return rect
    
    def get_iso(self, pos):
        x,y = pos[0] - self.rect.left, pos[1] - self.rect.top
        xiso = (x+2*y-self.xfix+2)/ (self.xoffset*2) - self.ylen/2
        yiso = (self.rect.width-x-self.yfix+2*y-1)/ (self.xoffset*2) - self.xlen/2
            
        return xiso, yiso
        
    
    
    def get_tl(self, (x,y)):
        xpos = self.rect.left + self.topx + x * self.xoffset - y * self.xoffset
        ypos = self.rect.top + x * self.yoffset + y * self.yoffset        
        return xpos, ypos
    
    def get_bl(self, (x,y)):
        xpos,ypos = self.get_tl((x,y))
        return xpos, ypos + self.yoffset*2
    
    def get_tr(self, pos):
        xpos,ypos = self.get_tl(pos)
        return xpos + self.xoffset*2, ypos + self.yoffset*2
        
    def get_mb(self, (x,y)):
        xpos,ypos = self.get_tl((x,y))
        return xpos + self.xoffset , ypos + self.yoffset*2
    
    def get_mt(self,(x,y)):
        xpos,ypos = self.get_tl((x,y))
        return xpos + self.xoffset, ypos
    
    def get_snap(self,pos):
         return self.get_tl(self.get_iso(pos))




class IsoGrid(object):
    def __init__(self, (xoffs, yoffs), top_pos):
        self.xoffset = xoffs
        self.yoffset = yoffs
        self.xhw = xoffs -1 # x half width, because offset is not even with width
        self.xtop, self.ytop = top_pos
            
    def align_top(self,pos):
        self.xtop, self.ytop = pos
    
    def get_iso(self, pos):
        x,y = pos[0] - self.xtop, pos[1] - self.ytop
        xiso = (x+2*y+1)/ (self.xoffset*2)
        yiso = (-x+2*y)/ (self.xoffset*2)
        return xiso, yiso
    
    # Following get methods gets coordinates for specified tiles
    def get_left(self,(x,y)):
        return self.xtop + x * self.xoffset - y * self.xoffset - self.xhw
    def get_right(self,(x,y)):
        return self.xtop + x * self.xoffset - y * self.xoffset + self.xhw
    def get_top(self,(x,y)):
        return self.ytop + x * self.yoffset + y * self.yoffset
    def get_bottom(self,(x,y)):
        return self.ytop + x * self.yoffset + y * self.yoffset + 2*self.yoffset
    def get_xmid(self,(x,y)):
        return self.xtop + x * self.xoffset - y * self.xoffset
    def get_ymid(self,(x,y)):
        return self.ytop + x * self.yoffset + y * self.yoffset + self.yoffset
    
    def get_ml(self, pos):
        return self.get_left(pos), self.get_ymid(pos)
    
    def get_mr(self, pos):
        return self.get_right(pos), self.get_ymid(pos)
    
    def get_mt(self, pos):
        return self.get_xmid(pos), self.get_top(pos)
    
    def get_mb(self, pos):
        return self.get_xmid(pos), self.get_bottom(pos)
    
    def get_bl(self, pos):
        return self.get_left(pos), self.get_bottom(pos)
    
    def get_br(self, pos):
        return self.get_right(pos), self.get_bottom(pos)
    
    def get_tl(self, pos):
        return self.get_left(pos), self.get_top(pos)
    
    def get_tr(self, pos):
        return self.get_left(pos), self.get_top(pos)

