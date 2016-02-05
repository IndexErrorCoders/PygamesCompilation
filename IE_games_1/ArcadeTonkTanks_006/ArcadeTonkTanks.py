#! /usr/bin/env python
#
# Arcade Tonk Tanks 0.0.6-WORK ****** THIS IS NOT A RELEASE VERSION, PLEASE DO NOT DISTRIBUTE !!!
#
# Version history: 0.0.1    : 2009-01-14 : created by Koen Lefever using Python 2.6.1 and Pygame 1.8
#                  0.0.2    : 2009-03-31 : added option to play in full screen or in a window
#                  0.0.3    : 2009-04-01 : corrected filenames (on Linux/UNIX they're case sensitive)
#                  0.0.4    : 2009-04-01 : replaced math.trunc() by int(): this works on both Python 2.5 and 2.6
#                  0.0.5    : 2009-09-25 : added graphics by Marc Carson & music by Artsense. Tested on Pygame 1.9.1
#                  0.0.5Win : 2009-10-04 : use freesansbold.ttf font (en lieu of the built-in font). 
#                  0.0.6    : 2009-10-29 : too many bullets bug solved
#                           : 2009-11-02 : moved all global variables into module GameData
#                           : 2009-11-03 : moved all game classes & functions to their own modules
#                           : 2009-11-04 : moved what is supposed to be the AI into module DefaultBot
#                           : 2009-12-06 : added BattleGround(), scenery, water
#                           : 2009-12-09 : debugging, re-organizing code & cleaning up
#                           : 2009-12-14 : added David Howe's explosion graphics
#
# Programming by Koen Lefever (koen.lefever@gmail.com); License: GPL v.3
# Graphics & explosion sound by Marc Carson (marc@marccarson.com); License: Creative Commons CC-BY-SA 3.0
# Explosion graphics by David Howe (http://homepage.ntlworld.com/david.howe50/page16a.html)
# Music "Only Depth" by Vladislav Malkov a.k.a. Artsense (http://www.myspace.com/artsensepsy)
#
# Look for the latest version on: http://www.pygame.org/project-Arcade+Tonk+Tanks-1078-2271.html
#                             or: http://code.google.com/p/arcade-tonk-tanks/
#
#####################################################################

import math                         # pi, sin & cos are needed for tank & bullet movement
import os.path
import pygame                       # http://www.pygame.org/
from pygame.locals import *
from pygame.mixer import *          # added in 0.0.5Win: this was not necessary with interpreted code, but for py2exe we need this 

from Source import BattleGround     # map class with background image, walls, water and respawn points
from Source import GameData         # contains all global variables
from Source import Tank             # Tank class
from Source import TankCopy         # Tank icon on scoreboard
from Source import Score            # Scoreboard class
from Source import Bullet           # Bullet class
from Source import Explosion        # Explosion class
from Source import Thermometer      # Thermometer class
from Source import RespawnPoint     # Respawn point class
from Source import Graphics         # auxiliary graphics functions
from Source import Soundf           # auxiliary sound functions
from Source import GameOver         # Game Over screen class
from Source import Logo             # Arcade Tonk tanks logo class
from Source import SplashScreen     # Splash screen class
from Source import Gear             # Gear class
from Source import StringOption     # String Option class
from Source import NumericalOption  # Numerical Option class
from Source import Options          # Options screen class
from Source import DefaultBot       # Not much of an AI here

#####################################################################

