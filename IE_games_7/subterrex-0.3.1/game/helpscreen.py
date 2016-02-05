"""The help screen for the game"""

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
import tree

class HelpScreen(serge.blocks.actors.ScreenActor):
    """The logic for the help screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(HelpScreen, self).__init__('item', 'help-screen')
        self.options = options

    def addedToWorld(self, world):
        """The screen was added to the world"""
        super(HelpScreen, self).addedToWorld(world)
        #
        # Logo
        L = theme.getTheme('help-screen').getProperty
        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'icon', 'ui', 
            center_position=L('logo-position'))
        #
        # Background
        bh = serge.blocks.utils.addSpriteActorToWorld(world, 'bg', 'bg', L('screen-background-sprite'), 'background', 
            center_position=L('screen-background-position'))
        #
        # Help text
        text = serge.blocks.utils.addSpriteActorToWorld(world, 'text', 'text', 'help-text', 'ui', 
            center_position=L('text-position'))
        #
        # Back link
        back = serge.blocks.utils.addVisualActorToWorld(world, 'button', 'back', 
            serge.visual.Text('Back', L('back-colour'), font_size=L('back-font-size')),
            'ui', 
            center_position=L('help-position'))
        back.linkEvent(serge.events.E_LEFT_CLICK, serge.blocks.utils.backToPreviousWorld('click'))
        #
        # Trees
        tree.addTrees(L, world)


    def updateActor(self, interval, world):
        """Update this actor"""
        super(HelpScreen, self).updateActor(interval, world)
        the_theme = theme.getTheme('help-screen')
        L = the_theme.getProperty
        self.camera.moveTo(*L('screen-background-position'))
                    
    
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = HelpScreen(options)
    world = serge.engine.CurrentEngine().getWorld('help-screen')
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

