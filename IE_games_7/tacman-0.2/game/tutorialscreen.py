"""The tutorial screen"""

import copy
import pygame
import networkx

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

class TutorialScreen(gameboard.GameBoard):
    """The logic for the tutorial screen"""
    
    
    def __init__(self):
        """Initialise the screen"""
        super(TutorialScreen, self).__init__('item', 'tutorial-screen')
        

    def addedToWorld(self, world):
        """The actor is ready to be populated"""
        super(TutorialScreen, self).addedToWorld(world)
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
            ' Tutorial Mode ', colour=G('subtitle-colour'), font_size=G('subtitle-font-size')))
        #
        # Block for menu
        self.menu_block =  serge.blocks.utils.addActorToWorld(world,
            serge.blocks.layout.HorizontalBar('menu-block', height=G('tutorial-menu-height'), width=G('tutorial-menu-width')), 
                layer_name='ui', center_position=G('tutorial-menu-position'))
        #
        self.back = self.menu_block.addActor(serge.blocks.actors.StringText('back', 'back',
            'Back', colour=G('menu-colour'), font_size=G('menu-font-size')))
        self.credits = self.menu_block.addActor(serge.blocks.actors.StringText('credits', 'credits',
            'Credits', colour=G('menu-colour'), font_size=G('menu-font-size')))
        #
        self.back.linkEvent(serge.events.E_LEFT_CLICK, self.doPlay)
        self.credits.linkEvent(serge.events.E_LEFT_CLICK, self.doCredits)
        #
        self.music_toggle = musictoggle.addToggle(world)
        #
        self.music = serge.sound.Music.getItem('start-music')
        self.music.play()
        self.level_music = serge.sound.Music.getItem('level-music')
        #
        # Create game play area
        level = 'tutorial'
        self.initGrid(world, level)
        self.initPlayers(world, level, interactive=True)
        self.initUIElements(world, level)
        self.initMoveOrder()
        self.setupDevMode(world)
        #
        # Create the help bubble
        self.help = serge.blocks.utils.addVisualActorToWorld(world, 'help', 'help',
            serge.blocks.visualblocks.SpriteText('Click on the Tacman to begin\nmaking your move.', 
                G('help-font-colour'), 'help-bubble', font_size=G('help-font-size')),
                'messages', G('help-position'))
        #
        self.manager.assignBehaviour(self, 
            serge.blocks.behaviours.TimedCallback(G('ghost-decision-time'), self.chooseMove), 'ghost-moving')
        self.manager.assignBehaviour(self, 
            serge.blocks.behaviours.TimedCallback(G('tutorial-step-time'), self.nextStep), 'tutorial-steps')
        #
        self.linkEvent('eat-yellow-pill', self.eatYellow)
        self.linkEvent('eat-ghost', self.eatGhost)
        self.linkEvent('hit-ghost', self.hitGhost)
        self._mode_toggle.linkEvent('fright-mode-over', self.frightOver)
        #
        self.manager.pauseBehaviours('moving')
        self.step = 'wait-first-click'
        self._told_icicle = False
        self._told_boost = False
        self._level_over = serge.actor.Actor('level-over')
        self._level_over.active = False
        
    def doPlay(self, obj, arg):
        """Play the game"""
        self.log.info('Clicked on play')
        self.engine.setCurrentWorldByName('start-screen')
        
    def doCredits(self, obj, arg):
        """Show the credits"""
        self.log.info('Clicked on credits')
        world = self.engine.setCurrentWorldByName('credit-screen')
        world.findActorByName('credit-screen').back = 'tutorial-screen'

    def updateActor(self, interval, world):
        """Update this actor"""
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            self.engine.setCurrentWorldByName('start-screen')

    def playerClicked(self, obj, arg):
        """The user clicked on the player"""
        if self.step == 'wait-first-click':
            self.help.active = False
            self.step = 'wait-first-destination'
        elif self.step == 'wait-second-click':
            self.help.visual.text_visual.setText(
                'Make Tacman eat the yellow\npill now by selecting the\nclosest green square.')
            self.step = 'wait-second-destination'
        elif self.step == 'wait-interesting':
            pass
        else:
            return
        super(TutorialScreen, self).playerClicked(obj, arg)

    def chooseDestination(self, *args, **kw):
        """A new destination square was clicked"""
        if self.step == 'wait-first-destination-click':
            self.help.active = False
            self.step = 'wait-first-arrival'
        elif self.step == 'wait-second-destination':
            self.help.active = False
            self.step = 'wait-second-arrival'
        elif self.step == 'wait-interesting':
            self.help.active = False
        else:
            return
        super(TutorialScreen, self).chooseDestination(*args, **kw)

    def actorArrived(self, *args, **kw):
        """An actor arrived at the destination"""
        if self.step == 'wait-first-arrival':
            self.help.active = True
            self.help.visual.text_visual.setText(
                'Now the ghosts will move.\nOnly red to begin with.')
            self.step = 'wait-first-ghost-arrival'
        elif self.step in ('wait-first-ghost-arrival', 'wait-first-ghost-arrival-pause'):
            self.help.active = False
            self.step = 'wait-first-ghost-arrival-pause'
        elif self.step == 'wait-interesting':
            pass
        else:
            return
        super(TutorialScreen, self).actorArrived(*args, **kw)
        #
        if self.players[0] == self._player:
            if self._moves_made.value >= 4 and not self._told_boost and not self.help.active:
                self._told_boost = True
                self.help.active = True
                self.help.visual.text_visual.setText(
                    'Click on the yellow star on\nthe right to get a quick speed\nboost for a single turn.') 
                self.step = 'wait-boost'
            if self._moves_made.value >= 7 and not self._told_icicle and not self.help.active:
                self._told_icicle = True
                self.help.active = True
                self.help.visual.text_visual.setText(
                    'Click on the blue icicles on the\nright to freeze all the\nghosts for a short time.')
                self.step = 'wait-icicle'
            if self._moves_made.value >= 10 and not self.help.active:
                self.help.active = True
                self.help.visual.text_visual.setText(
                    'Click on "Back" to return to the\nmain screen and play\nfor real.')
            
    def nextStep(self, world, actor, interval):
        """Next step in tutorial"""
        if self.step == 'wait-first-destination':
            self.help.visual.text_visual.setText('You can move to any green\nsquare. Click on one\nnow to start moving.')
            self.help.active = True
            self.step = 'wait-first-destination-click'
        elif self.step == 'wait-first-ghost-arrival-pause':
            self.help.active = True
            self.help.visual.text_visual.setText(
                'Click on Tacman to move again.')
            self.step = 'wait-interesting'
            
    def eatYellow(self, obj, arg):
        """The yellow pill is eaten"""
        self.help.visual.text_visual.setText('Eating a yellow pill turns the\nghosts blue. You can eat\nthem now also.')
        self.help.active = True

    def eatGhost(self, obj, arg):
        """The ghost is eaten"""
        self.help.visual.text_visual.setText('Eating a blue ghost will\nkill it. It will return\nhome and for a while.')
        self.help.active = True

    def hitGhost(self, obj, arg):
        """A ghost is hit"""
        self.help.visual.text_visual.setText('Hitting a ghost will kill\nyou and cost a life. You\nstart with only three lives.')
        self.help.active = True
        
    def frightOver(self, obj, arg):
        """Fright mode is over"""
        self.help.visual.text_visual.setText('Eventually the blue ghosts will\nturn back to normal and\nchase you again!')
        self.help.active = True
        
    def snowflakeClicked(self, event, arg):
        """The user clicked on a snowflake"""
        if self._told_icicle:
            self.step = 'wait-interesting'
            super(TutorialScreen, self).snowflakeClicked(event, arg)

    def boostsClicked(self, event, arg):
        """The user clicked on a boost"""
        if self._told_boost:
            self.step = 'wait-interesting'
            super(TutorialScreen, self).boostsClicked(event, arg)
    
        
def main(options):
    """Create the main logic"""
    world = serge.engine.CurrentEngine().getWorld('tutorial-screen')
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # The screen actor
    s = TutorialScreen()
    s.manager = manager
    world.addActor(s)
