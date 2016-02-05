"""Represents a flare in the game"""

import random

import serge.blocks.actors
import serge.blocks.utils
import serge.blocks.layout

from theme import G, theme
import common 


class Flare(serge.actor.Actor):
    """A flare that glows a certain colour and has smoke"""

    def __init__(self, tag, name, colour):
        """Initialise the Flare"""
        super(Flare, self).__init__(tag, name)
        #
        self.colour = colour
        self.smoke_probability = G('smoke-probability', colour)
        self.smoke_x_velocity = G('smoke-x-velocity', colour)
        self.smoke_y_velocity = G('smoke-y-velocity', colour)
        self.smoke_x_range = G('smoke-x-range', colour)
        self.smoke_y_range = G('smoke-y-range', colour)
        self.smoke_y_offset = G('smoke-y-offset', colour)
        #
        self.setSpriteName('flare')
        self.setLayerName('ropes')
                
    def addedToWorld(self, world):
        """Added the flare to the world"""
        super(Flare, self).addedToWorld(world)
        #
        self.world = world
        self.manager = world.findActorByName('behaviours')
        self.camera = serge.engine.CurrentEngine().getRenderer().getCamera()
    
    def updateActor(self, interval, world):
        """Update the flare"""
        super(Flare, self).updateActor(interval, world)
        #
        # Check if new smoke needed
        if self.camera.canSee(self) and random.random() < self.smoke_probability:
            #
            # Create a new piece of smoke
            smoke = Smoke('smoke', 'smoke', self.colour, self.smoke_x_velocity, self.smoke_y_velocity)
            self.world.addActor(smoke)
            smoke.moveTo(self.x, self.y+self.smoke_y_offset)
            #
            # Make sure it dissapears eventually
            x_range = (self.x-self.smoke_x_range, self.x+self.smoke_x_range)
            y_range = (self.y-self.smoke_y_range, self.y+self.smoke_y_range)
            self.manager.assignBehaviour(smoke, serge.blocks.behaviours.RemoveWhenOutOfRange(x_range, y_range), 'smoke-removal')
            
            
class Smoke(serge.actor.Actor):
    """Some smoke"""

    def __init__(self, tag, name, colour, vx_range, vy_range):
        """Initialise the Smoke"""
        super(Smoke, self).__init__(tag, name)
        #
        self.colour = colour
        self.vx_range = vx_range
        self.vy_range = vy_range
        #
        self.setSpriteName('%s-smoke' % self.colour)
        self.setLayerName('smoke')
        
    def updateActor(self, interval, world):
        """Update this smoke"""
        super(Smoke, self).updateActor(interval, world)
        #
        dx = random.triangular(*self.vx_range)*interval/1000.0
        dy = random.triangular(*self.vy_range)*interval/1000.0
        #
        self.move(dx, dy)
        #self.visual.setCell(random.randrange(0, 3))
        







