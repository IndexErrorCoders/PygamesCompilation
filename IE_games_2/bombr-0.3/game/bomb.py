"""A bomb on the screen"""

import random

import serge.sound
import serge.events
from serge.simplevecs import Vec2d
import serge.blocks.actors
import serge.blocks.animations

from theme import G, theme
import boardobject


class Bomb(boardobject.BoardObject):
    """A bomb on the screen"""

    state_id = 'B'
    is_explosion_barrier = False
    is_fragile = True
    fuse = G('explosion-propagation-time')
    max_distance = G('explosion-propagation-distance')
    explosion_time = G('explosion-time')
    propagation_time = G('explosion-propagation-time')

    def __init__(self, board, auto_explode=True):
        """Initialise the bomb"""
        super(Bomb, self).__init__('board-item')
        #
        self.setSpriteName(G('bomb-sprite'))
        self.setLayerName('bombs')
        #
        self.board = board
        self.auto_explode = auto_explode
        self.fuse = G('bomb-fuse-time')

    def addedToWorld(self, world):
        """Added to the world"""
        super(Bomb, self).addedToWorld(world)
        #
        self.world = world

    def updateActor(self, interval, world):
        """Update the actor"""
        super(Bomb, self).updateActor(interval, world)
        #
        self.fuse -= interval / 1000.0
        if self.fuse <= 0 and self.auto_explode:
            self.explodeBomb()

    def explodeBomb(self):
        """Explode the bomb"""
        self.log.debug('Bomb %s exploding' % self.getNiceName())
        serge.sound.Sounds.play('explode')
        explosion = Explosion(
            self.world, self.board, (self.x, self.y), [(-1, 0), (+1, 0), (0, -1), (0, +1)], 0)
        self.world.addActor(explosion)
        self.board.addManAt(explosion, self.board.getPosition(self))
        self.world.scheduleActorRemoval(self)
        self.board.addBombBlast(self)
        self.board.removeMan(self)

    def isMoveBlockedBy(self, other):
        """Return True if we are blocked by another"""
        raise NotImplemented('This should never be called for a bomb')

    def manMovesOnto(self, other):
        """Called when another man moves onto us"""
        if other.is_deadly:
            self.fuse = 0
            self.auto_explode = True


class Explosion(boardobject.BoardObject):
    """Represents an explosion coming from a bomb"""

    state_id = 'E'
    is_blockage = False
    is_deadly = True
    is_explosion_barrier = False

    fuse = G('explosion-propagation-time')
    max_distance = G('explosion-propagation-distance')
    max_time = G('explosion-time')
    after_explosion_sprite = G('after-explosion-sprite')

    number_particles = G('explosion-number')
    range_particles = G('explosion-range')
    particle_velocity = G('explosion-velocity')
    particle_sprites = G('explosion-sprites')
    particle_angular = G('explosion-angular')

    number_block_particles = G('block-number')
    block_velocity_particles = G('block-velocity')
    block_angular_velocity = G('block-angular-velocity')
    block_sprites = G('block-sprites')
    block_range = G('block-range')
    block_gravity = G('block-gravity')

    def __init__(self, world, board, (x, y), directions, distance):
        """Initialise the explosion"""
        super(Explosion, self).__init__('board-item')
        #
        #self.setSpriteName(G('explosion-sprite'))
        self.setLayerName('bombs')
        #
        self.world = world
        self.board = board
        self.directions = directions
        self.distance = distance
        #
        self._can_propagate = distance < self.max_distance
        #
        self.moveTo(x, y)
        self.createParticles(world, self.number_particles)

    def createParticles(self, world, particles):
        """Create some nice particles"""
        for i in range(particles):
            particle = serge.blocks.actors.SimplePhysicsActor(
                'particle', 'explosion',
                velocity=Vec2d(random.randrange(*self.particle_velocity), 0).rotated_degrees(random.randrange(0, 360)),
                angular_velocity=0.0,
                bounds=((self.x - self.range_particles, self.x + self.range_particles),
                (self.y - self.range_particles, self.y + self.range_particles))
            )
            particle.setLayerName('particles')
            particle.setSpriteName(random.choice(self.particle_sprites))
            particle.moveTo(self.x, self.y)
            particle.setAngle(random.randrange(0, 360))
            world.addActor(particle)
            #
            # Add animation to particle
            particle.addAnimation(
                serge.blocks.animations.TweenAnimation(
                    particle, 'setZoom', 3.0, 0.1, self.max_time * 1100.0, is_method=True,
                ),
                'enlarge'
            )

    def updateActor(self, interval, world):
        """Update the actor"""
        super(Explosion, self).updateActor(interval, world)
        #
        if random.random() < 0.1:
            self.createParticles(world, 1)
        #
        self.fuse -= interval / 1000.0
        if self._can_propagate and self.fuse <= 0:
            self.propagateExplosion()
            self._can_propagate = False
        elif -self.fuse > self.max_time:
            self.removeExplosion()

    def propagateExplosion(self):
        """Move the explosion to a new place"""
        for direction in self.directions:
            #
            # Get new location
            x, y = self.board.getPosition(self)
            nx, ny = (x + direction[0], y + direction[1])
            #
            # Can we move to the new location
            if self.board.canMove(self, direction):
                new_explosion = self.__class__(self.world, self.board,
                                               self.board.screenLocation((nx, ny)), [direction], self.distance + 1)
                self.world.addActor(new_explosion)
                self.board.addManAt(new_explosion, (nx, ny))
            elif self.board.canDestroy((nx, ny)):
                #
                # Destroy the block
                self.log.debug('Removing block from the board at %s, %s' % (nx, ny))
                self.board.destroyItemAt((nx, ny), self.after_explosion_sprite)
                self.explodeBlock()
                #
                # Add an explosion to cover the exploded block but make it so
                # that the explosion will not propagate
                new_explosion = self.__class__(self.world, self.board,
                                               self.board.screenLocation((nx, ny)), [direction], self.max_distance)
                self.world.addActor(new_explosion)
                self.board.addManAt(new_explosion, (nx, ny))

    def removeExplosion(self):
        """Remove the explosion"""
        self.log.debug('Removing explosion')
        self.world.scheduleActorRemoval(self)
        self.board.removeMan(self)

    def isMoveBlockedBy(self, other):
        """Return True if we are blocked by another"""
        return other.is_explosion_barrier

    def manMovesOnto(self, other):
        """Called when another moves onto this"""
        if other.is_fragile:
            other.manMovesOnto(self)

    def explodeBlock(self):
        """Explode a block"""
        serge.sound.Sounds.play('block-break')
        for i in range(self.number_block_particles):
            particle = serge.blocks.actors.SimplePhysicsActor(
                'particle', 'block-explosion',
                velocity=Vec2d(random.randrange(*self.block_velocity_particles), 0).rotated_degrees(random.randrange(0, 360)),
                angular_velocity=random.randrange(*self.block_angular_velocity),
                bounds=((self.x - self.block_range, self.x + self.block_range),
                (self.y - self.block_range, self.y + self.block_range)),
                gravity=Vec2d(self.block_gravity)
            )
            particle.setLayerName('particles')
            particle.setSpriteName(random.choice(self.block_sprites))
            particle.moveTo(self.x, self.y)
            particle.setAngle(random.randrange(0, 360))
            self.world.addActor(particle)