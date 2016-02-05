"""The main launching point"""

import os
import pyglet

import engine
import levelscreen
import startscreen
import helpscreen
import settings
import sound


def main(options):
    """The main application start"""
    #
    # Switch settings if needed
    if options.cheat:
        settings.S = settings.D
    #
    # Configure pyglet
    pyglet.resource.path = [
        'data', os.path.join('data', 'levelicons'), os.path.join('data', 'music'),
        os.path.join('data', 'scified2002')]
    pyglet.resource.reindex()
    sound.initSound(options)
    #
    # Add font
    pyglet.resource.add_font('scifi2k2.ttf')
    #
    # Get the engine
    eng = engine.Engine(1024, 768, debug=options.cheat, fade_image_name='fade.png')
    #
    start = startscreen.StartScreen('start-screen', options)
    eng.addWorld(start)
    #
    level = levelscreen.LevelScreen('level-screen', options)
    eng.addWorld(level)
    #
    help = helpscreen.HelpScreen('help-screen', options)
    eng.addWorld(help)
    #
    eng.setCurrentWorld('start-screen' if not options.straight else 'level-screen')
    if options.straight:
        pass
    #
    # Music callback
    #pyglet.clock.schedule_interval(sound.Music)
    #
    eng.runEngine()