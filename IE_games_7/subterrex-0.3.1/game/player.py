"""Represents the player"""

import pygame
import time

import serge.actor
import serge.blocks.actors
from serge.simplevecs import Vec2d

from theme import G, theme
import common 
import climbing

class Player(climbing.Climber):
    """Initialise the player"""
    
    _velocity_flip = 10.0 # Minimum speed to alter the flip status of the sprite
    _falling_trigger = 1.0 # Minimum speed to be classed as falling
        
    def __init__(self, tag, name, maximum_reach=30, surface_tags=('surface',), 
                    jump_impulse=10000, walk_impulse=500, can_scramble=True):
        """Initialise the player"""
        super(Player, self).__init__(tag, name, maximum_reach, surface_tags, 
                    jump_impulse, walk_impulse, can_scramble)
        #
        self.setSpriteName('standing-still')
        self.setLayerName('actors')
        self.setStopped()
        self._flipped = False
        self._framerate_multiplier = G('player-framerate-multiplier')
        self._offset = G('player-surface-detection-offset')
        self._acceleration_silent = G('player-acceleration-silent')
        self._acceleration_death = G('player-acceleration-death')
        self._rock_sound = serge.sound.Sounds.getItem('player-hit-rock')
        #
        
    def addedToWorld(self, world):
        """Added to the world"""
        super(Player, self).addedToWorld(world)
        #
        self.manager = world.findActorByName('behaviours')
        
    def updateActor(self, interval, world):
        """Update the actor"""
        super(Player, self).updateActor(interval, world)
        #
        # Check for death
        if self.acceleration > self._acceleration_death:
            self.log.info('The player died')
            self.processEvent((common.E_PLAYER_DIED, self))
        elif self.acceleration > self._acceleration_silent:
            #
            # Make noise
            self._rock_sound.set_volume(0.4*self.acceleration/self._acceleration_death)
            self._rock_sound.play()
        #
        # Decide whether to flip or not
        v = self.getPhysical().body.velocity[0]
        if abs(v) >= self._velocity_flip:
            self._flipped =  v < 0
        #
        # Are we moving
        angle = 0.0
        if self.isJumping():
            self.setJumping()
        elif self.isHanging():
            if self.isOnSurface(self._offset):
                self.setStopped()
            else:
                self.setHanging()
                #angle = -((self.point_link.b.position-self.point_link.a.position).get_angle_degrees() - 90)
        elif self.isFalling():
            self.setFalling()
        elif self.isWalking():
            self.setWalking(v)
        elif self.getSpriteName() == 'walking':
            if self._last_walked and time.time() - self._last_walked > G('player-walk-time'):
                self.setStopped()
        else:
            self.setStopped()
        #
        # Flip
        self.visual.setHorizontalFlip(self._flipped)  
        #
        # Make sure we stay vertical - the angle code here isn't working very well right
        # now so let's leave it out
        #old_angle = self.getAngle()
        #self.setAngle((angle-old_angle)*0.1+old_angle, sync_physical=True)
        self.setAngle(0, sync_physical=True)
        #
        # Did we get to the bottom of the cave
        if self.y >= G('cave-vertical-screens')*G('screen-height'):
            self.log.info('Bottom of cave reached!')
            self.processEvent((common.E_CAVE_SOLVED, self))
 
                    
        
    def setStopped(self):
        """Stop the walking"""
        self.setSpriteName('standing-still')
        self._last_walked = None
        
    def setWalking(self, velocity):
        """Start walking"""
        self.setSpriteName('walking')
        self._last_walked = time.time()
        self.visual.frame_time = 1000.0/(abs(velocity)*self._framerate_multiplier)
        
    def setJumping(self):
        """Start jumping"""
        self.setSpriteName('standing-jump')

    def setFalling(self):
        """Start falling"""
        self.setSpriteName('falling')
        
    def setHanging(self):
        """Start hanging"""
        self.setSpriteName('hanging')    
        
    def isJumping(self):
        """Return True if we are jumping"""
        return super(Player, self).isJumping() or (self.getSpriteName() == 'standing-jump' and self.visual.running)
        
    def isFalling(self):
        """Return True if we are falling"""
        v = self.getPhysical().body.velocity[1]
        return v >= self._falling_trigger

