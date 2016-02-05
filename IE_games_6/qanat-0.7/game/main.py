"""Main module for the game"""

import os
import logging

import serge.engine
import serge.world
import serge.actor
import serge.zone
import serge.render
import serge.sound
import serge.common
import serge.visual
import serge.events

try:
    import serge.builder.builder
except ImportError:
    pass

import serge.blocks.utils
import serge.blocks.achievements

import common
import mainscreen
import creditsscreen
import highscorescreen

from theme import G, theme


def registerSounds():
    """Register the sounds to use"""
    serge.sound.Sounds.setPath('sound')
    r = serge.sound.Sounds.registerItem
    r('click', '76177__mattpavone__space-title-sfx-1.wav')
    r('countdown', '11453__jovica__dirty-wave-c6.wav')
    r('start', '11453__jovica__dirty-wave-c6 modified.wav')
    r('shoot', '76177__mattpavone__space-title-sfx-2.wav')
    r('alien-explosion', '8098__bliss__fragmentedkickexplosion1.wav')
    r('player-explosion', '100773__cgeffex__impact-explosion.wav')
    r('gun-hot', '18634__corsica-s__clicks-and-pops-10.wav')
    r('crash', '41459__belloq__small-rocket-flybys-and-explosion.wav')
    r('fall', '41459__belloq__small-rocket-flybys-and-explosion-2.wav')
    r('bullet-fragment', '41459__belloq__small-rocket-flybys-and-explosion-3.wav')
    r('life', '26875__cfork__cf-fx-batch-jingle-glock-n-kloing.wav')
    r('bomb-fragment', '156498__unfa__small-far-explosion.wav')


def registerMusic():
    """Register the music to use"""
    serge.sound.Music.setPath('music')
    r = serge.sound.Music.registerItem
    r('track-1', 'Anitek_-_01_-_Calling.ogg')
    r('track-2', 'Anitek_-_05_-_Light-year.ogg')
    r('track-3', 'Anitek_-_07_-_Contact.ogg')


def registerGraphics():
    """Register the graphics to use"""
    serge.visual.Sprites.setPath('graphics')
    r = serge.visual.Sprites.registerItem
    rf = serge.visual.Sprites.registerFromFiles
    r('icon', 'icon.png')
    r('logo', 'logo.png')
    rf('player-ship', 'player-ship-%d.png', 6, 32, False, zoom=1.0, loop=False)
    rf('player-hot-ship', 'player-hot-ship-%d.png', 3, 8, True, zoom=1.0, loop=True)
    r('player-ship-small', 'player-small-ship.png', 4, 1, 2, True, loop=False)
    r('player-explosion', 'player-explosion.png', 4)
    r('player-bullet', 'player-bullet.png', convert_alpha=True)
    r('player-hot-bullet', 'player-hot-bullet.png', convert_alpha=True)
    r('green-bomb', 'green-bomb.png', convert_alpha=True)
    r('yellow-bomb', 'yellow-bomb.png', convert_alpha=True)
    r('red-bomb', 'red-bomb.png', convert_alpha=True)
    r('violet-bomb', 'violet-bomb.png', convert_alpha=True)
    r('bomb-bomb', 'bomb-bomb.png', convert_alpha=True)
    rf('smoke', 'smoke-%d.png', 3)
    r('raindrop', 'raindrop.png')
    r('ground-explosion', 'explosion.png', 8, 1, 32, True, loop=False)
    r('air-explosion', 'ship-explosion.png', 8, 1, 32, True, loop=False)
    rf('blue-alien', 'blue-alien-%d.png', 2, 2, True, convert_alpha=True)
    rf('blue-half', 'blue-half-%d.png', 2, convert_alpha=True)
    rf('red-alien', 'red-alien-%d.png', 2, 2, True, convert_alpha=True)
    rf('red-half', 'red-half-%d.png', 2, convert_alpha=True)
    rf('yellow-alien', 'yellow-alien-%d.png', 2, 2, True, convert_alpha=True)
    rf('yellow-half', 'yellow-half-%d.png', 2, convert_alpha=True)
    rf('green-alien', 'green-alien-%d.png', 2, 2, True, convert_alpha=True)
    rf('green-half', 'green-half-%d.png', 2, convert_alpha=True)
    rf('fire-alien', 'fire-alien-%d.png', 2, 4, True, convert_alpha=True)
    rf('fire-half', 'fire-half-%d.png', 2, convert_alpha=True)
    rf('violet-alien', 'violet-alien-%d.png', 2, 4, True, convert_alpha=True)
    rf('violet-half', 'violet-half-%d.png', 2, convert_alpha=True)
    rf('bomb-alien', 'bomb-alien-%d.png', 2, 4, True, convert_alpha=True)
    rf('bomb-open-alien', 'bomb-open-alien-%d.png', 2, 4, True, convert_alpha=True)
    rf('bomb-half', 'bomb-half-%d.png', 2, convert_alpha=True)
    rf('mother-ship', 'mother-ship-%d.png', 6, 3, True, convert_alpha=True)
    rf('background', 'background-%d.png', 1, 1, True, zoom=2.0, convert_alpha=True)
    r('credits', 'credits.png')
    r('ground', 'ground.png', convert_alpha=True)
    r('ground-overlay', 'ground-overlay.png', convert_alpha=True)
    rf('achievement', 'achievement-%d.png', 2, False)
    #
    serge.visual.Fonts.setPath('fonts')
    serge.visual.Fonts.registerItem('CONTROL', 'DouarOutline.ttf')
    serge.visual.Fonts.registerItem('CLEAR', 'BerenikaBook.ttf')
    serge.visual.Fonts.registerItem('DEFAULT', 'Ramasuri.ttf')


