"""Encapsulate adding physics to an actor"""

import pymunk

import common


DEFAULT_FRICTION = 0.5
DEFAULT_ELASTICITY = 0.5

class PhysicsAdder(common.Loggable):
    """A base helper class to add physics to an actor

    This is probably not the best way to architect this
    but it should work OK

    """

    def __init__(self, mass=0, friction=DEFAULT_FRICTION, elasticity=DEFAULT_ELASTICITY):
        """Initialise the adder"""
        self.addLogger()
        #
        self.mass = mass
        self.friction = friction
        self.elasticity = elasticity
        self.body = None
        self.shape = None

    def addPhysicsTo(self, actor):
        """Add physics to the given actor"""
        #
        # Set properties on the actor
        actor.body = self.body
        actor.shape = self.shape
        #
        # Make sure to copy the other properties
        self.shape.friction = self.friction
        self.shape.elasticity = self.elasticity


class CircleSpritePhysics(PhysicsAdder):
    """Add physics of a circle based on sprite dimensions"""

    def addPhysicsTo(self, actor):
        """Add physics of a circle"""
        if self.mass:
            self.body = pymunk.Body(
                self.mass,
                moment=pymunk.moment_for_circle(self.mass, actor.width / 2, actor.width / 2)
            )
        else:
            self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, actor.width / 2)
        #
        super(CircleSpritePhysics, self).addPhysicsTo(actor)


class PolygonSpritePhysics(PhysicsAdder):
    """Add physics based on a polygon scaled to the sprite dimensions

    The points should be set for a shape of unit width and height. These will
    then be scaled to the sprite and the whole shape centered on the middle of
    the sprite

    """

    def __init__(self, mass=0, friction=DEFAULT_FRICTION, elasticity=DEFAULT_ELASTICITY, points=None):
        """Initialise the adder"""
        super(PolygonSpritePhysics, self).__init__(mass, friction, elasticity)
        self.points = points

    def addPhysicsTo(self, actor):
        """Add physics of a polygon"""
        w, h = actor.width, actor.height
        #
        # Scale the polygon points
        actual_points = [(px * w - w / 2.0, py * h - h / 2.0) for px, py in self.points]
        if self.mass:
            self.body = pymunk.Body(self.mass, moment=pymunk.moment_for_box(self.mass, w, h))
        else:
            self.body = pymunk.Body()
        self.shape = pymunk.Poly(self.body, actual_points)
        #
        super(PolygonSpritePhysics, self).addPhysicsTo(actor)


class RectangleSpritePhysics(PolygonSpritePhysics):
    """Add physics based on a rectangle with the sprite dimensions"""

    def __init__(self, mass=0, friction=DEFAULT_FRICTION, elasticity=DEFAULT_ELASTICITY):
        """Initialise the adder"""
        super(RectangleSpritePhysics, self).__init__(
            mass, friction, elasticity,
            [(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
        )

