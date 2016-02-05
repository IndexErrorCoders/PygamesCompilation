"""The first level"""

import time
import pyglet
import pymunk

from .. import mainscreen
from .. import engine
from .. import common
from .. import settings
from aranara.items import collector, attractor, emitter, block, harvester


class Level(mainscreen.MainScreen):

    name = 'Opposites Attract'
    icon = 'aranara6.png'
    background_tween = [(255, 255, 255), (200, 200, 255)]

    def initLevel(self):
        """Level specific logic"""
        super(Level, self).initLevel()
        #
        # Set physics
        self.space.gravity = (0, -300.0)
        #
        # Create actors
        fore = engine.SpriteActor('foreground', 'moon-surface-2.png', 1024 / 2, -100, batch=self.main_batch, group=self.game_main)
        fore.addPhysics(settings.S.main_ground_physics)
        self.addActor(fore)
        #
        self.score = 0
        self.score_text = engine.TextActor('score', pyglet.text.decode_attributed(
            '{color (255,255,255,255)}{font_size 32}Score 0'), batch=self.main_batch, group=self.game_main)
        self.score_text.x = 50
        self.score_text.y = 720
        self.addActor(self.score_text)
        #
        def getRock1(world):
            """Return a rock"""
            a = engine.SpriteActor(engine.getUID('rock-%s'), 'helium.png', batch=self.main_batch, group=self.game_main)
            a.rotation = float(engine.RandomGenerator(0, 360))
            a.tag = 'helium'
            a.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
            return a
        #
        # The main emitter
        e1 = emitter.Emitter(
            'emitter1',
            'emitter.png',
            getRock1,
            engine.RandomGenerator(0.1, 0.5),
            offset=(0, -40),
            velocity=settings.S.Level1.emitter_velocity,
            angular_spread=settings.S.Level1.emitter_angular_spread,
            x=750,
            y=700,
            batch=self.main_batch, group=self.game_main
        )
        e1.tag = 'helium'
        e1.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(e1)
        #
        def getRock2(world):
            """Return a rock"""
            a = engine.SpriteActor(engine.getUID('rock-%s'), 'helium2.png', batch=self.main_batch, group=self.game_main)
            a.rotation = float(engine.RandomGenerator(0, 360))
            a.tag = 'helium2'
            a.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
            return a
        #
        # The main emitter
        e2 = emitter.Emitter(
            'emitter2',
            'emitter.png',
            getRock2,
            engine.RandomGenerator(0.1, 0.5),
            offset=(0, -40),
            velocity=settings.S.Level1.emitter_velocity,
            angular_spread=settings.S.Level1.emitter_angular_spread,
            x=350,
            y=700,
            batch=self.main_batch, group=self.game_main
        )
        e2.tag = 'helium'
        e2.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(e2)
        #
        #
        # Add harvester
        col1 = harvester.SmallHarvester(
            'harvester1',
            {'helium': 1, 'helium2': -3}, settings.S.normal_harvester_capacity,
            x=200, y=100, batch=self.main_batch, group=self.game_main)
        col1.color = (255, 255, 210)
        self.addActor(col1)
        #
        # Get collisions
        col1.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)
        self.harvesters.append(col1)
        #
        #
        # Add harvester
        col2 = harvester.SmallRightHarvester(
            'harvester2',
            {'helium': -3, 'helium2': 1}, settings.S.normal_harvester_capacity,
            x=900, y=100, batch=self.main_batch, group=self.game_main)
        col2.color = (255, 210, 255)
        self.addActor(col2)
        #
        # Get collisions
        col2.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)
        self.harvesters.append(col2)
        #
        return [
            ('attractor-btn.png', common.heliumAttractor, 1),
            ('repeller-btn.png', common.helium2Repeller, 1),
            ('red-block-btn.png', common.defaultBlock, 2),
        ]

m = mainscreen

Level.conversation_logic = [
    (
        'Initial greeting', True,
        [
            lambda w: w[m.W_INITIAL],
        ],
        [
            (m.Say, 'Here are the new harvesters, Sam. Each one can process either Helium-3<br>'
                    ' or Helium-4. Unfortunately they cannot process both.'),
            (m.Set, m.W_INITIAL, False),
        ]
    ),
    (
        'Bad score', True,
        [
            lambda w: w[m.W_SCORED_NEGATIVE] < -150,
        ],
        [
            (m.ChangeState, m.S_CONCERNED),
            (m.Say, 'Each harvester can only process its own kind of Helium. Try to keep<br>'
                    ' the two streams of Helium separated Sam.'),
        ]
    ),
    (
        'Really bad score', True,
        [
            lambda w: w[m.W_SCORED_NEGATIVE] < -300,
        ],
        [
            (m.ChangeState, m.S_WORRIED),
            (m.Say, 'A lot of Helium is going to the wrong harvester Sam! Try to create two<br>'
                    ' streams that cross over by using the repulsion units.'),
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
    (
        'Complete', True,
        [
            lambda w: w[m.W_LEVEL_COMPLETE],
            lambda w: (time.time() - w[m.W_LAST_SPOKE] > 2 * settings.S.gerty_short_short_text),
        ],
        [
            (m.Say, 'Great. That was a tricky one, Sam. I think you are back to at least<br>'
                    ' 90% mental functioning. I can barely see the impact of the accident at<br>'
                    ' all.'),
        ]
    ),
    (
        'Complete prod again', True,
        [
            lambda w: w[m.W_LEVEL_COMPLETE],
            lambda w: (w[m.W_TIME_SINCE_COMPLETE] > 4 * settings.S.gerty_impairment_time),
        ],
        [
            (m.ChangeState, m.S_CONCERNED),
            (m.Say, 'Sam, are you still there. Click on the "Level Complete" whenever<br>'
                    ' you are ready.'),
        ]
    ),
]

