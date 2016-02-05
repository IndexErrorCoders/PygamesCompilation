"""The user paused the game"""

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
import mainscreen
import gameboard

class ResumeScreen(gameboard.GameBoard):
    """The logic for the resume screen"""
    
    
    def __init__(self):
        """Initialise the screen"""
        super(ResumeScreen, self).__init__('item', 'resume-screen')
        

    def addedToWorld(self, world):
        """The actor is ready to be populated"""
        super(ResumeScreen, self).addedToWorld(world)
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
                layer_name='ui', center_position=G('menu-position'))
        #
        self.restart = self.menu_block.addActor(serge.blocks.actors.StringText('restart', 'restart',
            'Restart', colour=G('menu-colour'), font_size=G('menu-font-size')))
        self.play = self.menu_block.addActor(serge.blocks.actors.StringText('play', 'play',
            'Resume', colour=G('menu-colour'), font_size=G('menu-font-size')))
        self.quit = self.menu_block.addActor(serge.blocks.actors.StringText('quit', 'quit',
            'Quit', colour=G('menu-colour'), font_size=G('menu-font-size')))
        #
        self.restart.linkEvent(serge.events.E_LEFT_CLICK, self.doStart)
        self.play.linkEvent(serge.events.E_LEFT_CLICK, self.doPlay)
        self.quit.linkEvent(serge.events.E_LEFT_CLICK, self.doQuit)
        #
        self.music_toggle = musictoggle.addToggle(world)
        #
        # Create interesting display
        self.initGrid(world, 'start')
        self.initPlayers(world, 'start', interactive=False)
                
    def doStart(self, obj, arg):
        """Go to the start"""
        self.log.info('Clicked on start')
        world = self.engine.getWorld('main-screen')
        world.clearActors()
        mainscreen.main(self.options)
        self.engine.setCurrentWorldByName('start-screen')
        
    def doPlay(self, obj, arg):
        """Play the game"""
        self.log.info('Clicked on play')
        self.engine.setCurrentWorldByName('main-screen')
        
    def doQuit(self, obj, arg):
        """Quit the game"""
        self.log.info('Clicked on quit')
        self.engine.stop()
        
        
def main(options):
    """Create the main logic"""
    world = serge.engine.CurrentEngine().getWorld('resume-screen')
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    manager.assignBehaviour(manager, serge.blocks.behaviours.KeyboardQuit(), 'quit')
    world.addActor(manager)
    #
    # The screen actor
    s = ResumeScreen()
    s.manager = manager
    s.options = options
    world.addActor(s)
