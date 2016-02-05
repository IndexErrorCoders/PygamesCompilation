"""Base class for the gameboard"""

import pygame
import networkx
import copy

import serge.blocks.actors
import serge.blocks.utils
import serge.blocks.layout

from theme import G, theme
import common 
import ghost
import objects

class GameBoard(serge.blocks.actors.ScreenActor):
    """Represents a board for the game"""
    
    _devmode = False
    
    def initGrid(self, world, level):
        """Initialise the grid"""
        theme.selectTheme('level-%s' % level)
        self._board = copy.deepcopy(G('board'))
        self._mode = G('mode-initial')
        #
        # Create a grid to handle layout of our actors
        w, h = len(self._board[0]), len(self._board)
        self._grid = serge.blocks.utils.addActorToWorld(world, 
            serge.blocks.layout.MultiGrid('grid', 'grid', (w, h), width=w*G('grid-size')[0], height=h*G('grid-size')[1]),
            layer_name='foreground', origin=G('grid-origin'))
        #
        # Populate the grid with actors
        for r, row in enumerate(self._board):
            for c, name in enumerate(row):
                obj = objects.BoardItems[name]
                if obj:
                    self._grid.addActor((c, r), obj())
        #
        # Make graph
        self.makeGraph()
        #
        # The background
        serge.blocks.utils.addSpriteActorToWorld(world, 'bg', 'bg', G('background'), 'background', 
            center_position=G('bg-position'))

    def initUIElements(self, world, level):
        """Initialise elements of the UI"""
        #
        # The current lives
        self._lives_display = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.RepeatedVisualActor('lives', 'lives', G('initial-lives'), G('lives-offset')),
            'static-pacman', 'ui', origin=G('lives-position'))
        #
        # The current snowflakes
        self._snowflakes_display = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.RepeatedVisualActor('snowflakes', 'snowflakes', G('initial-snowflakes'), G('snowflakes-offset'),
                                                    orientation='vertical'),
            'snowflakes', 'ui', origin=G('snowflakes-position'))
        self._snowflakes_display.linkEvent(serge.events.E_LEFT_CLICK, self.snowflakeClicked)
        #
        # The current boosts
        self._boosts_display = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.RepeatedVisualActor('boosts', 'boosts', G('initial-boosts'), G('boosts-offset'),
                                                    orientation='vertical'),
            'boosts', 'ui', origin=G('boosts-position'))
        self._boosts_display.linkEvent(serge.events.E_LEFT_CLICK, self.boostsClicked)
        #
        # The score
        self._score = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.NumericText('score', 'score', 'Score: %d', G('score-colour'), 
            font_size=G('score-size'), justify='left', value=0), layer_name='ui', center_position=G('score-position'))
        #
        # The moves
        self._moves_made = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.NumericText('moves-made', 'moves-made', 'Moves: %d', G('moves-colour'), 
            font_size=G('moves-size'), justify='left', value=0), layer_name='ui', center_position=G('moves-position'))

    def initPlayers(self, world, level, interactive=True):
        """Initialise the players"""
        #
        # The player
        self._player = self._grid.addActor(G('start'), objects.Pacman('player', 'player', G('player-speed')), 'player')
        self._player.setSpriteName('pacman')
        self._player.direction = 'e'
        self._player_movement = self.manager.assignBehaviour(self, 
            serge.blocks.behaviours.TimedCallback(G('move-interval'), self._player.turnMove), 'turn-moving')
        #
        # Controls to show highlights
        self._highlighter = serge.blocks.utils.addActorToWorld(world, serge.actor.CompositeActor('highlight', 'highlight'))
        #
        # Initialise the ghosts
        self._red = self._grid.addActor(G('red-start'), ghost.RedGhost(self, self._devmode), 'main')
        self._pink = self._grid.addActor(G('pink-start'), ghost.PinkGhost(self, self._devmode), 'main')
        self._orange = self._grid.addActor(G('orange-start'), ghost.OrangeGhost(self, self._devmode), 'main')
        self._blue = self._grid.addActor(G('blue-start'), ghost.BlueGhost(self, self._devmode), 'main')
        self._blue.red = self._red # Blue needs red to target!
        self._ghosts = serge.actor.ActorCollection([self._red, self._pink, self._blue, self._orange])
        self._ghosts.forEach().gotoMode(self._mode)
        #
        # Link events to the ghosts
        for g in self._ghosts:
            self.manager.assignBehaviour(self, 
                serge.blocks.behaviours.TimedCallback(G('move-interval'), g.turnMove), '%s-turn-moving' % g.colour)
            g.linkEvent(serge.events.E_ACTOR_ARRIVED, self.actorArrived)
        #
        # Player control
        if interactive:
            self._player.linkEvent(serge.events.E_LEFT_CLICK, self.playerClicked)
        self._player.linkEvent(serge.events.E_ACTOR_ARRIVED, self.actorArrived)           
        #
        self._mode_toggle = ModeToggle(self._ghosts)
        self._destinations = self._square = None
        
    def makeGraph(self):
        """Make a graph of the board"""
        self.log.debug('Making graph from the board')
        self.graph = networkx.Graph()
        #
        # Add nodes for all valid squares
        for x in range(self._grid.cols):
            for y in range(self._grid.rows):
                occupants = self._grid.getActorsAt((x, y))
                if not occupants.hasActorWithTag('wall'):
                    self.graph.add_node((x,y))
                    #
                    # Add edges
                    for direction in 'nesw':
                        dx, dy = serge.blocks.directions.getVectorFromCardinal(direction)
                        try:
                            new_occupants = self._grid.getActorsAt((x+dx, y+dy))
                        except serge.blocks.layout.OutOfRange:
                            pass
                        else:
                            if not new_occupants.hasActorWithTag('wall'):
                                #
                                # Weight the edges to make the choice the most reasonable
                                weight, ghost_weight = 1, 0
                                if new_occupants.hasActorWithTag('pill'):
                                    weight -= .002
                                if new_occupants.hasActorWithName('yellow-pill'):
                                    weight -= .010
                                if new_occupants.hasActorWithTag('ghost'):
                                    ghost_weight += -0.035
                                    weight += .030 if self._mode_toggle.mode != 'fright' else -0.005
                                #
                                # The ghost weight weighting accounts for when we are not in fright
                                # mode but our path puts us in ghost mode during the path
                                self.graph.add_edge((x,y), (x+dx,y+dy), 
                                    weight=weight, eat_weight=weight+ghost_weight)


                
    def playerClicked(self, obj, arg):
        """The user clicked on the player"""
        if self.players[0] == self._player and not self._level_over.active:
            serge.sound.Sounds.getItem('select').play()
            self.selectPlayer(obj, arg)
                        
    def selectPlayer(self, obj, arg):
        """Select the player"""
        if self._highlighter.hasChildren():
            self._highlighter.removeChildren()
        else:
            avoid = [] if self._mode_toggle.mode != 'freeze' else self._ghosts
            self._player.highlightMoves(self, self._grid, self._highlighter, self.graph, self.chooseDestination, avoid)
            
    def chooseDestination(self, obj, ((nx, ny), actor, highlight)):
        """A new destination square was clicked"""
        serge.sound.Sounds.getItem('select').play()
        self.makeGraph()
        highlight.setSpriteName('chosen-square')
        cx, cy = self._grid.findActorLocation(actor)
        base_path = networkx.shortest_path(self.graph, (cx, cy), (nx, ny), weight='weight')[1:]
        #
        # Check for second path option, which might contain a yellow pill
        other_path = networkx.shortest_path(self.graph, (cx, cy), (nx, ny), weight='eat_weight')[1:]
        if other_path != base_path:
            #
            # Check to see if we eat the pill before we hit the ghost
            first = None
            for cell in other_path:
                if self._grid.getActorsAt(cell).hasActorWithTag('ghost'):
                    first = 'ghost'
                    break
                if self._grid.getActorsAt(cell).hasActorWithName('yellow-pill'):
                    first = 'pill'
                    break
            #
            # See what came first
            if first == 'pill':
                # A good path
                self.log.info('Switching paths - can get pill before ghost')
                base_path = other_path
            elif first is None:
                raise ValueError('Alternate path logic failed. "first" is None')
        actor.setTargetList(base_path)

    def snowflakeClicked(self, event, arg):
        """The user clicked on a snowflake"""
        if self.players[0] != self._player or self._level_over.active:
            return
        self.log.info('Snowflake clicked, %d left' % self._snowflakes_display.getRepeat())
        if self._snowflakes_display.getRepeat() and self._mode_toggle.mode != 'freeze':
            serge.sound.Sounds.getItem('freeze').play()
            self._snowflakes_display.reduceRepeat()
            self._ghosts.forEach().freezeGhost(self._mode_toggle.mode_timings['freeze'])
            self._mode_toggle.gotoMode('freeze')
            if self._highlighter.hasChildren():
                self._highlighter.removeChildren()
                self.selectPlayer(self._player, None)

    def boostsClicked(self, event, arg):
        """The user clicked on a boost"""
        if self.players[0] != self._player or self._level_over.active:
            return
        self.log.info('Boost clicked, %d left' % self._boosts_display.getRepeat())
        if self._boosts_display.getRepeat():
            serge.sound.Sounds.getItem('boost').play()
            self._boosts_display.reduceRepeat()
            self._player.moves = G('player-boost-moves')
            self._player_movement._behaviour.interval = G('move-boost-interval')
            if self._highlighter.hasChildren():
                self._highlighter.removeChildren()
            self.selectPlayer(self._player, None)

    def initMoveOrder(self):
        """Initialise the move order"""
        self.players = serge.actor.ActorCollection([self._player, self._red, self._pink, self._orange, self._blue])

    def actorArrived(self, obj, arg):
        """An actor arrived at the destination"""
        if obj != self.players[0]:
            self.log.info('Arrival or non-active player %s, skipping' % obj.getNiceName())
            return
        #
        self.log.info('Arrival of %s, next up %s' % (obj.getNiceName(), self.players[1].getNiceName())) 
        #
        # Watch for arrival of returning ghost
        if obj != self._player and obj.mode == 'return':
            obj.returnedFromDeath(self._mode_toggle.mode) 
        #
        if self.players[0] == self._player:
            self._moves_made.value += 1
        #
        # Move to next player
        self.players.append(self.players.pop(0))  
        if self.players[0] is not self._player:
            g = self.players[0]
            if g.isFrozen():
                self.log.info('%s is frozen, skipping to next ghost' % g.getNiceName())
                g.skipMove()
                self.actorArrived(g, None)
                return
            #
            # Watch for returning ghost, which goes straight home
            if g.mode == 'return':
                self._square = g.getHome()
            else:
                #
                # Highlight the possible destinations
                self._destinations = g.highlightMoves(self, self._grid, self._highlighter, 
                        self.graph, self.chooseDestination, self._ghosts)
                if not self._destinations:
                    self.log.info('%s cannot move' % g.getNiceName())
                    self.actorArrived(g, None)
                    return
            #
            # Find the target
            self._ghosts_target = px, py = g.getCurrentTarget() 
            g._target.moveTo(*self._grid.getCoords((px, py)))

        else:
            if self._mode_toggle.doTurn():
                self.switchToMode(self._mode_toggle.mode)
            self._highlighter.removeChildren()
            #
            # Cancel boost
            self._player.moves = G('player-moves')
            self._player_movement._behaviour.interval = G('move-interval')
            
    def chooseMove(self, world, actor, interval):
        """Choose a move """
        if self.players[0] is not self._player and not self._level_over.active:
            if self._destinations:
                #
                # Rank destinations by distance from the ghost's target square
                ranked_destinations = [((x-self._ghosts_target[0])**2+abs(y-self._ghosts_target[1])**2, (x,y)) for x, y in self._destinations]
                ranked_destinations.sort()
                self.log.debug('Destinations are %s' % (ranked_destinations,))
                #
                # Choose the one to go to
                _, self._square = ranked_destinations[0]
                h = self._highlighter.getChildren().findActorByName('h-(%d, %d)' % self._square)
                h.setSpriteName('chosen-square')
                self._destinations = None
            elif self._square:
                cx, cy = self._grid.findActorLocation(self.players[0])
                nx, ny = self._square
                self._square = None       
                if (cx, cy) == (nx, ny):
                    self.actorArrived(self.players[0], None)
                else:
                    self.players[0].setTargetList(networkx.shortest_path(self.graph, (cx, cy), (nx, ny))[1:])

    def setupDevMode(self, world):
        """Set up the developer mode"""
        self._target = serge.blocks.utils.addActorToWorld(world, 
            serge.blocks.actors.FormattedText('dev', 'target', 'Target mode: %(mode)s', 
                G('dev-target-colour'), font_size=G('dev-target-size'), justify='left', mode=self._mode),
            layer_name='ui', center_position=G('dev-target-position'))
        self._target_time = serge.blocks.utils.addActorToWorld(world, 
            serge.blocks.actors.NumericText('dev', 'target-time', 'Target time: %d', G('dev-target-colour'), 
                font_size=G('dev-target-size'), justify='left', value=0),
            layer_name='ui', center_position=G('dev-target-time-position'))
        self._target.active = self._devmode
        self._target_time.active = self._devmode

    def switchToMode(self, mode):
        """Switch to ghost mode"""
        self.log.info('Changing ghost mode to %s' % mode)
        #
        # Update debugging
        self._target.setValue('mode', mode)
        self._ghosts.forEach().gotoMode(mode)

    def playerDeath(self):
        """The player died"""
        self.processEvent(('hit-ghost', None))
        self._lives_display.reduceRepeat()
        if self._lives_display.getRepeat() == 0:
            self._level_over.setText('Game Over!')
            self._level_over.active = True
            self._restart.active = True
        else:
            #
            # The visual effect
            self._fade_down = serge.blocks.effects.AttributeFade(self.engine.getRenderer().getLayer('background'), 'visibility', 
                            start=255, end=0, decay=2, done=self.fadeDone)
            self.world.addActor(self._fade_down)                

        #
        # Cancel any movement
        self.players[0].clearTargets()
        self._highlighter.removeChildren()
        self.initMoveOrder()
        #
        # Cancel boost
        self._player.moves = G('player-moves')
        self._player.setSpriteName('pacman-death')

    def fadeDone(self, effect):
        """The fade has completed"""
        self._grid.moveActor(G('start'), self._player)
        self._ghosts.forEach().moveToHome(self._grid)
        #
        # The visual effect
        self._fade_up = serge.blocks.effects.AttributeFade(self.engine.getRenderer().getLayer('background'), 'visibility', 
                        start=0, end=255, decay=1)
        self.world.addActor(self._fade_up)
        self._player.setSpriteName('pacman')                

       
class ModeToggle(serge.common.EventAware):
    """A toggle for the mode"""
    
    def __init__(self, ghosts):
        """Initialise the toggle"""
        self.initEvents()
        self.ghosts = ghosts
        self.mode = G('mode-initial')
        self.mode_timings = G('mode-timings')
        self.mode_ticker = self.mode_timings[self.mode]
        self.last_mode = 'chase'
        
    def doTurn(self):
        """Do a turn - return True if the mode changes"""
        self.mode_ticker -= 1
        if self.mode_ticker <= 0:
            if self.mode == 'fright' or self.mode == 'freeze':
                if self.mode == 'fright':
                    self.processEvent(('fright-mode-over', None))
                self.gotoMode(self.last_mode)
            elif self.mode == 'chase':
                self.gotoMode('scatter')
            else:
                self.gotoMode('chase')
            return True
        else:
            return False
                
    def gotoMode(self, mode):
        """Go to the new mode"""
        if mode == 'fright' or mode == 'freeze':
            #
            # Store the last good mode as long as it isn't a transient mode
            if self.mode not in ('fright', 'freeze'):
                self.last_mode = self.mode
        self.mode = mode
        self.mode_ticker = self.mode_timings[self.mode]
        

