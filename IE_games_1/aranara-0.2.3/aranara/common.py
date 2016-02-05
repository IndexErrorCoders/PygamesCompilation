"""Common parts of the game"""

version = '0.2.3'

import pyglet
import pymunk

from items import attractor, block, gun
import engine
import settings

# Events
E_ITEM_COLLECTED = 'item-collected'


total_time = 0


def defaultAttractor(batch):
    """Return the default attractor"""
    att = attractor.Attractor(
        engine.getUID('rep-%s'), 'attractor.png', ['helium'],
        [
            (attractor.Attractor.getPowerLawAttractor(*settings.S.standard_attractor_1), 20),
            (attractor.Attractor.getPowerLawAttractor(*settings.S.standard_attractor_2), 50),
            (attractor.Attractor.getPowerLawAttractor(*settings.S.standard_attractor_3), 80),
        ],
        x=500, y=300, batch=batch
    )
    att.draggable = True
    att.rotatable = True
    att.addPhysics(engine.RectangleSpritePhysics())
    return att


def heliumAttractor(batch):
    """Return a yellow attractor"""
    obj = defaultAttractor(batch)
    obj.particle_tint = (255, 255, 0)
    obj.attract_tags = ['helium']
    return obj


def helium2Attractor(batch):
    """Return a purple attractor"""
    obj = defaultAttractor(batch)
    obj.particle_tint = (255, 0, 255)
    obj.attract_tags = ['helium2']
    return obj


def defaultRepeller(batch):
    """Return the default repeller"""
    att = attractor.Repeller(
        engine.getUID('rep-%s'), 'repeller.png', ['helium'],
        [
            (attractor.Attractor.getPowerLawAttractor(*settings.S.standard_repeller_1), 20),
            (attractor.Attractor.getPowerLawAttractor(*settings.S.standard_repeller_2), 50),
            (attractor.Attractor.getPowerLawAttractor(*settings.S.standard_repeller_3), 80),
        ],
        x=500, y=300, batch=batch
    )
    att.draggable = True
    att.rotatable = True
    att.addPhysics(engine.RectangleSpritePhysics())
    return att


def heliumRepeller(batch):
    """Return a yellow repeller"""
    obj = defaultRepeller(batch)
    obj.particle_tint = (255, 255, 0)
    obj.attract_tags = ['helium']
    return obj


def helium2Repeller(batch):
    """Return a purple repeller"""
    obj = defaultRepeller(batch)
    obj.particle_tint = (255, 0, 255)
    obj.attract_tags = ['helium2']
    return obj


def defaultBlock(batch):
    """Return the default block"""
    b = block.Block(
        engine.getUID('b-%s'), 'red-block.png',
        batch=batch
    )
    b.draggable = b.rotatable = True
    b.addPhysics(engine.RectangleSpritePhysics())
    return b


def defaultGun(batch):
    """Return the default gun"""
    g = gun.Gun(engine.getUID('gun-%s'),
            gun.Rocket.getRocketGenerator(
                'rocket.png', 100000, 200, 100,
                ['rock', 'decoration'], 0, 0.2, batch
            ),
            pyglet.window.key.ENTER,
            pymunk.Vec2d(50, 00),
            x=900, y=300, batch=batch
    )
    g.rotation = 0
    g.addPhysics(engine.RectangleSpritePhysics())
    g.draggable = True
    return g