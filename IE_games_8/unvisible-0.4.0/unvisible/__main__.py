"""Main loop for the game"""

import pygame

import settings as S
import loggable
import drawable
import sound
import gamestate
import outofgamestate
import sound
import common
import time
import os


def initPygame():
    """Initialise pygame"""
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.set_num_channels(S.Sound.number_audio_channels)
    screen = pygame.display.set_mode((S.Screen.width, S.Screen.height))
    pygame.display.set_caption('Unvisible')
    return screen


def main(options, args):
    """Main loop"""
    #
    # Set options
    loggable.logger.setLevel(options.log)
    sound.MUTED = options.mute
    #
    log = loggable.getLogger('engine')
    log.info('Starting engine (v%s' % common.__version__)
    #
    running = True
    #
    screen = initPygame()
    #
    # Control when out of the game
    other_screens = outofgamestate.OutOfGame(options.speed)
    sound.Sounds.playMusic(S.Music.start_music)
    #
    # Setup game state
    game = gamestate.GameState(other_screens, options.speed)
    app = other_screens
    #
    log.info('Initialisation complete')
    screenshot_id = 1
    #
    # Main loop of the engine
    while running:
        clicked_on = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYUP:
                if app.processKey(event.key) == pygame.QUIT:
                    running = False
                elif event.key == pygame.K_s:
                    pygame.image.save(screen, os.path.join('screenshots', 'screenshot-%d.png' % screenshot_id))
                    screenshot_id += 1
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                clicked_on = app.processClick(event.type, event.pos)
        #
        # Switch between game and other screen
        if other_screens.state == outofgamestate.S_GAME_SCREEN:
            app = game
        elif other_screens.state == outofgamestate.S_NEW_GAME:
            game = gamestate.GameState(other_screens, options.speed)
            app = game
            other_screens.state = outofgamestate.S_GAME_SCREEN
        else:
            app = other_screens
        #
        # Update and render
        app.updateState(clicked_on)
        screen.fill(S.Screen.background_colour)
        app.renderTo(screen)
        #
        pygame.display.flip()
        #
        if other_screens.state == outofgamestate.S_QUIT:
            break
    #
    log.info('Engine quiting')

