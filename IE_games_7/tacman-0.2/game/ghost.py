"""The ghost actors

The algorithms for the different coloured ghosts comes from 
the excellent article: http://gameinternals.com/post/2072558330/understanding-pac-man-ghost-behavior


"""

import math
import random
import objects

import serge.blocks.directions

from common import G
import common
import serge.actor

class Ghost(objects.BoardItem):
    """Controls a ghost"""

    colour = 'unknown'
    mode = None
    rgb = (255, 255, 255, 255)
    target_radius = 20
    mobile = True
    rotate_actor = False
    player_rank_target = 100
     
    def __init__(self, game, devmode):
        """Initialise the Ghost"""
        super(Ghost, self).__init__('ghost', '%s-ghost' % self.colour, G('%s-speed' % self.colour))
        self.setSpriteName(self.name)
        game.manager.assignBehaviour(self, serge.blocks.behaviours.TimedCallback(G('move-interval'), self.moveGhost), 'moving')
        self._game = game
        self._last_direction = None
        self._devmode = devmode
        self._target = None
        self._reverse_request = False
        self._waiting_for = G('%s-initial-frozen' % self.colour)
        self._frozen_for = 0
        self._cube = serge.actor.Actor('ice-cube', '%s-ice-cube' % self.colour)
        self._cube.setSpriteName('ice-cube')
        self._cube.setLayerName('overlay')
        self._cube.active = False

    def addedToWorld(self, world):
        """Setup extras"""
        super(Ghost, self).addedToWorld(world)
        world.addActor(self._cube)
        #
        if not self._target:
            self._target = serge.blocks.utils.addVisualActorToWorld(world, 'dev', ('%s-target' % self.colour), 
                serge.blocks.visualblocks.Circle(self.target_radius, self.rgb, 2), 'main')
            self._target.active = self._devmode

    def moveGhost(self, world, actor, interval):
        """Update the position of the ghost"""
        mx, my = self._game._grid.findActorLocation(self)
        #
        # Reversing?
        if self._reverse_request and self._last_direction:
            possibles = [(None, serge.blocks.directions.getOppositeVector(self._last_direction))]
        else:
            px, py = self.getTarget() if self.mode == 'chase' else self.getScatter() if self.mode == 'scatter' else self.getFright()
            self._target.moveTo(*self._game._grid.getCoords((px, py)))
            #
            # Red finds the best square to get close to the player
            possibles = []
            for (dx, dy) in ((-1,0), (+1,0), (0,-1), (0,+1)):
                #
                # Don't go back on yourself
                if self._last_direction:
                    if (dx, dy) == serge.blocks.directions.getOppositeVector(self._last_direction):
                        continue
                try:
                    occupants = self._game._grid.getActorsAt((mx+dx, my+dy))
                except serge.blocks.layout.OutOfRange:
                    pass
                else:
                    if not (occupants.hasActorWithTag('ghost') or occupants.hasActorWithTag('wall')):
                        # Ok can move here - store this move and the result
                        possibles.append([(mx+dx-px)**2+(my+dy-py)**2, (dx, dy)])
            #
            # Look for best move
            possibles.sort()
        #
        # Move if we can
        if possibles:
            _, (dx, dy) = possibles[0]
            self._game._grid.moveActor((mx+dx, my+dy), self)
            self._last_direction = (dx, dy)
        else:
            #
            # Since no move is possible we should clear the last move
            # to avoid getting stuck
            self._last_direction = None
        #
        self._reverse_request = False


    def getCurrentTarget(self):
        """Get the current target"""
        return (
            self.getTarget() if self.mode == 'chase' 
            else self.getScatter() if self.mode == 'scatter' 
            else self.getHome() if self.mode == 'return'
            else self.getFright()
        )
    
    def getTarget(self):
        """Return the target square for the ghost"""
        raise NotImplementedError

    def getScatter(self):
        """Return the scatter target for the ghost"""
        return self.scatter
    
    def getFright(self):
        """Return the fright target for the ghost"""
        dx, dy = serge.blocks.directions.getVectorFromCardinal(random.choice('nsew'))
        x, y = self._game._grid.findActorLocation(self)
        return (x+self.moves*dx, y+self.moves*dy)
    
    def getHome(self):
        """Return the home square"""
        return G('%s-start' % self.colour)
    
    def reverseDirection(self):
        """Request to reverse direction at the next chance"""
        self._reverse_request = True

    def playerVisited(self, grid, game, player):
        """The player landed on a ghost"""
        self.log.debug('Visit of %s to %s' % (player, self))
        if player is self:
            return
        if not player.ai_controlled:
            if self.mode == 'return':
                self.log.debug('Player landed on returning ghost %s' % self)
                pass
            elif self.mode == 'fright':
                self.log.debug('Player landed on frightened ghost %s' % self)
                game._score.value += G('ghost-score')
                self.setReturning()
                game.processEvent(('eat-ghost', None))
            else:
                self.log.debug('Player landed on ghost %s' % self)
                game.playerDeath()
                game.processEvent(('hit-ghost', None))
                return 'reset'
    
    def resetSprite(self):
        """Reset the sprite back to normal"""
        self.setSpriteName('%s-ghost' % self.colour)

    def setFrightened(self):
        """Set the mode to frightened"""
        self.setSpriteName('frightened-ghost')

    def setReturning(self):
        """Set the mode to returning"""
        self.gotoMode('return')
        self.setSpriteName('eyes')
        
    def moveToHome(self, grid):
        """Move the ghost to the home location"""
        grid.moveActor(G('%s-start' % self.colour), self)   
        self._waiting_for = G('%s-initial-frozen' % self.colour)     
    
    def returnedFromDeath(self, mode):
        """The ghost returned home after dieing"""
        self.gotoMode(mode)
        self._frozen_for = G('after-death-freeze')
            
    def gotoMode(self, mode):
        """Switch to this mode"""
        if (self.mode == 'fright' or self.mode == 'return') and mode != self.mode:
            self.resetSprite()
        #
        # Reverse direction for all mode switches other than from "fright"
        if self.mode != 'fright':
            self.reverseDirection()            
        #
        self.mode = mode
        if mode == 'fright':
            self.setFrightened()

    def freezeGhost(self, time):
        """Freeze this ghost"""
        self._frozen_for = time
        self._cube.active = True
        self._cube.moveTo(self.x, self.y)

    def removeCube(self):
        """Remove the cube for this ghost"""
        self._cube.active = False

    def isFrozen(self):
        """Return if we are frozen"""
        return self._frozen_for != 0 or self._waiting_for != 0

    def skipMove(self):
        """Skip a move"""
        old_frozen = self._frozen_for
        self._frozen_for = max(0, self._frozen_for-1)
        self._waiting_for = max(0, self._waiting_for-1)
        if old_frozen and self._frozen_for == 0:
            self.removeCube()
            
