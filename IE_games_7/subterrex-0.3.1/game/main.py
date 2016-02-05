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
try:
    import serge.builder.builder
except ImportError:
    pass

import serge.blocks.utils

import common
import mainscreen
import startscreen
import helpscreen
import creditsscreen
import namescreen
import collectionscreen
import history

from theme import G, theme

def registerSounds():
    """Register the sounds to use"""
    serge.sound.Sounds.setPath('sound')
    r = serge.sound.Sounds.registerItem
    r('click', '525__jenc__pang.wav')
    r('wet-cave', '26910__thedapperdan__sewer-drain.ogg')
    r('ambience', '147919__klankbeeld__horror-ambience-22.wav')
    r('water', '26910__thedapperdan__sewer-drain.ogg')
    r('crystal', '65382__digifishmusic__aceeeent.wav')
    r('take-crystal', '153101__mlteenie__crystal-glass.wav')
    r('ok-crystal', '30__anton__glass-d-ff.wav')
    r('exit-sound', '12693__connum__melancholic-burble-in-f-major.wav')
    r('crystal-banner', '29591__erh__atmosphere-2.wav')
    r('fire-rope', '65734__erdie__bow02.wav')
    r('flare-start', '23533__percy-duke__match-strike.wav')
    r('flare', '82393__benboncan__camping-stove.wav')
    r('player-hit-rock', '7136__mystiscool__rocks2.wav')
    r('player-death', '85532__maj061785__body-hitting-mat.wav')
    r('meadow', '122014__klankbeeld__white-noise-meadow-land-road-spring-moerputten.wav')
    r('frog-1', '117863__klankbeeld__frog-003.wav')
    r('frog-2', '117866__klankbeeld__frog-006.wav')
    r('bat-1', '47413__klankschap__bat2.wav')
    r('bat-2', '43823__digifishmusic__bats-hunting-for-insects-8x-slower.wav')
    r('dino-1', '89547__cgeffex__dinosaur-dino-growl1.wav')
    r('dino-2', '94589__robinhood76__01569-monster-breath.wav')
    
def registerMusic():
    """Register the music to use"""
    serge.sound.Music.setPath('music')
    r = serge.sound.Music.registerItem
    r('title-music', 'Broke_For_Free_-_07_-_Spellbound.mp3')

def registerGraphics():
    """Register the graphics to use"""
    serge.visual.Sprites.setPath('graphics')
    r = serge.visual.Sprites.registerItem
    rf = serge.visual.Sprites.registerFromFiles
    rm = serge.visual.Sprites.registerMultipleItems
    rp = serge.visual.Sprites.registerItemsFromPattern
    r('icon', 'icon.png')
    r('logo', 'icon.png', zoom=1.0, convert_alpha=True)
    r('small-icon', 'icon.png', zoom=0.2)
    r('help-text', 'help-text.png')
    rf('mute-button', 'music-%d.png', 2, zoom=0.5)
    rf('achievement', 'achievement-%d.png', 2)
    #
    rm(['moss', 'red', 'yellow', 'blue',
        'magenta', 'orange', 'rock', 'black',
        'lime', 'cyan', 'fuscia', 'brown'], 
        'generic-tileset.png', 4, 3, zoom=G('tile-scale'))
    r('light', 'light.png', zoom=0.5)
    r('flare', 'flare.png')
    r('timer', 'timer.png', zoom=0.5)
    r('floor', 'floor.png')
    r('crystal', 'crystal.png', 2, framerate=1, running=True, zoom=0.1)
    r('big-crystal', 'crystal.png', 2, framerate=1, running=True, zoom=0.25)
    #rf('smoke', 'smoke-%d.png', 3, zoom=0.25)
    r('water', 'water.png', 7, 5)
    r('foam', 'foam.png')
    rp(r'(\w+)-smoke.png', w=2, h=1, running=True, framerate=1, loop=False, one_direction=True, convert_alpha=True)
    r('surface', 'surface.png', convert_alpha=True)
    r('background', 'background.png', convert_alpha=True)
    r('lamp', 'lamp.png', 4, 1, 2, True, loop=True)
    r('standing-still', 'standing-still.png', 5, 5, running=True, framerate=10, loop=True, convert_alpha=True)
    r('standing-jump', 'standing-jump.png', 5, 19, running=True, framerate=100, loop=False, convert_alpha=True)
    r('falling', 'falling.png', 5, 18, running=True, framerate=25, loop=False, convert_alpha=True)
    r('hanging', 'hanging.png', 5, 18, running=True, framerate=25, loop=True, convert_alpha=True)
    r('walking', 'walking.png', 5, 20, running=True, framerate=50, one_direction=True, convert_alpha=True)
    r('climbing', 'climbing.png', 2, 1, running=True, framerate=10, convert_alpha=True)
    rf('named-crystal', 'named-crystal-%d.png', 2, running=True, framerate=10)
    r('dead-body', 'death.png')
    r('bug', 'bug.png', zoom=0.25)
    rp('(\w+)-light.png', zoom=0.25)
    #
    # Fonts
    serge.visual.Fonts.setPath('fonts')
    serge.visual.Fonts.registerItem('DEFAULT', 'BIGBB___.TTF')
           
def registerEvents():
    """Register all the events"""
    broadcaster = serge.events.getEventBroadcaster()
    broadcaster.registerEventsFromModule(common)

