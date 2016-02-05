"""A controller for the player's man"""

import pygame
import time

import serge.engine
import serge.sound

from theme import G


class Player(object):
    """Represents the player's control of the actor"""

    def __init__(self):
        """Initialise the controller"""
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        self._last_move = time.time()
        self._move_interval = G('player-move-interval')
        self.walk = serge.sound.Sounds.getItem('walk')

    def updateController(self, interval, man, board):
        """Update the control of the actor"""
        #
        # Find out the way the player wants to go
        direction = None
        if self.keyboard.isDown(pygame.K_LEFT):
            direction = (-1, 0)
        if self.keyboard.isDown(pygame.K_RIGHT):
            direction = (+1, 0)
        if self.keyboard.isDown(pygame.K_UP):
            direction = (0, -1)
        if self.keyboard.isDown(pygame.K_DOWN):
            direction = (0, +1)
        #
        # Check that we can go there
        if direction and board.canMove(man, direction) and time.time() - self._last_move > self._move_interval:
            man.log.debug('Moving player by %s, %s' % direction)
            board.moveMan(man, direction)
            self.walk.play()
            self._last_move = time.time()
        #
        # See if any bombs should be dropped
        if self.keyboard.isClicked(pygame.K_SPACE):
            if man.canDropBomb():
                board.dropBomb(man)
                serge.sound.Sounds.play('drop')
