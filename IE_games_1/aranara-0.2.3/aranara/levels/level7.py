
import time
import random
import pyglet

from .. import mainscreen
from .. import engine
from .. import common
from .. import settings
from aranara.items import collector, attractor, emitter, block


class Level(mainscreen.MainScreen):
    """The first level"""

    name = 'Level 7'

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

        #
        self.level_batch = self.addBatch('level-batch')
        #
        greeting = engine.TextActor(
            'greeting',
            pyglet.text.decode_html(
                '<font color="white" size="7">Aranara<br></font>'
                '<font size="3" color="red">This is level 7</font>'),
            width=500,
            multiline=True,
            batch=self.level_batch
        )
        greeting.x, greeting.y = 500, 500
        self.addActor(greeting)
        #
        b1 = block.Block('b1', 'red-block.png', x=400, y=400, batch=self.level_batch)
        b1.addPhysics(engine.RectangleSpritePhysics())
        b1.draggable = True
        b1.rotatable = True
        self.addActor(b1)
        #
        b2 = block.RotatingBlock('b2', 'red-block.png',
                                 0, 180, 5,
                                 x=600, y=400, batch=self.level_batch)
        b2.addPhysics(engine.RectangleSpritePhysics())
        b2.draggable = True
        self.addActor(b2)

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
            angular_spread=10,
            x=400,
            y=700,
            batch=rocks
        )
        e1.tag = 'helium'
        e1.addPhysics(engine.RectangleSpritePhysics())
        e1.draggable = True
        self.addActor(e1)


m = mainscreen

Level.conversation_logic = [
    (
        'Initial greeting', True,
        [
            lambda w: w[m.W_INITIAL],
        ],
        [
            (m.Say, 'Hello there Sam. Good to see you again'),
            (m.Set, m.W_INITIAL, False),
        ]
    ),
    (
        'After greeted', True,
        [
            lambda w: (time.time() - w[m.W_LAST_SPOKE] > settings.S.gerty_short_short_text),
        ],
        [
            (m.Say, 'Well it has been a while since I saw you'),
        ]
    ),
    (
        'Hide greeted', True,
        [
            lambda w: (time.time() - w[m.W_LAST_SPOKE] > settings.S.gerty_short_short_text),
        ],
        [
            (m.Hide, ),
        ]
    )

]