def registerAchievements(options):
    """Register the achievements for the game"""
    r = serge.blocks.achievements.initManager('serge-potholer').safeRegisterAchievement
    a = serge.blocks.achievements.Achievement
    r(a('Shallow grave', 'Die within 200ft of the surface', 
        'badge', False, 'death', condition_string='depth : depth < 1000'))
    r(a('Cave novice', 'Beat at least one cave', 
        'badge', False, 'solve', condition_string='caves, this_cave, tme : caves >= 1'))
    r(a('Cave expert', 'Beat at least five caves', 
        'badge', False, 'solve', condition_string='caves, this_cave, tme : caves >= 5'))
    r(a('Deja vu', 'Beat the same cave more than once', 
        'badge', False, 'solve', condition_string='caves, this_cave, tme : this_cave >= 2'))
    r(a('Speed climber', 'Beat a cave in less that two minutes', 
        'badge', False, 'solve', condition_string='caves, this_cave, tme : tme <= 120'))
    r(a('Crystal spotter', 'Collect at least two crystals in a cave', 
        'badge', False, 'crystals', condition_string='number, total : number >= 2'))
    r(a('Crystal ferret', 'Collect all the crystals in a cave', 
        'badge', False, 'crystals', condition_string='number, total : number == total'))
    r(a('Crystal collector', 'Collect 5 named crystals', 
        'badge', False, 'named-crystals', condition_string='number : number >= 5'))
    r(a('Crystal curator', 'Collect 10 named crystals', 
        'badge', False, 'named-crystals', condition_string='number : number >= 10'))
    r(a('Crystal archivist', 'Collect 30 named crystals', 
        'badge', False, 'named-crystals', condition_string='number : number >= 30'))
    serge.blocks.achievements.addAchievementsWorld(options, theme)
    
def startEngine(options):
    """Start the main engine"""
    engine = serge.engine.Engine(width=G('screen-width'), height=G('screen-height'), 
        title=G('screen-title'), fullscreen=options.fullscreen)
    serge.blocks.utils.createVirtualLayersForEngine(engine, ['background', 'foreground', 'foam', 'main', 
        'ropes', 'smoke', 'actors', 'trees', 'light', 'ui-back', 'ui-highlight', 'ui', 'overlay'])
    serge.blocks.utils.createWorldsForEngine(engine, ['start-screen', 'name-screen', 
        'main-screen', 'credits-screen', 'help-screen', 'collection-screen'])
    #
    if options.engine_profile:
        engine.profilingOn()
    #
    # The layers which don't move with the camera
    for layer in ('ui', 'ui-back', 'ui-highlight'):
        engine.getRenderer().getLayer(layer).setStatic(True)
    #
    # For the start screen we want to isolate the rope from the cave since they move independently so
    # we create two zones. 
    world = engine.getWorld('start-screen')
    rope_zone = serge.zone.TagIncludeZone(['player', 'rope', 'rope-anchor', 'rope-link'])
    none_rope_zone = serge.zone.TagExcludeZone(['player', 'rope', 'rope-anchor', 'rope-link'])
    rope_zone.active = none_rope_zone.active = True
    rope_zone.physics_stepsize = 1.0
    world.clearZones()
    world.addZone(rope_zone)
    world.addZone(none_rope_zone)
    #
    engine.setCurrentWorldByName('start-screen' if not options.skip else 'main-screen')
    return engine

def stoppingNow(obj, arg):
    """We are about to stop"""
    #
    # Fade out music and wait for a bit before going away
    serge.sound.Music.fadeout(G('pre-stop-pause')*1000)
    time.sleep(G('pre-stop-pause'))
       


def main(options, args):
    """Start the engine and the game"""
    #
    # For ropes and things we typically need a higher number of iterations
    serge.zone.PHYSICS_ITERATIONS = 100
    #
    # Create the engine
    engine = startEngine(options)
    engine.linkEvent(serge.events.E_BEFORE_STOP, stoppingNow)
    #
    registerSounds()
    registerMusic()
    registerGraphics()
    registerEvents()
    #
    # Change theme settings
    if options.theme:
        theme.updateFromString(options.theme)
    #
    # Muting
    mute = serge.blocks.actors.MuteButton('mute-button', 'ui', alpha=G('mute-button-alpha'))
    serge.blocks.utils.addMuteButtonToWorlds(mute, center_position=G('mute-button-position'))
    #
    if options.musicoff:
        mute.toggleSound()
    #
    # Initialise the main logic
    globals = serge.blocks.singletons.Store.registerItem('globals')  
    globals.history = history.History('history', 'history')
    globals.last_cave_name = 'RANDOM-CAVE'
    #
    registerAchievements(options)
    if options.skip:
        mainscreen.main(options)
    else:
        startscreen.main(options)
        #
        # Force a rendering of the overlay - this puts
        # up the "loading ..." screen so the user has something
        # to see while we create the cave and trees etc
        w = engine.getWorld('start-screen')
        w.log.info('Rendering overlay')
        w.renderTo(engine.getRenderer(), 1000)
        engine.getRenderer().render()
        pygame.display.flip()
    #
    helpscreen.main(options)
    creditsscreen.main(options)
    namescreen.main(options)
    collectionscreen.main(options)
    #   
    #
    if options.movie:
        serge.blocks.utils.RecordDesktop(options.movie)
    if options.debug:
        serge.builder.builder.main(engine, options.framerate)
    else:
        try:
            engine.run(options.framerate)
        except:
            # Make sure this event is raised so that any workers can be killed
            engine.processEvent((serge.events.E_BEFORE_STOP, None))
            raise
    #
    # Display profile statistic if needed
    if options.engine_profile:
        prof = engine.getProfiler()
        data = [(prof.byTag(n).get('renderActor', (0,0))[1], n) for n in prof.getTags()]
        data.sort()
        data.reverse()
        print '\n\nEngine profiling\n\nTag\tTime(s)'
        for tme, tag in data:
            print '%s\t%s' % (tag, tme)
        print '\n\n'
