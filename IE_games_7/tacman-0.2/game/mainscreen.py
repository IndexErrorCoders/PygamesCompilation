"""The main screen for the game"""

import random
import math
import copy

import networkx
import pygame

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.sound
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

class MainScreen(gameboard.GameBoard):
    """The logic for the main screen"""
    
    
    def __init__(self, level, devmode, number):
        """Initialise the screen"""
        super(MainScreen, self).__init__('item', 'main-screen')
        self._current_level = level
        self._devmode = devmode
        self._paused = False
        self._lives = G('initial-lives')
        if number:
            theme.setProperty('player-moves', number, 'level-%s' % level)
        
    def addedToWorld(self, world):
        """Update this actor"""
        super(MainScreen, self).addedToWorld(world)
        self._initLevel(world, self._current_level)
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.resetTheme)
        
    def resetTheme(self, event, arg):
        """Reset the theme in case another screen set it"""
        theme.selectTheme('level-%s' % self.level)        
        
    def _initLevel(self, world, level):
        """Put the pills on the screen"""
        self.level = level
        #
        # The behaviour manager
        self.manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
        world.addActor(self.manager)
        #
        self.initGrid(world, level)
        self.initUIElements(world, level)
        self.initPlayers(world, level)
        self.initMoveOrder()
        #
        self.manager.assignBehaviour(self, 
            serge.blocks.behaviours.TimedCallback(G('ghost-decision-time'), self.chooseMove), 'ghost-moving')
        #
        self.setupDevMode(world)
        #
        self.manager.pauseBehaviours('moving')
        #
        # The level over display
        self._level_over = serge.blocks.utils.addVisualActorToWorld(world, 'level-over', 'level-over', 
            serge.visual.Text('Complete', G('level-over-colour'), font_size=G('level-over-size')),
            'messages', G('level-over-position'))
        self._level_over.active = False
        self._restart = serge.blocks.utils.addVisualActorToWorld(world, 'level-restart', 'level-restart',
            serge.blocks.visualblocks.RectangleText('Restart', G('restart-font-colour'), G('restart-size'), 
                G('restart-back-colour'), font_size=G('restart-font-size')),
                'messages', G('restart-position'))
        self._restart.active = False
        self._restart.linkEvent(serge.events.E_LEFT_CLICK, self.restartClick)
        #
        self._next = serge.blocks.utils.addVisualActorToWorld(world, 'level-restart', 'level-restart',
            serge.blocks.visualblocks.RectangleText('New Level', G('restart-font-colour'), G('restart-size'), 
                G('restart-back-colour'), font_size=G('restart-font-size')),
                'messages', G('restart-position'))
        self._next.active = False
        self._next.linkEvent(serge.events.E_LEFT_CLICK, self.nextClick)
        #
        musictoggle.addToggle(world)
            
            
    def updateActor(self, interval, world):
        """Update this actor"""
        #
        # Update score
        self._target_time.value = self._mode_toggle.mode_ticker
        #
        # Check for game over
        if len(self._grid.getChildrenWithTag('pill')) <= 0 and not self._level_over.active:
            self._level_over.active = True
            self._next.active = True
            self.manager.pauseBehaviours('turn-moving')
            self._highlighter.removeChildren()
        #
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            self.engine.setCurrentWorldByName('resume-screen')
    
    def restartClick(self, event, arg):
        """Restart was clicked"""
        self.world.clearActors()
        main(self.options)
        self.engine.setCurrentWorldByName('start-screen')            

    def nextClick(self, event, arg):
        """Next was clicked"""
        self.world.clearActors()
        main(self.options)
        self.engine.setCurrentWorldByName('start-screen')            
                    
def main(options):
    """Create the main logic"""
    world = serge.engine.CurrentEngine().getWorld('main-screen')
    world.clearActors()
    #
    # The screen actor
    s = MainScreen(options.level, options.developer, options.number)
    s.options = options
    world.addActor(s)

