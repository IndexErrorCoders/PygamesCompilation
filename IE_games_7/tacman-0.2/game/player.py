"""Logic for the player"""

import math
import networkx 

import serge.actor
import serge.sound
import serge.blocks.directions
from theme import G, theme

class NoValidTarget(Exception): """Asked an actor to chose a target and there wasn't a valid one"""


class MobileActor(serge.actor.Actor):
    """An actor that moves"""
    
    mobile = True
    ai_controlled = False
    rotate_actor = True
    mode = None
    player_rank_target = 10
    
    def __init__(self, tag, name, speed, *args, **kw):
        """Initialise the actor"""
        super(MobileActor, self).__init__(tag, name, *args, **kw)
        self.targets = []
        self.speed = speed # pixels per second
        self.moves = 0 if not self.mobile else G('%s-moves' % tag)
        self.current_target = None
    
    def setTargetList(self, targets):
        """Set the list of targets we will move towards"""
        self.targets = targets
        self.selectNewTarget()

    def selectNewTarget(self):
        """Set the new target"""
        try:
            self.current_target = self.targets.pop(0)
        except IndexError:
            self.current_target = None
    
    def clearTargets(self):
        """Clear all targets"""
        self.targets[:] = []
        self.current_target = None
           
    def arrivedAtDestination(self):
        """The actor arrived"""
        self.processEvent((serge.events.E_ACTOR_ARRIVED, self))

    def getSquaresInRange(self, (cx, cy), graph):
        """Return a list of the squares that are in range"""
        in_range, destination = [], []
        for dx in range(-self.moves, 1+self.moves):
            for dy in range(-self.moves, 1+self.moves):
                square = nx, ny = (cx+dx, cy+dy)
                try:
                    length = networkx.shortest_path_length(graph, (cx, cy), (nx, ny))
                except (networkx.exception.NetworkXError, networkx.NetworkXNoPath):
                    # Cannot get there
                    pass
                else:
                    if length == self.moves:
                        destination.append(square)
                    elif length < self.moves:
                        in_range.append(square)
        return in_range, destination
                    
    def turnMove(self, world, game, interval):
        """Move the actor when needed"""
        if not self.current_target:
            self.selectNewTarget()
        if self.current_target:
            cx, cy = game._grid.findActorLocation(self)
            nx, ny = self.current_target
            dx, dy = (nx-cx, ny-cy)
            game._grid.moveActor((nx, ny), self)
            serge.sound.Sounds.getItem('step').play()
            #
            # Make sure the visual is right
            if self.rotate_actor:
                if dx:
                    self.visual.horizontal_flip = dx < 0
                    self.visual.setAngle(0)
                else:
                    self.visual.horizontal_flip = False
                    self.visual.setAngle(90 if dy < 0 else 270)
            #
            self.direction = serge.blocks.directions.getCardinalFromVector((dx, dy))
            self.current_target = None
            #
            # Visit everything else on there
            occupants = game._grid.getActorsAt((nx, ny))
            self.log.debug('Occupants are %s' % (occupants,))
            if not 'reset' in occupants.forEach().playerVisited(game._grid, game, self):
                #
                # Flag our arrival
                if not self.targets:
                    self.arrivedAtDestination()
            
    def highlightMoves(self, game, grid, highlighter, graph, callback, avoid):
        """Highlight the squares that this actor can move to"""
        cx, cy = grid.findActorLocation(self)
        self.log.info('Highlighting actor at %d, %d' % (cx, cy))  
        #
        # Remove nodes from the graph to avoid particular items unless in return mode
        removed_edges = []
        for avoid_actor in avoid:
            if avoid_actor is not self:
                # Find position to avoid
                ax, ay = grid.findActorLocation(avoid_actor)
                # 
                # Remove node but remember the edges we are removing as we want to restore them
                # Don't do this if it has already been done or we have two ghosts on the same
                # square (eg at the begining of the game)
                if (ax, ay) in graph.nodes() and (ax, ay) != grid.findActorLocation(self) and (ax, ay) != self.getHome():
                    self.log.debug('Removed node %d, %d' % (ax, ay))
                    removed_edges.extend(graph.edges((ax, ay)))
                    graph.remove_node((ax, ay))
        #
        # Also avoid the home square if we are not on it
        home = self.getHome()
        if home and (cx, cy) != home:
            removed_edges.extend(graph.edges(home))
            graph.remove_node(home)
        #
        # Highlight these
        highlighter.removeChildren()
        in_range, destination =self.getSquaresInRange((cx, cy), graph)
        for square in in_range:
            h = serge.actor.Actor('h', 'h-%s' % (square,))
            h.setSpriteName('range-square')
            h.setLayerName('foreground')
            highlighter.addChild(h)
            h.moveTo(*grid.getCoords(square))
            if game._devmode and not self.ai_controlled:
                h.linkEvent(serge.events.E_LEFT_CLICK, callback, (square, self, h))
        #
        # Highlight squares that you can really move to
        for square in destination:
            h = serge.actor.Actor('h', 'h-%s' % (square,))
            h.setSpriteName('destination-square')
            h.setLayerName('foreground')
            highlighter.addChild(h)
            h.moveTo(*grid.getCoords(square))
            if not self.ai_controlled:
                h.linkEvent(serge.events.E_LEFT_CLICK, callback, (square, self, h))
        #
        # Restore the graph
        graph.add_edges_from(removed_edges)
        #
        return destination
    
    def getHome(self):
        """Return the home square"""
        return None
