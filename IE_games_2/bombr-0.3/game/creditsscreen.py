"""The credits screen for the game"""

import random
import math
import pygame
import threading

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common 


### Credits ### 
AUTHOR = 'Paul Paterson'
URL = 'http://perpetualpyramid.com'
MUSIC = [
    '- Kris Keyser -',
    '"New Blood", "OHC3", "Summoner", and "Batsly Labs"',
    '',
    '- Rolemusic -',
    '"Shipwreck in the Pacific Ocean"',
    '"He plays me the best rhythms"',
]
BUILT_USING = 'pygame'
GAME_ENGINE = 'serge'
FONTS = ['James Fordyce - Pleasantly Plump']


class CreditsScreen(serge.blocks.actors.ScreenActor):
    """The logic for the credits screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(CreditsScreen, self).__init__('item', 'help-screen')
        self.options = options

    def addedToWorld(self, world):
        """The screen was added to the world"""
        super(CreditsScreen, self).addedToWorld(world)
        #
        # Logo
        the_theme = theme.getTheme('credits-screen')
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
        # Text on the page
        serge.blocks.utils.addTextItemsToWorld(world, [
                    ('Game concept, design and coding', 'author-title'),
                    (AUTHOR, 'author'),
                    (URL, 'url', self.launchURL),
                    ('Music', 'music-title1'),
                    ('from the FreeMusicArchive.org', 'music-title2'),
                    ('Sound', 'sound-title1'),
                    ('From FreeSound.org', 'sound-title2'),
                    ('Built using', 'built-title'),
                    (BUILT_USING, 'built'),
                    ('Game engine', 'engine-title'),
                    (GAME_ENGINE, 'engine'),  
                    ('(v' + serge.common.version + ')', 'engine-version'),
                    ('Fonts', 'font-title1'),
                    ('from the OpenFontLibrary.org', 'font-title2'), 
                    ('Back', 'back', common.tweenBackWorlds('start-screen')),
                ],
                the_theme, 'foreground')
        #
        back = serge.blocks.utils.addSpriteActorToWorld(
            world, 'back', 'back', 'back',
            layer_name='ui',
            center_position=L('back-position'),
        )
        #
        x, y = L('music-position')
        for idx, track in enumerate(MUSIC):
            serge.blocks.utils.addVisualActorToWorld(world, 'title', 'music-item', 
                serge.visual.Text(track, L('music-colour'), 
                font_size=L('music-font-size')), 'foreground', 
                center_position=(x, y+idx*20))
        #
        x, y = L('font-position')
        for idx, font in enumerate(FONTS):
            serge.blocks.utils.addVisualActorToWorld(world, 'title', 'font-item', 
                serge.visual.Text(font, L('font-colour'), 
                font_size=L('font-font-size')), 'foreground', 
                center_position=(x, y+idx*20))

    def updateActor(self, interval, world):
        """Update this actor"""
        super(CreditsScreen, self).updateActor(interval, world)
            
    def launchURL(self, obj, arg):
        """Launch the url"""
        def doit():
            import webbrowser
            webbrowser.open(URL)
        t = threading.Thread(target=doit)
        t.setDaemon(True)
        t.start()
            
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = CreditsScreen(options)
    world = serge.engine.CurrentEngine().getWorld('credits-screen')
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

