"""Represents the main game board"""

import random
import collections
import networkx

import serge.actor
import serge.visual
import serge.blocks.settings
import serge.blocks.directions
import serge.blocks.actors
import serge.blocks.tiled
import serge.blocks.layout
import serge.blocks.utils
import serge.blocks.visualblocks

import bomb
import powerups
from theme import G, theme


class NoSpawnPoints(Exception):
    """There were no spawn points free"""


class NoPath(Exception):
    """There was no path from the start to end point"""


class Metadata(serge.blocks.settings.Bag):
    """Store data on squares"""


class Board(serge.blocks.actors.ScreenActor):
    """Represents the board that the game is played on"""

    def __init__(self, tag, name, tile_sprite_name, options):
        """Initialise the board"""
        super(Board, self).__init__(tag, name)
        #
        self.tile_sprite_name = tile_sprite_name
        self.options = options
        #
        # Prepare the tiled module
        self.tiles = self.men = self.movement = self.objects = self.layout = None
        serge.blocks.tiled.LAYER_TYPES += ('start', 'power-ups')
        serge.blocks.tiled.Tiled.resetLayerTypes()
        #
        self.size = G('board-size')
        self.cell_size = G('board-cell-size')
        self.blanks = G('board-blanks')
        self.destructible = G('board-destructible')
        self.default_weight = G('default-movement-weight')
        self.random_items = [getattr(powerups, name) for name in G('random-item-names')]
        #
        self._visual_dirty = True
        self._total_time = 0.0

    def initFrom(self, filename):
        """Initialise from the given level file"""
        self.tiles = serge.blocks.tiled.Tiled(filename)
        self.size = (self.tiles.width, self.tiles.height)
        self.visual_layer = self.tiles.getLayerByType('visual')
        self.powerup_layer = self.tiles.getLayerByType('power-ups')
        self.updateMovementGraph()
        self.men = {}
        #
        # Find places to put random items
        self.random_locations = [cell for cell in self.visual_layer.getLocationsWithSpriteName(self.blanks[0])]
        #
        # Create a place to store all the men at a certain location
        self.squares = []
        self.metadata = []
        for x in range(self.size[0]):
            self.squares.append([])
            self.metadata.append([])
            for y in range(self.size[1]):
                self.squares[-1].append([])
                item = Metadata()
                item.safe_after = 0.0
                self.metadata[-1].append(item)
        #
        # Add the power ups
        self.power_ups = []
        for location in self.powerup_layer.getLocationsWithTile():
            item_factory = powerups.getItem(self.powerup_layer.getSpriteFor(location).name)
            item = item_factory(self)
            self.power_ups.append((item, location))
        #
        self.h_footstep = serge.visual.Sprites.getItem(G('footstep-h-sprite'))
        self.v_footstep = serge.visual.Sprites.getItem(G('footstep-v-sprite'))
        self.bomb_blast = serge.visual.Sprites.getItem(G('bomb-blast-sprite'))
        self.gore = serge.visual.Sprites.getItem(G('gore-sprite'))

    def addedToWorld(self, world):
        """Added to the world"""
        super(Board, self).addedToWorld(world)
        #
        # Create layout for objects
        self.layout = serge.blocks.layout.Grid(
            'grid', 'grid', self.size,
            self.size[0] * self.cell_size[0], self.size[1] * self.cell_size[1],
        )
        #
        # Create background board graphic
        self.visual = serge.visual.SurfaceDrawing(
            self.size[0] * self.cell_size[0],
            self.size[1] * self.cell_size[1]
        )
        self.overlay = serge.visual.SurfaceDrawing(
            self.size[0] * self.cell_size[0],
            self.size[1] * self.cell_size[1]
        )
        #
        # Add powerups
        for item, location in self.power_ups:
            self.addManAt(item, location)
            self.world.addActor(item)
        #
        # Debugging overlays
        if self.options.cheat and G('ai-show-unsafe'):
            self.unsafe = serge.blocks.utils.addVisualActorToWorld(
                world, 'debug', 'show-unsafe',
                serge.visual.SurfaceDrawing(
                    self.size[0] * self.cell_size[0],
                    self.size[1] * self.cell_size[1]
                ),
                center_position=(self.x, self.y),
                layer_name='debug',
            )
        else:
            self.unsafe = None

    def updateActor(self, interval, world):
        """Update the actor"""
        super(Board, self).updateActor(interval, world)
        #
        self._total_time += interval / 1000.0
        #
        # Update the visual if we need to
        if self._visual_dirty:
            self.updateVisual()
        #
        # Update debugging views
        if self.unsafe:
            self.updateUnsafe()

    def updateVisual(self):
        """Update the visual for the background"""
        w, h = self.size
        cw, ch = self.cell_size
        layer = self.tiles.getLayerByType('visual')
        self.visual.clearSurface()
        surface = self.visual.getSurface()
        #
        # Put all sprites in the grid
        for x in range(w):
            for y in range(h):
                sprite = layer.getSpriteFor((x, y))
                cx, cy = self.layout.getCoords((x, y))
                sprite.renderTo(0, surface, (cx - cw / 2, cy - ch / 2))
                #
        #
        # Put overlay on
        self.visual.getSurface().blit(self.overlay.getSurface(), (0, 0))
        self._visual_dirty = False

    def addFootsteps(self, (x, y), (dx, dy)):
        """Add some footsteps to the screen"""
        px, py = self.layout.getCoords((x, y))
        w, h = self.cell_size
        #
        if dx != 0:
            ax = -w / 2
            ay = h * random.random() * 0.2 - h / 2
            footstep = self.h_footstep
        else:
            ax = w * random.random() * 0.2 - w / 2
            ay = -h / 2
            footstep = self.v_footstep
        #
        footstep.renderTo(0, self.visual.getSurface(), (px + ax, py + ay))
        footstep.renderTo(0, self.overlay.getSurface(), (px + ax, py + ay))

    def addBombBlast(self, man):
        """Add some bomb blasts to the screen"""
        #
        # Calculate location on the visuals to put the blasts
        px, py = self.layout.getCoords(self.getPosition(man))
        w, h = self.cell_size
        x, y = px - w / 2 - 3, py - h / 2 - 3
        #
        # Put all parts of the blast on the overlays
        for i in range(G('number-bomb-blasts')):
            angle = random.randrange(0, 360)
            self.bomb_blast.setAngle(angle)
            self.bomb_blast.renderTo(0, self.visual.getSurface(), (x, y))
            self.bomb_blast.renderTo(0, self.overlay.getSurface(), (x, y))

    def addGore(self, man):
        """Add some gore to the screen"""
        #
        # Calculate location on the visuals to put the blasts
        px, py = self.layout.getCoords(self.getPosition(man))
        w, h = self.cell_size
        x, y = px - w / 2 - 3, py - h / 2 - 3
        #
        # Put all parts of the blast on the overlays
        for i in range(G('number-gore')):
            angle = random.randrange(0, 360)
            self.gore.setAngle(angle)
            self.gore.renderTo(0, self.visual.getSurface(), (x, y))
            self.gore.renderTo(0, self.overlay.getSurface(), (x, y))

    def updateUnsafe(self):
        """Update the overlay of unsafe areas"""
        self.unsafe.visual.clearSurface()
        rectangle = serge.blocks.visualblocks.Rectangle(self.cell_size, G('ai-unsafe-colour'))
        w, h = self.size
        sx, sy = self.cell_size
        for x in range(w):
            for y in range(h):
                if not self.isSafe((x, y)):
                    rectangle.renderTo(0, self.unsafe.visual.getSurface(),
                                       (x * sx, y * sy))

    def getSpawnPoint(self, sprite_name):
        """Return a possible spawn point for a sprite"""
        #
        # Find the spawn layer
        layer = self.tiles.getLayerByType('start')
        positions = layer.getLocationsWithSpriteName(sprite_name)
        for position in positions:
            if position not in self.men.values():
                return position
        else:
            raise NoSpawnPoints('There are no free spawn points for "%s"' % sprite_name)

    def getLocationsWithManOfType(self, cls):
        """Return locations with men of a certain type"""
        return [location for man, location in self.men.iteritems() if isinstance(man, cls)]

    def addManAt(self, man, (x, y)):
        """Add a man at a certain position"""
        #
        # Notify all the men on the same square that this man moved onto them
        self.men[man] = (x, y)
        self.squares[x][y].append(man)
        for existing in self.getOverlapping((x, y)):
            if existing != man:
                existing.manMovesOnto(man)
        man.moveTo(*self.screenLocation((x, y)))
        #
        # Update movement weights if we need to
        if man.movement_weight:
            for edge, weights in self.movement[(x, y)].iteritems():
                weights['weight'] = man.movement_weight
            for edge, weights in self.unrestricted[(x, y)].iteritems():
                weights['weight'] = man.movement_weight

    def removeMan(self, man):
        """Remove a man from the board"""
        x, y = self.men[man]
        del(self.men[man])
        self.squares[x][y].remove(man)
        #
        # Update movement weights if we need to
        if man.movement_weight:
            for edge, weights in self.movement[(x, y)].iteritems():
                weights['weight'] = self.default_weight
            for edge, weights in self.unrestricted[(x, y)].iteritems():
                weights['weight'] = self.default_weight

    def destroyItemAt(self, (x, y), sprite_name):
        """Destroy the item at the location"""
        #
        # Get a blank sprite
        blank = serge.visual.Sprites.getItem(sprite_name)
        #
        # Put it at the right location
        self.visual_layer.setSpriteFor((x, y), blank)
        #
        # Redo the movement logic
        self._visual_dirty = True
        self.updateMovementGraph()

    def updateMovementGraph(self):
        """Update the movement graph"""
        self.log.info('Regenerating the movement graph')
        #
        self.movement = networkx.Graph()
        self.unrestricted = networkx.Graph()
        layer = self.visual_layer
        w, h = self.size
        #
        for x in range(w):
            for y in range(h):
                sprite = layer.getSpriteFor((x, y))
                #
                # Is this a blank cell?
                if sprite.name in self.blanks:
                    self.movement.add_node((x, y))
                    #
                    # Look for places to move to
                    for dx, dy in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
                        nx, ny = x + dx, y + dy
                        #
                        # Is the new place in the board?
                        if 0 <= nx < w and 0 <= ny < h:
                            to_sprite = layer.getSpriteFor((nx, ny))
                            if to_sprite.name in self.blanks:
                                self.movement.add_node((nx, ny))
                                self.movement.add_edge((x, y), (nx, ny), weight=self.default_weight)
                                self.unrestricted.add_node((nx, ny))
                                self.unrestricted.add_edge((x, y), (nx, ny), weight=self.default_weight)
                            elif to_sprite.name in self.destructible:
                                self.unrestricted.add_node((nx, ny))
                                self.unrestricted.add_edge((x, y), (nx, ny), weight=self.default_weight)

    def canMove(self, man, (dx, dy)):
        """Return True if a man can move in a certain direction"""
        cx, cy = self.men[man]
        nx, ny = cx + dx, cy + dy
        #
        # Is there a path
        if (nx, ny) not in self.movement.neighbors((cx, cy)):
            return False
            #
        # Is something in the way
        return self.canOccupy(man, (nx, ny))

    def canOccupy(self, man, (x, y)):
        """Return True if the man can occupy a square"""
        for item, position in self.men.iteritems():
            if position == (x, y):
                return not man.isMoveBlockedBy(item)
        else:
            return True

    def canDestroy(self, (x, y)):
        """Return True if a block can be destroyed"""
        return self.visual_layer.getSpriteFor((x, y)).name in self.destructible

    def moveMan(self, man, (dx, dy)):
        """Move a man in a certain way"""
        cx, cy = self.men[man]
        self.removeMan(man)
        nx, ny = cx + dx, cy + dy
        self.addManAt(man, (nx, ny))
        self.addFootsteps((nx, ny), (dx, dy))

    def screenLocation(self, (x, y)):
        """Return the screen location of a cell"""
        px, py = self.layout.getCoords((x, y))
        return px + self.x - self.width / 2, py + self.y - self.height / 2

    def dropBomb(self, man):
        """Drop a bomb at a man's location"""
        x, y = self.men[man]
        self.dropBombAt((x, y))

    def dropBombAt(self, (x, y), auto_explode=True):
        """Drop a bomb at a location"""
        new_bomb = bomb.Bomb(self, auto_explode=auto_explode)
        self.world.addActor(new_bomb)
        self.addManAt(new_bomb, (x, y))
        #
        # Mark squares around the bomb as dangerous
        if new_bomb.auto_explode:
            w, h = self.size
            #
            for direction in 'nesw':
                dx, dy = serge.blocks.directions.getVectorFromCardinal(direction)
                for i in range(new_bomb.max_distance + 1):
                    safe_time = new_bomb.fuse + (i + 2) * new_bomb.propagation_time + new_bomb.explosion_time
                    if 0 < x + dx < w and 0 < y + dy < h:
                        nx, ny = x + dx * i, y + dy * i
                        will_destruct = self.isDestructible((nx, ny))
                        if not self.isBlank((nx, ny)) and not will_destruct:
                            break
                        else:
                            #
                            # If this is a destructible block *and* it is marked as
                            # safe after then this means that the block will be
                            # destroyed so we treat it as though it is blank
                            effectively_blank = self.metadata[ny][nx].safe_after
                            #
                            # Mark as dangerous
                            self.metadata[ny][nx].safe_after = self._total_time + safe_time
                            #
                            # If it was destructible then can move on but we have still
                            # marked the destructible square as dangerous
                            if will_destruct and not effectively_blank:
                                break

    def getPosition(self, man):
        """Return the position of the man"""
        return self.men[man]

    def getMenOverlapping(self, man):
        """Return the men who overlap the position of the given man"""
        x, y = self.getPosition(man)
        return self.getOverlapping((x, y))

    def getOverlapping(self, (x, y)):
        """Return the men overlap a position"""
        return self.squares[x][y][:]

    def getSquaresAround(self, man, distance):
        """Return the squares around a man"""
        w, h = self.size
        x, y = self.getPosition(man)
        squares = []
        for dx in range(-distance, distance + 1):
            squares.append([])
            for dy in range(-distance, distance + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    occupants = self.getOverlapping((nx, ny))
                    if occupants:
                        squares[-1].append(occupants[0].state_id)
                    else:
                        squares[-1].append(self.visual_layer.tiles[ny][nx])
                else:
                    squares[-1].append(0)
        return squares

    def getPath(self, (sx, sy), (ex, ey), unrestricted=False):
        """Return the path from the start to end locations - raise exception is no path"""
        try:
            path = networkx.shortest_path(
                self.movement if not unrestricted else self.unrestricted,
                (sx, sy), (ex, ey), weight='weight')
        except (networkx.NetworkXError, networkx.NetworkXNoPath), err:
            raise NoPath('There was no path from %s to %s' % ((sx, sy), (ex, ey)))
        else:
            return path

    def breadthFirstDestinationSearch(self, man, (x, y)):
        """Return possible destinations, breadth first, starting from x, y"""
        #
        # Algorithm adapted from the networkx function bfs_edges
        neighbors = self.movement.neighbors_iter
        visited = set([(x, y)])
        queue = collections.deque([((x, y), neighbors((x, y)))])
        while queue:
            parent, children = queue[0]
            try:
                child = next(children)
                if child not in visited and self.canOccupy(man, child):
                    yield parent, child
                    visited.add(child)
                    queue.append((child, neighbors(child)))
            except StopIteration:
                queue.popleft()

    def breadthFirstUnrestrictedDestinationSearch(self, (x, y)):
        """Return possible destinations, breadth first, starting from x, y with no block restrictions"""
        return networkx.bfs_edges(self.unrestricted, (x, y))

    def isDestructible(self, (x, y)):
        """Return True if the cell is destructible"""
        return self.visual_layer.getSpriteFor((x, y)).name in self.destructible

    def isBlank(self, (x, y)):
        """Return True if the cell is blank"""
        return self.visual_layer.getSpriteFor((x, y)).name in self.blanks

    def isSafe(self, (x, y)):
        """Return True if the square is safe"""
        #
        # Marked as unsafe?
        if self._total_time < self.metadata[y][x].safe_after:
            return False
        #
        return not self.isDeadly((x, y))

    def isDeadly(self, (x, y)):
        """Return True if stepping on the square would kill you"""
        #
        # Is there an explosion there?
        return any(man.is_deadly for man in self.getOverlapping((x, y)))

    def gameOver(self):
        """The game was over"""