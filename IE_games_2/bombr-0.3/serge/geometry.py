"""Geometric classes"""

import pygame
import math

import common
import serialize

# Some shapes
RECTANGLE = 1
CIRCLE = 2
FRAME = 3 # Rectangle with sides as walls and center is open


class SimpleRect(list):
    """A simple rectangle implementation"""
    
    def __init__(self, *args):
        """Initialise the rectangle"""
        super(SimpleRect, self).__init__(args)
    
    def colliderect(self, other):
        """Return True if this rectangle collides with another"""
        r1 = pygame.rect.Rect(self)
        r2 = pygame.rect.Rect(other)
        return r1.colliderect(r2)
        
    def contains(self, other):
        """Return True if this rectangle contains another"""
        r1 = pygame.rect.Rect(self)
        r2 = pygame.rect.Rect(other)
        return r1.contains(r2)

    def collidepoint(self, x, y):
        """Return True if this rectangle collides with another"""
        r1 = pygame.rect.Rect(self)
        return r1.collidepoint(x, y)

    def inflate(self, w, h):
        """Inflate to new width and height staying in the same centered place"""
        if self[2] == 0 and self[3] == 0:
            return SimpleRect(0, 0, w, h)
        cx, cy = self[0] + 0.5*self[2], self[1] + 0.5*self[3]
        new = SimpleRect(0, 0, w, h)
        new[0] = cx-w/2
        new[1] = cy-h/2
        return new

    def inflate_ip(self, w, h):
        """Inflate current rectangle to new width and height staying in the same centered place"""
        if self[2] == 0 and self[3] == 0:
            self[2] = w
            self[3] = h
            return
        cx, cy = self[0] + 0.5*self[2], self[1] + 0.5*self[3]
        self[0] = cx-float(w)/2
        self[1] = cy-float(h)/2
        self[2] = w
        self[3] = h

    def move_ip(self, dx, dy):
        """Move in place"""
        self[0] += dx
        self[1] += dy
        
    @property
    def width(self): return self[2]
    @property
    def height(self): return self[3]
    @property
    def x(self): return self[0]
    @x.setter
    def x(self, v): self[0] = v
    @property
    def y(self): return self[1]
    @y.setter
    def y(self, v): self[1] = v
    left = x
    top = y
    
class SpatialObject(object):
    """Represents a spatial object"""
    
    def isInside(self, other):
        """Return True if this object is inside another"""
        raise NotImplemented

    def isOverlapping(self, other):
        """Return True if this object overlaps another"""
        raise NotImplemented
        
            
class Rectangle(SpatialObject, serialize.Serializable):
    """Represents a rectangle"""
    
    my_properties = (
        serialize.L('rect', (0, 0, 0, 0), 'the spatial extent of the actor'),
    )

    def __init__(self, x=0, y=0, w=0, h=0):
        """Return a new object based on top left, top right, width and height"""
        self.rect = SimpleRect(x, y, w, h)
    
    def init(self):
        """Initialize from serialized"""
        if not hasattr(self, 'rect'):
            self.rect = SimpleRect(0, 0, 0, 0)
        else:
            self.rect = SimpleRect(*self.rect)
        
    @classmethod
    def fromCenter(cls, cx, cy, w, h):
        """Return a new rectangle giving the center x, y and width, height"""
        return cls(cx-w/2, cy-h/2, w, h)
        
    def isInside(self, other):
        """Return True if this object is inside another"""
        return other.rect.contains(self.rect) == 1
    
    def isOverlapping(self, other):
        """Return True if this object overlaps another"""
        return other.rect.colliderect(self.rect) == 1

    def setSpatial(self, x, y, w, h):
        """Set the spatial details of ourself"""
        self.rect = SimpleRect(x, y, w, h)
    
    def setOrigin(self, x ,y):
        """Set the left and top coords"""
        self.moveTo(x+self.width/2, y+self.height/2)

    def getOrigin(self):
        """Get the left and top coords"""
        return self.rect[0], self.rect[1]
                
    def getSpatial(self):
        """Return spatial details"""
        return self.rect

    def setSpatialCentered(self, x, y, w, h):
        """Set the spatial details of ourself"""
        self.setSpatial(x-w/2, y-h/2, w, h)
        
    def getSpatialCentered(self):
        """Return spatial details"""
        x, y, w, h = self.getSpatial()
        return (x+w/2, y+h/2, w, h)
    
    def getRelativeLocation(self, other):
        """Return the relative location of another object"""
        return (other.rect.x - self.rect.x, other.rect.y - self.rect.y)

    def getRelativeLocationCentered(self, other):
        """Return the relative location of another object"""
        l1, l2 = self.getSpatialCentered(), other.getSpatialCentered()
        return (l2[0] - l1[0], l2[1] - l1[1])

    def getDistanceFrom(self, other):
        """Return the distance we are from another"""
        if isinstance(other, SpatialObject):
            return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2)
        else:
            return math.sqrt((self.x-other[0])**2 + (self.y-other[1])**2)
    
    def move(self, dx, dy):
        """Move the actor"""
        self.moveTo(self.x+dx, self.y+dy)
        
    def moveTo(self, x, y, override_lock=False):
        """Move the center of this object to the given location, unless it is locked
        
        This is the main method used to implement the position of the 
        shape. This is the one to override.
        
        """
        self.rect.x = x-self.rect.width/2
        self.rect.y = y-self.rect.height/2
        
    def resizeBy(self, w, h):
        """Resize the spatial by the given extent"""
        self.rect.inflate_ip(w+self.width, h+self.height)

    def resizeTo(self, w, h):
        """Resize the spatial by the given extent"""
        self.resizeBy(w-self.width, h-self.height)
        
    def scale(self, factor):
        """Rescale the spatial extent"""
        _, _, w, h = self.rect
        nw, nh = w*factor, h*factor
        self.resizeTo(nw, nh)

    def getArea(self):
        """Return the area of the shape"""
        return self.rect.width * self.rect.height
    
           
    ### Simple access ###
    
    @property
    def x(self): return self.rect.x+self.rect.width/2
    @x.setter
    def x(self, value): 
        self.moveTo(value, self.y)
    @property
    def y(self): return self.rect.y+self.rect.height/2
    @y.setter
    def y(self, value):
        self.moveTo(self.x, value)
    @property
    def width(self): return self.rect.width
    @property
    def height(self): return self.rect.height
    
    
class Point(Rectangle):
    """Represents a point"""

    @classmethod
    def __init__(self, x, y):
        """Return a new object based on a point"""
        self.rect = SimpleRect(x, y, 0, 0)
    
    def isInside(self, other):
        """Return True if this object is inside another"""
        return other.rect.collidepoint(self.rect[0], self.rect[1]) == 1    
        
    def isOverlapping(self, other):
        """Return True if this object overlaps another"""
        return self.isInside(other)
