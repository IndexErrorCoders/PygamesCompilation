
#coding=utf-8
from __future__ import division
import math

class Vector(object):
    def __init__(self, (x,y), secpos = None):
        if not secpos:
            self.x = x
            self.y = y
        else:
            self.x = secpos[0] - x
            self.y = secpos[1] - y
        
    def reinit(self,(x,y)):
        self.x = x
        self.y = y
    
    def __add__(self,(x,y)):
        return self.x + x, self.y + y
    
    def __mul__(self,scalar):
        return self.x * scalar, self.y * scalar
    
    def get_len(self):
        return math.hypot(self.x, self.y)
    
    def normalize(self):
        l = self.get_len()
        self.x = self.x / l
        self.y = self.y / l
    
    def get_normalized(self):
        l = self.get_len()
        return Vector((self.x/l, self.y/l))
    
    def get_projected(self, scalar):
        return self.get_normalized() * scalar
    
    
def get_sign(value):
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0

def get_len((x,y)):
    return math.hypot(float(x),float(y))

def normalize((x,y)):
    if x != 0 and y != 0:
        len = get_len((x,y))
        return float(x)/len, float(y) / len
    elif x == 0 and y != 0:
        return 0.0,get_sign(y)
    elif x != 0 and y == 0:
        return get_sign(x), 0.0
    else:
        return 0.0,0.0

def get_mul((x,y), scalar):
    return x * scalar, y * scalar

def get_add((x,y),(xb,yb)):
    return x + xb, y + yb

def get_sub((x,y),(xb,yb)):
    return x - xb, y - yb

    
def get_projected(xy, scalar):
    n = normalize(xy)
    return get_mul(n, scalar)
    

def intersect(A,B,C,D):
    return opposite_sides(A,B,C,D) and opposite_sides(C,D,A,B)

def opposite_sides((ax,ay),(bx,by),(cx,cy),(dx,dy)):
    if cx == dx:
        return (ax < cx) ^ (bx < cx)
    
    else:
        k = (dy - cy)/(dx - cx)
        m = cy - k * cx
        
        return (ay < ax *k +m) ^ (by < bx *k +m)


def add((x,y),(xb,yb)):
    return x + xb, y + yb
def mul((x,y),(xb,yb)):
    return x * xb, y * yb

def ccw((Ax,Ay),(Bx,By),(Cx,Cy)):
	return (Cy-Ay)*(Bx-Ax) > (By-Ay)*(Cx-Ax)


def intersect2(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def itersum(*args):
    x = y = 0
    for i in args:
        x+= i[0]
        y+= i[1]
    return x,y
        