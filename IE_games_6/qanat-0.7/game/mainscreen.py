"""The main screen for the game"""

import random
import pygame
import time

import serge.engine
import serge.sound
import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.visualeffects

from theme import G, theme
import common
import player
import aliens
import ui
import weather
import serge.blocks.achievements
import serge.blocks.themes
import serge.zone


class MainScreen(serge.blocks.actors.ScreenActor):
    """The logic for the main screen"""

    def __init__(self, options):
        """Initialise the screen"""
        super(MainScreen, self).__init__('item', 'main-screen')
        self.options = options
        self.level = G('demo-level')
        self.snapshots = 0
        self.level_start_time = 0

    def addedToWorld(self, world):
        """We were added to the world"""
        super(MainScreen, self).addedToWorld(world)
        self.world = world
        self.manager = world.findActorByName('behaviours')
        self.checkTotalLevels()
        #
        # Create something to help pause
        self.pause_control = PauseControl('pause_control', 'pause_control', self, world, self.options)
        #
        # The player
        self.player = serge.blocks.utils.addActorToWorld(world, player.PlayerShip('player', 'player'))
        #
        # The background
        self.bg = serge.blocks.utils.addSpriteActorToWorld(
            world, 'bg', 'bg', 'background', 'background',
            G('bg-position'))
        self.manager.assignBehaviour(
            self.bg, serge.blocks.behaviours.ParallaxMotion(self.player, G('player-bg-speed')), 'movement')
        #
        # The ground
        self.ground = serge.blocks.utils.addSpriteActorToWorld(
            world, 'ground', 'ground', 'ground', 'ground',
            G('ground-position'))
        self.manager.assignBehaviour(
            self.ground, serge.blocks.behaviours.ParallaxMotion(
                self.player, G('player-ground-speed')), 'movement')
        #
        # The ground overlay
        self.ground_overlay = serge.blocks.utils.addSpriteActorToWorld(world, 'ground', 'ground-overlay',
                                                                       'ground-overlay', 'ground-overlay',
                                                                       G('ground-overlay-position'))
        self.manager.assignBehaviour(self.ground_overlay,
                                     serge.blocks.behaviours.ParallaxMotion(self.player,
                                                                            G('player-ground-overlay-speed')),
                                     'movement')
        #
        # Useful pieces
        self.state = serge.blocks.utils.addActorToWorld(world, ui.GameState('gamestate', 'gamestate', self.options))
        self.state.options = self.options
        self.achievements = serge.blocks.achievements.getManager()
        self.broadcaster.linkEvent(common.E_PLAYER_DESTROYED, self.playerDestroyed)
        self.broadcaster.linkEvent(common.E_ALIEN_DESTROYED, self.alienDestroyed)
        self.broadcaster.linkEvent(common.E_RESTART_GAME, self.restartGame)
        self.broadcaster.linkEvent(common.E_LOST_GAME, self.lostGame)
        #
        # UI for level over etc
        self.level_over = serge.blocks.utils.addVisualActorToWorld(world, 'text', 'level-over',
                                                                   serge.visual.Text('???', G('level-over-colour'),
                                                                                     font_size=G('level-over-size'),
                                                                                     font_name='CONTROL',
                                                                                     justify='center'),
                                                                   'ui', (G('level-over-x'), G('level-over-y')))
        self.level_over.active = False
        self.get_ready = serge.blocks.utils.addActorToWorld(world,
                                                            serge.blocks.actors.NumericText('text', 'get-ready',
                                                                                            'Get Ready %d',
                                                                                            G('get-ready-colour'),
                                                                                            font_size=G(
                                                                                                'get-ready-size'),
                                                                                            justify='left',
                                                                                            font_name='CONTROL',
                                                                                            value=G('get-ready-time')),
                                                            layer_name='ui',
                                                            center_position=(G('get-ready-x'), G('get-ready-y')))
        self.level_over.active = False
        self.get_ready.active = False
        self.countdown = self.manager.assignBehaviour(self,
                                                      serge.blocks.behaviours.TimedCallback(1000, self.countdownTick),
                                                      'get-ready')
        self.countdown.pause()
        self.level_over_callback = self.manager.assignBehaviour(self,
                                                                serge.blocks.behaviours.TimedCallback(
                                                                    G('level-over-time') * 1000,
                                                                    self.newLevelCountdown), 'level-change')
        self.level_over_callback.pause()
        #
        # Cheating stuff
        if self.options.cheat:
            fps = serge.blocks.actors.FPSDisplay(50, 550, (255, 255, 0), 12, font_name='CLEAR')
            world.addActor(fps)
            #
        # Weather
        self.weather_manager = weather.Weather('weather', 'weather')
        world.addActor(self.weather_manager)
        #
        self.createWaves()
        self.started = False
        self.repeats = 0
        #
        # Music
        playlist = ['track-1', 'track-2', 'track-3']
        random.shuffle(playlist)
        serge.sound.Music.setPlaylist(playlist)

    def updateActor(self, interval, world):
        """Update this actor"""
        if self.started:
            super(MainScreen, self).updateActor(interval, world)
            for wave in self.waves + self.descending_waves:
                if not wave.isComplete():
                    break
            else:
                if not self.state.isGameOver():
                    self.levelOver()
                #
            if self.options.debug and self.keyboard.isClicked(pygame.K_F2):
                # Open a shell
                from IPython.Shell import IPythonShellEmbed

                ipshell = IPythonShellEmbed(['-gthread'], 'Game Interactive Shell', 'Left Shell', user_ns=locals())
                ipshell() # this call anywhere in your program will start IPython
                #
            if self.options.debug and self.keyboard.isClicked(pygame.K_F3):
                self.levelOver()

    def checkTotalLevels(self):
        """Try to see how many levels there are"""
        for idx in range(100):
            try:
                _ = G('alien-waves', str(idx))
            except serge.blocks.themes.BadInheritance:
                # Ok, found the end
                break
            #
        self.log.info('Found %d total levels' % (idx - 1))
        self.total_levels = idx - 1

    def createWaves(self):
        """Create waves for this level"""
        theme.selectTheme(str(self.level))
        #
        # Alien waves
        self.waves = []
        for row, lineup in enumerate(G('alien-waves')):
            controller = aliens.WAVE_CONTROLLERS[G('wave-controller')]
            a = serge.blocks.utils.addActorToWorld(
                self.world, controller(row, G('alien-x'), G('alien-y') + row * G('alien-y-spacing'), lineup))
            self.waves.append(a)
            #
        # Descending waves
        self.descending_waves = []

    def clearWaves(self):
        """Clear all the waves"""
        for actor in self.world.findActorsByTag('wave'):
            self.world.removeActor(actor)

    def playerDestroyed(self, (collider, ship), arg):
        """The player was destroyed"""
        if not self.state.level_starting and not self.player.flashing:
            self.player.destroyTurret()
            self.world.scheduleActorRemoval(collider)

    def alienDestroyed(self, (collider, alien), arg):
        """An alien was destroyed"""
        self.world.scheduleActorRemoval(collider)
        alien.hitByBomb(collider)

    def levelOver(self):
        """The level has finished"""
        self.log.info('Level is over')
        self.achievements.makeReport('level-time', start=self.level_start_time, time=time.time())
        self.level += 1
        #
        if self.level > self.total_levels:
            self.repeats += 1
            self.achievements.makeReport('levels', repeats=self.repeats)
            self.level = 1
            self.broadcaster.processEvent((common.E_LEVEL_REWIND, self))
            self.player.makeHarder()
        self.level_over.active = True
        self.active = False
        self.level_over.visual.setText(G('level-over-title'))
        self.level_over_callback.restart()

    def newLevelCountdown(self, world, actor, interval):
        """Start countdown for new level"""
        self.get_ready.active = True
        self.countdown.restart()
        serge.sound.Sounds.play('countdown')
        self.level_over_callback.pause()
        self.clearWaves()

    def countdownTick(self, world, actor, interval):
        """Tick the countdown timer"""
        self.get_ready.value -= 1
        if self.get_ready.value <= 0:
            self.get_ready.value = G('get-ready-time')
            self.newLevel(world, actor, interval)
            self.countdown.pause()
            self.level_start_time = time.time()
            serge.sound.Sounds.play('start')
        else:
            serge.sound.Sounds.play('countdown')

    def newLevel(self, world, actor, interval):
        """A new level should begin"""
        self.active = True
        self.createWaves()
        self.level_over.active = False
        self.get_ready.active = False
        self.broadcaster.processEvent((common.E_NEW_LEVEL, self))

    def restartGame(self, obj, arg):
        """Restart the game"""
        for actor in self.world.findActorsByTag('yellow-bomb') + self.world.findActorsByTag(
                'green-bomb') + self.world.findActorsByTag('red-bomb'):
            self.world.removeActor(actor)
        for actor in self.world.findActorsByTag('alien'):
            self.world.removeActor(actor)
        self.level = G('start-level')
        self.clearWaves()
        self.createWaves()
        self.active = True
        self.started = True

    def lostGame(self, obj, arg):
        """The game was lost"""
        self.level_over.active = self.get_ready.active = False
        if self.level_over_callback.isRunning():
            self.level_over_callback.pause()
            self.level_over_callback._behaviour.timer = 0
        if self.countdown.isRunning():
            self.countdown.pause()
            self.countdown._behaviour.timer = 0
            self.get_ready.value = G('get-ready-time')


