"""Represents some smoke"""

import random
import math
import time

import serge.actor
import serge.visual
import serge.events
import serge.blocks.behaviours
import serge.common
if serge.common.PYMUNK_OK:
    from pymunk import Vec2d
else:
    from serge.simplevecs import Vec2d

from theme import G
import common 


class Smoke(serge.actor.Actor):
    """Represents some smoke on the screen"""

    def __init__(self, parent):
        """Initialise the Smoke"""
        super(Smoke, self).__init__('smoke')
        self.parent = parent
        
    def addedToWorld(self, world):
        """Added the smoke to the world"""
        super(Smoke, self).addedToWorld(world)
        #
        # Set our properties
        self.setLayerName('main' if random.random()<0.6 else 'effects')
        self.setSpriteName('smoke')
        self.moveTo(self.parent.x, self.parent.y)
        self.setAngle(random.randrange(0, 360))
        self.setZoom(random.uniform(*G('smoke-zoom-range')))
        self.remove_after = time.time() + random.uniform(*G('smoke-lifetime-range'))
        self.visual.setCell(random.randrange(0, self.visual.getNumberOfCells()))
        
    def updateActor(self, interval, world):
        """Update the smoke"""
        super(Smoke, self).updateActor(interval, world)
        #
        if time.time() > self.remove_after:
            world.scheduleActorRemoval(self)

