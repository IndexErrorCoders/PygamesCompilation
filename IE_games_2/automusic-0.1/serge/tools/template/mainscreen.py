"""The main screen for the game"""

import random
import math
import pygame


import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common 

class MainScreen(serge.blocks.actors.ScreenActor):
    """The logic for the main screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(MainScreen, self).__init__('item', 'main-screen')
        self.options = options

    def addedToWorld(self, world):
        """Added to the world"""
        super(MainScreen, self).addedToWorld(world)
        #
        # Cheating
        if self.options.cheat:
            fps = serge.blocks.utils.addActorToWorld(world,
                serge.blocks.actors.FPSDisplay(G('fps-x'), G('fps-y'), G('fps-colour'), G('fps-size')))

    def updateActor(self, interval, world):
        """Update this actor"""
        super(MainScreen, self).updateActor(interval, world)
            
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = MainScreen(options)
    world = serge.engine.CurrentEngine().getWorld('main-screen')
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(), 'keyboard-quit')
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

