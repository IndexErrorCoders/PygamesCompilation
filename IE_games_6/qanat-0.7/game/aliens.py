"""Represents the aliens"""

import random
import math

import serge.actor
import serge.visual
import serge.events
import serge.blocks.behaviours
import serge.blocks.actors
import serge.common
import serge.sound
from serge.simplevecs import Vec2d

from theme import G
import common
import bullet
import smoke

COLOURS = {
    'r': 'red',
    'b': 'blue',
    'y': 'yellow',
    'g': 'green',
    'f': 'fire',
    'v': 'violet',
    'B': 'bomb',
}
SCORES = {
    'blue': 125,
    'red': 275,
    'yellow': 325,
    'green': 380,
    'fire': 420,
    'violet': 450,
    'bomb': 650,
}


class Wave(serge.actor.CompositeActor):
    """Represents a wave of aliens - essentially a single row"""

    def __init__(self, row, x, y, aliens):
        """Initialise the wave"""
        super(Wave, self).__init__('wave')
        self.init_position = (x, y)
        self.aliens = aliens
        self.chaser = None
        self.row = row

    def addedToWorld(self, world):
        """Add this wave to the world"""
        super(Wave, self).addedToWorld(world)
        self.log.info('Creating new wave %s' % self.getNiceName())
        for idx, colour_id in enumerate(self.aliens):
            if colour_id != ' ':
                x = self.init_position[0] - (float(idx) - (len(self.aliens) / 2.0)) * G('alien-x-spacing')
                alien = ALIEN_TYPES.get(colour_id, ForceBasedAlien)(x, self.init_position[1], COLOURS[colour_id])
                alien.score = SCORES[alien.colour]
                self.addChild(alien)
        self.setLeader()
        self.manager = world.findActorByName('behaviours')
        self.player = world.findActorByName('player')

    def setLeader(self):
        """Set the leader for the wave"""
        children = self.getChildren()
        if children:
            self.leader = children[int(len(children) / 2)]
        else:
            self.leader = None

    def isComplete(self):
        """Return True when this wave is complete"""
        return not self.hasChildren()


# FEATURE: make emerging aliens ignore the target_x for the first ~5 seconds of flight

class TimedWave(Wave):
    """Represents a wave of aliens that are released on a time basis"""

    def __init__(self, row, x, y, (delay, aliens)):
        """Initialise the wave"""
        super(TimedWave, self).__init__(row, x, y, aliens)
        #
        self.initial_y = G('timed-wave-initial-y')
        self.target_y = G('timed-wave-target-y')
        self.ship_y = G('ship-y')
        self.wave_counter = delay
        self.wave_started = False

    def addedToWorld(self, world):
        """Add this wave to the world"""
        super(Wave, self).addedToWorld(world)
        #
        self.setSpriteName('mother-ship')
        self.setLayerName('ship')
        self.y = self.ship_y

    def updateActor(self, interval, world):
        """Update the wave"""
        super(TimedWave, self).updateActor(interval, world)
        #
        self.wave_counter -= interval / 1000.0
        if not self.wave_started and self.wave_counter <= 0:
            self.log.info('Creating new wave %s' % self.getNiceName())
            self.wave_started = True
            for idx, colour_id in enumerate(self.aliens):
                if colour_id != ' ':
                    x = self.init_position[0] - (float(idx) - (len(self.aliens) / 2.0)) * G('alien-x-spacing')
                    alien = ALIEN_TYPES.get(colour_id, ForceBasedAlien)(x, self.initial_y, COLOURS[colour_id])
                    alien.score = SCORES[alien.colour]
                    alien.target_y = self.target_y
                    self.addChild(alien)
            self.setLeader()
            self.manager = world.findActorByName('behaviours')
            self.player = world.findActorByName('player')

    def setLeader(self):
        """Set the leader for the wave"""
        children = self.getChildren()
        if children:
            self.leader = children[int(len(children) / 2)]
        else:
            self.leader = None

    def isComplete(self):
        """Return True when this wave is complete"""
        return self.wave_started and not self.hasChildren()


class Alien(serge.actor.Actor):
    """An alien"""

    bomb_class = bullet.Bullet

    def __init__(self, x, y, colour):
        """Initialise the Alien"""
        self.colour = colour
        super(Alien, self).__init__('alien', '%s-alien' % self.colour)
        self.init_position = (x, y)
        self.bomb_prob = G('bomb-prob', self.colour)
        self.bomb_direction = G('bomb-direction', self.colour)
        self.vx = self.vy = 0.0
        self.drop_angle = -90.0
        self.crashing = False
        self.fractured = False

    def addedToWorld(self, world):
        """The bullet was added to the world"""
        self.setSpriteName('%s-alien' % self.colour)
        self.setLayerName('foreground')
        self.moveTo(*self.init_position)
        self.world = world
        self.manager = world.findActorByName('behaviours')
        self.player = world.findActorByName('player')

    def updateActor(self, interval, world):
        """Update the bullet position"""
        super(Alien, self).updateActor(interval, world)
        #
        # Do we want to drop a bomb
        if not self.crashing and random.random() < self.bomb_prob:
            self.dropBomb()

    def dropBomb(self):
        """Drop a bomb"""
        self.log.info('%s dropping a bomb' % self.getNiceName())
        b = self.bomb_class(
            self.x, self.y + G('bomb-offset', self.colour),
            G('bomb-speed', self.colour), 'player', G('bomb-sprite', self.colour),
            common.E_PLAYER_DESTROYED, angle=self.drop_angle, direction=self.bomb_direction)
        self.world.addActor(b)


