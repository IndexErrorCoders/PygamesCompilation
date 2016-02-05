
import time
import random
import pyglet

from .. import mainscreen
from .. import engine
from .. import common
from .. import settings
from .. import ui
from aranara.items import collector, attractor, emitter


class Level(mainscreen.MainScreen):
    """The first level"""

    name = 'Level 5'

    def initLevel(self):
        """Level specific logic"""
        #
        # Set the current world
        background = self.addBatch('background')
        foreground = self.addBatch('foreground')
        rocks = self.addBatch('rocks')
        ui = self.addBatch('ui')
        #
        # Set physics
        self.space.gravity = (0, -30.0)
        #
        # Create actors
        back = self.addActor(
            engine.SpriteActor('background', 'starfield-small.jpg', 1024 / 2, 640 / 2 + 100, batch=background))
        fore = engine.SpriteActor('foreground', 'moon-surface-2.png', 1024 / 2, 0, batch=foreground)
        fore.addPhysics(engine.PolygonSpritePhysics(
            0, 0.5, 0.5,
            [
                (0.00, 0.00),
                (1.00, 0.00),
                (1.00, 0.61),
                (0.65, 0.89),
                (0.00, 0.75),
            ]
        ))
        self.addActor(fore)
        #
        self.score = 0
        self.score_text = engine.TextActor('score', pyglet.text.decode_attributed(
            '{color (255,255,255,255)}{font_size 32}Score 0'), batch=ui)
        self.score_text.x = 50
        self.score_text.y = 720
        self.addActor(self.score_text)

        def getRock(world):
            """Return a rock"""
            typ = random.randint(0, 1)
            a = engine.SpriteActor(
                engine.getUID('rock-%s'),
                'helium.png' if typ == 0 else 'helium2.png',
                batch=rocks)
            a.rotation = float(engine.RandomGenerator(0, 360))
            a.tag = 'helium' if typ == 0 else 'helium2'
            a.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
            return a

        e1 = emitter.Emitter(
            'emitter1',
            'emitter.png',
            getRock,
            0.3,
            offset=(0, -40),
            velocity=engine.RandomGenerator(50, 500),
            x=400,
            y=700,
            batch=rocks
        )
        e1.tag = 'helium'
        e1.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(e1)
        #
        self.level_batch = self.addBatch('level-batch')
        #
        greeting = engine.TextActor(
            'greeting',
            pyglet.text.decode_html(
                '<font color="white" size="7">Aranara<br></font>'
                '<font size="3" color="red">This is level 3</font>'),
            width=500,
            multiline=True,
            batch=self.level_batch
        )
        greeting.x, greeting.y = 500, 500
        self.addActor(greeting)
        #
        #
        # Add collector
        col1 = collector.Collector('col-1', 'collector.png',
                                   {'helium': 1, 'helium2': -5},
                                   x=200, y=200, batch=self.level_batch)
        col1.tag = 'collider'
        col1.addPhysics(engine.RectangleSpritePhysics())
        col1.draggable = True
        self.addActor(col1)
        #
        # Get collisions
        col1.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)
        #
        att = attractor.Attractor(
            'att', 'attractor.png', ['helium'],
            attractor.Attractor.getPowerLawAttractor(5000, -2),
            x=500, y=300, batch=self.level_batch
        )
        att.addPhysics(engine.CircleSpritePhysics())
        self.addActor(att)
        att.draggable = True

m = mainscreen

Level.conversation_logic = [
    (
        'Initial greeting', True,
        [
            lambda w: w[m.W_INITIAL],
        ],
        [
            (m.Say, 'This is an easy level, Sam'),
            (m.Set, m.W_INITIAL, False),
        ]
    ),
    (
        'Hide greeted', False,
        [
            lambda w: w[m.W_GERTY].showing == True,
            lambda w: (time.time() - w[m.W_LAST_SPOKE] > settings.S.gerty_short_short_text),
        ],
        [
            (m.Hide, ),
        ]
    ),
    (
        'Small score', True,
        [
            lambda w: w[m.W_TOTAL_SCORE] >= 5,
        ],
        [
            (m.Say, 'You seem to be getting the hang of it Sam. Keep going.'),
        ]
    ),
    (
        'Medium score', True,
        [
            lambda w: w[m.W_TOTAL_SCORE] >= 30,
        ],
        [
            (m.Say, 'This is really quite impressive Sam. Keep it up.'),
        ]
    ),
    (
        'Bad score', True,
        [
            lambda w: w[m.W_TOTAL_SCORE] <= -10,
        ],
        [
            (m.ChangeState, ui.gerty.S_CONCERNED),
            (m.Say, 'Ouch Sam. You are losing like crazy'),
        ]
    ),
    (
        'Terrible score', True,
        [
            lambda w: w[m.W_TOTAL_SCORE] <= -30,
        ],
        [
            (m.ChangeState, ui.gerty.S_WORRIED),
            (m.Say, 'Sam? Are you feeling OK? I think I need to call for help.'),
            (m.Set, m.W_HAD_BAD_SCORE, True),
        ]
    ),
    (
        'Recovering score', True,
        [
            lambda w: w[m.W_HAD_BAD_SCORE],
            lambda w: w[m.W_TOTAL_SCORE] >= 0,
        ],
        [
            (m.ChangeState, ui.gerty.S_HAPPY),
            (m.Say, 'Thank goodness that you recovered from that bad spell, Sam.'),
        ]
    ),
]