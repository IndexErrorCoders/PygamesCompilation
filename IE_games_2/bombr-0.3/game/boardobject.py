"""Base class for objects on the board"""

import abc

import serge.actor
import serge.events
import serge.blocks.animations


class BoardObject(serge.blocks.animations.AnimatedActor):
    """Base class for objects on the board"""

    __metaclass__ = abc.ABCMeta

    is_blockage = True
    is_explosion_barrier = True
    is_deadly = False
    is_fragile = False
    state_id = 1000
    movement_weight = None
    is_player = False
    number_to_create = 1

    def addedToWorld(self, world):
        """Added to the world"""
        super(BoardObject, self).addedToWorld(world)
        #
        self.world = world
        self.mainscreen = world.findActorByName('main-screen')
        self.broadcaster = serge.events.getEventBroadcaster()

    @abc.abstractmethod
    def isMoveBlockedBy(self, other):
        """Return True if the presence of other would block this object from moving"""

    def manMovesOnto(self, other):
        """Called when another man moves onto the square we are occupying"""

    def isDestroyedBy(self, other):
        """Called when this is destroyed by another"""