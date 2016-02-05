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
import serge.events
import serge.blocks.achievements
import serge.blocks.textgenerator

import serge.visual
import serge.blocks.actors
import serge.blocks.utils
import serge.blocks.onlinescores

import common
import mainscreen
import startscreen
import helpscreen
import creditsscreen
import simulation
import levelscreen
import actionreplayscreen
import randomlevelscreen


from theme import G, theme


def registerSounds():
    """Register the sounds to use"""
    serge.sound.Sounds.setPath('sound')
    r = serge.sound.Sounds.registerItem
    r('click', '96128__bmaczero__contact2.wav')
    r('walk', '38874__swuing__footstep-grass.wav')
    r('drop', '150501__davdud101__cup-drop.wav')
    r('explode', '200465__wubitog__explosion-longer.wav')
    r('death', '180493__vincentoliver__boneclicks-goresquelches-7.wav')
    r('death-trill', '162457__kastenfrosch__verloren.wav')
    r('chunk-explode', '199924__thedapperdan__bubble-wrap-pop.wav')
    r('block-break', '41632__datasoundsample__thud.wav')
    r('tinkle', '17__anton__glass-a-pp.wav')
    r('hearts', '45807__themfish__coins2.wav')
    r('cycle-gift', '25885__acclivity__beeprising.wav')
    r('choose-gift', '25885__acclivity__beeprising_high.wav')
    r('flag-taken', '166540__qubodup__success-quest-complete-rpg-sound.wav')


def registerMusic():
    """Register the music to use"""
    serge.sound.Music.setPath('music')
    r = serge.sound.Music.registerItem
    r('titles', 'Kris_Keyser_-_06_-_Nitro.ogg')
    r('main-1', 'Kris_Keyser_-_01_-_New_Blood.ogg')
    r('main-2', 'Kris_Keyser_-_04_-_OHC3.ogg')
    r('main-3', 'Kris_Keyser_-_03_-_Summoner.ogg')
    r('main-4', 'Kris_Keyser_-_02_-_Batsly_Labs.ogg')
    r('death-music', 'Rolemusic_-_01_-_Shipwreck_In_The_Pacific_Ocean.ogg')
    r('success-music', 'Rolemusic_-_06_-_He_Plays_Me_The_Best_Rhythms.ogg')


def registerGraphics():
    """Register the graphics to use"""
    serge.visual.Sprites.setPath('graphics')
    r = serge.visual.Sprites.registerItem
    rf = serge.visual.Sprites.registerFromFiles
    rm = serge.visual.Sprites.registerMultipleItems
    rp = serge.visual.Sprites.registerItemsFromPattern
    r('icon', 'icon.png')
    r('logo', 'logo.png')
    r('title', 'title.png')
    r('start', 'start.png')
    r('resume', 'resume.png')
    r('back', 'back.png')
    r('generate', 'generate.png', zoom=0.6)
    r('select', 'select.png', zoom=0.6)
    r('credits', 'credits.png')
    r('help', 'help.png')
    r('help-keys', 'help-keys.png')
    r('vol-down', 'vol-down.png')
    r('vol-up', 'vol-up.png')
    r('slider', 'slider.png')
    r('gift-box', 'gift-box.png')
    rf('score-panel', 'score-panel-%d.png', 3)
    r('slider-back', 'slider-back.png')
    r('flag-status', 'flag-status.png')
    r('achievements', 'achievements.png')
    r('head', 'head.png')
    r('speech-bubble', 'speech-bubble.png')
    r('general-board', 'general-board.png', zoom=0.2)
    r('small-icon', 'icon.png', zoom=0.2)
    r('help-text', 'help-text.png')
    rf('mute-button', 'music-%d.png', 2, zoom=0.5)
    rf('achievement', 'achievement-%d.png', 2)
    r('background', 'background.png')
    r('dark-background', 'dark-background.png')
    r('main-background', 'main-background.png')
    r('very-dark-background', 'very-dark-background.png')
    r('replay-background', 'replay-background.png')
    rm(['tiles-%d' % i for i in range(25)], 'tiles.png', 5, 5)
    rf('face', 'face-%d.png', 5)
    rp('level-\d.png', zoom=0.2)
    r('random-level', 'random-level.png', zoom=0.2, w=2, framerate=2, running=True)
    rp('btn-\w+.png', prefix='forward-')
    rp('btn-\w+.png', prefix='backward-', angle=180)
    #
    # Fonts
    serge.visual.Fonts.setPath('fonts')
    serge.visual.Fonts.registerItem('main', 'PLUMP.ttf')


def registerEvents():
    """Register all the events"""
    broadcaster = serge.events.getEventBroadcaster()
    broadcaster.registerEventsFromModule(common)


