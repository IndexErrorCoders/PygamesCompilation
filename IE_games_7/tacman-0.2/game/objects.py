"""Objects that can be on the game board"""

import networkx

import serge.actor

from theme import G, theme
import player

class BoardItem(player.MobileActor):
    """Represents an item on the board"""
    
    ai_controlled = True
    
    def playerVisited(self, grid, game, player):
        """The player landed on the item"""
        pass
    
    
class StaticItem(BoardItem):
    """A static item on the board"""

    sprite_name = None
    mobile = False
    player_rank_target = 0
    
    def __init__(self):
        """Initialise the pill"""
        super(BoardItem, self).__init__(self.type_name, self.sprite_name, 50)
        if self.sprite_name:
            self.setSpriteName(self.sprite_name)


    
class RedPill(StaticItem):
    type_name = 'pill'
    sprite_name = 'red-pill'
    score = 1
    player_rank_target = -1

    def playerVisited(self, grid, game, player):
        """The player landed on a pill"""
        if not player.ai_controlled:
            game._score.value += self.score
            grid.removeActor(grid.findActorLocation(self), self)
        
        
class YellowPill(StaticItem):
    type_name = 'pill'
    sprite_name = 'yellow-pill'
    score = 5
    player_rank_target = -5

    def playerVisited(self, grid, game, player):
        """The player landed on a pill"""
        if not player.ai_controlled:
            game._score.value += self.score
            grid.removeActor(grid.findActorLocation(self), self)
            game._mode_toggle.gotoMode('fright')
            game.switchToMode('fright')
            game.processEvent(('eat-yellow-pill', None))
            serge.sound.Sounds.getItem('yellow').play()
    
class Wall(StaticItem):
    type_name = 'wall'
    
    
class Teleport(StaticItem):
    type_name = 'teleport'

    def playerVisited(self, grid, game, player):
        """The player landed on a teleport"""
        teleports = grid.getChildrenWithTag('teleport')
        if teleports[0] != self:
            nx, ny = grid.findActorLocation(teleports[0])
        else:
            nx, ny = grid.findActorLocation(teleports[1])        
        grid.moveActor((nx, ny), player)
    
class Pacman(BoardItem):
    """The pacman"""
    
    ai_controlled = False

    def playerVisited(self, grid, game, player):
        """Somebody landed on the player"""
        if player is self:
            return
        if player.mode == 'fright':
            game._score.value += G('ghost-score')
            player.setReturning()
            cx, cy = grid.findActorLocation(player)
            nx, ny = player.getHome()
            player.setTargetList(networkx.shortest_path(game.graph, (cx, cy), (nx, ny))[1:])
        elif player.mode != 'return':
            game.playerDeath()
            player.clearTargets()
    
BoardItems = {
    0: None,
    1: RedPill,
    2: YellowPill,
    'wall': Wall,
    'teleport': Teleport,
}

