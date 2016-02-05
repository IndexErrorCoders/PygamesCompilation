"""Power ups to add to the game"""

import boardobject
import bomb
import common
from theme import G


class PowerUp(boardobject.BoardObject):
    """Base class for power up"""

    name_of_sprite = 'unknown'
    is_blockage = False
    can_be_taken = True

    def __init__(self, board):
        """Initialise the power up"""
        super(PowerUp, self).__init__('board-item', 'item')
        #
        self.board = board
        self.setSpriteName(self.name_of_sprite)
        self.setLayerName('bombs')

    def isMoveBlockedBy(self, other):
        """Return True if our move is blocked by another"""
        return True

    def manMovesOnto(self, other):
        """A man moved onto us"""
        if self.can_be_taken:
            self.log.info('Power up %s taken by %s' % (self.getNiceName(), other.getNiceName()))
            self.board.removeMan(self)
            self.world.scheduleActorRemoval(self)


class Bomb(PowerUp):
    """A bomb power-up"""

    name_of_sprite = 'tiles-11'
    can_be_taken = False
    is_fragile = True
    is_explosion_barrier = False

    def isDestroyedBy(self, other):
        """We are destroyed"""
        self.log.info('Bomb destroyed by another')


class MultiBomb(Bomb):
    """A multiple bomb power-up"""

    name_of_sprite = 'tiles-35'
    number_to_create = 3


class Speed(PowerUp):
    """A speed up power-up"""

    name_of_sprite = 'tiles-13'
    is_fragile = True
    is_explosion_barrier = False


class Heart(PowerUp):
    """A heart power up"""

    name_of_sprite = 'tiles-31'
    is_fragile = True
    is_explosion_barrier = False
    can_be_taken = True
    movement_weight = G('heart-movement-weight')
    heart_increment = 1
    heart_taker = True

    def manMovesOnto(self, other):
        """A man moves onto us"""
        super(Heart, self).manMovesOnto(other)
        if other.is_player:
            self.mainscreen.heartIncrement(other, self.heart_increment, self.heart_taker)


class RedHeart(Heart):
    """A heart"""

    name_of_sprite = 'tiles-33'
    heart_increment = -1
    heart_taker = False


class Flag(PowerUp):
    """A flag to be captured"""

    name_of_sprite = 'tiles-34'
    is_fragile = True
    is_explosion_barrier = False
    can_be_taken = True
    movement_weight = G('flag-movement-weight')

    def manMovesOnto(self, other):
        """A man moves onto us"""
        super(Flag, self).manMovesOnto(other)
        #
        if other.is_player:
            self.broadcaster.processEvent((common.E_FLAG_CAPTURED, other))


def getItem(name):
    return {
        Bomb.name_of_sprite: bomb.Bomb,
        MultiBomb.name_of_sprite: MultiBomb,
        Speed.name_of_sprite: Speed,
        Heart.name_of_sprite: Heart,
        RedHeart.name_of_sprite: RedHeart,
        Flag.name_of_sprite: Flag,
    }[name]
