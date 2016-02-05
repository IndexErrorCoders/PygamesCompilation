"""The starting screen for the game"""

import copy
import pygame
import networkx
import threading

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
import gameboard

class StartScreen(gameboard.GameBoard):
    """The logic for the start screen"""
    
    
    def __init__(self):
        """Initialise the screen"""
        super(StartScreen, self).__init__('item', 'main-screen')
        

    def addedToWorld(self, world):
        """The actor is ready to be populated"""
        super(StartScreen, self).addedToWorld(world)
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
        # URL
        self.url = serge.blocks.utils.addVisualActorToWorld(world, 'u', 'u', 
            serge.visual.Text('http://perpetualpyramid.com', colour=G('url-colour'), font_size=G('url-font-size')),
            layer_name='ui', center_position=G('url-position'))
        self.url.linkEvent(serge.events.E_LEFT_CLICK, self.launchURL)
        #
        # Block for menu
        self.menu_block =  serge.blocks.utils.addActorToWorld(world,
            serge.blocks.layout.HorizontalBar('menu-block', height=G('menu-height'), width=G('menu-width')), 
                layer_name='ui', center_position=G('menu-position'))
        #
        self.tutorial = self.menu_block.addActor(serge.blocks.actors.StringText('tut', 'tut',
            'Tutorial', colour=G('menu-colour'), font_size=G('menu-font-size')))
        self.play = self.menu_block.addActor(serge.blocks.actors.StringText('play', 'play',
            'Play', colour=G('menu-colour'), font_size=G('menu-font-size')))
        self.credits = self.menu_block.addActor(serge.blocks.actors.StringText('credits', 'credits',
            'Credits', colour=G('menu-colour'), font_size=G('menu-font-size')))
        #
        self.tutorial.linkEvent(serge.events.E_LEFT_CLICK, self.doTutorial)
        self.play.linkEvent(serge.events.E_LEFT_CLICK, self.doPlay)
        self.credits.linkEvent(serge.events.E_LEFT_CLICK, self.doCredits)
        #
        self.music_toggle = musictoggle.addToggle(world)
        #
        self.start_playlist = ['start-music']
        serge.sound.Music.setPlaylist(self.start_playlist)
        #
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.worldActivated)
        #
        # Create interesting display
        self.initGrid(world, 'start')
        self.initPlayers(world, 'start', interactive=False)

        
    def doTutorial(self, obj, arg):
        """Show the tutorial"""
        self.log.info('Clicked on tutorial')
        self.engine.setCurrentWorldByName('tutorial-screen')
        
    def doPlay(self, obj, arg):
        """Play the game"""
        self.log.info('Clicked on play')
        self.engine.setCurrentWorldByName('level-screen')
        
    def doCredits(self, obj, arg):
        """Show the credits"""
        self.log.info('Clicked on credits')
        world = self.engine.setCurrentWorldByName('credit-screen')
        world.findActorByName('credit-screen').back = 'start-screen'
        
    def worldActivated(self, obj, arg):
        """The world we are in was activated"""
        serge.sound.Music.setPlaylist(self.start_playlist)
    
    def launchURL(self, obj, arg):
        """Launch the url"""
        def doit():
            import webbrowser
            webbrowser.open('http://perpetualpyramid.com')
        t = threading.Thread(target=doit)
        t.setDaemon(True)
        t.start()
        

def main(options):
    """Create the main logic"""
    world = serge.engine.CurrentEngine().getWorld('start-screen')
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(), 'keyboard-quit')
    #
    # The screen actor
    s = StartScreen()
    s.manager = manager
    world.addActor(s)