def registerAchievements(options):
    """Register the achievements for the game"""
    r = serge.blocks.achievements.initManager('qanat').safeRegisterAchievement
    a = serge.blocks.achievements.Achievement
    r(a('15k scorer', 'Achieve a score of 15,000 or more in one game',
        'badge', False, 'score', condition_string='score : score>15000'))
    r(a('30k scorer', 'Achieve a score of 30,000 or more in one game',
        'badge', False, 'score', condition_string='score : score>30000'))
    r(a('50k scorer', 'Achieve a score of 50,000 or more in one game',
        'badge', False, 'score', condition_string='score : score>50000'))
    r(a('Life extender', 'Earn an extra life',
        'badge', False, 'life', condition_string='lives : True'))
    r(a('Partially immortal', 'Accumulate at least six lives',
        'badge', False, 'life', condition_string='lives : lives >= 6'))
    r(a('Immortal god', 'Accumulate at least 10 lives',
        'badge', False, 'life', condition_string='lives : lives >= 10'))
    r(a('Get to the end', 'Complete all the levels and return back to the beginning',
        'badge', False, 'levels', condition_string='repeats : repeats >= 1'))
    r(a('Return to the end', 'Complete all the levels at least twice',
        'badge', False, 'levels', condition_string='repeats : repeats >= 2'))
    r(a('Hot shooter', 'Complete a level in less than 3 seconds',
        'badge', False, 'level-time', condition_string='start, time : (time-start)<=3'))
    r(a('Slow poke', 'Take more than 3 minutes to complete a level',
        'badge', False, 'level-time', condition_string='start, time : (time-start)>=180 and start != 0'))
    serge.blocks.achievements.addAchievementsWorld(options, theme)


def startEngine(options):
    """Start the main engine"""
    engine = serge.engine.Engine(width=G('screen-width'), height=G('screen-height'),
                                 title=G('screen-title'), icon=os.path.join('graphics', 'icon.png'),
                                 fullscreen=options.fullscreen)
    serge.blocks.utils.createVirtualLayersForEngine(
        engine, ['background', 'ground', 'main', 'foreground', 'effects', 'ship',
                 'ground-overlay', 'ui'])
    serge.blocks.utils.createWorldsForEngine(engine, [
        'start-screen', 'main-screen', 'credit-screen', 'high-score-screen'])
    #
    engine.setCurrentWorldByName('main-screen')
    return engine


def main(options, args):
    """Start the engine and the game"""
    #
    if not options.log:
        serge.common.logger.setLevel(logging.ERROR)
    #
    # Set rotation type for sprites - smooth_rotate seems to cause ghosting problems
    # so use the base one, which looks fine even though there is some aliasing
    serge.visual.Sprite.rotate = serge.visual.Sprite.base_rotate
    #
    # Create the engine
    engine = startEngine(options)
    #
    registerSounds()
    registerMusic()
    registerGraphics()
    #
    # Muting the sound
    if options.musicoff or options.musiconlyoff:
        serge.sound.Music.pause()
    if options.musicoff:
        serge.sound.Sounds.pause()
        #
    # Change theme settings
    if options.theme:
        theme.updateFromString(options.theme)
        #
    broadcaster = serge.events.getEventBroadcaster()
    broadcaster.registerEventsFromModule(common)
    #
    # Initialise the main logic
    creditsscreen.main(options)
    mainscreen.main(options)
    highscorescreen.main(options)
    registerAchievements(options)
    #
    if options.movie:
        serge.blocks.utils.RecordDesktop(options.movie)
        #
    if options.debug:
        serge.builder.builder.main(engine, options.framerate)
    else:
        engine.run(options.framerate)

