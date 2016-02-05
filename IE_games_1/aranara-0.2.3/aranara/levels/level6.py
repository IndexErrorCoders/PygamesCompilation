
import random
import pyglet
import pymunk

from .. import mainscreen
from .. import engine
from .. import common
from .. import settings
from aranara.items import collector, attractor, emitter, rock, gun, harvester


class Level(mainscreen.MainScreen):
    """The first level"""

    name = 'Level 6'

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
        e1.tag = 'decoration'
        e1.addPhysics(engine.RectangleSpritePhysics())
        e1.draggable = e1.rotatable = True
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
        col1 = harvester.LargeHarvester(
            'col-1',
            {'helium': 1, 'helium2': -5},
            x=200, y=200, batch=self.level_batch)
        self.addActor(col1)
        #
        # Get collisions
        col1.linkEvent(common.E_ITEM_COLLECTED, self.gotHelium)
        #
        att = attractor.Attractor(
            'att', 'attractor.png', ['xrock', 'xhelium'],
            attractor.Attractor.getPowerLawAttractor(2000, -2),
            x=500, y=400, batch=self.level_batch
        )
        att.tag = 'decoration'
        att.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(att)
        #
        # Rocks
        r1 = rock.Rock('r1', 'rock-1.png', x=500, y=350, batch=self.level_batch)
        r1.addPhysics(engine.CircleSpritePhysics(100))
        r1.tag = 'rock'
        self.addActor(r1)
        r1.draggable = True
        r2 = rock.Rock('r2', 'rock-2.png', x=530, y=350, batch=self.level_batch)
        r2.addPhysics(engine.CircleSpritePhysics(100))
        r2.tag = 'rock'
        self.addActor(r2)
        r2.draggable = True
        #
        g = gun.Gun('gun',
                    gun.Rocket.getRocketGenerator(
                        'rocket.png', 50000, 100, 100,
                        ['rock', 'helium', 'decoration'], 10000, 1, self.level_batch
                    ),
                    pyglet.window.key.F,
                    pymunk.Vec2d(50, 20),
                    x=900, y=300, batch=self.level_batch)
        g.rotation = 0
        g.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(g)
        g.flipHorizontal()
        g.draggable = True
        #
        # self.tweens.append(engine.Tween(
        #     g, 'aiming_rotation', 0, 45, 4, engine.Tween.sinInOut, repeat=True,
        # ))
        g2 = gun.Gun('gun2',
                    gun.Rocket.getRocketGenerator(
                        'rocket.png', 50000, 100, 100,
                        ['rock', 'helium', 'decoration'], 10000, 1, self.level_batch
                    ),
                    pyglet.window.key.D,
                    settings.S.gun_rocket_offset,
                    x=100, y=300, batch=self.level_batch)
        g2.rotation = 0
        g2.addPhysics(engine.RectangleSpritePhysics())
        self.addActor(g2)
        g2.draggable = True
        #
        self.tweens.append(engine.Tween(
            g2, 'aiming_rotation', 0, -45, 4, engine.Tween.sinInOut, repeat=True,
        ))
