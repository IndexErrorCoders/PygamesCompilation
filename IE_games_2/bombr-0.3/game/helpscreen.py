"""The help screen for the game"""

import random
import math
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

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common 

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
        the_theme = theme.getTheme('help-screen')
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
        # Help text
        text = serge.blocks.utils.addSpriteActorToWorld(world, 'text', 'text', 'help-keys', 'foreground',
            center_position=L('text-position'))
        #
        serge.blocks.utils.addTextItemsToWorld(world, [
                    ('Cursor keys to move. SPACE to Bomb.', 'keys-title'),
                    ('Music Volume', 'music-title'),
                ],
                the_theme, 'foreground')
        #
        # Back link
        #
        back = serge.blocks.utils.addSpriteActorToWorld(
            world, 'back', 'back', 'back',
            layer_name='ui',
            center_position=L('back-position'),
        )
        back.linkEvent(serge.events.E_LEFT_CLICK, common.tweenBackWorlds('start-screen'))
        #
        # Volume control
        self.down = serge.blocks.utils.addSpriteActorToWorld(
            world, 'btn', 'vol-down', 'vol-down',
            layer_name='ui',
            center_position=L('vol-down-position')
        )
        self.down.linkEvent(serge.events.E_LEFT_CLICK, self.changeVolume, -L('vol-change-amount'))
        self.up = serge.blocks.utils.addSpriteActorToWorld(
            world, 'btn', 'vol-up', 'vol-up',
            layer_name='ui',
            center_position=L('vol-up-position')
        )
        self.up.linkEvent(serge.events.E_LEFT_CLICK, self.changeVolume, +L('vol-change-amount'))
        #
        self.volume = serge.blocks.utils.addActorToWorld(
            world, serge.blocks.actors.NumericText(
                'text', 'volume', '%d%%', L('volume-colour'),
                font=L('volume-font'), font_size=L('volume-size'),
                value=G('volume', 'start-screen') * 100.0
            ),
            layer_name='ui',
            center_position=L('vol-position')
        )

    def updateActor(self, interval, world):
        """Update this actor"""
        super(HelpScreen, self).updateActor(interval, world)
            
    def changeVolume(self, obj, amount):
        """Change the volume of the music"""
        self.volume.value = max(0, min(100, self.volume.value + amount))
        serge.sound.Music.setVolume(self.volume.value / 100.0)


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

