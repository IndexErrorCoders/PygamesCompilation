"""The start screen for the game"""

import random
import os
import time
import pygame

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.sound
from serge.simplevecs import Vec2d
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.animations

from theme import G, theme
import common 
import smacktalker
import powerups


class StartScreen(serge.blocks.actors.ScreenActor):
    """The logic for the start screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(StartScreen, self).__init__('item', 'main-screen')
        self.options = options
        self._take_screenshots = G('auto-screenshots')
        self._screenshot_interval = G('screenshot-interval')
        self._last_screenshot = time.time() - self._screenshot_interval + 1.0
        self._screenshot_path = G('screenshot-path')
        self.music = common.MAIN_MUSIC = serge.sound.Music.getItem('titles')
        serge.sound.Music.setVolume(G('volume', 'start-screen'))
        self.music.play(-1)

    def addedToWorld(self, world):
        """The start screen was added to the world"""
        super(StartScreen, self).addedToWorld(world)
        #
        # Logo
        the_theme = theme.getTheme('start-screen')
        L = the_theme.getProperty
        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'logo', 'foreground',
            center_position=L('logo-position'))
        title = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'title', 'title', 'foreground',
            center_position=L('title-position'))
        bg = serge.blocks.utils.addSpriteActorToWorld(
            world, 'bg', 'bg', 'main-background',
            layer_name='background',
            center_position=(G('screen-width') / 2, G('screen-height') / 2),
        )
        #
        # Face
        self.face = serge.blocks.utils.addSpriteActorToWorld(
            world, 'face', 'face', 'face',
            layer_name='ui',
            center_position=L('face-position'),
        )
        self.face.linkEvent(serge.events.E_LEFT_CLICK, common.tweenWorlds('level-screen'))
        #
        start = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'start', 'start', 'foreground',
            center_position=L('start-position'))
        start.linkEvent(serge.events.E_LEFT_CLICK, common.tweenWorlds('level-screen'))
        credits = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'credits', 'credits', 'foreground',
            center_position=L('credits-position'))
        credits.linkEvent(serge.events.E_LEFT_CLICK, common.tweenWorlds('credits-screen'))
        help = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'help', 'help', 'foreground',
            center_position=L('help-position'))
        help.linkEvent(serge.events.E_LEFT_CLICK, common.tweenWorlds('help-screen'))
        achievements = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'achievements', 'achievements', 'foreground',
            center_position=L('achievements-position'))
        achievements.linkEvent(serge.events.E_LEFT_CLICK, common.tweenWorlds('achievements-screen'))
        achievements.active = False
        #
        serge.blocks.utils.addTextItemsToWorld(world, [
                    ('v' + common.version, 'version'),
                ],
                the_theme, 'foreground'
        )
        #
        # Sprite to show items that appear for the AI to comment on
        self.appearing_item = serge.blocks.utils.addSpriteActorToWorld(
            world, 'item', 'appearing-item', 'tiles-31',
            center_position=L('item-start-position'),
            layer_name='ui',
            actor_class=serge.blocks.animations.AnimatedActor
        )
        self.appearing_item.setZoom(L('item-zoom'))
        items = list(set([getattr(powerups, name) for name in G('random-item-names')]))
        random.shuffle(items)
        self.items = items
        #
        # Smack talking
        self.smack = smacktalker.RandomlyAppearingSmacker('smack', 'smack', 'start-screen', 'TOBEREPLACED')
        self.setSmackConversation()
        world.addActor(self.smack)
        self.smack.visible = False
        self.smack.linkEvent(common.E_SMACK_APPEAR, self.showItem)
        self.smack.linkEvent(common.E_SMACK_HIDE, self.hideItem)

    def updateActor(self, interval, world):
        """Update this actor"""
        super(StartScreen, self).updateActor(interval, world)
        #
        # Keypresses
        if self.keyboard.isClicked(pygame.K_RETURN):
            self.engine.setCurrentWorldByName('level-screen')
        #
        # Face update
        if random.random() * 1000.0 / interval < G('face-probability', 'start-screen'):
            self.face.visual.setCell(random.randint(1, self.face.visual.getNumberOfCells() - 1))
        if self._take_screenshots:
            if time.time() - self._last_screenshot > self._screenshot_interval:
                filename = '%s-%s' % (self.name, time.strftime('%m-%d %H:%M:%S.png'))
                serge.blocks.utils.takeScreenshot(os.path.join(self._screenshot_path, filename))
                self._last_screenshot = time.time()
                self.log.debug('Taking screenshot - %s', filename)

    def showItem(self, obj, arg):            
        """Show the random item"""
        self.log.debug('Showing the random item')
        the_theme = theme.getTheme('start-screen')
        L = the_theme.getProperty
        self.zoom_in = self.appearing_item.addAnimation(
            serge.blocks.animations.MovementTweenAnimation(
                self.appearing_item, Vec2d(L('item-start-position')), Vec2d(L('item-end-position')),
                duration=L('item-animation-time'),
                function=serge.blocks.animations.MovementTweenAnimation.sinInOut,
                set_immediately=True,
            ),
            'item-enter',
        )
        #
        self.appearing_item.setSpriteName(self.items[0].name_of_sprite)
        self.items.append(self.items.pop(0))
        self.setSmackConversation()

    def setSmackConversation(self):
        """Set the smack conversation"""
        self.smack.conversation = 'show-%s' % self.items[0].__name__.lower()

    def hideItem(self, obj, arg):            
        """Show the random item"""
        self.log.debug('Hiding the random item')
        the_theme = theme.getTheme('start-screen')
        L = the_theme.getProperty
        self.zoom_out = self.appearing_item.addAnimation(
            serge.blocks.animations.MovementTweenAnimation(
                self.appearing_item, Vec2d(L('item-end-position')), Vec2d(L('item-start-position')),
                duration=L('item-animation-time'),
                function=serge.blocks.animations.MovementTweenAnimation.sinInOut,
                set_immediately=False,
            ),
            'item-leave',
        )

        
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = StartScreen(options)
    world = serge.engine.CurrentEngine().getWorld('start-screen')
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

