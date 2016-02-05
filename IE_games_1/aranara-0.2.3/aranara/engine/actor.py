"""Represents an actor in the game

The actor typically has some visual representation and some
game logic and so will be called once per cycle to render
and once per cycle to update its game logic.

An actor is also linked to the pymunk physical space for
simulating physics.

An actor
    Subclasses sprite
    Has a physical body
    Automatically update their physics locations

"""

import math
import time
import pyglet
import pymunk

import common
import events


class Actor(pyglet.sprite.Sprite, common.Loggable, events.EventAware):
    """Represents an actor in the game world"""

    def __init__(self, name, *args, **kw):
        """Initialise the actor"""
        super(Actor, self).__init__(*args, **kw)
        self.addLogger()
        self.initEvents()
        self.name = name if name is not None else 'Actor-%s' % time.time()
        self.body = None
        self.shape = None
        self.world = None
        self.force = pymunk.Vec2d(0, 0)
        self._tag = "object"

    def addedToWorld(self, world):
        """Called when the actor is added to the world"""
        self.world = world

    def removedFromWorld(self, world):
        """Called when the actor was removed from the world"""

    def updateActor(self, world, dt):
        """Update the actor position from physics"""
        if self.hasPhysics():
            self.physicsUpdate(dt)

    def physicsUpdate(self, dt):
        """Update the physics for the actor"""
        self.x = self.body.position.x
        self.y = self.body.position.y
        self.rotation = math.degrees(-self.body.angle)

    def addPhysics(self, adder):
        """Add physics to this object from the physics adder"""
        adder.addPhysicsTo(self)
        self.shape.collision_type = hash(self.tag)
        self.syncPhysics()

    def hasPhysics(self):
        """Return True if this actor has physics"""
        return self.body is not None

    def isStatic(self):
        """Return True if the actor is static"""
        # TODO: the following check is pretty bad and should be replaced by an inf check
        return True if not self.hasPhysics() else self.body.mass > 1e10

    def syncPhysics(self):
        """Sync the pymunk physics to the sprite"""
        self.body.position.x = self.x
        self.body.position.y = self.y
        self.body.angle = math.radians(-self.rotation)

    def addImpulseForce(self, force):
        """Add an impulse force"""
        self.force += force

    def resetForces(self):
        """Reset forces on the actor"""
        self.force = pymunk.Vec2d(0, 0)

    def getCenter(self):
        """Return the center position of the actor"""
        return self.x + self.image.anchor_x, self.y + self.image.anchor_y

    def getSize(self):
        """Return the width and height of the content"""
        return self.width, self.height

    @property
    def rotation(self):
        """Return the rotation"""
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        """Set the rotation"""
        super(Actor, self)._set_rotation(rotation)
        if self.hasPhysics():
            self.body.angle = math.radians(-self.rotation)
            if self.isStatic():
                # Static bodies do not automatically update when you rotate them
                self.world.space.reindex_shape(self.shape)

    @property
    def position(self):
        """Return the position"""
        return self._x, self._y

    @position.setter
    def position(self, position):
        """Set the position"""
        super(Actor, self).set_position(*position)
        if self.hasPhysics():
            self.syncPhysics()
            if self.isStatic():
                # Static bodies do not automatically update when you move them
                self.world.space.reindex_shape(self.shape)

    def __repr__(self):
        """Nice representation"""
        return '<%s %s>' % (self.__class__.__name__, self.name)

    @property
    def tag(self):
        """Return the tag"""
        return self._tag

    @tag.setter
    def tag(self, value):
        """Set the tag"""
        self._tag = value
        if self.shape:
            self.shape.collision_type = hash(self.tag)