def main(winstyle = 0):
    # Initialize pygame
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print 'Warning, no sound'
        pygame.mixer = None
    clock = pygame.time.Clock()

    # Set the display mode # added in 0.0.2
    print "------------------------------------------------"
    print "---      Arcade Tonk Tanks - v. 0.0.6-11     ---"
    print "------------------------------------------------"
    print "---       Programming by Koen Lefever        ---"
    print "---         Graphics by Marc Carson          ---"
    print "---     Explosion graphics by David Howe     ---"
    print "---    Music by Artsense (Vladislav Malkov)  ---"
    print "------------------------------------------------"
    print "-  http://code.google.com/p/arcade-tonk-tanks/ -"
    print "------------------------------------------------"
    print " 1: play in full screen."
    print " 2: play in a window."
    screenmode = raw_input('(1-2) ')
    if screenmode == '1':
        bestdepth = pygame.display.mode_ok(GameData.screenrect.size, pygame.FULLSCREEN, 32)
        screen = pygame.display.set_mode(GameData.screenrect.size, pygame.FULLSCREEN, bestdepth)
    else:
        screen = pygame.display.set_mode(GameData.screenrect.size)

    #Load images, assign to sprite classes (Linux/Unix filenames are case sensitive)
    Tank.images = Graphics.load_images('Red_tank_0.bmp','Red_tank_1.bmp','Red_tank_2.bmp','Red_tank_3.bmp','Red_tank_4.bmp','Red_tank_5.bmp',
        'Blue_tank_0.bmp','Blue_tank_1.bmp','Blue_tank_2.bmp','Blue_tank_3.bmp','Blue_tank_4.bmp','Blue_tank_5.bmp',
        'Green_tank_0.bmp','Green_tank_1.bmp','Green_tank_2.bmp','Green_tank_3.bmp','Green_tank_4.bmp','Green_tank_5.bmp',
        'Yellow_tank_0.bmp','Yellow_tank_1.bmp','Yellow_tank_2.bmp','Yellow_tank_3.bmp','Yellow_tank_4.bmp','Yellow_tank_5.bmp',
        'Grey_tank_0.bmp','Grey_tank_1.bmp','Grey_tank_2.bmp','Grey_tank_3.bmp','Grey_tank_4.bmp','Grey_tank_5.bmp',
        'Purple_tank_0.bmp','Purple_tank_1.bmp','Purple_tank_2.bmp','Purple_tank_3.bmp','Purple_tank_4.bmp','Purple_tank_5.bmp')
    TankCopy.images = Tank.images
    Bullet.images = Graphics.load_images('Red_bullet.bmp','Blue_bullet.bmp','Green_bullet.bmp','Yellow_bullet.bmp','Grey_bullet.bmp','Purple_bullet.bmp')
    Explosion.images0 = Graphics.load_images('boom-1-0001.png', 'boom-1-0002.png', 'boom-1-0003.png', 'boom-1-0004.png', 'boom-1-0005.png',
                                             'boom-1-0006.png', 'boom-1-0007.png', 'boom-1-0008.png', 'boom-1-0009.png', 'boom-1-0010.png',
                                             'boom-1-0011.png', 'boom-1-0012.png', 'boom-1-0013.png', 'boom-1-0014.png', 'boom-1-0015.png',
                                             'boom-1-0016.png', 'boom-1-0017.png', 'boom-1-0018.png', 'boom-1-0019.png', 'boom-1-0020.png',
                                             'boom-1-0027.png', 'boom-1-0030.png', 'boom-1-0033.png', 'boom-1-0036.png', 'boom-1-0039.png',
                                             'boom-1-0042.png', 'boom-1-0045.png', 'boom-1-0048.png', 'boom-1-0051.png', 'boom-1-0054.png',
                                             'boom-1-0057.png', 'boom-1-0060.png', 'boom-1-0063.png', 'boom-1-0066.png', 'boom-1-0069.png',
                                             'boom-1-0072.png', 'boom-1-0075.png', 'boom-1-0078.png', 'boom-1-0081.png', 'boom-1-0084.png',
                                             'boom-1-0087.png', 'boom-1-0090.png', 'boom-1-0093.png', 'boom-1-0096.png', 'boom-1-0099.png')
    Explosion.images1 = Graphics.load_images('boom-3-0001.png', 'boom-3-0002.png', 'boom-3-0003.png', 'boom-3-0004.png', 'boom-3-0005.png',
                                             'boom-3-0006.png', 'boom-3-0007.png', 'boom-3-0008.png', 'boom-3-0009.png', 'boom-3-0010.png',
                                             'boom-3-0011.png', 'boom-3-0012.png', 'boom-3-0013.png', 'boom-3-0014.png', 'boom-3-0015.png',
                                             'boom-3-0016.png', 'boom-3-0017.png', 'boom-3-0018.png', 'boom-3-0019.png', 'boom-3-0020.png',
                                             'boom-3-0027.png', 'boom-3-0030.png', 'boom-3-0033.png', 'boom-3-0036.png', 'boom-3-0039.png',
                                             'boom-3-0042.png', 'boom-3-0045.png', 'boom-3-0048.png', 'boom-3-0051.png', 'boom-3-0054.png',
                                             'boom-3-0057.png', 'boom-3-0060.png', 'boom-3-0063.png', 'boom-3-0066.png', 'boom-3-0069.png',
                                             'boom-3-0072.png', 'boom-3-0075.png', 'boom-3-0078.png', 'boom-3-0081.png', 'boom-3-0084.png',
                                             'boom-3-0087.png', 'boom-3-0090.png', 'boom-3-0093.png', 'boom-3-0096.png', 'boom-3-0099.png')                                             
    Explosion.images2 = Graphics.load_images('boom-5-0001.png', 'boom-5-0002.png', 'boom-5-0003.png', 'boom-5-0004.png', 'boom-5-0005.png',
                                             'boom-5-0006.png', 'boom-5-0007.png', 'boom-5-0008.png', 'boom-5-0009.png', 'boom-5-0010.png',
                                             'boom-5-0011.png', 'boom-5-0012.png', 'boom-5-0013.png', 'boom-5-0014.png', 'boom-5-0015.png',
                                             'boom-5-0016.png', 'boom-5-0017.png', 'boom-5-0018.png', 'boom-5-0019.png', 'boom-5-0020.png',
                                             'boom-5-0027.png', 'boom-5-0030.png', 'boom-5-0033.png', 'boom-5-0036.png', 'boom-5-0039.png',
                                             'boom-5-0042.png', 'boom-5-0045.png', 'boom-5-0048.png', 'boom-5-0051.png', 'boom-5-0054.png',
                                             'boom-5-0057.png', 'boom-5-0060.png', 'boom-5-0063.png', 'boom-5-0066.png', 'boom-5-0069.png',
                                             'boom-5-0072.png', 'boom-5-0075.png', 'boom-5-0078.png', 'boom-5-0081.png', 'boom-5-0084.png',
                                             'boom-5-0087.png', 'boom-5-0090.png', 'boom-5-0093.png', 'boom-5-0096.png', 'boom-5-0099.png')
    Thermometer.images = Graphics.load_images('temp_0.bmp','temp_1.bmp','temp_2.bmp','temp_3.bmp','temp_4.bmp','temp_5.bmp')
    RespawnPoint.images = Graphics.load_images('respawn_point_0.bmp','respawn_point_1.bmp','respawn_point_2.bmp','respawn_point_3.bmp','respawn_point_4.bmp','respawn_point_5.bmp')
    GameOver.images = [Graphics.load_image('game_over.bmp')]
    Logo.images = Graphics.load_images('ArcadeTonkTanks_0.bmp','ArcadeTonkTanks_1.bmp','ArcadeTonkTanks_2.bmp')
    SplashScreen.image = Graphics.load_image('splash_screen.bmp')
    Gear.images = Graphics.load_images('gear_R.bmp','gear_R.bmp','gear_N.bmp','gear_1.bmp','gear_2.bmp','gear_3.bmp','gear_4.bmp')
    Options.image = Graphics.load_image("Options.bmp")
    GameData.transparant_sprite = Graphics.load_image('transparant_sprite.bmp')
    
    #decorate the game window
    icon = pygame.transform.scale(Tank.images[6], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Arcade Tonk Tanks 0.0.6')
    pygame.mouse.set_visible(0)

    #create the background: tile the bgd image & draw the game maze
    bgdtile = Graphics.load_background(GameData.battleground[GameData.battlegroundnr].background, None)
    background = pygame.Surface(GameData.screenrect.size)
    Graphics.draw_background(background,bgdtile,screen)

    #load the sound effects
    boom_sound = Soundf.load_sound('boom.wav')
    if pygame.mixer:
        music = os.path.join('Sound', 'Artsense - Only Depth.ogg')
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    # Initialize Game Groups
    tanks = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    respawn_points = pygame.sprite.Group()
    tank_copies = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    splashscreens = pygame.sprite.Group()
    scores = pygame.sprite.Group()
    gameovers = pygame.sprite.Group()
    logos = pygame.sprite.Group()
    options = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    #assign default groups to each sprite class
    Score.containers = scores, all
    Tank.containers = tanks, all
    Bullet.containers = bullets, all
    Explosion.containers = explosions, all
    Thermometer.containers = all
    RespawnPoint.containers = respawn_points, all
    GameOver.containers = gameovers, all
    TankCopy.containers = tank_copies, all
    Logo.containers = logos, all
    SplashScreen.containers = splashscreens, all
    Gear.containers = all
    Options.containers = options, all
    NumericalOption.containers = options, all
    StringOption.containers = options, all

    step = 0    # used in calculation of animation cycles
        
    Logo()      # Display the animated Arcade Tonk Tanks logo
    
    # Create the respawn points
    for respawn_point in GameData.battleground[GameData.battlegroundnr].respawnpoints:
        RespawnPoint(respawn_point[0],respawn_point[1],respawn_point[2])

    thermometer = Thermometer() # Display the gun temperature
    gear = Gear()               # Display the gear of the red tank
    
    #####################################################################
    # main loop
    while True:
        # splash screen
        GameData.gamestate = "splash screen"
        active_screen = SplashScreen()
        all.clear(screen, background)

        for tank in tanks:
            tank.kill()
        for tank in tank_copies:
            tank.kill()
        for score in scores:
            score.kill()
        for explosion in explosions:
            explosion.kill()
        for bullet in bullets:
            bullet.kill()
        thermometer.temperature = 0
        thermometer.update()
        
        tanklist = [Tank(GameData.red, 0, 'Player'),
                    Tank(GameData.blue, 1, 'DefaultBot'),
                    Tank(GameData.green, 2, 'DefaultBot'),
                    Tank(GameData.yellow, 3, 'DefaultBot'),
                    Tank(GameData.grey, 4, 'DefaultBot'),
                    Tank(GameData.purple, 5, 'DefaultBot')]
                    # The 'Player' and 'DefaultBot' arguments don't do anything yet:
                    # the game is hardcoded to be played by the red tank
                    # ATTENTION: the ORDER of the tanks in the above list is important:
                    # The colour (as defined in GameData) of the tank is used as an index to a specific tank in the list

        # make tanks & respawn points which overlap the spash screen invisible
        Graphics.determine_visibility(respawn_points, tanks, tanklist, active_screen, True)
                         
        waiting = True
        while waiting:
        #get input
            for event in pygame.event.get():
                if event.type == QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                        return
            keystate = pygame.key.get_pressed()
            if keystate[K_SPACE]:
                waiting = False
            step = step + 1
            if step > 4:
                step = 0
                GameData.animstep = GameData.animstep + 1
                if GameData.animstep > 5:
                    GameData.animstep = 0
            # clear/erase the last drawn sprites
            all.clear(screen, background)
            tanks.update()
            tank_copies.update()
            respawn_points.update()
            logos.update()
            #draw the scene
            dirty = all.draw(screen)
            pygame.display.update(dirty)
            
            # cap the framerate
            clock.tick(40)

            #####################################################################
            # change game options
            if keystate[K_DELETE]:
                options_waiting = True
                for splashscreen in splashscreens:
                    splashscreen.kill()
                active_screen = Options()
                pygame.draw.rect(background, (0,0,0), (60,101,681,477), 0)
                optionscooldown = 0
                # make tanks & respawn points which overlap the options screen invisible
                Graphics.determine_visibility(respawn_points, tanks, tanklist, active_screen, True)
                while options_waiting:
                    for event in pygame.event.get():
                        if event.type == QUIT or \
                            (event.type == KEYDOWN and event.key == K_ESCAPE):
                                return
                    keystate = pygame.key.get_pressed()
                    if optionscooldown == 0:
                        if keystate[K_RIGHT]:
                            if GameData.battlegroundnr < len(GameData.battleground)-1:
                                GameData.battlegroundnr += 1
                            else:
                                GameData.battlegroundnr = 0
                            Graphics.determine_visibility(respawn_points, tanks, tanklist, active_screen, True)
                            bgdtile = Graphics.load_background(GameData.battleground[GameData.battlegroundnr].background, None)
                            Graphics.draw_background(background, bgdtile, screen, True)
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_LEFT]:
                            if GameData.battlegroundnr > 0:
                                GameData.battlegroundnr -= 1
                            else:
                                GameData.battlegroundnr = len(GameData.battleground)-1
                            Graphics.determine_visibility(respawn_points, tanks, tanklist, active_screen, True)
                            bgdtile = Graphics.load_background(GameData.battleground[GameData.battlegroundnr].background, None)
                            Graphics.draw_background(background, bgdtile, screen, True)
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_KP_MINUS] and GameData.maxbullets > 1:
                            GameData.maxbullets -= 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_KP_PLUS] and GameData.maxbullets < 99:
                            GameData.maxbullets += 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_UP] and GameData.gearcooldown < 99:
                            GameData.gearcooldown += 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_DOWN] and GameData.gearcooldown > 1:
                            GameData.gearcooldown -= 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_HOME] and GameData.bulletloadtime > 1:
                            GameData.bulletloadtime -= 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_END] and GameData.bulletloadtime < 99:
                            GameData.bulletloadtime += 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_k] and GameData.bulletspeed > 6:
                            GameData.bulletspeed -= 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_l] and GameData.bulletspeed < 20:
                            GameData.bulletspeed += 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_h] and GameData.triggerhappiness > 1:
                            GameData.triggerhappiness -= 1
                            optionscooldown = GameData.gearcooldown
                        if keystate[K_j] and GameData.triggerhappiness < 20:
                            GameData.triggerhappiness += 1
                            optionscooldown = GameData.gearcooldown
                    if keystate[K_RETURN] or keystate[K_KP_ENTER]:
                        options_waiting = False
                    if optionscooldown > 0:
                        optionscooldown -= 1
                    else:
                        optionscooldown = 0
                    step = step + 1
                    if step > 4:
                        step = 0
                        GameData.animstep = GameData.animstep + 1
                        if GameData.animstep > 5:
                            GameData.animstep = 0
                    # clear/erase the last drawn sprites
                    all.clear(screen, background)
                    tanks.update()
                    tank_copies.update()
                    respawn_points.update()
                    logos.update()
                    options.update()
                    #draw the scene
                    dirty = all.draw(screen)
                    pygame.display.update(dirty)
                    #cap the framerate
                    clock.tick(40)
                for option in options:
                    option.kill()
                Graphics.draw_background(background, bgdtile, screen)
                active_screen = SplashScreen()
                # make tanks & respawn points which overlap the options screen invisible
                Graphics.determine_visibility(respawn_points, tanks, tanklist, active_screen, True)
                
        for splashscreen in splashscreens:
            splashscreen.kill()

        # IN GAME
        # make all tanks & respawn points visible
        for respawn_point in respawn_points:
            respawn_point.visible = True
        for tank in tanks:
            tank.visible = True
        GameData.gamestate = "fighting"
        while tanklist[GameData.red].deaths < 10:   # The player dying 10 times is the losing condition (there is no way to win this game)
            #get input
            for event in pygame.event.get():
                if event.type == QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                        return
            keystate = pygame.key.get_pressed()

            # clear/erase the last drawn sprites
            all.clear(screen, background)

            #detect hits with bullets
            for bullet in bullets:
                btest = True  # Flag to prevent counting the same bullet more than once # added in 0.0.6
                for respawn_point in pygame.sprite.spritecollide(bullet, respawn_points, 0):
                    if tanklist[bullet.colour].bullets > 0:
                        tanklist[bullet.colour].bullets = tanklist[bullet.colour].bullets - 1
                    bullet.kill()
                    btest = False
                    break
                if btest:
                    for wall in GameData.battleground[GameData.battlegroundnr].walls:
                        if wall.colliderect(bullet.rect):
                            if tanklist[bullet.colour].bullets > 0:
                                tanklist[bullet.colour].bullets = tanklist[bullet.colour].bullets - 1
                            bullet.kill()
                            btest = False
                            break
                if btest:
                    for tank in pygame.sprite.spritecollide(bullet, tanks, 0):
                        if bullet.colour <> tank.colour:
                            boom_sound.play()
                            tanklist[bullet.colour].kills += 1
                            Explosion(tank)
                            tank.explode()
                            if tank.colour <> GameData.red:   # make bot come out of respawn point after being killed
                                for i in range(0,20):
                                    tank.command_queue.append("up")
                                    tank.command_queue.append("shoot")
                                tank.command_queue.append("flush")
                            if tanklist[bullet.colour].bullets > 0:
                                tanklist[bullet.colour].bullets = tanklist[bullet.colour].bullets - 1
                            bullet.kill()
                            btest = False
                            break
                if btest and ((bullet.x < 0) or (bullet.y < 0) or (bullet.x > 800) or (bullet.y > 768)):
                    if tanklist[bullet.colour].bullets > 0:
                        tanklist[bullet.colour].bullets = tanklist[bullet.colour].bullets - 1
                    bullet.kill()

            # All things tanks can do...
            for tank in tanks:
                if tank.gun_cooldown > 0:
                    tank.gun_cooldown = tank.gun_cooldown - 1
                if tank.gear_cooldown > 0:
                    tank.gear_cooldown = tank.gear_cooldown - 1
                if tank.colour <> GameData.red:
                    DefaultBot(tank) # AI control of enemy tanks
                else:
                    # handle player input
                    if keystate[K_UP]:
                        tank.command_queue.append("up")
                    if keystate[K_DOWN]:
                        tank.command_queue.append("down")
                    if keystate[K_LEFT]:
                        tank.command_queue.append("left")
                    if keystate[K_RIGHT]:
                        tank.command_queue.append("right")
                    if keystate[K_KP0]:
                        tank.command_queue.append("halt")
                    if keystate[K_SPACE]:
                        tank.command_queue.append("shoot")
                    # get rid of lag (if any) by purging the oldest commands 
                    while len(tank.command_queue) > 4:
                        dummy = tank.command_queue.pop(0)
                        
                # process commands for all tanks (player and A.I. alike)
                if len(tank.command_queue) > 0:
                    tank.process_commands(respawn_points)
                    
                tank.move()

            # display gun temperature (actually number of player bullets on screen)
            thermometer.temperature = tanklist[GameData.red].bullets
            gear.gear = tanklist[GameData.red].gear
            
            # animation cycle - needs cleanup using modula division
            step = step + 1
            if step > 4:
                step = 0
                GameData.animstep = GameData.animstep + 1
                if GameData.animstep > 5:
                    GameData.animstep = 0

            #update all the sprites
            all.update()

            #draw the scene
            dirty = all.draw(screen)
            pygame.display.update(dirty)

            #cap the framerate
            clock.tick(40)

        #####################################################################
        active_screen = GameOver()
        # make tanks & respawn points which overlap the spash screen invisible
        Graphics.determine_visibility(respawn_points, tanks, tanklist, active_screen, False)
        GameData.gamestate = "gameover"
        waiting = True
        while waiting:
            #get input
            for event in pygame.event.get():
                if event.type == QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                        return
            keystate = pygame.key.get_pressed()
            if keystate[K_RETURN] or keystate[K_KP_ENTER]:
                waiting = False
            step = step + 1
            if step > 4:
                step = 0
                GameData.animstep = GameData.animstep + 1
                if GameData.animstep > 5:
                    GameData.animstep = 0
            # clear/erase the last drawn sprites
            all.clear(screen, background)
            scores.update()
            tanks.update()
            tank_copies.update()
            respawn_points.update()
            explosions.update()
            logos.update()
            #draw the scene
            dirty = all.draw(screen)
            pygame.display.update(dirty)
            #cap the framerate
            clock.tick(40)
        for gameover in gameovers:
            gameover.kill()
                    
    print "--- Thanks for playing Arcade Tonk Tanks ---" # this never gets printed, since the above loop is infinite. Thanks for reading this program.

#####################################################################
#call the "main" function if running this script
if __name__ == '__main__': main()
