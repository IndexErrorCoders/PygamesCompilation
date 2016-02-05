"""Implements the player to show visuals for the music"""

import pygame

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

from theme import G, theme
import common 


class PlayerScreen(serge.blocks.actors.ScreenActor):
    """The logic for the player screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(PlayerScreen, self).__init__('item', 'player-screen')
        self.options = options

    def addedToWorld(self, world):
        """The start screen was added to the world"""
        super(PlayerScreen, self).addedToWorld(world)
        #
        # Logo
        the_theme = theme.getTheme('player-screen')
        L = the_theme.getProperty
        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'icon', 'foreground', 
            center_position=L('logo-position'))
        #
        serge.blocks.utils.addTextItemsToWorld(world, [
                    (L('title'), 'title'),
                    ('v' + common.version, 'version'),
                    ('Start', 'start',  serge.blocks.utils.worldCallback('main-screen', 'click')),
                    ('Help', 'help',  serge.blocks.utils.worldCallback('help-screen', 'click')),
                    ('Credits', 'credits',  serge.blocks.utils.worldCallback('credits-screen', 'click')),
                    ('Achievements', 'achievements', serge.blocks.utils.worldCallback('achievements-screen', 'click')),
                ],
                the_theme, 'foreground')

    def updateActor(self, interval, world):
        """Update this actor"""
        super(PlayerScreen, self).updateActor(interval, world)
            
            
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = PlayerScreen(options)
    world = serge.engine.CurrentEngine().getWorld('player-screen')
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


