"""Manages the weather in the game"""

import random
import math
import pygame
import time

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.visualeffects

from theme import G, theme
import common 
class Weather(serge.blocks.actors.ScreenActor):
    """Manage the weather in the game"""
    
    def addedToWorld(self, world):
        """The weather was added to the world"""
        self.manager = world.findActorByName('behaviours')
        #
        self.rain_probability = G('rain-probability')
        self.rain_x = G('rain-x')
        self.rain_y = G('rain-y')
        self.rain_dx = G('rain-vx')
        self.rain_dy = G('rain-vy')
        self.rain_limit_x = G('rain-limit-x')
        self.rain_limit_y = G('rain-limit-y')
        #
        self.rain_vx = 0.0
        self.rain_vy = 100.0
    def updateActor(self, interval, world):
        """Update the weather"""
        #
        # Handle rain
        if random.random() < self.rain_probability:
            drop = serge.actor.Actor('drop', 'drop')
            drop.setSpriteName('raindrop')
            drop.setLayerName('main')
            drop.moveTo(random.uniform(*self.rain_x), random.uniform(*self.rain_y))
            self.manager.assignBehaviour(drop, serge.blocks.behaviours.ConstantVelocity(
                random.uniform(*self.rain_dx)+self.rain_vx, 
                random.uniform(*self.rain_dy)+self.rain_vy), 
                'rain-falling')
            self.manager.assignBehaviour(drop, serge.blocks.behaviours.RemoveWhenOutOfRange(
                self.rain_limit_x, self.rain_limit_y), 
                'rain-removing')
            world.addActor(drop)
