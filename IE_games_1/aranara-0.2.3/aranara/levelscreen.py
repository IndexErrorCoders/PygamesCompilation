"""The entry screen for the game"""

import collections
import time
from pymunk import Vec2d
import pyglet

import engine
import levels
import settings
import sound
import ui
from ui.gerty import *
import mainscreen as m

# Gerty states
W_TOLD_OF_CORRUPTION = 'told-of-corruption'


class LevelScreen(engine.World):
    """The main start screen for the game"""

    conversation_logic = []
    
    def worldCreated(self):
        """The screen was created"""
        #
        # Create the batches
        text = self.addBatch('text')
        #
        back_layer = pyglet.graphics.OrderedGroup(0)
        icon_layer = pyglet.graphics.OrderedGroup(1)
        text_layer = pyglet.graphics.OrderedGroup(2)
        #
        bg = engine.SpriteActor('bg', 'start-bg.jpg', batch=text, group=back_layer)
        bg.position = settings.S.Start.bg_position
        self.addActor(bg)
        #
        # self.tweens.append(
        #     engine.Tween(bg, 'opacity', 255, engine.utils.RandomGenerator(150, 200),
        #                  engine.utils.RandomGenerator(3, 5),
        #                  engine.Tween.sinInOut, repeat=True)
        # )
        #
        logo = engine.SpriteActor('logo', 'logo.png', batch=text, group=text_layer)
        logo.position = settings.S.Start.logo_position
        self.addActor(logo)
        #
        back = engine.SpriteActor('back-button', 'back.png', batch=text, group=text_layer)
        back.position = settings.S.Level.back_btn_position
        back.linkEvent(engine.events.E_LEFT_CLICK, self.backClicked)
        self.addActor(back)
        #
        self.objects = []
        for idx, level in enumerate(levels.levels):
            #
            # The text for the level
            new_level = engine.TextActor(
                level.Level.name, pyglet.text.decode_attributed(
                    '{color (255,255,255,255)}{font_name "Sci Fied 2002"}%s' % level.Level.name), batch=text, group=text_layer)
            new_level.x = settings.S.Level.icons_start_x + (float(idx % settings.S.Level.icons_per_row) /
                                                            (settings.S.Level.icons_per_row - 1) - 0.5) * settings.S.Level.icons_width
            new_level.y = settings.S.Level.icons_start_y + settings.S.Level.icons_rows_height * (idx // settings.S.Level.icons_per_row)
            new_level.linkEvent(engine.events.E_LEFT_CLICK, self.startLevel, idx)
            self.addActor(new_level)
            new_level.target_x = new_level.x
            new_level.target_y = new_level.y
            new_level.level_num = idx
            #
            # The image for the level
            img = engine.SpriteActor('icon-%d' % idx, level.Level.icon, batch=text, group=icon_layer)
            img.x = img.target_x = new_level.x
            img.y = img.target_y = new_level.y - settings.S.Level.icon_offset_y
            self.addActor(img)
            img.linkEvent(engine.events.E_LEFT_CLICK, self.startLevel, idx)
            img.level_num = idx
            #
            self.objects.append(new_level)
            self.objects.append(img)
        #
        self.current_level = settings.S.start_level
        self.level_cache = {}
        #
        self.ui_back = pyglet.graphics.OrderedGroup(3)
        self.ui_middle = pyglet.graphics.OrderedGroup(4)
        self.ui_front = pyglet.graphics.OrderedGroup(5)
        self.gerty_back = pyglet.graphics.OrderedGroup(6)
        self.gerty_front = pyglet.graphics.OrderedGroup(7)
        self.gerty_text = pyglet.graphics.OrderedGroup(8)
        #
        # Gerty stuff
        self.gerty_state = collections.defaultdict(lambda: 0)
        self.gerty_state[W_INITIAL] = True
        self.gerty_state[W_TOTAL_TIME] = 0.0
        self.gerty_state[W_TOTAL_TIME] = 0.0
        self.gerty_state[W_LEVELS_SOLVED] = []
        #
        self.gerty = ui.gerty.GertyUI('gerty', batch=text, group=self.gerty_front)
        self.gerty.y = -1000
        self.addActor(self.gerty)
        self.gerty_state[W_GERTY] = self.gerty
        self.gerty.setWorldState(self.gerty_state)
        self.gerty.setConversation(self.conversation_logic)
        #
        self.age = 0

    def applyTweens(self, start_offset_x, start_offset_y, end_offset_x, end_offset_y, after=None, skip=None):
        """Apply the tweens to bring items on the screen"""
        #
        # Tween in the image
        idx = 0
        for item in self.objects:
            if item.level_num != skip:
                self.tweens.append(
                    engine.Tween(
                        item, 'position', Vec2d(item.target_x + start_offset_x, item.target_y + start_offset_y),
                        Vec2d(item.target_x + end_offset_x, item.target_y + end_offset_y),
                        settings.S.Level.tween_in_duration, engine.Tween.sinOut,
                        delay=float(settings.S.Level.tween_in_delay),
                        after=after if idx == 0 else None
                    )
                )
                idx += 1

    def onKeyPress(self, symbol, modifier):
        """Handle key presses"""
        super(LevelScreen, self).onKeyPress(symbol, modifier)
        #
        if symbol == pyglet.window.key.ESCAPE:
            self.engine.setCurrentWorld('start-screen')
            return pyglet.event.EVENT_HANDLED

    def onKeyRelease(self, symbol, modifier):
        """Handle key presses"""
        super(LevelScreen, self).onKeyRelease(symbol, modifier)
        #
        if symbol == pyglet.window.key.ESCAPE:
            return pyglet.event.EVENT_HANDLED
        #
        # Debugging code
        if self.options.cheat:
            if symbol == pyglet.window.key.P:
                self.log.debug('Trying to start sinister music')
                sound.Music.sinister.pause()

    def startClicked(self, obj, arg):
        """The start button was clicked"""
        self.log.info('Start was clicked - current level is %d' % self.current_level)
        #
        # Find the level
        if self.current_level in self.level_cache:
            level = self.level_cache[self.current_level]
        else:
            level_module = levels.levels[self.current_level]
            level = self.level_cache[self.current_level] = level_module.Level(self.options)
            self.engine.addWorld(level)
        #
        # Switch to it
        self.engine.fadeToWorld(level.name, settings.S.fade_screen_delay)
        #
        # Move on to next level
        self.current_level += 1
        if self.current_level >= len(levels.levels):
            self.current_level = 0

    def startLevel(self, obj, level):
        """Start a particular level"""
        sound.Sounds.click_accept.play()
        self.current_level = level
        self.applyTweens(
            0, 0, 0, settings.S.Level.tween_out_offset_y, after=self._startLevelReady,
            skip=level
        )
        self.gerty_state[W_LEVELS_SOLVED].append(self.current_level)
        self.gerty_state[W_TIME_LEVEL_ENTERED] = time.time()

    def _startLevelReady(self):
        """Ready to start the level"""
        self.startClicked(None, None)

    def backClicked(self, obj, arg):
        """Back was clicked"""
        self.log.info('Back was clicked')
        sound.Sounds.click_backward.play()
        self.applyTweens(0, 0, settings.S.Level.tween_in_offset_x, 0, after=self._backDone)

    def _backDone(self):
        """Back is ready to go"""
        self.engine.setCurrentWorld('start-screen')

    def activateWorld(self):
        """The world was activated"""
        super(LevelScreen, self).activateWorld()
        #
        if not sound.Music.sinister.playing:
            self.log.info('Trying to restart the music')
            sound.Music.sinister.play()
        self.applyTweens(settings.S.Level.tween_in_offset_x, 0, 0, 0)

    def deactivateWorld(self, next_world_name):
        """Deactivate the world"""
        if next_world_name != 'start-screen':
           sound.Music.sinister.pause()



LevelScreen.conversation_logic = [
    (
        'Introduce Tess', True,
        [
            lambda w: 2 in w[W_LEVELS_SOLVED],
            lambda w: time.time() - w[W_TIME_LEVEL_ENTERED] > settings.S.gerty_level_screen_wait,
        ],
        [
            (m.Say, 'I received another communication from Tess earlier today, Sam.<br>'
                    'I\'ll let you read it after the next test.'),
        ]
    ),
    (
        'Lost Tess', True,
        [
            lambda w: 3 in w[W_LEVELS_SOLVED],
            lambda w: time.time() - w[W_TIME_LEVEL_ENTERED] > settings.S.gerty_level_screen_wait,
        ],
        [
            (m.ChangeState, m.S_SAD),
            (m.Say, 'I\'m sorry Sam. But the file with the communication from Tess was<br>'
                    ' corrupted. I don\'t seem to be able to read it any more.'),
            (m.Set, W_TOLD_OF_CORRUPTION, True),
        ]
    ),
    (
        'Try to reconnect Tess', True,
        [
            lambda w: 4 in w[W_LEVELS_SOLVED],
            lambda w: time.time() - w[W_TIME_LEVEL_ENTERED] > settings.S.gerty_level_screen_wait,
        ],
        [
            (m.ChangeState, m.S_CONCERNED),
            (m.Say, 'I hope you are not mad at me Sam, for losing the communication<br>'
                    ' from. Tess. I know that you miss Tess and Eve very much. I will<br>'
                    ' try to initiate a connection from our side after the next test.'),
            (m.Set, W_TOLD_OF_CORRUPTION, True),
        ]
    ),
    (
        'Tess failure', True,
        [
            lambda w: 5 in w[W_LEVELS_SOLVED],
            lambda w: time.time() - w[W_TIME_LEVEL_ENTERED] > settings.S.gerty_level_screen_wait,
        ],
        [
            (m.ChangeState, m.S_WORRIED),
            (m.Say, 'I wasn\'t able to connect back to earth, Sam. The long range<br>'
                    ' transmission system doesn\'t seem to be functioning. I will<br>'
                    ' send out a drone to fix it.'),
            (m.Set, W_TOLD_OF_CORRUPTION, True),
        ]
    ),
    (
        'Tess hope', True,
        [
            lambda w: 6 in w[W_LEVELS_SOLVED],
            lambda w: time.time() - w[W_TIME_LEVEL_ENTERED] > settings.S.gerty_level_screen_wait,
        ],
        [
            (m.ChangeState, m.S_HAPPY),
            (m.Say, 'Good news, Sam. The file that I thought was corrupted was just<br>'
                    ' incomplete I should be able to play you the start of the file<br>'
                    ' after the next test.'),
            (m.Set, W_TOLD_OF_CORRUPTION, True),
        ]
    ),
    (
        'Hide spoken text', False,
        [
            lambda w: w[m.W_GERTY].showing == True,
            lambda w: (time.time() - w[m.W_LAST_SPOKE] > settings.S.gerty_short_short_text),
        ],
        [
            (m.ChangeState, m.S_HAPPY),
            (m.Hide, ),
        ]
    ),
]

