
import pyglet

from .. import mainscreen
from .. import engine
from .. import common
from aranara.items import collector, attractor, emitter


class Level(mainscreen.MainScreen):
    """The first level"""

    name = 'Level 3'

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
            a = engine.SpriteActor(engine.getUID('rock-%s'), 'helium.png', batch=rocks)
            a.rotation = float(engine.RandomGenerator(0, 360))
            a.tag = 'helium'
            a.addPhysics(engine.CircleSpritePhysics(10, .5, .1))
            return a

        e1 = emitter.Emitter(
            'emitter1',
            'emitter.png',
            getRock,
            2,
            offset=(0, -40),
            velocity=engine.RandomGenerator(50, 50),
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
        att = attractor.Attractor(
            'att', 'attractor.png', ['helium'],
            attractor.Attractor.getPowerLawAttractor(5000, -2),
            x=500, y=300, batch=self.level_batch
        )
        att.addPhysics(engine.CircleSpritePhysics())
        self.addActor(att)
        att.draggable = True
        #
        rep = attractor.Attractor(
            'rep', 'repeller.png', ['helium'],
            attractor.Attractor.getPowerLawAttractor(-2000, -2),
            x=500, y=450, batch=self.level_batch
        )
        rep.addPhysics(engine.CircleSpritePhysics())
        self.addActor(rep)
        rep.draggable = True
        #
        rep2 = attractor.Attractor(
            'rep2', 'repeller.png', ['helium'],
            attractor.Attractor.getPowerLawAttractor(-1000, -2),
            x=200, y=200, batch=self.level_batch
        )
        rep2.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(rep2)
        rep2.draggable = True