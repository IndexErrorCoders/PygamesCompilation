"""Class for all bugs"""

import pygame
import time
import random

import serge.actor
import serge.blocks.actors
from serge.simplevecs import Vec2d

from theme import G, theme
import common 

class Bug(serge.blocks.actors.ScreenActor):
    """Initialise the bug"""
    
    def __init__(self, tag, name, bug_type, parent):
        """Initialise the bug"""
        super(Bug, self).__init__(tag, '%s-%s' % (name, bug_type))
        self.parent = parent
        self.bug_type = bug_type
        #
        self.setSpriteName('bug')
        self.setLayerName('actors')
        #
        self.setAngle(random.randrange(0, 360))
        self.velocity = Vec2d(0, 0)
        self.mass = G('mass', self.bug_type)
        #
        # Forces for determining motion
        self.wall_attraction = G('wall-attraction', self.bug_type)
        self.player_attraction = G('player-attraction', self.bug_type)
        self.bug_attraction = G('bug-attraction', self.bug_type)
        self.damping_velocity, self.damping_force = G('damping-force', self.bug_type)
        self.light_target, self.light_force, self.light_power = G('light-target', self.bug_type)
        
    def updateActor(self, interval, world):
        """Update the bug"""
        super(Bug, self).updateActor(interval, world)
        #
        # Get overall force from environment
        force = self.getMovementForces()
        #
        # Slow down if going too fast
        if self.velocity.length >= self.damping_velocity:
            force = force + self.damping_force * self.velocity
        #
        # Calcuate change in conditions
        self.velocity = self.velocity + force/self.mass*interval/1000.0
        self.tryToMove(self.velocity*interval/1000.0)
        self.setAngle(-self.velocity.get_angle_degrees())
          
    def tryToMove(self, (dx, dy)):
        """Try to move"""
        nx, ny = self.x+dx+self.visual.width/2.0, self.y+dy
        x, y = self.parent.cave.layout.getLocation((nx, ny))
        if not self.parent.cave.tilemap.getLayer('rock').tiles[y][x]:
            self.move(dx, dy)
  
    def getMovementForces(self):
        """Return the forces governing movement"""
        #
        x, y = self.x, self.y
        me = Vec2d(x, y)
        cx, cy = self.parent.cave.layout.getLocation((x, y))
        #
        # Repelled from walls
        walls = self.parent.cave.tilemap.getLayer('rock').tiles
        wall_attraction = Vec2d(0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx and dy and walls[cy+dy][cx+dx]:
                    wall_attraction += self.getVectorForce(me, 
                        self.parent.cave.layout.getCoords((cx+dx, cy+dy)), *self.wall_attraction)
        #
        # Player attraction
        player = Vec2d(self.parent.player.x, self.parent.player.y)
        player_attraction = self.getVectorForce(me, player, *self.player_attraction)
        #
        # Bug to bug attraction
        bug_attraction = Vec2d(0, 0)
        for other in self.parent.bugs:
            if other != self:
                bug_attraction += self.getVectorForce(me, Vec2d(other.x, other.y), *self.bug_attraction)
        #
        # Light attraction
        light_field = self.parent.cave.light_field
        light_attraction = Vec2d(0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx and dy:
                    #
                    # If the test location is a wall, assume it is as bright as the current location
                    if walls[cy+dy][cx+dx]:
                        light_level = light_field[cy][cx][0]
                    else:
                        light_level = light_field[cy+dy][cx+dx][0]
                    #
                    # Calculate a force moving the bug to a specific light level
                    light_attraction += self.getVectorForce(me, 
                        self.parent.cave.layout.getCoords((cx+dx, cy+dy)), 1000,
                        (self.light_target - light_level)*self.light_force, self.light_power)
        #
        #self.log.debug('Forces are %s, %s, %s, %s' % (wall_attraction, player_attraction, bug_attraction, light_attraction))
        #
        return wall_attraction + player_attraction + bug_attraction + light_attraction
        
    def getVectorForce(self, me, target, max_dist, amplitude, power):
        """Return a vector force"""
        offset = target - me
        if offset.length > max_dist:
            return Vec2d(0, 0)
        else:
            return amplitude*offset.normalized()/(max(0.1, offset.length)**power)
            
        
