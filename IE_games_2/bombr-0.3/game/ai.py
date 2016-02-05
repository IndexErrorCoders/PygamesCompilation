"""Controller for the AI"""

import random

import serge.actor
import serge.common
import serge.sound
import serge.blocks.directions
import serge.blocks.fysom
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.settings
from theme import G, theme

from board import NoPath
import bomb
import powerups


# States
S_WAITING = 'waiting'
S_MOVING = 'moving'
S_ESCAPING = 'escaping'
S_CLEARING = 'clearing'
S_MOVING_FOR_KILL = 'moving-for-kill'

# Events
E_ARRIVED = 'arrived'
E_CHOSE_ATTACK = 'chose_attack'
E_CHOSE_ESCAPE = 'chose_escape'
E_CHOSE_CLEAR = 'chose_clear'
E_DROP_BOMB = 'drop_bomb'
E_ENDANGERED = 'endangered'
E_KILL_SPOTTED = 'kill_spotted'

# Strategies
X_CLOSE_BY = 'close-by'
X_FAR_FROM = 'far-from'
X_PLAYER = 'player'
X_HEART = 'heart'
X_FLAG = 'flag'


class AI(serge.common.Loggable):
    """Represents the AI's control of the actor"""

    long_term_memory = {}

    def __init__(self, enemy=None):
        """Initialise the AI"""
        self.addLogger()
        #
        self.enemy = enemy
        self._last_move = 0.0
        self._total_time = 0.0
        self.move_interval = G('ai-move-interval')
        self.selected_path = None
        #
        self.state = serge.blocks.fysom.Fysom({
            'initial': S_WAITING,
            'events': [
                {'name': E_ARRIVED,
                 'src': [S_MOVING, S_CLEARING, S_ESCAPING],
                 'dst': S_WAITING,
                 },
                {'name': E_DROP_BOMB,
                 'src': [S_MOVING, S_CLEARING, S_ESCAPING, S_WAITING],
                 'dst': S_ESCAPING,
                 },
                {'name': E_ENDANGERED,
                 'src': [S_MOVING, S_CLEARING, S_WAITING, S_ESCAPING],
                 'dst': S_ESCAPING,
                 },
                {'name': E_KILL_SPOTTED,
                 'src': [S_WAITING],
                 'dst': S_MOVING_FOR_KILL,
                 },
            ],
            'callbacks': {
                'onarrived': self.onArrived,
                'onendangered': self.onEndangered,
            }
        })
        self.walk = serge.sound.Sounds.getItem('walk')
        #
        self.strategy_offsets = {
            X_CLOSE_BY: [G('ai-squares-view') * serge.blocks.directions.getVectorFromCardinal(i)
                         for i in 'nesw'],
            X_FAR_FROM: [3 * G('ai-squares-view') * serge.blocks.directions.getVectorFromCardinal(i)
                         for i in 'nesw'],
        }
        self.selectStrategy()
        #
        self.heart_grab_distance = G('heart-grab-distance')

    def updateController(self, interval, man, board):
        """Update the control of the actor"""
        self._last_move += interval / 1000.0
        self._total_time += interval / 1000.0
        if self._last_move > self.move_interval:
            self._last_move = 0.0
            #
            # Do the move
            if self.state.current == S_WAITING:
                self.chooseDestination(man, board)
            elif self.state.current in (S_MOVING, S_ESCAPING, S_CLEARING):
                self.makeNextMove(man, board)
            #
            # Change strategy if needed
            if random.random() < G('ai-strategy-flip-probability'):
                self.selectStrategy()

    def selectStrategy(self):
        """Select a new strategy"""
        self.current_strategy = random.choice(self.strategy_offsets.keys())

    def makeMove(self, move, man, board):
        """Make a move"""
        if move == ' ':
            pass
        elif move == 'b':
            board.dropBomb(man)
        else:
            direction = serge.blocks.directions.getVectorFromCardinal(move)
            board.moveMan(man, direction)

    def makeNextMove(self, man, board):
        """Make the next move to our destination"""
        if not self.selected_path:
            self.state.arrived(man=man, board=board)
        else:
            mx, my = board.getPosition(man)
            nx, ny = self.selected_path[0]
            event = serge.blocks.settings.Bag()
            event.man = man
            event.board = board
            #
            # Only make the move if we can
            if not board.canOccupy(man, (nx, ny)):
                self.log.debug('%s cannot move to %s, %s' % (man.getNiceName(), nx, ny))
                if board.isSafe((nx, ny)):
                    self.state.current = S_WAITING
                else:
                    if self.state != S_ESCAPING:
                        self.onEndangered(event)
                    self.state.endangered(man=man, board=board)
            elif board.isSafe((nx, ny)) or (self.state.current == S_ESCAPING and not board.isDeadly((nx, ny))):
                #
                # Only if it is safe or if we are escaping
                if not self.walk.isPlaying():
                    self.walk.play()
                board.moveMan(man, (nx - mx, ny - my))
                self.selected_path.pop(0)
            else:
                #
                # Ok - it isn't safe to make the move
                self.log.debug('Not safe for %s to move to %s, %s' % (man.getNiceName(), nx, ny))
                if not board.isSafe((mx, my)):
                    if self.state != S_ESCAPING:
                        self.onEndangered(event)
                    self.state.endangered(man=man, board=board)
                else:
                    self.state.current = S_WAITING

    def onArrived(self, event):
        """We arrived at our destination"""
        self.log.debug('%s arrived at destination' % event.man.getNiceName())
        if event.src in (S_MOVING, S_CLEARING):
            self.tryToDropBomb(event.man, event.board)
        elif event.src == S_ESCAPING:
            #
            # When we arrive at the escape square then we should
            # wait for quite a bit to allow the bomb to go off
            self._last_move -= G('ai-wait-cycles') * self.move_interval

    def onEndangered(self, event):
        """We were endangered"""
        self.log.debug('%s is endangered - escaping' % event.man.getNiceName())
        self.chooseEscapeDestination(event.man, event.board)
        self.state.current = S_ESCAPING

    def tryToDropBomb(self, man, board):
        """Try to drop a bomb"""
        if self.isSafeToDropBomb(man, board):
            self.makeMove('b', man, board)
            serge.sound.Sounds.play('drop')
            self.state.drop_bomb()
            self.chooseEscapeDestination(man, board)
        else:
            self.log.info('Not safe for %s to drop bomb' % man.getNiceName())

    def chooseDestination(self, man, board):
        """Choose the next destination"""
        self.log.debug('Looking for possible attack locations')
        #
        # Pick attack locations
        mx, my = board.getPosition(man)
        ex, ey = board.getPosition(self.enemy)
        possible = []
        for dx, dy in self.strategy_offsets[self.current_strategy]:
            nx, ny = ex + dx, ey + dy
            if board.canOccupy(man, (nx, ny)):
                possible.append((X_PLAYER, nx, ny))
        #
        # Look for heart locations
        possible.extend([(X_HEART, nx, ny) for nx, ny in board.getLocationsWithManOfType(powerups.Heart)])
        possible.extend([(X_FLAG, nx, ny) for nx, ny in board.getLocationsWithManOfType(powerups.Flag)])
        #
        # Find the closest one we can get to
        paths = []
        for strategy, x, y in possible:
            try:
                path = board.getPath((mx, my), (x, y))
            except NoPath:
                # Ok - there is no path
                pass
            else:
                if strategy == X_PLAYER:
                    paths.append((len(path), path))
                elif strategy == X_FLAG:
                    paths.append((-1000 + len(path), path))
                elif strategy == X_HEART:
                    if len(path) < self.heart_grab_distance:
                        paths.append((len(path) - self.heart_grab_distance, path))
                    else:
                        paths.append((len(path), path))
                else:
                    raise ValueError('Unknown strategy %s' % strategy)
        #
        # Find shortest, if there is one
        if paths:
            paths.sort(lambda a, b: cmp(a[0], b[0]))
            self.selected_path = paths[0][1][1:]
            self.state.current = S_MOVING
        else:
            #
            # No paths so find a clearing path
            self.chooseClearingDestination(man, board)

    def chooseEscapeDestination(self, man, board):
        """Choose a location to escape to"""
        #
        # From the current square - do a breadth first
        # search of the places that we can get to. Choose the
        # path that is safe
        x, y = board.getPosition(man)
        for _, (dx, dy) in board.breadthFirstDestinationSearch(man, (x, y)):
            if board.isSafe((dx, dy)):
                self.log.debug('Found escape square %s, %s for %s' % (dx, dy, man.getNiceName()))
                break
        else:
            #
            # No place to go - just pick the last anyway
            self.log.debug('No escape square for %s' % man.getNiceName())
            self.selected_path = []
            return
        #
        path = board.getPath((x, y), (dx, dy))
        self.selected_path = path[1:]

    def chooseClearingDestination(self, man, board):
        """Choose a destination to drop a bomb to clear a way"""
        self.log.debug('Looking for clearing path for %s' % man.getNiceName())
        #
        # Find the best path from us to the enemy
        x, y = board.getPosition(man)
        ex, ey = board.getPosition(self.enemy)
        try:
            path = board.getPath((x, y), (ex, ey), unrestricted=True)
        except NoPath:
            path = None
        #
        # Make sure we have a path
        if not path:
            self.log.debug('No path found')
            return
        #
        # Look for the bombing location
        chosen_path = []
        for (px, py) in path[1:]:
            if board.isDestructible((px, py)):
                self.log.debug('Found path')
                break
            chosen_path.append((px, py))
        else:
            #
            # This probably means that a block was already destroyed
            # so we should just wait for another cycle
            self.log.debug('No path with destructible found')
            return
        #
        self.state.current = S_CLEARING
        self.selected_path = chosen_path

    def isSafeToDropBomb(self, man, board):
        """Check if it is safe to drop a bomb at the current time"""
        #
        # It is safe if we can get to a location which is safe
        # beyond the blast radius of our bomb
        x, y = board.getPosition(man)
        blast_radius = bomb.Bomb.max_distance
        max_search = 2 * blast_radius
        for _, (sx, sy) in board.breadthFirstDestinationSearch(man, (x, y)):
            if (sx != x and sy != y) and board.isSafe((sx, sy)):
                #
                # Ok, out of line of fire of this bomb and safe
                return True
            elif (abs(sx - x) > blast_radius or abs(sy - y) > blast_radius) and board.isSafe((sx, sy)):
                #
                # Ok, outside of the blast radius
                return True
            elif abs(sx - x) + abs(sy - y) > max_search:
                #
                # Nothing close to us
                return False
        else:
            #
            # No path to safety
            return False


