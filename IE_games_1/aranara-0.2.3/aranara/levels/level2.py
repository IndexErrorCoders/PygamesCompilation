"""The second level"""

import random
import pyglet

from .. import mainscreen
from .. import engine
from .. import common
from aranara.items import collector, attractor, emitter


class Level(mainscreen.MainScreen):
    """The first level"""

    name = 'Level 2'

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
        # a1 = engine.SpriteActor('R1', 'rock-1.png', 400, 450, batch=rocks)
        # a1.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
        # a1.body.velocity = (100, 0)
        # a2 = engine.SpriteActor('R2', 'rock-2.png', 500, 410, batch=rocks)
        # a2.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
        # a3 = engine.SpriteActor('R3', 'rock-3.png', 740, 410, batch=rocks)
        # a3.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
        # self.addActor(a1)
        # self.addActor(a2)
        # self.addActor(a3)
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
                '<font size="7" color="red">This is level 2</font>'),
            width=500,
            multiline=True,
            batch=self.level_batch
        )
        greeting.x, greeting.y = 500, 500
        self.addActor(greeting)
        #
        for i in range(5):
            block = engine.SpriteActor('block-%d' % i, 'red-block.png', x=100 + 150 * i, y=400, batch=self.level_batch)
            block.addPhysics(engine.RectangleSpritePhysics())
            self.addActor(block)
            #
            self.tweens.append(engine.Tween(block, 'rotation', -30, 30, random.uniform(3,6),
                                            engine.Tween.sinInOut, delay=random.uniform(0, 1), repeat=True))
        #
        # Add collector
        col1 = collector.Collector('col-1', 'collector.png', {'helium': 1}, x=200, y=200, batch=self.level_batch)
        col1.tag = 'collider'
        col1.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(col1)
        #
        col2 = collector.Collector('col-2', 'collector.png', {'helium': 1}, x=800, y=200, batch=self.level_batch)
        col2.tag = 'collider'
        col2.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(col2)
        col2.draggable = True
        #
        # Get collisions
        col1.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)
        col2.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)
        #
        att = attractor.Attractor(
            'att', 'attractor.png', ['helium'],
            attractor.Attractor.getPowerLawAttractor(1000, -2),
            x=500, y=300, batch=self.level_batch
        )
        att.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(att)
        att.draggable = True