class SpriteActor(Actor):
    """Represents a sprite"""

    def __init__(self, name, image_name, *args, **kw):
        """Initialise the sprite"""
        #
        # Create the image and set the anchor point to the center
        # TODO: clean up this bit - should be a better way to distinguish animations from images
        if isinstance(image_name, str):
            self.image_name = image_name
            image = pyglet.resource.image(image_name)
            image.anchor_x = image.width / 2
            image.anchor_y = image.height / 2
        else:
            image = image_name
            for img in image.frames:
                img.image.anchor_x = img.image.width / 2
                img.image.anchor_y = img.image.height / 2
            image.anchor_x = img.image.anchor_x
            image.anchor_y = img.image.anchor_y
        #
        self.flipped_x = self.flipped_y = False
        #
        super(SpriteActor, self).__init__(name, image, *args, **kw)

    def removedFromWorld(self, world):
        """Called when the actor was removed from the world"""
        self.delete()

    def flipHorizontal(self):
        """Flip the sprite image horizontally"""
        self.flipped_x = not self.flipped_x
        self._resetImage()

    def flipVertical(self):
        """Flip the sprite image vertical"""
        self.flipped_y = not self.flipped_y
        self._resetImage()

    def _resetImage(self):
        """Set the image"""
        self.image = pyglet.resource.image(self.image_name, self.flipped_x, self.flipped_y)
        self.image.anchor_x = self.image.width / 2
        self.image.anchor_y = self.image.height / 2


class MountableActor(SpriteActor):
    """An actor that can have child actors mounted to it"""

    def __init__(self, *args, **kw):
        """Initialise the actor"""
        super(MountableActor, self).__init__(*args, **kw)
        #
        self.actors = []

    def mountActor(self, actor, (x, y)):
        """Add an actor at an offset"""
        self.actors.append((actor, (x, y)))
        self.world.addActor(actor)
        return actor

    def updateActor(self, world, dt):
        """Update the actor"""
        super(MountableActor, self).updateActor(world, dt)
        #
        for actor, (x, y) in self.actors:
            actor.x = self.x + x
            actor.y = self.y + y
            if actor.hasPhysics():
                actor.syncPhysics()

    def _resetImage(self):
        """Reset the image"""
        super(MountableActor, self)._resetImage()
        for actor, _ in self.actors:
            actor.flipped_x = self.flipped_x
            actor.flipped_y = self.flipped_y
            actor._resetImage()


class TextActor(pyglet.text.layout.TextLayout, common.Loggable, events.EventAware):
    """Represents an actor to draw something"""

    def __init__(self, name, document, *args, **kw):
        """Initialise the text"""
        super(TextActor, self).__init__(document, *args, **kw)
        #
        self.anchor_x = "center"
        self.anchor_y = "center"
        self.addLogger()
        self.initEvents()
        self.name = name
        self.tag = "text"
        # TODO: this attribute only in for compatibility it does not have any effect
        self.visible = True

    def updateActor(self, world, dt):
        """Update the actor position from physics"""

    def addPhysics(self, added):
        """Add physics to the object - not implemented for text"""
        raise NotImplementedError('Cannot add physics to text objects (%s)' % self)

    def hasPhysics(self):
        """Return True if this actor has physics"""
        return False

    def isStatic(self):
        """Return True if the actor is static"""
        return True

    def addImpulseForce(self, force):
        """Add an impulse force"""
        raise NotImplementedError('Cannot add forces to text objects (%s)' % self)

    def resetForces(self):
        """Reset forces on the actor"""
        self.force = pymunk.Vec2d(0, 0)

    def getSize(self):
        """Return the width and height of the content"""
        return self.content_width, self.content_height

    def getCenter(self):
        """Return the center of the actor"""
        return self.x, self.y

    def __repr__(self):
        """Nice representation"""
        return '<%s %s>' % (self.__class__.__name__, self.name)

    def addedToWorld(self, world):
        """Called when the actor is added to the world"""
        self.world = world

    def removedFromWorld(self, world):
        """Called when the actor was removed from the world"""
        self.delete()

    @property
    def position(self):
        """Return the position"""
        return self.x, self.y

    @position.setter
    def position(self, value):
        """Set the position"""
        self.x, self.y = value