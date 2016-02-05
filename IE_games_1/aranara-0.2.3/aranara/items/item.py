"""Base class for all game items"""

import pymunk

from .. import engine
from .. import settings
from .. import sound


class BaseItem(engine.MountableActor):
    """Base class for all items"""

    def __init__(self, name, sprite_name, *args, **kw):
        """Initialise the item"""
        super(BaseItem, self).__init__(name, sprite_name, *args, **kw)
        #
        self.rotatable = False
        self.draggable = False
        self.dragging = False
        self.drop_offset = pymunk.Vec2d(0, 0)

    def addedToWorld(self, world):
        """Added to the world"""
        super(BaseItem, self).addedToWorld(world)
        #
        # Capture mouse clicks
        self.linkEvent(engine.events.E_LEFT_CLICK, self.leftClick)
        self.linkEvent(engine.events.E_RIGHT_CLICK, self.rightClick)

    def leftClick(self, (x, y, button, modifiers), arg):
        """Item was clicked on"""
        self.log.info('%s was clicked on' % self)
        sound.Sounds.click.play()
        if self.draggable:
            self.setDragging(not self.dragging, (x, y))

    def rightClick(self, actor, arg):
        """Item was right clicked on"""
        self.log.info('%s was right clicked on' % self)

    def setDragging(self, state, position=None):
        """Set whether we are dragging or not"""
        self.dragging = state
        if state:
            self.opacity = settings.S.dragging_opacity
            self.world.linkEvent(engine.events.E_MOUSE_DRAG, self.draggingItem)
            self.world.linkEvent(engine.events.E_MOUSE_RELEASE, self.releaseItem)
            self.world.linkEvent(engine.events.E_MOUSE_SCROLL, self.scrollItem)
            self.drop_offset = pymunk.Vec2d(position) - pymunk.Vec2d(self.x, self.y)
            self.log.debug('Offset was %s' % self.drop_offset)

        else:
            self.opacity = 255
            self.world.unlinkEvent(engine.events.E_MOUSE_DRAG, self.draggingItem)
            self.world.unlinkEvent(engine.events.E_MOUSE_RELEASE, self.releaseItem)
            self.world.unlinkEvent(engine.events.E_MOUSE_SCROLL, self.scrollItem)

    def draggingItem(self, (x, y, dx, dy, button, modifiers), arg):
        """We are being dragged"""
        self.log.debug('%s is being dragged' % self)
        self.x, self.y = pymunk.Vec2d(x, y) - self.drop_offset
        self.syncPhysics()

    def releaseItem(self, (x, y, button, modifiers), arg):
        """We stopped being dragged"""
        self.log.debug('%s stopped being dragged' % self)
        sound.Sounds.drop.play()
        self.setDragging(False)

    def scrollItem(self, (x, y, scroll_x, scroll_y), arg):
        """We are being rotated"""
        if self.rotatable:
            self.log.debug('%s is being rotated' % self)
            self.rotation += scroll_y
            self.syncPhysics()
            # TODO: should be able to use the constants for this
            self.world.gerty_state['rotation-occurred'] = True
