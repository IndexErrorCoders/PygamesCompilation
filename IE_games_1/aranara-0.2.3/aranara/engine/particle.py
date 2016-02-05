"""A particle system"""

import pymunk

import actor
import utils


class Particle(actor.SpriteActor):
    """A simple particle"""

    def __init__(self, image_name, lifetime, velocity_fn=None, size_fn=None, opacity_fn=None, colour_fn=None, rotation_fn=None, **kw):
        """Initialise the particle"""
        super(Particle, self).__init__(utils.getUID('particle-%d'), image_name, **kw)
        #
        self.velocity_fn = velocity_fn
        self.size_fn = size_fn
        self.opacity_fn = opacity_fn
        self.colour_fn = colour_fn
        self.rotation_fn = rotation_fn
        self.lifetime = lifetime
        self.age = 0.0

    def updateActor(self, world, dt):
        """Update the particle"""
        #
        # Expire the particle if needed
        self.age += dt
        if self.age >= self.lifetime:
            world.scheduleActorRemoval(self)
            return
        #
        # Apply changes
        #
        # Velocity
        if self.velocity_fn:
            velocity = self.velocity_fn(self.age)
        else:
            velocity = pymunk.Vec2d(0, 0)
        self.position = pymunk.Vec2d(self.position) + velocity * dt
        #
        # Colour
        if self.colour_fn:
            colour = self.colour_fn(self.age)
            self.color = colour
        #
        # Size
        if self.size_fn:
            scale = self.size_fn(self.age)
            self.scale = scale
        #
        # Rotation
        if self.rotation_fn:
            rotation = self.rotation_fn(self.age)
            self.rotation = rotation
        #
        # Opacity
        if self.opacity_fn:
            opactity = self.opacity_fn(self.age)
            self.opacity = opactity


    @staticmethod
    def linearGrow(initial, amount_per_second):
        """A linear growth function"""
        def fn(age):
            """Return the growth"""
            return initial + amount_per_second * age
        return fn

    @staticmethod
    def fractionalGrow(initial, fraction_per_second):
        """A growth based on an overall fraction"""
        def fn(age):
            """Return the grown"""
            return initial * (fraction_per_second ** age)
        return fn

    @staticmethod
    def constantValue(value):
        """Return a constant"""
        return lambda age: value