def registerAchievements(options):
    """Register the achievements for the game"""
    r = serge.blocks.achievements.initManager('bomberman').safeRegisterAchievement
    a = serge.blocks.achievements.Achievement
    r(a('Played the game', 'You played the game at least once', 
        'badge', False, 'play', condition_string=': True'))
    serge.blocks.achievements.addAchievementsWorld(options, theme)
    

def startEngine(options):
    """Start the main engine"""
    engine = serge.engine.Engine(
        width=G('screen-width'), height=G('screen-height'),
        title=G('screen-title'), icon=os.path.join('graphics', G('screen-icon-filename')))
    serge.blocks.utils.createVirtualLayersForEngine(
        engine,
        ['background', 'foreground', 'main', 'bombs', 'particles', 'men', 'ui', 'ui-front', 'debug'])
    serge.blocks.utils.createWorldsForEngine(
        engine, ['start-screen', 'credits-screen', 'help-screen',
                 'level-screen', 'action-replay-screen', 'random-level-screen'])
    #
    # Handle the simulation mode (main world can run at faster than real time)
    if G('simulation-on'):
        serge.blocks.utils.createWorldsForEngine(
            engine, ['main-screen'],
            lambda name: simulation.SimulationWorld(name, G('simulation-rtf'), G('simulation-fps'), options)
        )
    else:
        serge.blocks.utils.createWorldsForEngine(
            engine, ['main-screen'],
            lambda name: simulation.SimulationWorld(name, 1, 60, options)
        )
    #
    engine.setCurrentWorldByName('start-screen' if not options.straight else 'main-screen')
    return engine


def stoppingNow(obj, arg):
    """We are about to stop"""
    #
    # Fade out music and wait for a bit before going away
    serge.sound.Music.fadeout(G('pre-stop-pause')*1000)
    #
    # Show a message
    ending = serge.blocks.utils.LoadingScreen(
        G('end-colour'), G('end-size'), G('end-font'), G('end-position'), 'ui',
        background='background', background_layer='background',
        icon_name='head', icon_position=G('end-icon-position'),
    )
    #
    # Generate random leaving message
    generator = serge.blocks.textgenerator.TextGenerator()
    generator.addExamplesFromFile(os.path.join('game', 'smack-talk.txt'))
    #
    ending.showScreen(generator.getRandomSentence('@{final-goodbye}@'))
    time.sleep(G('pre-stop-pause'))
       

def createHighScores(options):
    """Create the high score table"""
    hs = serge.blocks.onlinescores.HighScoreSystem(
        G('app-url', 'high-score-screen'), secret_user=options.cheat)
    app_name = G('app-name', 'high-score-screen')
    if hs.gameExists(app_name):
        return
    #
    common.log.info('Creating high score table')
    hs.createGame(app_name)
    #
    # Create categories
    # hs.createGameCategory(
    #     app_name,
    #     'CATEGORY_NAME',
    #     'SCORE_NAME',
    #     LOWER_IS_BETTER,
    #     MAX_PLAYER_SCORES
    # )


def main(options, args):
    """Start the engine and the game"""
    #
    # Set the levels to use - this allows us to switch to AI testing
    # levels rather than the main levels
    if options.test:
        import tests
        theme.setProperty('start-level', 1)
        common.levels = tests
    #
    # Check networkx install
    if not serge.blocks.utils.checkNetworkXVersion(1.8):
        return
    #
    # Create the high scores
    if options.high_score:
        createHighScores(options)
    #
    # Create the engine
    engine = startEngine(options)
    engine.linkEvent(serge.events.E_BEFORE_STOP, stoppingNow)
    engine.addWorld(common.TWEENER)
    #
    registerSounds()
    registerMusic()
    registerGraphics()
    registerEvents()
    #
    # Record a movie
    if options.movie:
        serge.blocks.utils.RecordDesktop(options.movie)
    #
    # Change theme settings
    if options.theme:
        theme.updateFromString(options.theme)
    #
    # Muting
    mute = serge.blocks.actors.MuteButton('mute-button', 'ui', alpha=G('mute-button-alpha'))
    serge.blocks.utils.addMuteButtonToWorlds(mute, center_position=G('mute-button-position'))
    #
    if options.muted:
        mute.toggleSound()
    if options.music_off:
        serge.sound.Music.toggle()
    #
    # Initialise the main logic
    registerAchievements(options)
    mainscreen.main(options)
    startscreen.main(options)
    helpscreen.main(options)
    creditsscreen.main(options)
    levelscreen.main(options)
    actionreplayscreen.main(options)
    randomlevelscreen.main(options)
    #
    if options.debug:
        serge.builder.builder.main(engine, options.framerate)
    else:
        engine.run(options.framerate)
