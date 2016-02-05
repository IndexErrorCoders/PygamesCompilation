"""The main screen of the game"""

import random
import time
import itertools
import collections
import pyglet
from aranara.items import emitter

import engine
import settings
import sound
import ui.gerty
import ui.palette
import ui.scorehud
import common
from ui.gerty import *


class MainScreen(engine.World):
    """The main screen in the game"""

    name = 'unknown'
    icon = 'aranara1.png'
    conversation_logic = []
    music ='lunar'
    possible_musics = ['lunar', 'crystal', 'spiritual']
    background_tween = [(255, 255, 255), (255, 255, 255)]

    def __init__(self, options):
        """Initialise the screen"""
        super(MainScreen, self).__init__(self.name, options)
        #
        self.music = random.choice(self.possible_musics)

    def worldCreated(self):
        """The world was created"""
        super(MainScreen, self).worldCreated()
        #
        # Drawing layers
        self.game_back = pyglet.graphics.OrderedGroup(0)
        self.game_main = pyglet.graphics.OrderedGroup(1)
        self.game_fore = pyglet.graphics.OrderedGroup(2)
        self.ui_back = pyglet.graphics.OrderedGroup(3)
        self.ui_middle = pyglet.graphics.OrderedGroup(4)
        self.ui_front = pyglet.graphics.OrderedGroup(5)
        self.gerty_back = pyglet.graphics.OrderedGroup(6)
        self.gerty_front = pyglet.graphics.OrderedGroup(7)
        self.gerty_text = pyglet.graphics.OrderedGroup(8)
        #
        self.setBounds(-500, -500, 1500, 1000)
        self.harvesters = []
        self.level_complete = False
        #
        self.gerty_state = collections.defaultdict(lambda: 0)
        self.gerty_state[W_INITIAL] = True
        self.gerty_state[W_TOTAL_TIME] = 0.0
        self.gerty_state[W_TOTAL_TIME] = 0.0
        #
        self.main_batch = self.addBatch('ui-layer')
        #
        back = self.addActor(
            engine.SpriteActor('background', 'starfield-small.jpg', 1024 / 2, 640 / 2, batch=self.main_batch,
                               group=self.game_back))
        back.scale = 1.5
        self.tweens.append(
            engine.Tween(
                back, 'color', self.background_tween[0], self.background_tween[1], 10,
                engine.Tween.colourTween, repeat=True
            )
        )
        self.palette_buttons = self.initLevel()
        #
        self.palette = ui.palette.Palette('palette', batch=self.main_batch, group=self.ui_back)
        self.addActor(self.palette)
        self.palette.show()
        if self.palette_buttons:
            self.palette.addButtons(self.palette_buttons)
        #
        self.gerty = ui.gerty.GertyUI('gerty', batch=self.main_batch, group=self.gerty_front)
        self.addActor(self.gerty)
        self.gerty_state[W_GERTY] = self.gerty
        self.gerty.setWorldState(self.gerty_state)
        self.gerty.setConversation(self.conversation_logic)
        #
        # The level complete flag
        self.complete_banner = engine.SpriteActor('complete', 'level-complete.png', batch=self.main_batch, group=self.ui_back)
        self.complete_banner.position = settings.S.complete_position
        self.complete_banner.visible = False
        self.tweens.append(
            engine.Tween(self.complete_banner, 'color', [255, 255, 255], [100, 255, 100], 0.2,
                         engine.Tween.colourTween, repeat=True)
        )
        self.complete_banner.linkEvent(engine.events.E_LEFT_CLICK, self.levelCompleteClick)
        self.addActor(self.complete_banner)

        #
        # The score HUD
        self.scorehud = ui.scorehud.ScoreHUD('score-hud', batch=self.main_batch, group=self.ui_middle)
        self.addActor(self.scorehud)
        self.scorehud.show()

    def initLevel(self):
        """Initialise level specific logic and content"""

    def onKeyPress(self, symbol, modifier):
        """Handle key presses"""
        super(MainScreen, self).onKeyPress(symbol, modifier)
        #
        if symbol == pyglet.window.key.ESCAPE:
            self.engine.fadeToWorld('level-screen', settings.S.fade_screen_delay)
            return pyglet.event.EVENT_HANDLED

    def onKeyRelease(self, symbol, modifier):
        """Handle key presses"""
        super(MainScreen, self).onKeyRelease(symbol, modifier)
        #
        # Some debugging code
        if self.options.cheat:
            if symbol == pyglet.window.key.G:
                self.gerty.toggle()
            if symbol == pyglet.window.key.H:
                self.gerty.setState(ui.gerty.S_HAPPY)
            if symbol == pyglet.window.key.C:
                self.gerty.setState(ui.gerty.S_CONCERNED)
            if symbol == pyglet.window.key.W:
                self.gerty.setState(ui.gerty.S_WORRIED)
            if symbol == pyglet.window.key.Q:
                self.gerty.say('<b>Sam</b>, your current score is %d' % self.score)
            if symbol == pyglet.window.key.R:
                getattr(sound.Music, self.music).play()
            if symbol == pyglet.window.key.T:
                getattr(sound.Music, self.music).pause()

    def gotHelium(self, (collector, helium, score), arg):
        """Got some helium"""
        #
        # Record world states for Gerty
        if score > 0:
            self.gerty_state[W_SCORED] += score
        else:
            self.gerty_state[W_SCORED_NEGATIVE] += score
        self.score += score
        self.gerty_state[W_LAST_SCORE] = time.time()
        self.gerty_state[W_TOTAL_SCORE] = self.score

    def activateWorld(self):
        """The world was activated"""
        super(MainScreen, self).activateWorld()
        #
        getattr(sound.Music, self.music).play()

    def deactivateWorld(self, next_world_name):
        """The world was deactivated"""
        super(MainScreen, self).deactivateWorld(next_world_name)
        #
        getattr(sound.Music, self.music).pause()

    def updateWorld(self, dt):
        """Update the world"""
        super(MainScreen, self).updateWorld(dt)
        #
        # Check if all harvesters are full
        if not self.level_complete and all(harvester.isFull() for harvester in self.harvesters):
            self.log.info('The level is complete')
            self.level_complete = True
            self.complete_banner.visible = True
            sound.Sounds.end_of_level.play()
            self.gerty_state[W_LEVEL_COMPLETE] = True
            self.gerty_state[W_TIME_SINCE_COMPLETE] = 0.0
            self.gerty_state[W_TIME_LEVEL_SOLVED] = time.time()
        elif self.level_complete:
            self.gerty_state[W_TIME_SINCE_COMPLETE] += dt
        #
        # Update Gerty stats
        self.gerty_state[W_TOTAL_TIME] += dt

    def levelCompleteClick(self, obj, arg):
        """Clicked on the complete level"""
        #
        # Go back to level screen
        sound.Sounds.click_backward.play()
        self.engine.fadeToWorld('level-screen', settings.S.fade_screen_delay)


def Say(text, world_state, gerty):
    """Function to say something"""
    gerty.say(text)
    world_state[W_LAST_SPOKE] = time.time()


def Set(name, value, world_state, gerty):
    """Function to set something"""
    world_state[name] = value


def Hide(world_state, gerty):
    """Hide Gerty"""
    gerty.hide()


def ChangeState(state, world_state, gerty):
    """Change Gerty's state"""
    gerty.setState(state)