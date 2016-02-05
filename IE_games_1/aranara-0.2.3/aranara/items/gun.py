"""A gun that fires rockets"""

import random
import math
import pyglet
import pymunk

from .. import engine
from .. import settings
import item


class Gun(item.BaseItem):
    """A gun that fires rockets"""

    def __init__(self, name, rocket_generator, fire_key, offset, *args, **kw):
        """Initialise the gun"""
        super(Gun, self).__init__(name, 'gun-back.png', *args, **kw)
        #
        self.fire_key = fire_key
        self.offset = offset
        self.rocket_generator = rocket_generator
        self._aiming_rotation = 0

    def addedToWorld(self, world):
        """Added to the world"""
        super(Gun, self).addedToWorld(world)
        #
        self.chamber = self.mountActor(
            engine.SpriteActor('%s-chamber' % self.name, 'gun-front.png', batch=self.batch),
            settings.S.gun_chamber_offset,
        )
        #
        world.linkEvent(engine.events.E_KEY_PRESS, self.keyPress)
        #
        # world.tweens.append(
        #     engine.Tween(
        #         self, 'aiming_rotation', 10, -30, 5, engine.Tween.sinInOut, repeat=True
        #     )
        # )

    def keyPress(self, (symbol, modifier), arg):
        """A key was pressed"""
        if symbol == self.fire_key:
            self.log.info('The fire key was pressed')
            self.fireRocket()

    def fireRocket(self):
        """Fire a rocket"""
        # TODO: flipped guns are not working but it is taking too long
        #
        # Set the properties of the new rocket
        obj = self.rocket_generator()
        angle = self.aiming_rotation
        offset = self.offset.rotated_degrees(-angle)
        obj.x = (self.x + offset.x) if not self.flipped_x else (self.x - offset.x)
        obj.y = self.y + offset.y
        obj.rotation = angle
        obj.body.velocity.rotate(-math.radians(angle))
        obj.syncPhysics()
        #
        # Put into the world
        self.world.addActor(obj)

    @property
    def aiming_rotation(self):
        """Return the rotation of the chamber"""
        return self._aiming_rotation

    @aiming_rotation.setter
    def aiming_rotation(self, value):
        """Set the rotation of the chamber"""
        self._aiming_rotation = value
        self.chamber.rotation = value


class Rocket(engine.SpriteActor):
    """A rocket which moves user it's own power"""

    def __init__(self, name, sprite_name, power, explode_tags, explosion_force, explosion_duration, *args, **kw):
        """Initialise the rocket"""
        super(Rocket, self).__init__(name, sprite_name, *args, **kw)
        #
        self.power = power
        self.explode_tags = explode_tags
        self.explosion_force = explosion_force
        self.explosion_duration = explosion_duration

    def addedToWorld(self, world):
        """Added to the world"""
        super(Rocket, self).addedToWorld(world)
        #
        self.log.debug('Rocket (%s) will explode with %s' % (self.tag, self.explode_tags, ))
        for tag in self.explode_tags:
            world.space.add_collision_handler(hash(self.tag), hash(tag), self.collisionOccurred)

    def updateActor(self, world, dt):
        """Update the rocket"""
        super(Rocket, self).updateActor(world, dt)
        #
        # Accelerate
        force = self.power * dt * self.body.velocity.normalized()
        self.addImpulseForce(force)
        #
        # Emit smoke if we need to
        if random.random() < dt * settings.S.rocket_smoke_per_second:
            self.log.debug('Adding new smoke particle')
            #
            p = engine.Particle('smoke.png', settings.S.rocket_smoke_lifetime,
                                opacity_fn=engine.Particle.fractionalGrow(255, 0.1),
                                size_fn=engine.Particle.linearGrow(0.1, 2),
                                batch=self.batch, group=self.world.ui_back)
            p.position = self.position
            world.addActor(p)

    @classmethod
    def getRocketGenerator(cls, sprite_name, power, initial_velocity, mass,
                           explode_tags, explosion_force, explosion_duration, batch):
        """Provide a function that can generate new rockets on demand"""
        def function():
            """Rocket generator"""
            obj = cls(engine.getUID('rocket-%s'), sprite_name, power,
                      explode_tags, explosion_force, explosion_duration, batch=batch)
            obj.addPhysics(engine.RectangleSpritePhysics(mass))
            obj.body.velocity = pymunk.Vec2d(initial_velocity, 0)
            obj.tag = 'rocket'
            return obj
        return function

    def collisionOccurred(self, space, arbiter):
        """We collided with something that would cause us to explode"""
        self.explodeRocket(self.world.getActorByShape(space.shapes[1]))
        return True

    def explodeRocket(self, other):
        """Explode the rocket"""
        self.log.debug('Rocket %s exploding %s' % (self, other))
        #
        # Add an explosion to the world
        explosion = Explosion(engine.getUID('explosion-%s'), 'explosion.png', self.explosion_force,
                              self.explosion_duration, x=self.x, y=self.y, batch=self.batch)
        self.world.addActor(explosion)
        #
        # TODO: this shouldn't be here but it is only 2 hours to go before PyWeek ends!
        for i in range(settings.S.rocket_explosion_helium):
            h = engine.SpriteActor(engine.getUID('helium-%s'), 'helium.png',
                                   x=self.x + random.uniform(-20, 20),
                                   y=self.y + random.uniform(-20, 20),
                                   batch=self.batch, group=self.group
            )
            h.tag = 'helium'
            h.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
            h.body.velocity = pymunk.Vec2d(random.uniform(-100, 100), random.uniform(-100, 100))
            self.world.scheduleActorAddition(h)
        #
        # Remove the rocket
        self.world.scheduleActorRemoval(self)


class Explosion(engine.Particle):
    """An explosion - a visual plus a repulsive force on all physics actors"""

    def __init__(self, name, sprite_name, force, duration, *args, **kw):
        """Initialise the explosion"""
        super(Explosion, self).__init__(sprite_name, 1, *args, **kw)
        #
        self.size_fn = engine.Particle.fractionalGrow(1.0, 0.1)
        self.opacity_fn = engine.Particle.fractionalGrow(255, 0.1)
        self.force = force
        self.duration = duration

    def updateActor(self, world, dt):
        """Update the explosion"""
        super(Explosion, self).updateActor(world, dt)
        #
        # Get all objects in the space and apply an explosive force to them
        my_position = pymunk.Vec2d(self.getCenter())
        for actor in self.world.getPhysicsActors():
            if actor != self:
                offset = pymunk.Vec2d(actor.getCenter()) - my_position
                force = self.force * (offset.length ** -1) * offset.normalized()
                actor.addImpulseForce(force)
        #
        self.rotation += random.uniform(-30, 30)
