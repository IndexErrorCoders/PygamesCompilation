"""Main module for the game"""

import pygame
import os
import time

import serge.engine
import serge.world
import serge.actor
import serge.zone
import serge.render
import serge.sound 
import serge.render
try:
    import serge.builder.builder
except ImportError:
    pass

import serge.blocks.utils
import serge.blocks.visualeffects

import common
import mainscreen
import startscreen
import creditsscreen 
import resumescreen
import tutorialscreen
import levelscreen

from theme import G

def registerSounds():
    """Register the sounds to use"""
    serge.sound.Sounds.setPath('sound')
    r = serge.sound.Sounds.registerItem
    r('step', 'click-01.wav')
    r('select', '674_1233172263.wav')
    r('yellow', 'Wiper Park.wav')
    r('freeze', 'thunk.wav')
    r('boost', 'MLaunch.wav')
    
def registerMusic():
    """Register the music to use"""
    serge.sound.Music.setPath('music')
    r = serge.sound.Music.registerItem
    r('start-music', 'Haute_Culture_-_04_-_Gladias.mp3')
    r('level-music', 'Man_Mantis_-_04_-_Teacups_of_Our_Ashes.ogg')
    r('level-music-2', 'DjCode_-_02_-_Journey_To_The_Moon.ogg')

    
def registerGraphics():
    """Register the graphics to use"""
    serge.visual.Sprites.setPath('graphics')
    r = serge.visual.Sprites.registerItem
    rf = serge.visual.Sprites.registerFromFiles
    r('icon', 'icon.png')
    r('lstart-background', 'lstart-background.png')
    r('tutorial-background', 'tutorial-background.png')
    r('l0-background', 'l0-background.png')
    r('l1-background', 'l1-background.png')
    r('l2-background', 'l2-background.png')
    r('l3-background', 'l3-background.png')
    r('red-pill', 'red-pill.png')
    r('yellow-pill', 'yellow-pill.png')
    r('range-square', 'range-square.png')
    r('destination-square', 'destination-square.png')
    r('chosen-square', 'chosen-square.png')
    rf('ice-cube', 'ice-cube-%d.png', 4, 1, True)
    rf('static-pacman', 'pacman-%d.png', 4, 10, False)
    rf('pacman', 'pacman-%d.png', 4, 10, True)
    rf('red-ghost', 'red-ghost-%d.png', 8, 5, True)
    rf('pink-ghost', 'pink-ghost-%d.png', 8, 5, True)
    rf('orange-ghost', 'orange-ghost-%d.png', 8, 5, True)
    rf('blue-ghost', 'blue-ghost-%d.png', 8, 5, True)
    rf('frightened-ghost', 'darkblue-ghost-%d.png', 8, 5, True)
    rf('eyes', 'eyes-%d.png', 2, 2, True)
    rf('snowflakes', 'snowflake-%d.png', 4, 1, True)
    rf('boosts', 'boost-%d.png', 4, 1, True)
    r('pacman-death', 'pacman-death.png', 11, 1, 8, running=True, loop=False)
    r('credits', 'credits.png')
    rf('music-button', 'music-%d.png', 2, zoom=0.5)
    rf('sound-button', 'sound-%d.png', 2, zoom=0.25)
    r('help-bubble', 'help-bubble.png')
    rf('toggle-button', 'toggle-button-%d.png', 2)
    #
    serge.visual.Fonts.setPath('fonts')
    serge.visual.Fonts.registerItem('DEFAULT', 'intuitive.ttf')
    #
    # Set images for levels
    for level_name in G('active-levels'):
        sprite_name = G('background', level_name)
        try:
            r(('%s-small' % sprite_name), ('%s.png' % sprite_name), zoom=0.2)
        except serge.registry.DuplicateItem:
            pass
        
def startEngine(options):
    """Start the main engine"""
    engine = serge.engine.Engine(width=G('screen-width'), height=G('screen-height'), title=G('screen-title'), icon=G('screen-icon'))
    engine.getRenderer().addLayer(serge.blocks.visualeffects.FadingLayer('background', 0))
    serge.blocks.utils.createVirtualLayersForEngine(engine, ['foreground', 'main', 'player', 'overlay'])
    engine.getRenderer().addLayer(serge.render.Layer('ui', 5))
    engine.getRenderer().addLayer(serge.render.VirtualLayer('messages', 6))
    serge.blocks.utils.createWorldsForEngine(engine, ['start-screen', 'main-screen', 'credit-screen', 'resume-screen',
        'tutorial-screen', 'level-screen'])
    #
    engine.setCurrentWorldByName('start-screen')
    return engine

        


def main(options, args):
    """Start the engine and the game"""
    registerSounds()
    registerMusic()
    registerGraphics()
    #
    if options.musicoff:
        serge.sound.Music.pause()
        serge.sound.Sounds.pause()
    #
    # Create the engine
    engine = startEngine(options)
    #
    # Initialise the main logic
    mainscreen.main(options)
    startscreen.main(options)
    creditsscreen.main(options)
    resumescreen.main(options)
    tutorialscreen.main(options)
    levelscreen.main(options)
    #
    if options.straight:
        engine.setCurrentWorldByName('main-screen')
    if options.tutorial:
        engine.setCurrentWorldByName('tutorial-screen')        
    #   
    if options.debug:
        serge.builder.builder.main(engine, options.framerate)
    else:
        engine.run(options.framerate)
