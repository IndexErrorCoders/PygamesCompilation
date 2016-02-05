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

    name = 'A simple drop'
    music = 'crystal'
    icon = 'aranara1.png'
    background_tween = [(255, 255, 255), (255, 100, 100)]

    def initLevel(self):
        """Level specific logic"""
        super(Level, self).initLevel()
        #
        # Set the current world
        #
        # Set physics
        self.space.gravity = (0, -300.0)
        #
        # Create actors
        #
        fore = engine.SpriteActor('self.main_batch', 'moon-surface-2.png', 1024 / 2, -100, batch=self.main_batch, group=self.game_main)
        fore.addPhysics(settings.S.main_ground_physics)
        self.addActor(fore)
        #
        def getRock(world):
            """Return a rock"""
            a = engine.SpriteActor(engine.getUID('rock-%s'), 'helium.png', batch=self.main_batch, group=self.game_fore)
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
            batch=self.main_batch,
            group=self.game_fore
        )
        e1.tag = 'helium'
        e1.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(e1)
        #
        #
        # Add harvester
        col1 = harvester.SmallHarvester(
            'harvester',
            {'helium': 1}, settings.S.normal_harvester_capacity,
            x=200, y=100, batch=self.main_batch, group=self.game_fore)
        self.addActor(col1)
        #
        # Get collisions
        col1.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)
        self.harvesters.append(col1)
        #
        self.score = 0
        #
        return [
            ('attractor-btn.png', gamecommon.defaultAttractor, 1),
        ]


m = mainscreen

Level.conversation_logic = [
    (
        'Initial greeting', True,
        [
            lambda w: w[m.W_INITIAL],
        ],
        [
            (m.Say, 'You seem to be disoriented from your accident, Sam. Here is'
            ' a<br>simple test to check for mental impairment.'),
            (m.Set, m.W_INITIAL, False),
        ]
    ),
    (
        'Instruction', True,
        [
            lambda w: not w[m.W_INITIAL],
            lambda w: not w[m.W_GERTY].showing,
            lambda w: not w[m.W_CLICKED_PALETTE],
            lambda w: (time.time() - w[m.W_LAST_SPOKE] > 2 * settings.S.gerty_short_short_text),
        ],
        [
            (m.Say, 'Guide the Helium rich rocks into the harvester. There is an attraction<br>'
                    'unit on the left, Sam. Click on it and then drag it to the right location.'),
        ]
    ),
    (
        'Reinforce click', True,
        [
            lambda w: w[m.W_CLICKED_PALETTE],
            lambda w: (time.time() - w[m.W_LAST_SPOKE] > 2 * settings.S.gerty_short_short_text),
        ],
        [
            (m.Say, 'Good job Sam. Now drag the attraction unit to the right location.'),
        ]
    ),
    (
        'Are you ok', True,
        [
            lambda w: not w[m.W_CLICKED_PALETTE],
            lambda w: w[m.W_TOTAL_TIME] > settings.S.gerty_impairment_time,
        ],
        [
            (m.ChangeState, m.S_CONCERNED),
            (m.Say, 'Are you OK, Sam? Click on the attraction unit on the left.'),
        ]
    ),
    (
        'Are you really ok', True,
        [
            lambda w: not w[m.W_CLICKED_PALETTE],
            lambda w: w[m.W_TOTAL_TIME] > 2 * settings.S.gerty_impairment_time,
        ],
        [
            (m.ChangeState, m.S_WORRIED),
            (m.Say, 'I\'m worried about you, Sam? Are you suffering mental impairment?<br>'
                    'Click on the attraction unit on the left.'),
        ]
    ),
    (
        'Hide greeted', False,
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
        'Small score', True,
        [
            lambda w: 5 <= w[m.W_TOTAL_SCORE] <= 15,
        ],
        [
            (m.Say, 'You seem to be getting the hang of it Sam. Keep going.'),
        ]
    ),
    (
        'Medium score', True,
        [
            lambda w: w[m.W_TOTAL_SCORE] >= 20,
        ],
        [
            (m.Say, 'This is really quite impressive Sam. Keep it up.'),
        ]
    ),
    (
        'Complete', True,
        [
            lambda w: w[m.W_LEVEL_COMPLETE],
            lambda w: (time.time() - w[m.W_LAST_SPOKE] > 2 * settings.S.gerty_short_short_text),
        ],
        [
            (m.Say, 'Great job, Sam. I knew you could do it.'),
        ]
    ),
    (
        'Complete prod', True,
        [
            lambda w: w[m.W_LEVEL_COMPLETE],
            lambda w: (w[m.W_TIME_SINCE_COMPLETE] > settings.S.gerty_impairment_time),
        ],
        [
            (m.Say, 'OK, Sam. Click on the "Level Complete" whenever you are ready.'),
        ]
    ),
    (
        'Complete prod again', True,
        [
            lambda w: w[m.W_LEVEL_COMPLETE],
            lambda w: (w[m.W_TIME_SINCE_COMPLETE] > 2 * settings.S.gerty_impairment_time),
        ],
        [
            (m.ChangeState, m.S_CONCERNED),
            (m.Say, 'Sam, are you still there. Click on the "Level Complete" whenever<br>'
                    ' you are ready.'),
        ]
    ),
]