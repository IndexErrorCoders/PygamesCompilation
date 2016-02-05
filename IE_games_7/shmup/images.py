#!/usr/bin/env python
#coding=utf-8
# holding loaded images and image handling functions
import pygame
from pygame.locals import *

import utils
from isospace import IsoGrid
from constants import *

# a buildingset is 4 images: 
# 1 the building image
# 2 image divided into vertical slices (name + "set")
# 3 image with other color, to show when placing new (name + "hint")
# 4 image with other color, to show when malplacing new (name + "badhint")
def make_buildingset(name, size, filename, cls = None):
        i = utils.load_image(filename)
        set = cut_img(i,size)
        hint = colortint(i,(10,255,10))
        badhint = colortint(i,(255,10,10))
        
        globals()[name] = i
        globals()[name+"set"] = set
        globals()[name+"hint"] = hint
        globals()[name+"badhint"] = badhint
        if cls:
            cls.image = i
            cls.imageset = set
            cls.hint = hint
            cls.badhint = badhint
            
def cut_img(image, (x,y)): # cuts an image into pieces fit for isometric rendering
    rect = image.get_rect()
    xoffset = y*TX -1
    yoffset = rect.height - x*TY - y*TY
    isoG = IsoGrid((TX,TY),(xoffset,yoffset))
    
    r = pygame.Rect((0,0),(TW,rect.height))
    r.bottomleft = isoG.get_left((x-1,y-1)),rect.height
    midpiece = cut(image,r)
    
    xpieces = []
    for n in range(x-1):
        l,b = isoG.get_bl((n,y-1))
        r.height = b
        r.width = TX
        r.bottomleft = l,b
        xpieces.append(cut(image,r))
    ypieces = []
    for n in range(y-1):
        l,b = isoG.get_mb((x-1,n))
        r.height = b
        r.width = TX
        r.bottomleft = l -1, b
        ypieces.append(cut(image,r))
        
    return tuple([midpiece,] + xpieces + ypieces)

def cut(surface, rect):
    print surface.get_size()
    print rect
    return surface.subsurface(rect).copy()

def colortint(image, color):
    overlay = pygame.Surface(image.get_size())
    overlay.fill(color)
    re_img = image.copy()
    re_img.blit(overlay,(0,0),None, BLEND_MIN)
    return re_img
   
def cut_sheet(sheet,fsize):
    rect = pygame.Rect((0,0),fsize)
    l = []
    for n in range(sheet.get_width()/rect.width):
        rect.left = rect.width*n
        l.append(cut(sheet,rect))
    return l