class AIUI(serge.actor.Actor):
    """A user interface to report on the state of the AI"""

    def __init__(self, controller, board, name):
        """Initialise the ui"""
        super(AIUI, self).__init__('debug', name)
        #
        self.controller = controller
        self.board = board

    def addedToWorld(self, world):
        """Added to the world"""
        super(AIUI, self).addedToWorld(world)
        #
        # The debugging text
        self.text = serge.blocks.utils.addTextToWorld(
            world, 'AIUI', self.name, theme, 'ui'
        )
        self.text.tag = 'debug'
        #
        # The destination square
        self.destination = serge.blocks.utils.addVisualActorToWorld(
            world, 'debug', 'desintation',
            serge.blocks.visualblocks.Rectangle(
                G('board-cell-size'), G('%s-destination-colour' % self.name),
            ),
            'ui',
        )
        self.destination.visible = False
        self.destination.active = G('ai-show-destinations')

    def updateActor(self, interval, world):
        """Update the actor"""
        super(AIUI, self).updateActor(interval, world)
        #
        # Update debug text
        self.text.visual.setText(
            'Strategy: %s\nState: %s\nDest: %s\nLength: %s' %
            (self.controller.current_strategy, self.controller.state.current,
             'n/a' if not self.controller.selected_path else self.controller.selected_path[-1],
             'n/a' if not self.controller.selected_path else len(self.controller.selected_path)),
        )
        #
        # Update destination square
        if self.controller.selected_path:
            self.destination.visible = True
            self.destination.moveTo(*self.board.screenLocation((self.controller.selected_path[-1])))