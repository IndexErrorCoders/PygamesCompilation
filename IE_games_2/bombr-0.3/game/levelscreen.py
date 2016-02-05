"""The level screen for the game"""

import random
import math
import os
import glob
import time
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

from theme import G, theme
import common


class LevelScreen(serge.blocks.actors.ScreenActor):
    """The logic for the level screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(LevelScreen, self).__init__('item', 'main-screen')
        self.options = options
        self._take_screenshots = G('auto-screenshots')
        self._screenshot_interval = G('screenshot-interval')
        self._last_screenshot = time.time() - self._screenshot_interval + 1.0
        self._screenshot_path = G('screenshot-path')
        self.music = common.MAIN_MUSIC

    def addedToWorld(self, world):
        """The level screen was added to the world"""
        super(LevelScreen, self).addedToWorld(world)
        #
        # Logo
        the_theme = theme.getTheme('level-screen')
        L = the_theme.getProperty
        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'logo', 'foreground',
            center_position=L('logo-position'))
        title = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'title', 'title', 'foreground',
            center_position=L('title-position'))
        bg = serge.blocks.utils.addSpriteActorToWorld(
            world, 'bg', 'bg', 'dark-background',
            layer_name='background',
            center_position=(G('screen-width') / 2, G('screen-height') / 2),
        )
        #
        # Find all the levels
        levels = common.levels.LEVEL_FILES[:-1]
        self.level_grid = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.layout.MultiGrid('grid', 'grid', size=L('grid-size'), width=L('grid-width'),
                                     height=L('grid-height')),
            center_position=L('grid-position'),
            layer_name='ui',
        )
        w, h = self.level_grid.getSize()
        for idx in range(1, len(levels) + 1):
            x, y = ((idx - 1) % w, (idx - 1) // w)
            tile = self.level_grid.addActor(
                (x, y),
                serge.actor.Actor('tile', 'tile-%s' % idx),
            )
            if self.options.test:
                tile.setSpriteName('general-board')
            else:
                tile.setSpriteName('level-%d' % idx)
            tile.linkEvent(serge.events.E_LEFT_CLICK, self.selectLevel, idx)
            title = self.level_grid.addActor(
                (x, y),
                serge.blocks.actors.StringText(
                    'title', 'title-%s' % idx, common.levels.LEVELS[idx - 1][0],
                    colour=L('title-colour'), font_name=L('title-font'),
                    font_size=int(L('title-font-size') * (0.5 if self.options.test else 1.0))),
            )
            title.y += L('title-offset-y')
        #
        # Random level button
        random_level = serge.blocks.utils.addSpriteActorToWorld(
            world, 'random-level', 'random-level', 'random-level',
            layer_name='ui',
            center_position=L('random-level-position'),
            actor_class=serge.actor.MountableActor,
        )
        random_level.linkEvent(serge.events.E_LEFT_CLICK, common.tweenWorlds('random-level-screen'))        #
        random_title = random_level.mountActor(
            serge.blocks.actors.StringText(
                'title', 'title-random', 'Random Generated Maze',
                colour=L('title-colour'), font_name=L('title-font'),
                font_size=int(L('title-font-size') * (0.5 if self.options.test else 1.0))),
            (0, L('title-offset-y'))
        )
        random_title.setLayerName('ui')
        # Back button
        back = serge.blocks.utils.addSpriteActorToWorld(
            world, 'back', 'back', 'back',
            layer_name='ui',
            center_position=L('back-position'),
        )
        back.linkEvent(serge.events.E_LEFT_CLICK, common.tweenBackWorlds('start-screen'))
        #
        # Resume button
        self.resume = serge.blocks.utils.addSpriteActorToWorld(
            world, 'resume', 'resume', 'resume',
            layer_name='ui',
            center_position=L('resume-position'),
        )
        self.resume.linkEvent(serge.events.E_LEFT_CLICK, common.tweenWorlds('main-screen'))
        #
        # Events
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.activatedWorld)
        world.linkEvent(serge.events.E_DEACTIVATE_WORLD, self.deactivatedWorld)

    def activatedWorld(self, obj, arg):
        """The world was activated"""
        if self.engine.getCurrentWorld().name != 'start-screen':
            self.music.play(-1)
        self.resume.active = common.LEVEL_IN_PROGRESS

    def deactivatedWorld(self, obj, arg):
        """The world was deactivated"""
        #self.music.pause()

    def selectLevel(self, obj, level_number):
        """Select a level number"""
        self.log.info('Selected level %d' % level_number)
        serge.sound.Sounds.play('click')
        world = self.engine.getWorld('main-screen')
        controller = world.findActorByName('main-screen')
        controller.current_level = level_number
        controller.restartGame()
        common.tweenWorlds('main-screen')()
        common.LEVEL_IN_PROGRESS = True

    def updateActor(self, interval, world):
        """Update this actor"""
        super(LevelScreen, self).updateActor(interval, world)
        #
        # Keypresses
        if self.keyboard.isClicked(pygame.K_RETURN):
            self.selectLevel(None, G('start-level'))
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            common.tweenBackWorlds('start-screen')(None, None)
        #
        if self._take_screenshots:
            if time.time() - self._last_screenshot > self._screenshot_interval:
                filename = '%s-%s' % (self.name, time.strftime('%m-%d %H:%M:%S.png'))
                serge.blocks.utils.takeScreenshot(os.path.join(self._screenshot_path, filename))
                self._last_screenshot = time.time()
                self.log.debug('Taking screenshot - %s', filename)

            
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = LevelScreen(options)
    world = serge.engine.CurrentEngine().getWorld('level-screen')
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

