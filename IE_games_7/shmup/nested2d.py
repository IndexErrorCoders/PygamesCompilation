#!/usr/bin/env python
#coding=utf-8
import array
import collections
import copy

class Nested2d(object):
    def __init__(self, x_len, y_len, fill = 0):
        self.list = [ [fill]*y_len for d in range(x_len)]
        self.x_len = x_len
        self.y_len = y_len
    
    def __getitem__(self, key):
        return self.list[key]
    def __setitem__(self, key, value):
        self.list[key] = value
        
    def __iter__(self):
        return self.list.__iter__()
    
    def get_sublist(self, left, top, x_sublen, y_sublen):
        ## removing these 'safing' calculations is an option if i can
        ## be sure to crop the x and y arguments before passing
        if left < 0: left = 0
        if top < 0: top = 0
        
        if left + x_sublen > self.x_len:
            right = self.x_len
        else:
            right = left + x_sublen
        
        if top + x_sublen > self.y_len:
            bottom = self.y_len
        else:
            bottom = top + y_sublen
        
        returnlist = []
        
        for i in self.list[left : right]:
            returnlist.append(self.list[top : bottom])
        return returnlist
    
    def loop_specified(self, start, end, vertical = False):
        xlen = end[0] -start[0]
        ylen = end[1] -start[1]     
        xdir = xlen /abs(xlen)
        ydir = ylen /abs(ylen)
        xlen = abs(xlen) +1
        ylen = abs(ylen) +1

        if vertical:  # going vertical
            for n in range(xlen *ylen):
                yield self.list[start[0] + xdir*(n/ylen)] [start[1] + ydir*(n%ylen)]
        else:         # going horizontal
            for n in range(xlen* ylen):
                yield self.list[start[0] + xdir*(n%xlen)] [start[1] + ydir*(n/xlen)]
    
    def loop_all(self):
        for x, collumn in enumerate(self.list):
            for y, i in enumerate(collumn):
                yield i, x, y
        
        
        
            
    def loop_part(self, topleft, bottomright):
        """ Loop through a subset of the nested2d list, from topleft item going through
        the collumns from top, to bottomright item."""
        
        for x, collumn in enumerate(self.list[topleft[0] : bottomright[0]+1]):
            for y, i in enumerate(collumn[topleft[1] : bottomright[1]+1]):
                yield i, x, y
                
    def loop_part_i(self, topleft, bottomright):
        for x, collumn in enumerate(self.list[topleft[0] : bottomright[0]+1]):
            for y, i in enumerate(collumn[topleft[1] : bottomright[1]+1]):
                yield i, topleft[0] +x, topleft[1] +y
        

    def get_rotated(self, r):

        rotated = Nested2d(self.x_len, self.y_len, None)
        for x , collumn in enumerate(self.list):
            for y , i in enumerate(collumn):
                
                if v == 1:
                    rotated[self.x_len][y][x]
    
    def get_copy(self):
        return copy.deepcopy(self)
    
def nested2d_fromstring(string, func):
    #Parse the level
    
    ylen = len(string.split("\n")[0:-2])
    xlen = len(string.split("\n")[1])
    
    tiles = Nested2d(xlen, ylen, None)
    
    for y, row in enumerate(string.split("\n")[1:-1]):
        
        #tiles.append([])
        for x, char in enumerate(row):

            #A passed function is run for every item item in the character in the string
            #to customize respond to different string characters.
            #Or if passed a dict the char is key and value enters the Nested2d
            if isinstance(func, dict):
                tiles[x][y] = func[char]
            else:
                func(char, tiles, x, y)

    return tiles