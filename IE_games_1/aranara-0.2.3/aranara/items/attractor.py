"""An attractor - attracts (or repels) actors with certain tags"""

import pymunk
import pyglet
import random

from .. import engine
import item
from .. import settings

# TODO: attractor physics should mimic a jet of air rather than just a gravity force


class Attractor(item.BaseItem):
    """An attractor to attract certain tagged actors"""

    particle_tint = None
    max_range = settings.S.attractor_max_range

    def __init__(self, name, sprite_name, attract_tags, attract_function, *args, **kw):
        """Initialise the attractor"""
        super(Attractor, self).__init__(name, pyglet.image.Animation(self.getAnimationFrames()), *args, **kw)
        #
        self.attract_tags = attract_tags
        self.function = attract_function
        self.tracked_actors = []
        #
        self.s1 = engine.SpriteActor(engine.getUID('s1=%s'), 'helium2.png', batch=self.batch)
        self.s2 = engine.SpriteActor(engine.getUID('s1=%s'), 'helium2.png', batch=self.batch)
        self.s3 = engine.SpriteActor(engine.getUID('s1=%s'), 'helium2.png', batch=self.batch)
        self.s1.visible = self.s2.visible = self.s3.visible = settings.S.show_attractors

    def getAnimationFrames(self):
        """Return the animation frames"""
        return [
            pyglet.image.AnimationFrame(pyglet.resource.image('attractor-4.png'), 0.2),
            pyglet.image.AnimationFrame(pyglet.resource.image('attractor-3.png'), 0.2),
            pyglet.image.AnimationFrame(pyglet.resource.image('attractor-2.png'), 0.2),
            pyglet.image.AnimationFrame(pyglet.resource.image('attractor-1.png'), 0.2),
        ]

    def addedToWorld(self, world):
        """The attractor was added to the world"""
        super(Attractor, self).addedToWorld(world)
        #
        self.group = world.ui_front
        #
        # We need to be notified of actors being added and removed so we
        # can add and remove forces
        world.linkEvent(engine.events.E_ACTOR_ADDED, self.actorAdded)
        world.linkEvent(engine.events.E_ACTOR_REMOVED, self.actorRemoved)
        #
        # Get all actors we should be tracking
        for actor in world.getPhysicsActors():
            if actor.tag in self.attract_tags:
                self.tracked_actors.append(actor)

    def actorAdded(self, actor, arg):
        """An actor was added to the world"""
        if actor.tag in self.attract_tags:
            self.tracked_actors.append(actor)

    def actorRemoved(self, actor, arg):
        """An actor was remove from the world"""
        if actor.tag in self.attract_tags:
            self.tracked_actors.remove(actor)

    def updateActor(self, world, dt):
        """Update the attractor"""
        super(Attractor, self).updateActor(world, dt)
        #
        # Add the forces for all tracked actors
        my_position = pymunk.Vec2d(self.position)
        for actor in self.tracked_actors:
            #
            # Calculate the force between the attractor and the actor
            force = 0
            for idx, (fn, extra_offset) in enumerate(self.function):
                attraction_center = my_position + pymunk.Vec2d(extra_offset, 0).rotated_degrees(-self.rotation)
                offset = attraction_center - pymunk.Vec2d(actor.position)
                #
                # Ignore interaction if far away
                if offset.length > self.max_range:
                    break
                magnitude = fn(offset.length)
                force += offset.normalized() * magnitude
            #
            # Apply the force
            actor.addImpulseForce(force)
        #
        # Emit particles to give nice effect
        if settings.S.show_particles and random.random() < settings.S.attractor_particles_per_second / dt:
            p = self.getParticle(dt)
            if self.particle_tint:
                p.color = self.particle_tint
            world.addActor(p)

    def getParticle(self, dt):
        """Return a particle to use for visually highlighting the attraction"""
        angle = random.uniform(-self.rotation - settings.S.attractor_angle_spread,
                               -self.rotation + settings.S.attractor_angle_spread)
        velocity = pymunk.Vec2d(random.uniform(*settings.S.attractor_velocity_spread), 0)
        velocity = velocity.rotated_degrees(angle)
        position = pymunk.Vec2d(self.position) + velocity * settings.S.attractor_particle_lifetime
        #
        return engine.Particle(
            'air.png',
            lifetime=settings.S.attractor_particle_lifetime,
            velocity_fn=engine.Particle.constantValue(-velocity),
            opacity_fn=engine.Particle.fractionalGrow(255, 0.1),
            size_fn=engine.Particle.linearGrow(2.5, -5.0),
            x=position.x, y=position.y, batch=self.batch, group=self.world.ui_back,
        )

    @staticmethod
    def getPowerLawAttractor(reference_force, exponent, reference_distance=30):
        """Return a power law attractor F = A * dist ** B

        The multiplier is the force at the reference distance - this makes
        it easier to balance forces

        """
        multiplier = reference_force / (reference_distance ** exponent)
        def fn(dist):
            return multiplier * (max(dist, reference_distance) ** exponent)
        return fn


class Repeller(Attractor):
    """A unit that repels objects"""

    def getParticle(self, dt):
        """Return a particle to use for visually highlighting the attraction"""
        return engine.Particle(
            'air.png',
            lifetime=settings.S.attractor_particle_lifetime,
            velocity_fn=engine.Particle.constantValue(
                pymunk.Vec2d(random.uniform(
                    *settings.S.attractor_velocity_spread), 0).rotated_degrees(
                        random.uniform(-self.rotation - settings.S.attractor_angle_spread,
                                       -self.rotation + settings.S.attractor_angle_spread),
                ),
            ),
            opacity_fn=engine.Particle.fractionalGrow(255, 0.1),
            size_fn=engine.Particle.linearGrow(1.0, 5.0),
            x=self.x, y=self.y, batch=self.batch, group=self.world.ui_back,
        )

    def getAnimationFrames(self):
        """Return the animation frames"""
        return [
            pyglet.image.AnimationFrame(pyglet.resource.image('repeller-1.png'), 0.2),
            pyglet.image.AnimationFrame(pyglet.resource.image('repeller-2.png'), 0.2),
            pyglet.image.AnimationFrame(pyglet.resource.image('repeller-3.png'), 0.2),
            pyglet.image.AnimationFrame(pyglet.resource.image('repeller-4.png'), 0.2),
        ]