class PauseControl(serge.blocks.actors.ScreenActor):
    """Simple helper to help pause the entire game"""

    def __init__(self, tag, name, screen, world, options):
        """Added to the world"""
        super(PauseControl, self).__init__(tag, name)
        #
        self.screen = screen
        self.options = options
        #
        self.addedToWorld(world)
        #
        self.zone = list(world.zones)[0]
        new_zone = serge.zone.Zone()
        new_zone.active = True
        new_zone.addActor(self)
        world.addZone(new_zone)
        #
        self.paused = False
        #
        self.visual = serge.visual.Text(
            'Paused   P to Resume', G('pause-colour'), G('pause-font'), G('pause-size'))
        self.moveTo(*G('pause-position'))
        self.setLayerName('ui')
        self.visible = False

    def updateActor(self, interval, world):
        """Update the pause_control"""
        if self.screen.started and self.keyboard.isClicked(pygame.K_p):
            self.paused = not self.paused
            self.log.info('Pause changed to %s' % self.paused)
            self.zone.active = not self.paused
            self.visible = self.paused
            if not self.options.musicoff:
                serge.sound.Music.toggle()


def main(options):
    """Create the main logic"""
    #
    # The behaviour manager
    world = serge.engine.CurrentEngine().getWorld('main-screen')
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # The screen actor
    s = MainScreen(options)
    world.addActor(s)
    #
    # Snapshotting
    if options.screenshot:
        manager.assignBehaviour(None,
                                serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                                    , overwrite=False, location='screenshots'), 'screenshot')