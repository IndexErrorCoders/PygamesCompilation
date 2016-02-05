"""Classes to help with cameras"""

import common
import math

import serialize
import geometry 

class Camera(common.Loggable, geometry.Rectangle):
    """Represents a camera"""
    
    my_parameters = (
        serialize.F('zoom', 1.0, 'the camera zoom'),
    )
    
    def __init__(self):
        """Initialise the Camera"""
        super(Camera, self).__init__()
        self.target = None    
        self.zoom = 1.0 

    def init(self):
        """Initialise from serialized"""
        self.zoom = 1.0
        
    def setZoom(self, zoom, x, y):
        """Set the new zoom centered on the given x and y"""
        self.scale(zoom/self.zoom)
        self.zoom = zoom
          
    def canSeeActors(self, actors):
        """Return the actors that we can see from a list of actors"""
        return [actor for actor in actors if self.canSee(actor)]
    
    def canSee(self, actor):
        """Return True if we can see the actor"""
        return self.isOverlapping(actor)            

    def setTarget(self, target):
        """Set the target for the camera to head towards"""
        self.target = target
        
    def getTarget(self):
        """Return the camera's target location"""
        return self.target
    
    def update(self, interval):
        """Update the location of the camera"""
        #
        # If we have a target then move towards it
        if self.target:
            dx, dy = self.target.getRelativeLocationCentered(self)
            mx = my = 100.0 * interval/1000.0
            if abs(dx) > mx:
                dx = math.copysign(mx, dx)
            if abs(dy) > my:
                dy = math.copysign(my, dy)
            self.move(-dx, -dy)

    def getRelativeLocation(self, other):
        """Return the relative location of one from another"""
        x, y = super(Camera, self).getRelativeLocation(other)
        return x*self.zoom, y*self.zoom
   
class NullCamera(Camera):
    """A camera that can see everything"""
    
    zoom = 1.0
    
    def __init__(self):
        """Initialise"""
        self.setSpatial(0, 0, 1000, 1000)
        self.zoom = 1.0
        self.addLogger()
        
    def canSee(self, actor):
        """Can we see it? Yes we can"""
        return True
    
    def init(self):
        """Initialise"""
        self.addLogger()
    