class ForceBasedAlien(Alien):
    """An alien moving in a force field with various repulsive and attracive forces"""

    def __init__(self, x, y, colour):
        """Initialise the ForceBasedAlien"""
        super(ForceBasedAlien, self).__init__(x, y, colour)
        self.target_y = y
        self.da = 0.0
        self.descending = False

    def addedToWorld(self, world):
        """The alien was added to the world"""
        super(ForceBasedAlien, self).addedToWorld(world)
        self.repulsive_force = G('repulsive-force', self.colour)
        self.attractive_force = G('attractive-force', self.colour)
        self.player_force = G('player-force', self.colour)
        self.vertical_force = G('vertical-force', self.colour)
        self.bullet_force = G('bullet-force', self.colour)
        self.descend_prob = G('descend-prob', self.colour)
        self.descend_amount = G('descend-amount', self.colour)
        self.target_offset = G('target-offset', self.colour)
        self.point_at_player = G('point-at-player', self.colour)
        self.fracture_probability = G('alien-fracture-probability')
        self.max_player_force_diff = G('max-player-force-diff', self.colour)
        self.player = world.findActorByName('player')
        self.broadcaster = serge.events.getEventBroadcaster()

    def updateActor(self, interval, world):
        """Update the wave"""
        super(ForceBasedAlien, self).updateActor(interval, world)
        #
        if random.random() < self.descend_prob:
            self.descending = not self.descending
            self.log.debug('%s changed descent to %s' % (self.getNiceName(), self.descending))
            #
        # Find the forces on the alien based on how we are currently moving
        if self.crashing:
            fx, fy = self.getCrashingForces()
            world.addActor(smoke.Smoke(self))
        else:
            fx, fy = self.getFlyingForces()
            #
        # Update actor
        self.vx += fx * interval / 1000
        self.vy += fy * interval / 1000
        self.x += self.vx * interval / 1000
        self.y += self.vy * interval / 1000
        #
        # Change the angle of the ship
        if self.crashing:
            self.setAngle(self.getAngle() + self.da * interval / 1000.0)
        elif self.point_at_player:
            player_angle = math.degrees(math.atan((self.player.x - self.x) / (self.player.y - self.y)))
            self.setAngle(player_angle)
            self.drop_angle = player_angle - 90
        else:
            if self.vx < -1:
                self.setAngle(-self.vx / 5)
            elif self.vx > 1:
                self.setAngle(-self.vx / 5)
            else:
                self.setAngle(0)
                #
            # Watch for crashing alien dropping off the screen
        if self.y > G('alien-offscreen-highy'):
            self.log.debug('Removing crashed alien %s' % self.getNiceName())
            self.world.scheduleActorRemoval(self)
            explosion = serge.blocks.actors.AnimateThenDieActor('explosion', 'explosion', 'ground-explosion', 'effects')
            explosion.moveTo(self.x, G('explosion-y'))
            world.addActor(explosion)
            serge.sound.Sounds.play('crash')
            #
        # Watch out to see if we collided with the player
        if self.player.active and self.isOverlapping(self.player):
            self.broadcaster.processEvent((common.E_PLAYER_DESTROYED, (self, self.player)))

    def getFlyingForces(self):
        """Return the force on the alien during normal flight"""
        #
        fx = fy = pfx = pfy = bfx = bfy = player_angle = 0.0
        for actor in self.world.getActors():
            if actor != self:
                dfx = dfy = 0.0
                if actor.tag == 'alien' or actor.tag == 'fragment':
                    dfx, dfy = self.getForce(self, actor)
                elif actor.tag == 'player':
                    pfx, pfy = self.getPlayerForce(self, actor)
                    player_angle = math.degrees(math.atan((actor.x - self.x) / (actor.y - self.y)))
                elif actor.tag == 'player-bullet':
                    ddfx, ddfy = self.getBulletForce(self, actor)
                    bfx += ddfx
                    bfy += ddfy
                fx += dfx
                fy += dfy
            #
        if bfx == 0 and bfy == 0:
            fx += pfx
            fy += pfy
        else:
            fx += bfx
            fy += bfy
            #
        dfx, dfy = self.getVerticalForce()
        fx += dfx - 1.0 * self.vx
        fy += dfy - 1.0 * self.vy
        #
        return fx, fy

    def getCrashingForces(self):
        """Return the force on the alien when we are crashing"""
        fx = G('alien-falling-horizontal-force') * math.copysign(math.cos(math.radians(self.getAngle())),
                                                                 self.getAngle())
        fy = G('alien-falling-force')
        return fx, fy

    def getForce(self, a, b):
        """Return the force between the two actors"""
        v = Vec2d(a.x, a.y) - Vec2d(b.x, b.y)
        d = max(v.length / 4, 0.1)
        f1 = +self.attractive_force / (d * 0.05) ** 4
        f2 = -self.repulsive_force / (d * 0.2) ** 2
        f = (f1 + f2) * v.normalized()
        return f.x, f.y

    def getPlayerForce(self, a, b):
        """Return the force between the two aliens"""
        base_diff = b.x - a.x
        diff = math.copysign(min(self.max_player_force_diff, base_diff), base_diff)
        d = diff - math.copysign(self.target_offset, diff)
        return (self.player_force * math.copysign((d - 20), d) if abs(d) > 20 else 0), 0

    def getVerticalForce(self):
        """Return the force to keep one the same row"""
        d = self.y - (self.target_y if not self.descending else self.target_y + self.descend_amount)
        return 0, -(self.vertical_force * d) - .8 * self.vy

    def getBulletForce(self, a, b):
        """Return the force between the the bullet"""
        d = a.x - b.x
        fx = math.copysign(-self.bullet_force / max(abs(d), 1), d) if abs(d) < 50 else 0
        return fx, 0

    def hitByBomb(self, bomb):
        """The alien was hit by a bomb"""
        if not self.crashing:
            self.da = G('alien-bomb-angle-multiplier') * (bomb.x - self.x)
            self.crashing = True
            self.createExplosion()
        elif not self.fractured:
            if random.random() < self.fracture_probability:
                self.fractureAlien()

    def fractureAlien(self):
        """Fracture this alien in two"""
        current_velocity = Vec2d(self.vx, self.vy)
        #
        # Send one fragment off in a randomized direction. Set the other one
        # based on conservation of momentum. 
        delta_angle = random.uniform(*G('alien-fracture-angle-range'))
        v1 = current_velocity.rotated_degrees(delta_angle)
        v2 = current_velocity - v1
        #
        # Do the same for the spins
        da1 = random.uniform(*G('alien-fracture-spin'))
        da2 = self.da - da1
        #
        # Set our new properties
        self.setSpriteName('%s-half' % self.colour)
        self.fractured = True
        self.vx, self.vy = v1
        self.da = da1
        self.score = 0
        #
        # Create another fragment
        other = self.__class__(self.x, self.y, self.colour)
        self.world.addActor(other)
        other.setSpriteName(self.getSpriteName())
        other.vx, other.vy = v2
        other.da = da2
        other.visual.setCell(1)
        other.fractured = other.crashing = True
        other.score = 0
        #
        self.createExplosion()

    def createExplosion(self):
        """Create an explosion at our current position"""
        serge.sound.Sounds.play('alien-explosion')
        serge.sound.Sounds.play('fall')
        explosion = serge.blocks.actors.AnimateThenDieActor('explosion', 'explosion', 'air-explosion', 'main', self)
        explosion.setZoom(random.uniform(*G('alien-explosion-zoom')))
        self.world.addActor(explosion)


