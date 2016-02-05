"""The representation of the gun

The gun fires but can overheat

"""

import pygame
import sys
import os
import time

import serge.actor
import serge.visual
import serge.events
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.utils
import serge.blocks.scores

from theme import G
import common


class Gun(serge.blocks.actors.ScreenActor):
    """The gun on the screen"""

    def __init__(self, tag, name):
        """Initialise the Gun"""
        super(Gun, self).__init__(tag, name)
        self.fire_rate = G('gun-fire-rate')
        
    def addedToWorld(self, world):
        """comment"""
        super(Gun, self).addedToWorld(world)
        #
        # Set up the other visual elements
        self.layout = serge.blocks.layout.Grid('grid', 'gun-grid', (2, 4),
            G('gun-grid-width'), G('gun-grid-height'))
        self.layout.setLayerName('main')
        self.layout.moveTo(*G('gun-grid-position'))
        world.addActor(self.layout)
        #
        # Labels
        self.temp_label = serge.blocks.actors.StringText('text', 'temp', 'Temp', colour=G('gun-label-colour'),
            font_size=G('gun-label-size'), justify='center')
        self.layout.addActor((0, 1), self.temp_label)
        #
        # Bars
        self.temp = serge.actor.Actor('ammo', 'ammo')
        self.temp.visual = serge.blocks.visualblocks.ProgressBar(G('gun-bar-size'), 
            value_ranges=G('gun-bar-temp-range'),
            border_colour=G('gun-bar-border-colour'), border_width=G('gun-bar-border-size'))
        self.layout.addActor((1, 1), self.temp)
        #
        self.counter = serge.blocks.actors.NumericText('counter', 'counter', '%d', colour=G('gun-label-colour'),
            font_size=G('gun-counter-size'), justify='left', value=0)
        self.counter.moveTo(self.temp.x + G('gun-counter-offset-x'), self.temp.y + G('gun-counter-offset-y'))
        self.counter.setLayerName('main')
        world.addActor(self.counter)
        #
        self.player = world.findActorByName('player')
        #
        self.resetGun()
        
    def canShoot(self):
        """Return True if we can shoot"""
        return self.temp_lockout_timer <= 0 
        
    def takeShot(self):
        """Take a shot"""
        if self.temp.visual.value + G('gun-fire-temp') >= G('gun-max-temp'):
            #
            # Gun too hot - lock it out
            self.temp.visual.value = G('gun-max-temp')
            self.temp_lockout_timer = G('gun-temp-lockout-time')
            self.counter.active = True
            self.counter.value = G('gun-temp-lockout-time')
            self.player.gunOverheated()
        else:
            serge.sound.Sounds.play('shoot')
            if self.temp_lockout_timer == 0:
                self.temp.visual.value += G('gun-fire-temp')
            
    def updateActor(self, interval, world):
        """comment"""
        super(Gun, self).updateActor(interval, world)
        #
        if self.temp_lockout_timer == 0:
            self.temp.visual.value = max(0, self.temp.visual.value-(interval/1000.0)/G('gun-temp-cool-rate'))
        elif self.temp_lockout_timer == -1:
            self.temp.visual.value = max(0, self.temp.visual.value-(interval/1000.0)/G('gun-temp-fast-cool-rate'))
            if self.temp.visual.value == 0:
                self.temp_lockout_timer = 0
        else:
            self.temp_lockout_timer -= interval/1000.0
            self.counter.value = int(self.temp_lockout_timer)
            if self.temp_lockout_timer <= 0:
                self.temp_lockout_timer = -1
                self.counter.active = False
                self.player.gunNormal()
                
    def resetGun(self):
        """Reset the gun"""
        self.temp.visual.value = 0
        self.temp_lockout_timer = 0
        self.counter.active = False
        self.fire_rate = G('gun-fire-rate')
        
    def makeHarder(self):
        """Make it harder"""
        self.fire_rate = self.fire_rate+1
        
    def regenerateOnce(self, interval):
        """Do a regeneration step"""
        
