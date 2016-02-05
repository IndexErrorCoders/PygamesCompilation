"""Screen for credits"""


import pygame

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.layout
import serge.blocks.directions
import serge.blocks.effects

from theme import G, theme
import common 
import ghost
import objects
import musictoggle

class CreditsScreen(serge.blocks.actors.ScreenActor):
    """The logic for the credits screen"""
    
    
    def __init__(self):
        """Initialise the screen"""
        super(CreditsScreen, self).__init__('item', 'credit-screen')
        self.back = 'start-screen'

    def addedToWorld(self, world):
        """The actor is ready to be populated"""
        super(CreditsScreen, self).addedToWorld(world)
        #
        # Block for titles
        self.title_block = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.layout.VerticalBar('title-block', height=G('title-height')), 
                layer_name='ui', center_position=G('title-position'))
        #
        # Titles
        self.title_block.addActor(serge.blocks.actors.StringText('t', 't',
            'TACMAN', colour=G('title-colour'), font_size=G('title-font-size')))
        self.title_block.addActor(serge.blocks.actors.StringText('st', 'st',
            ' Turn-based, tactical PACMAN', colour=G('subtitle-colour'), font_size=G('subtitle-font-size')))
        #
        # Version
        self.version = serge.blocks.utils.addVisualActorToWorld(world, 'v', 'v', 
            serge.visual.Text(('v%s' % common.version), colour=G('version-colour'), font_size=G('version-font-size')),
            layer_name='ui', center_position=G('version-position'))
        #
        # Block for menu
        self.menu_block =  serge.blocks.utils.addActorToWorld(world,
            serge.blocks.layout.HorizontalBar('menu-block', height=G('menu-height'), width=G('menu-width')), 
                layer_name='ui', center_position=G('credits-menu-position'))
        #
        self.back = self.menu_block.addActor(serge.blocks.actors.StringText('back', 'back',
            'Back', colour=G('menu-colour'), font_size=G('menu-font-size')))
        self.back.linkEvent(serge.events.E_LEFT_CLICK, self.doBack)
        #
        self.bg = serge.blocks.utils.addSpriteActorToWorld(world, 'bg', 'bg', 'credits', 'main', 
            center_position=G('credits-bg-position'))
        #
        musictoggle.addToggle(world)
        
    def doBack(self, obj, arg):
        """Back to the start"""
        self.log.info('Clicked on back')
        self.engine.setCurrentWorldByName(self.back)
        
        
def main(options):
    """Create the main logic"""
    world = serge.engine.CurrentEngine().getWorld('credit-screen')
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(), 'keyboard-quit')
    #
    # The screen actor
    s = CreditsScreen()
    s.manager = manager
    world.addActor(s)
