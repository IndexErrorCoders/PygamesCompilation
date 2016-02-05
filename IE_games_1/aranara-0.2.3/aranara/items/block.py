"""An attractor - attracts (or repels) actors with certain tags"""

import pymunk

from .. import engine
import item


class Block(item.BaseItem):
    """An block that exists in space - it can move or rotate etc"""

    def __init__(self, name, sprite_name, *args, **kw):
        """Initialise the attractor"""
        super(Block, self).__init__(name, sprite_name, *args, **kw)

    def addedToWorld(self, world):
        """Added to the world"""
        super(Block, self).addedToWorld(world)
        #
        self.group = world.ui_middle


class MovingBlock(Block):
    """A block that moves"""

    def __init__(self, name, sprite_name, start, end, duration, *args, **kw):
        """Initialise the block"""
        super(MovingBlock, self).__init__(name, sprite_name, *args, **kw)
        #
        self.start = start
        self.end = end
        self.duration = duration

    def addedToWorld(self, world):
        """The actor was added to the world"""
        super(MovingBlock, self).addedToWorld(world)
        #
        world.tweens.append(engine.Tween(
            self, 'position', self.start, self.end, self.duration,
            engine.Tween.sinInOut, repeat=True,
        ))


class RotatingBlock(Block):
    """A block that rotates"""

    def __init__(self, name, sprite_name, start, end, duration, *args, **kw):
        """Initialise the block"""
        super(RotatingBlock, self).__init__(name, sprite_name, *args, **kw)
        #
        self.start = start
        self.end = end
        self.duration = duration

    def addedToWorld(self, world):
        """The actor was added to the world"""
        super(RotatingBlock, self).addedToWorld(world)
        #
        world.tweens.append(engine.Tween(
            self, 'rotation', self.start, self.end, self.duration,
            engine.Tween.sinInOut, repeat=True,
        ))


class MovingRotatingBlock(Block):
    """A block that moves and rotates"""

    def __init__(self, name, sprite_name, move_start, move_end, move_duration,
                 rotate_start, rotate_end, rotate_duration, *args, **kw):
        """Initialise the block"""
        super(MovingRotatingBlock, self).__init__(name, sprite_name, *args, **kw)
        #
        self.move_start = move_start
        self.move_end = move_end
        self.move_duration = move_duration
        self.rotate_start = rotate_start
        self.rotate_end = rotate_end
        self.rotate_duration = rotate_duration

    def addedToWorld(self, world):
        """The actor was added to the world"""
        super(MovingRotatingBlock, self).addedToWorld(world)
        #
        world.tweens.append(engine.Tween(
            self, 'position', self.move_start, self.move_end, self.move_duration,
            engine.Tween.sinInOut, repeat=True,
        ))
        world.tweens.append(engine.Tween(
            self, 'rotation', self.rotate_start, self.rotate_end, self.rotate_duration,
            engine.Tween.sinInOut, repeat=True,
        ))

