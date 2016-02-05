"""The first level"""

import time
import pyglet
import pymunk

from .. import mainscreen
from .. import engine
from .. import common
from .. import settings
from .. import common as gamecommon
from aranara.items import collector, attractor, emitter, block, harvester


class Level(mainscreen.MainScreen):

    name = 'Push and Block'
    icon = 'aranara4.png'
    background_tween = [(255, 255, 255), (255, 200, 255)]

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
        def getRock(world):
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
            getRock,
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
        #
        # Add harvester
        col1 = harvester.SmallRightHarvester(
            'harvester',
            {'helium': 1}, settings.S.normal_harvester_capacity,
            x=500, y=120, batch=self.main_batch, group=self.game_main)
        self.addActor(col1)
        #
        # Get collisions
        col1.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)
        self.harvesters.append(col1)
        #
        return [
            ('repeller-btn.png', gamecommon.defaultRepeller, 1),
            ('red-block-btn.png', gamecommon.defaultBlock, 1)
        ]

m = mainscreen


Level.conversation_logic = [
    (
        'Initial greeting', True,
        [
            lambda w: w[m.W_INITIAL],
        ],
        [
            (m.Say, 'I\'ve been able to repair one unit Sam.<br>'
                    'See if you can use it along with this block.'),
            (m.Set, m.W_INITIAL, False),
        ]
    ),
    (
        'Didn\'t use them all', True,
        [
            lambda w: w[m.W_ITEMS_IN_PALETTE] > 0,
            lambda w: w[m.W_TOTAL_TIME] > 2 * settings.S.gerty_impairment_time,
        ],
        [
            (m.ChangeState, m.S_CONCERNED),
            (m.Say, 'You still have other items to use, Sam. See them on the<br>'
                    ' left there?'),
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
            (m.Say, 'Well done, Sam. I don\'t detect any mental impairment from the<br>'
                    ' accident. I think you are ready to take on more complex tests.'),
        ]
    ),
    (
        'Complete prod again', True,
        [
            lambda w: w[m.W_LEVEL_COMPLETE],
            lambda w: (w[m.W_TIME_SINCE_COMPLETE] > 3 * settings.S.gerty_impairment_time),
        ],
        [
            (m.ChangeState, m.S_CONCERNED),
            (m.Say, 'Sam, are you still there. Click on the "Level Complete" whenever<br>'
                    ' you are ready.'),
        ]
    ),
]

