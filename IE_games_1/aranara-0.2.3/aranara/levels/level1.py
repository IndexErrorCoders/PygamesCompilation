"""The first level"""

import time
import pyglet
import pymunk

from .. import mainscreen
from .. import engine
from .. import common
from .. import settings
from aranara.items import collector, attractor, emitter, block


class Level(mainscreen.MainScreen):
    """The first level"""

    name = 'Level 1'

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
        self.space.gravity = (0, -300.0)
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
            a = engine.SpriteActor(engine.getUID('rock-%s'), 'helium.png', batch=rocks)
            a.rotation = float(engine.RandomGenerator(0, 360))
            a.tag = 'helium'
            a.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
            return a

        e1 = emitter.Emitter(
            'emitter1',
            'emitter.png',
            getRock,
            engine.RandomGenerator(0.1, 0.5),
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
        e2 = emitter.Emitter(
            'emitter2',
            'emitter.png',
            getRock,
            engine.RandomGenerator(0.1, 0.2),
            offset=(0, -40),
            velocity=engine.RandomGenerator(500, 800),
            x=800,
            y=700,
            batch=rocks
        )
        e2.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(e2)
        #
        # Add tween to rotate the source
        self.tweens.append(engine.Tween(e1, 'rotation', -90, +90, 5, engine.Tween.linearTween, repeat=True))
        self.tweens.append(engine.Tween(e2, 'rotation', 45, -45, 1, engine.Tween.linearTween, repeat=True))
        #
        self.level_batch = self.addBatch('level-batch')
        #
        greeting = engine.TextActor(
            'greeting',
            pyglet.text.decode_html(
                '<font color="white" size="7">Aranara<br></font>'
                '<font size="3" color="red">This is level 1</font>'),
            width=500,
            multiline=True,
            batch=self.level_batch
        )
        greeting.x, greeting.y = 500, 500
        self.addActor(greeting)
        #
        for i in range(5):
            b = block.Block('block-%d' % i, 'red-block.png', x=100 + 150 * i, y=400, batch=self.level_batch)
            b.addPhysics(engine.RectangleSpritePhysics())
            self.addActor(b)
        #
        # Moving block
        mblock = block.MovingBlock(
            'mblock', 'red-block.png', pymunk.Vec2d(200, 600), pymunk.Vec2d(400, 500),
            5, batch=self.level_batch,
        )
        mblock.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(mblock)
        #
        # Rotating block
        rblock = block.RotatingBlock(
            'rblock', 'red-block.png', 0, 90,
            3, x=500, y=500, batch=self.level_batch,
        )
        rblock.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(rblock)
        #
        # Moving rotating block
        mrblock = block.MovingRotatingBlock(
            'mrblock', 'red-block.png',
            pymunk.Vec2d(900, 600), pymunk.Vec2d(900, 300), 4,
            0, 90, 3,
            x=500, y=500, batch=self.level_batch,
        )
        mrblock.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(mrblock)
        #
        # Add collector
        col = collector.Collector('col-1', 'collector.png', {'helium': 1}, x=200, y=200, batch=self.level_batch)
        col.tag = 'collider'
        col.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(col)
        #
        # Get collisions
        col.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)


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
    )
]