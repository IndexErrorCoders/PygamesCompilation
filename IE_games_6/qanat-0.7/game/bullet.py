"""Represents a bullet"""

import math
import random

import serge.actor
import serge.visual
import serge.events
import serge.blocks.behaviours
from serge.simplevecs import Vec2d

from theme import G
import common 


class Bullet(serge.actor.Actor):
    """Represents a bullet"""
    
    has_gravity = False

    def __init__(self, x, y, speed, target, sprite, event, angle=-0, direction=-1):
        """Initialise the bullet"""
        super(Bullet, self).__init__(sprite)
        self.moveTo(x, y)
        self.initial_speed = speed
        self.target = target
        self.event = event
        self.angle = angle if direction == -1 else 45
        self.direction = direction
        self.broadcaster = serge.events.getEventBroadcaster()
        
    def addedToWorld(self, world):
        """The bullet was added to the world"""
        self.setSpriteName(self.tag)
        self.setLayerName('foreground')
        self.world = world
        self.setAngle(self.angle)
        if self.direction == -1:
            self.speed = self.initial_speed
        else:
            self.speed = -self.initial_speed

    def updateActor(self, interval, world):
        """Update the bullet position"""
        #
        # Move the bullet
        dx, dy = (
            self.speed*math.cos(math.radians(self.angle)), 
            -self.speed*math.sin(math.radians(self.angle)) + 
                (G('bullet-fragment-force')*interval/1000.0 if self.has_gravity else 0)
        )
        self.move(dx, dy)
        self.setAngle(-Vec2d(dx, dy).get_angle_degrees())
        #
        if G('bullet-offscreen-highy') < self.y or G('bullet-offscreen-lowy') > self.y or \
           G('bullet-offscreen-highx') < self.x or G('bullet-offscreen-lowx') > self.x:
            world.scheduleActorRemoval(self)
            self.log.debug('Bullet off screen')
        #
        # Look for collisions
        for actor in self.world.findActorsByTag(self.target):
            if actor.active and self.isOverlapping(actor):
                self.log.info('Bullet %s collided with %s' % (self.getNiceName(), actor.getNiceName()))
                self.broadcaster.processEvent((self.event, (self, actor)))
        #
        if self.direction != -1:
            self.speed -= self.direction*interval/1000.0


class HotBullet(Bullet):
    """Represents a hot bullet"""

    bomb_direction = 1
    bomb_fragments = 3.0
    explosion_sound = 'bullet-fragment'

    def __init__(self, *args, **kw):
        """Intialise the bullet"""
        super(HotBullet, self).__init__(*args, **kw)
        self.explosion_probability = G('hot-bullet-explosion-probability')
        
    def updateActor(self, interval, world):
        """Update the bullet"""
        super(HotBullet, self).updateActor(interval, world)
        #
        # Watch to see if we are going to explode
        if random.random() < self.explosion_probability * interval/1000.0:
            self.log.debug('Hot bullet is exploding')
            self.explodeBullet(world)

    def explodeBullet(self, world):
        """The bullet explodes into fragments"""
        explosion = serge.blocks.actors.AnimateThenDieActor(
            'explosion', 'explosion', 'air-explosion', 'effects', self)
        explosion.setZoom(G('bullet-fragment-explosion-zoom'))
        self.world.addActor(explosion)
        serge.sound.Sounds.play(self.explosion_sound)
        #
        # Create some fragments of the bullet
        total_velocity = Vec2d(0, self.bomb_direction * self.speed)
        for idx in range(int(self.bomb_fragments)):
            #
            # Create velocity of the fragment
            if idx != self.bomb_fragments - 1:
                v = Vec2d(
                    random.uniform(*G('bullet-fragment-vx-range')),
                    self.bomb_direction * random.uniform(*G('bullet-fragment-vy-range')))
                total_velocity -= v/self.bomb_fragments
            else:
                # Conserve x momentum of all fragments
                v = self.bomb_fragments * total_velocity
            #
            # Create the fragment
            fragment = Bullet(self.x, self.y, v.length, self.target, self.getSpriteName(), self.event,
                v.get_angle_degrees(), self.direction)
            self.world.addActor(fragment)
        #
        world.scheduleActorRemoval(self)


class ExplodingBomb(HotBullet):
    """A bomb that explodes into fragments at a certain height"""

    bomb_direction = -1
    explosion_sound = 'bomb-fragment'

    def __init__(self, *args, **kw):
        """Initialise the bomb"""
        super(ExplodingBomb, self).__init__(*args, **kw)
        #
        properties = random.choice(G('explosion-possibles', 'bomb'))
        self.explosion_height, self.bomb_fragments = properties
        self.explosion_probability = 0

    def updateActor(self, interval, world):
        """Update the bullet"""
        super(ExplodingBomb, self).updateActor(interval, world)
        #
        # Watch to see if we are going to explode
        if self.y > self.explosion_height:
            self.log.debug('Exploding bomb is exploding')
            self.explodeBullet(world)