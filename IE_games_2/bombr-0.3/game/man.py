"""A man that moves around"""

import random

import serge.actor
import serge.sound
from serge.simplevecs import Vec2d
import serge.blocks.animations
import serge.blocks.actors

import common
import boardobject
from theme import G


class Man(boardobject.BoardObject):
    """A man who moves around on the screen"""

    is_explosion_barrier = False
    is_fragile = True
    is_dead = False
    is_player = True

    def __init__(self, tag, name, sprite_name, board, controller):
        """Initialise the man"""
        super(Man, self).__init__(tag, name)
        #
        self.board = board
        self.controller = controller
        self.setSpriteName(sprite_name)
        self.moving = True

    def spawnMan(self):
        """Spawn the man at a relevant location"""
        position = self.board.getSpawnPoint(self.getSpriteName())
        self.board.addManAt(self, position)

    def updateActor(self, interval, world):
        """Update the man"""
        super(Man, self).updateActor(interval, world)
        #
        # Move man
        if self.moving:
            self.controller.updateController(interval, self, self.board)

    def canDropBomb(self):
        """Return true if the man can drop a bomb"""
        return True

    def isMoveBlockedBy(self, other):
        """Return True if we are blocked by another"""
        return other.is_blockage

    def manMovesOnto(self, other):
        """A man moved onto our square"""
        if other.is_deadly:
            self.processEvent((common.E_MAN_DIED, 'blew-up'))

    def deathAnimation(self):
        """Initialise the death animation"""
        self.addAnimation(
            serge.blocks.animations.TweenAnimation(
                self, 'setAngle', 0, 180.0, 200.0, is_method=True
            ),
            'death-animation-angle',
        )
        self.addAnimation(
            serge.blocks.animations.TweenAnimation(
                self, 'setZoom', 1.0, 0.1, 500.0, is_method=True,
                after=self.afterDeath
            ),
            'death-animation-size',
        )

    def afterDeath(self):
        """Called when the death animation is complete"""
        serge.sound.Sounds.play('chunk-explode')
        #
        self.visible = False
        for i in range(G('chunk-number')):
            #
            # Create a chunk of body to go flying off
            chunk = serge.blocks.actors.SimplePhysicsActor(
                'chunk', 'chunnk',
                Vec2d(random.randrange(*G('chunk-velocity')), 0).rotated_degrees(random.randrange(0, 360)),
                random.randrange(*G('chunk-angular-velocity')),
                bounds=((0, G('screen-width')), (0, G('screen-height'))),
                gravity=Vec2d(*G('chunk-gravity'))
            )
            chunk.moveTo(self.x, self.y)
            chunk.setSpriteName(random.choice(G('chunk-sprites')))
            chunk.setLayerName('main')
            self.world.addActor(chunk)