class RedGhost(Ghost):
    """The red ghost"""
    
    colour = 'red'
    scatter = (13,-2)
    rgb = (255, 0, 0, 100)
    target_radius = 22
    
    def getTarget(self):
        """Return the target square for the ghost"""
        return self._game._grid.findActorLocation(self._game._player)


class PinkGhost(Ghost):
    """The pink ghost"""
    
    colour = 'pink'
    scatter = (2, -2)
    rgb = (255, 128, 128, 100)
    target_radius = 24

    def getTarget(self):
        """Return the target square for the ghost"""
        px, py = self._game._grid.findActorLocation(self._game._player)
        dx, dy = serge.blocks.directions.getVectorFromCardinal(self._game._player.direction)
        return (px+4*dx, py+4*dy)


class OrangeGhost(Ghost):
    """The orange ghost"""
    
    colour = 'orange'
    scatter = (2, 18)
    rgb = (255, 153, 83, 100)
    target_radius = 26

    def getTarget(self):
        """Return the target square for the ghost"""
        px, py = self._game._grid.findActorLocation(self._game._player)
        mx, my = self._game._grid.findActorLocation(self)
        dist = math.sqrt((px-mx)**2 + (py-my)**2)
        self.log.debug('Orange dist is %s' % dist)
        if dist >= 8:
            return px, py
        else:
            return self.scatter

class BlueGhost(Ghost):
    """The blue ghost"""
    
    colour = 'blue'
    scatter = (13, 18)
    rgb = (0, 0, 255, 100)
    target_radius = 28

    def getTarget(self):
        """Return the target square for the ghost"""
        #
        # First part is two squares ahead of the player
        px, py = self._game._grid.findActorLocation(self._game._player)
        dx, dy = serge.blocks.directions.getVectorFromCardinal(self._game._player.direction)
        t1x, t1y = (px+2*dx, py+2*dy)
        #
        # Find red's position
        rx, ry = self._game._grid.findActorLocation(self.red)
        #
        # Get vector from red to t1
        vx, vy = (t1x-rx, t1y-ry)
        #
        self.log.debug('Blue ghost p %s, d %s, t1 %s, r %s, v %s' % (
            (px, py), (dx, dy), (t1x, t1y), (rx, ry), (vx, vy)))
        #
        return (rx+vx*2, ry+vy*2)        
