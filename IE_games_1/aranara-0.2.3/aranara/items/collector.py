"""Collects items when they come in range"""

from .. import engine
from .. import common
import item


class Collector(item.BaseItem):
    """A collector that collects objects that come in range

    All objects with a tag in a defined list will be collected

    """

    def __init__(self, name, sprite_name, collect_tags, *args, **kw):
        """Initialise the collector"""
        super(Collector, self).__init__(name, sprite_name, *args, **kw)
        #
        self.collect_tags = collect_tags

    def addedToWorld(self, world):
        """We were added to the world"""
        super(Collector, self).addedToWorld(world)
        #
        # Get a callback when an interesting object collides with us
        for tag in self.collect_tags.keys():
            world.space.add_collision_handler(hash(self.tag), hash(tag), self.collisionOccurred)

    def collisionOccurred(self, space, arbiter):
        """A collision occurred"""
        #
        # Find out what we collided with
        actor = self.world.getActorByShape(arbiter.shapes[1])
        me = self.world.getActorByShape(arbiter.shapes[0])
        self.log.debug('Collision detected with %s (%s, %s)' % (self, me, actor))
        #
        # Tell the world about it
        me.processEvent(common.E_ITEM_COLLECTED, (self, actor))
        #
        # And get rid of the thing we collided with
        self.world.scheduleActorRemoval(actor)
        #
        return True


