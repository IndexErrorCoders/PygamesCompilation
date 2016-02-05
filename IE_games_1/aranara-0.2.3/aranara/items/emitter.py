"""An emitter that keeps creating objects"""

import time
import math
import random
import pymunk
import pyglet

from .. import engine
from .. import settings
import item


class Emitter(item.BaseItem):
    """An emitter to keep creating objects"""

    def __init__(self, name, sprite_name, obj_creator, interval, offset=(0, 0), velocity=0.0,
                 angular_spread=0.0, **kw):
        """Initialise the emitter"""
        super(Emitter, self).__init__(name, pyglet.image.Animation(self.getAnimationFrames()), **kw)
        #
        self.interval = interval
        self.obj_creator = obj_creator
        self.offset = pymunk.Vec2d(offset)
        self.velocity = velocity
        self.paused = False
        self.angular_spread = angular_spread
        self.last_emitted = time.time()

    def getAnimationFrames(self):
        """Return the animation frames"""
        return [
            pyglet.image.AnimationFrame(pyglet.resource.image('emitter-%d.png' % idx), 0.1) for idx in range(1, 4)
        ]

    def addedToWorld(self, world):
        """Added to the world"""
        super(Emitter, self).addedToWorld(world)
        #
        offset = pymunk.Vec2d(settings.S.emitter_rock_offset)
        offset.rotate_degrees(-self.rotation)
        #
        self.mined_rock = engine.SpriteActor('%s-mined-rock' % self.name, 'mined-rock.png',
                               batch=self.batch, group=world.ui_front)
        self.mined_rock.tag = 'decoration'
        self.mined_rock.addPhysics(engine.RectangleSpritePhysics())
        self.mountActor(
            self.mined_rock,
            offset,
        )
        self.mined_rock.rotation = self.rotation

    def updateActor(self, world, dt):
        """Update the actor"""
        super(Emitter, self).updateActor(world, dt)
        #
        # Do we need to emit an obj
        if time.time() - self.last_emitted > float(self.interval):
            self.emitObject(world)
            self.last_emitted = time.time()

    def emitObject(self, world):
        """Emit an object into the world"""
        obj = self.obj_creator(world)
        self.log.debug('Emitting new object %s' % obj)
        #
        # Set the properties of the new object
        angle = random.uniform(self.rotation - self.angular_spread, self.rotation + self.angular_spread)
        offset = self.offset.rotated_degrees(-angle)
        obj.x = self.x + offset.x
        obj.y = self.y + offset.y
        obj.rotation = angle
        obj.body.velocity = float(self.velocity) * offset.normalized()
        obj.syncPhysics()
        #
        # Put into the world
        world.addActor(obj)