class BombAlien(ForceBasedAlien):
    """An alien that has a big bomb that falls every so often"""

    bomb_class = bullet.ExplodingBomb

    def __init__(self, x, y, colour):
        """Initialise the alien"""
        super(BombAlien, self).__init__(x, y, colour)
        #
        self.bomb_interval = G('bomb-interval', self.colour)
        self.bomb_delay = G('bomb-delay', self.colour)
        self.bomb_counter = random.random() * self.bomb_interval + self.bomb_delay
        self.bomb_doors_open = False

    def updateActor(self, interval, world):
        """Update the alien"""
        super(BombAlien, self).updateActor(interval, world)
        #
        # Now check the bomb doors
        self.bomb_counter -= interval / 1000.0
        if self.bomb_counter <= 0:
            self.dropBomb()
            self.bomb_counter = self.bomb_delay + self.bomb_interval
            self.closeBombDoors()
        elif not self.bomb_doors_open and self.bomb_counter <= self.bomb_delay:
            self.openBombDoors()

    def openBombDoors(self):
        """Open the bomb doors"""
        self.log.debug('Opening bomb doors for %s' % self.getNiceName())
        self.setSpriteName('%s-open-alien' % self.colour)
        self.bomb_doors_open = True

    def closeBombDoors(self):
        """Close the bomb doors"""
        self.log.debug('Closing bomb doors for %s' % self.getNiceName())
        self.setSpriteName('%s-alien' % self.colour)
        self.bomb_doors_open = False


ALIEN_TYPES = {
    'B': BombAlien,
}

WAVE_CONTROLLERS = {
    'normal': Wave,
    'time-based': TimedWave,
}