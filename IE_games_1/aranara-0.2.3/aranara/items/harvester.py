"""A harvester"""

import pyglet

from .. import engine
from .. import settings
from .. import common
from .. import sound
from .. items import item, collector


# TODO: harvester should have polygon physics
# TODO: need right hand versions of these harvesters


class Harvester(item.BaseItem):
    """A harvester"""

    image_name = 'unknown'
    size_name = 'unknown'
    flip = False

    def __init__(self, name, collect_tags, capacity, *args, **kw):
        """Initialise the harvester"""
        super(Harvester, self).__init__(name, pyglet.image.Animation(self.getAnimationFrames()), *args, **kw)
        #
        self.collect_tags = collect_tags
        self.content = 0
        self.vertex_list = []
        self.capacity = capacity
        self.addPhysics(engine.PolygonSpritePhysics(points=getattr(settings.S, '%s_harvester_poly' % self.size_name)))

    def getAnimationFrames(self):
        """Return the animation frames"""
        return [
            pyglet.image.AnimationFrame(pyglet.resource.image('%s-harvester-1.png' % self.image_name, flip_x=self.flip), 0.5),
            pyglet.image.AnimationFrame(pyglet.resource.image('%s-harvester-2.png' % self.image_name, flip_x=self.flip), 0.5),
            pyglet.image.AnimationFrame(pyglet.resource.image('%s-harvester-3.png' % self.image_name, flip_x=self.flip), 0.5),
            pyglet.image.AnimationFrame(pyglet.resource.image('%s-harvester-4.png' % self.image_name, flip_x=self.flip), 0.5),
        ]

    def addedToWorld(self, world):
        """Added to the world"""
        super(Harvester, self).addedToWorld(world)
        #
        # Set main drawing group
        self.group = world.ui_back
        #
        # The collector part that will collect the helium
        self.col = collector.Collector('%s-collector' % self.name, 'collector.png', self.collect_tags)
        self.col.scale = getattr(settings.S, '%s_harvester_collector_scale' % self.size_name)
        self.col.tag = 'collider'
        self.col.addPhysics(engine.RectangleSpritePhysics())
        self.mountActor(self.col, getattr(settings.S, '%s_harvester_collector_offset' % self.size_name))
        #
        # The percent full bar
        self.col.linkEvent(common.E_ITEM_COLLECTED, self.collectedItem)
        multiplier = 1 if not self.flip else -1
        x1, y1, x2, y2 = (self.x + settings.S.small_harvester_contents_offset.x * multiplier,
                          self.y + settings.S.small_harvester_contents_offset.y,
                          self.x + settings.S.small_harvester_contents_offset.x * multiplier,
                          self.y + settings.S.small_harvester_contents_offset.y + settings.S.small_harvester_contents_height
        )
        self.vertex_list = self.batch.add(4, pyglet.gl.GL_QUADS, world.ui_front,
                                     ('v2i', map(int, [x1, y1, x2, y1, x2, y2, x1, y2])),
                                     ('c4B', settings.S.small_harvester_colour * 4))

    def collectedItem(self, (obj, collected), arg):
        """Pass on event"""
        score = self.collect_tags[collected.tag]
        self.log.info('%s got some %s with score %d' % (self.name, collected.tag, score))
        #
        # Play appropriate sound
        if score > 0:
            sound.Sounds.collect.play()
        else:
            sound.Sounds.collect_bad.play()
        self.processEvent(common.E_ITEM_COLLECTED, (self, collected, score))
        #
        # Redraw the percentage bar that shows our contents
        self.content = min(self.capacity, max(0, self.content + score))
        self._updatePercentBar()

    def _updatePercentBar(self):
        """Update the vertices for the percent bar"""
        if self.flip:
            x1, y1, x2, y2 = (self.x - settings.S.small_harvester_contents_offset.x - float(self.content) / self.capacity * settings.S.small_harvester_contents_width,
                              self.y + settings.S.small_harvester_contents_offset.y,
                              self.x - settings.S.small_harvester_contents_offset.x,
                              self.y + settings.S.small_harvester_contents_offset.y + settings.S.small_harvester_contents_height
        )
        else:
            x1, y1, x2, y2 = (self.x + settings.S.small_harvester_contents_offset.x,
                              self.y + settings.S.small_harvester_contents_offset.y,
                              self.x + settings.S.small_harvester_contents_offset.x + float(self.content) / self.capacity * settings.S.small_harvester_contents_width,
                              self.y + settings.S.small_harvester_contents_offset.y + settings.S.small_harvester_contents_height
        )
        self.vertex_list.vertices = map(int, [x1, y1, x2, y1, x2, y2, x1, y2])

    def isFull(self):
        """Return True if we are full"""
        return self.content == self.capacity

    def syncPhysics(self):
        """Sync the physics"""
        super(Harvester, self).syncPhysics()
        #
        if self.vertex_list:
            self._updatePercentBar()


class SmallHarvester(Harvester):
    """A small harvester"""

    image_name = 'small'
    size_name = 'small'


class SmallRightHarvester(Harvester):
    """A small harvester"""

    image_name = 'small'
    size_name = 'small_right'
    flip = True


class LargeHarvester(Harvester):
    """A large harvester"""

    image_name = 'large'
    size_name = 'large'