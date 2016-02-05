"""Screen for level select"""


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

class LevelScreen(serge.blocks.actors.ScreenActor):
    """The logic for the level screen"""
    
    
    def __init__(self, options):
        """Initialise the screen"""
        super(LevelScreen, self).__init__('item', 'level-screen')
        self.back_world = 'start-screen'
        self.options = options
        self.difficulties = {'easy' : 6, 'normal' : 5, 'hard' : 4}
        self.difficulty_levels = dict((v, k) for k, v in self.difficulties.iteritems())
        
    def addedToWorld(self, world):
        """The actor is ready to be populated"""
        super(LevelScreen, self).addedToWorld(world)
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
        musictoggle.addToggle(world)
        #
        # A menu to select which level to play
        self.level_block = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.layout.HorizontalBar('level-block', width=G('level-block-width'), height=G('level-block-height')),
            layer_name='ui', center_position=G('level-block-position'))
        #
        # Show the levels we can choose
        for idx, level_name in enumerate(G('active-levels')):
            sprite_name = '%s-small' % G('background', level_name)
            button = serge.actor.MountableActor('level-button', ('level-button-%d' % idx))
            label = serge.blocks.actors.StringText('level-label', ('level-label-%d' % idx), G('level-title', level_name),
                        colour=G('level-title-colour'), font_size=G('level-title-font-size'))
            label.setLayerName('ui')
            button.mountActor(label, G('level-title-offset'))
            button.setSpriteName(sprite_name)
            self.level_block.addActor(button)
            button.linkEvent(serge.events.E_LEFT_CLICK, self.levelSelect, level_name)
        #
        # Show the difficulty select
        self.difficulty_block = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.layout.HorizontalBar('difficulty-block', width=G('difficulty-block-width'), 
            height=G('difficulty-block-height')), layer_name='ui', center_position=G('difficulty-block-position'))
        #
        # Add all difficulties
        self.buttons = serge.actor.ActorCollection()
        for difficulty in ('easy', 'normal', 'hard'):
            button = serge.actor.Actor('difficulty-button', ('difficulty-%s' % difficulty))
            button.visual = serge.blocks.visualblocks.TextToggle(
                difficulty.capitalize(), G('difficulty-colour'), 'toggle-button', font_size=G('difficulty-font-size'))
            button.linkEvent(serge.events.E_LEFT_CLICK, self.difficultySelect, (button, difficulty))
            self.difficulty_block.addActor(button)
            self.log.debug('For diff %s, current is %s' % (difficulty, self.difficulty_levels[self.options.number]))
            if self.difficulty_levels[self.options.number] == difficulty:
                button.visual.setOn()
            else:
                button.visual.setOff()
            self.buttons.append(button)
        #
        self.level_playlist = ['level-music', 'level-music-2']

    def doBack(self, obj, arg):
        """Back to the start"""
        self.log.info('Clicked on back')
        self.engine.setCurrentWorldByName(self.back_world)
        
    def updateActor(self, interval, world):
        """Update the actor"""
        #
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            self.engine.setCurrentWorldByName('start-screen')
    
    def levelSelect(self, obj, level_name):
        """Selected a level"""
        self.log.info('Selected level %s with %d moves' % (level_name, self.options.number))
        self.options.level = level_name.replace('level-', '')
        mainscreen.main(self.options)
        self.engine.setCurrentWorldByName('main-screen')
        serge.sound.Music.setPlaylist(self.level_playlist)

    def difficultySelect(self, obj, (button, difficulty)):
        """Selected a difficulty"""
        self.log.info('Selected difficulty %s' % difficulty)
        for the_button in self.buttons:
            if the_button is button:
                the_button.visual.setOn()
                self.options.number = self.difficulties[difficulty]
            else:
                the_button.visual.setOff()

def main(options):
    """Create the main logic"""
    world = serge.engine.CurrentEngine().getWorld('level-screen')
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # The screen actor
    s = LevelScreen(options)
    s.manager = manager
    world.addActor(s)
