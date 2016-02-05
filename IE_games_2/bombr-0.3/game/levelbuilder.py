"""Automatic builder for levels"""

import random
import networkx

import terrain.builders.main
import terrain.renderers.main
import terrain.evolution
from terrain import common



class BomberProcedural(terrain.builders.main.Builder):
    """A procedural approach to bomberman level building"""

    def __init__(self, configuration):
        """Initialise the builder"""
        super(BomberProcedural, self).__init__(configuration)
        #
        # Get properties
        self.symmetry = common.getString(configuration, 'symmetry').lower().strip()
        self.width = common.getInt(configuration, 'width')
        self.height = common.getInt(configuration, 'height')
        self.blocks_between = common.getInt(configuration, 'blocksBetweenEnemies')
        self.destructible_blocks = common.getInt(configuration, 'destructibleBlocks')
        self.keep_clear_distance = common.getInt(configuration, 'keepClearDistance')
        self.maze_like = common.getTrue(configuration, 'makeLike')

    def buildOnWorld(self, world):
        """Build the bomberman level"""
        #
        # Initialise the world
        world = world.__class__(self.width, self.height)
        self.generateCells(world.width, world.height)
        #
        # Build the world
        for cx, cy in self.always_space:
            self.setCell(cx, cy, self.symmetry, world, 'S')
        for cx, cy in self.optional_walls:
            self.setCell(cx, cy, self.symmetry, world, 'S')
        #
        # Get a pathing graph to use to evaluate the world
        graph = self.generateGraph(world)
        #
        # We are going to progressively remove walls until the graph becomes disconnected
        cells = self.optional_walls[:]
        #
        # Do the removal
        all_removed = []
        while True:
            self.log.debug('Starting progressive removal cycle')
            #
            random.shuffle(cells)
            remaining, removed = self.removeCells(world, graph, cells)
            all_removed.extend(removed)
            if len(remaining) == len(cells):
                # Didn't remove anything
                break
            cells = remaining
        #
        # Now add blocks
        self.addBlocks(world, graph, all_removed)
        #
        return world

    def getBlockCandidateLocations(self, world):
        """Return suitable block locations"""
        w, h = world.width, world.height
        candidate_blocked = []
        candidate_open = []
        #
        # Locate candidates - A candidate location is one where it
        # would be between two other blocks in a line
        for x in range(1, h - 1):
            for y in range(1, w - 1):
                #
                # Keep a region around the start locations clear
                for px, py in ((1, 1), (h - 2, w - 2), (h - 2, 1), (1, w - 2)):
                    dist = abs(x - px) + abs(y - py)
                    if dist <= self.keep_clear_distance:
                        break
                else:
                    #
                    # OK, this would keep the start positions clear
                    cell = world.getCell(x, y)
                    #
                    # Look blocks in a line with a free line in the orthogonal direction
                    for dx, dy in [(-1, 0), (+1, 0)]:
                        cell_1 = world.getCell(x - dx, y - dy)
                        cell_2 = world.getCell(x + dx, y + dy)
                        cell_3 = world.getCell(x - dy, y - dx)
                        cell_4 = world.getCell(x + dy, y + dx)
                        #
                        # Is the new place in the board?
                        if cell_1 == '-' and cell_2 == '-' and cell_3 == 'S' and cell_4 == 'S':
                            # Is candidate
                            if cell == '-':
                                candidate_blocked.append((x, y))
                            else:
                                candidate_open.append((x, y))
        return candidate_blocked, candidate_open

    def addBlocks(self, world, graph, removed):
        """Add destructible blocks to the board"""
        #
        # Find candidate locations to put blocks.
        candidate_blocked, candidate_open = self.getBlockCandidateLocations(world)
        #
        # Look for open candidate block locations along the path between the
        # two start points
        self.log.debug('Trying to putting %d blocks on path between start points' % self.blocks_between)
        path = networkx.algorithms.shortest_path(graph, (1, 1), (world.height - 2, world.width - 2))
        path_candidates = []
        for cell in path:
            if cell in candidate_open:
                path_candidates.append(cell)
        self.log.debug('Found %d candidates on the path' % len(path_candidates))
        #
        # Put the blocks in there - we are going to use the path candidates
        # as the target locations but in case we run out of suitable candidates
        # we will also use any other open candidates
        random.shuffle(path_candidates)
        random.shuffle(candidate_open)
        self.addSpecificBlocksToBoard(world, path_candidates + candidate_open, self.blocks_between, add_to_open=True)
        #
        # Now put some of the walls back in as removable blocks
        random.shuffle(candidate_blocked)
        self.addSpecificBlocksToBoard(world, candidate_blocked, self.destructible_blocks, add_to_open=False)

    def addSpecificBlocksToBoard(self, world, candidates, number, add_to_open=True):
        """Try to add a specific number of blocks to the board"""
        self.log.debug('Trying to add %d %s blocks' % (number, 'open' if add_to_open else 'closed'))
        placed = 0
        while candidates and placed < number:
            cx, cy = candidates.pop()
            #
            # Check candidates again as placing blocks can change things
            candidate_blocked, candidate_open = self.getBlockCandidateLocations(world)
            if (cx, cy) in (candidate_open if add_to_open else candidate_blocked):
                self.setCell(cx, cy, self.symmetry, world, 'B')
                placed += 1
        self.log.debug('Able to place %d blocks' % placed)

    def removeCells(self, world, graph, cells):
        """Try to remove cells but do not break the connectivity of the pathing graph"""
        remaining = []
        removed = []
        for cell in cells:
            #
            # First save the edges so we can restore them and then remove the cells
            # taking into account the symmetry of the board
            edges = []
            self.log.debug('Trying to remove cell "%s": %s' % (cell, self.getEquivalentCells(cell)))
            equivalent_cells = self.getEquivalentCells(cell)
            for this_cell in equivalent_cells:
                edges.extend(graph.edges(this_cell))
                graph.remove_node(this_cell)
            #
            # Is the graph still connected?
            if not networkx.is_connected(graph):
                #
                # No longer connected - add cells back and move to the next one
                self.log.debug('Would break connectivity - skipping')
                graph.add_nodes_from(equivalent_cells)
                graph.add_edges_from(edges)
                remaining.append(cell)
            else:
                # Removing it worked so put a wall there
                self.setCell(cell[0], cell[1], self.symmetry, world, '-')
                removed.extend(equivalent_cells)
        #
        return remaining, removed

    def getEquivalentCells(self, cell):
        """Return the equivalent cells based on the symmetry"""
        x, y = cell
        cells = [(x, y)]
        if 'ew' in self.symmetry and y != self.width / 2:
            cells.append((x, self.width - 1 - y))
        if 'ns' in self.symmetry and x != self.height / 2:
            cells.append((self.height - 1 - x, y))
        if 'ns-ew' == self.symmetry and y != self.width / 2 and x != self.height / 2:
            cells.append((self.height - 1 - x, self.width - 1 - y))
        return cells

    def generateCells(self, width, height):
        """Generate the cells which can be adjusted"""
        self.always_wall = []
        self.always_space = []
        self.optional_walls = []
        #
        # Generate effective dimensions to take account of symmetry
        effective_width = width / 2 + 1 if 'ew' in self.symmetry else width
        effective_height = height / 2 + 1 if 'ns' in self.symmetry else height
        #
        # Get the cells
        for cy in range(0, effective_width):
            for cx in range(0, effective_height):
                if cx == 0 or cy == 0 or cx == height - 1 or cy == width - 1:
                    self.always_wall.append((cx, cy))
                elif self.maze_like and (cx - 1) % 2 == 0 and (cy - 1) % 2 == 0:
                    self.always_space.append((cx, cy))
                elif not self.maze_like and (cx == 1 and cy == 1 or cx == self.height - 2 and cy == self.width - 2):
                    self.always_space.append((cx, cy))
                else:
                    self.optional_walls.append((cx, cy))

    def setCell(self, x, y, symmetry, new_world, cell):
        """Set a cell value"""
        new_world.setCell(x, y, cell)
        if 'ns' in symmetry:
            new_world.setCell(new_world.height - 1 - x, y, cell)
        if 'ew' in symmetry:
            new_world.setCell(x, new_world.width - 1 - y, cell)
        if symmetry == 'ns-ew':
            new_world.setCell(new_world.height - 1 - x, new_world.width - 1 - y, cell)

    def generateGraph(self, world):
        """Return a pathing graph from the world"""
        #
        # Generate a graph to test for pathing
        graph = networkx.Graph()
        w, h = world.width, world.height
        #
        # Build the graph
        for x in range(h):
            for y in range(w):
                cell = world.getCell(x, y)
                if cell != '-':
                    self.log.debug('Adding cell "%s, %s"' % (x, y))
                    graph.add_node((x, y))
                    #
                    # Look for places to move to
                    for dx, dy in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
                        nx, ny = x + dx, y + dy
                        #
                        # Is the new place in the board?
                        if 0 <= nx < h and 0 <= ny < w:
                            to_cell = world.getCell(nx, ny)
                            if to_cell != '-':
                                graph.add_node((nx, ny))
                                graph.add_edge((x, y), (nx, ny))
        #
        return graph


class BomberTiledRenderer(terrain.renderers.main.TiledRenderer):
    """Renderer for tiled file"""

    def getOtherLines(self, world):
        """Return the additional lines"""
        lines = []
        #
        # Start positions
        lines.extend([
            ' <layer name="Start Positions" width="%d" height="%d">' % (world.width, world.height),
            '  <properties>',
            '   <property name="type" value="start"/>',
            '  </properties>',
            '  <data encoding="csv">',
        ])
        for idx in range(world.width):
            if idx == 1:
                lines.append('0,6,' + '0,' * (world.height - 2))
            elif idx == world.width - 2:
                lines.append('0,' * (world.height - 2) + '7,0,')
            elif idx == world.width - 1:
                lines.append('0,' * (world.height - 1) + '0')
            else:
                lines.append('0,' * world.height)
        lines.extend([
            '</data>',
            '</layer>',
        ])
        #
        # Power ups
        lines.extend([
            ' <layer name="Power Ups" width="%d" height="%d">' % (world.width, world.height),
            '  <properties>',
            '   <property name="type" value="power-ups"/>',
            '  </properties>',
            '  <data encoding="csv">',
        ])
        for idx in range(world.width):
            if idx == world.width - 1:
                lines.append('0,' * (world.height - 1) + '0')
            else:
                lines.append('0,' * world.height)
        #
        lines.extend([
            '</data>',
            '</layer>',
        ])
        #
        return lines

    def getTileset(self):
        """Return the tileset specification"""
        lines = [
             '<tileset firstgid="1" name="tiles" tilewidth="20" tileheight="20">',
             ' <image source="../graphics/tiles.png" width="100" height="140"/>',
             '</tileset>',
             '<tileset firstgid="36" name="generic-tileset" tilewidth="20" tileheight="20">',
             ' <image source="../graphics/generic-tileset.png" width="80" height="60"/>',
             '</tileset>',
        ]
        return lines


class BomberEvolution(terrain.builders.main.Builder):
    """A builder for bomberman levels using evolution to create interesting levels"""

    reports_progress = True

    def __init__(self, configuration):
        """Initialise the builder"""
        super(BomberEvolution, self).__init__(configuration)
        #
        # Get properties
        self.initial_pool_size = common.getInt(configuration, 'initialPoolSize')
        self.tournament_size = common.getInt(configuration, 'tournamentSize')
        self.max_iterations = common.getInt(configuration, 'maxIterations')
        self.width = common.getInt(configuration, 'width')
        self.height = common.getInt(configuration, 'height')
        #
        self.percent_space = common.getFloat(configuration, 'targetPercentSpace')
        self.percent_space_multiplier = common.getFloat(configuration, 'percentSpaceMultiplier')
        self.target_blocks = common.getFloat(configuration, 'targetBlocks')
        self.target_blocks_multiplier = common.getFloat(configuration, 'targetBlocksMultiplier')

    def buildOnWorld(self, world):
        """Build the bomberman level"""
        #
        LevelController.target_percent_space = self.percent_space
        LevelController.percent_space_multiplier = self.percent_space_multiplier
        LevelController.target_blocks = self.target_blocks
        LevelController.target_blocks_multiplier = self.target_blocks_multiplier
        #
        LevelDNA.generateCells(self.width, self.height)
        world = world.__class__(self.width, self.height)
        controller = LevelController(world, self)
        controller.setDNA(LevelDNA)
        controller.createInitialPool(self.initial_pool_size)
        controller.performTournament(self.tournament_size, self.max_iterations, world)
        #
        for item in controller.getPool():
            self.log.debug('Ranking for item is %s: %s' % (item.score, item.chromosomes))
        #
        world.updateFrom(controller.getPool()[0].makeOrganism(world))
        #
        controller.scoreFitness(world, detail=True)
        #
        return world


class LevelDNA(terrain.evolution.DNA):
    """DNA to generate a bomberman level"""

    # Moves are moving in the cardinal directions. Upper case means dig in
    # that direction.
    #
    # Numbers mean to go to a location
    # 0 = left, 1 = top, 2 = middle
    #
    symmetries = ['ew', 'ns', 'ns-ew']
    always_walls = []
    always_space = []
    optional_walls = []
    options = '-SB'

    @classmethod
    def getRandomInitialChromosomes(cls):
        """Return initial chromosomes"""
        return '%s:%s' % (
            random.choice(cls.symmetries),
            'S' * len(cls.optional_walls),
        )

    @terrain.evolution.mutator(1.0)
    def flipPath(self, world):
        """Add a new direction"""
        symmetry, paths = self.chromosomes.split(':')
        pos = random.randrange(0, len(paths))
        #
        available_options = self.options.replace(paths[pos], '')
        new_item = random.choice(available_options)
        #
        new = LevelDNA('%s:%s' % (
            symmetry,
            paths[:pos] + new_item + paths[pos+1:]
        ))
        return new

    def makeOrganism(self, world):
        """Make the new world"""
        #
        # New base world
        new_world = world.getCopy()
        #
        symmetry, paths = self.chromosomes.split(':')
        w, h = world.width, world.height
        #
        # Build the world
        for cx, cy in self.always_space:
            self.setCell(cx, cy, symmetry, new_world, 'S')
        for (cx, cy), cell in zip(self.optional_walls, paths):
            self.setCell(cx, cy, symmetry, new_world, cell)
        #
        return new_world

    def setCell(self, x, y, symmetry, new_world, cell):
        """Set a cell value"""
        new_world.setCell(x, y, cell)
        if 'ns' in symmetry:
            new_world.setCell(new_world.width - 1 - x, y, cell)
        if 'ew' in symmetry:
            new_world.setCell(x, new_world.height - 1 - y, cell)
        if symmetry == 'ns-ew':
            new_world.setCell(new_world.width - 1 - x, new_world.height - 1 - y, cell)

    @classmethod
    def generateCells(cls, width, height):
        """Generate the cells which can be adjusted"""
        cls.always_wall = []
        cls.always_space = []
        cls.optional_walls = []
        #
        for cx in range(0, width):
            for cy in range(0, height):
                if cx == 0 or cy == 0 or cx == height - 1 or cy == width - 1:
                    cls.always_wall.append((cx, cy))
                elif (cx - 1) % 2 == 0 and (cy - 1) % 2 == 0:
                    cls.always_space.append((cx, cy))
                else:
                    cls.optional_walls.append((cx, cy))


class LevelController(terrain.evolution.Controller):
    """A controller to control the level generation"""

    target_percent_space = 50
    percent_space_multiplier = 0.0
    target_blocks = 50
    target_blocks_multiplier = 0.0

    def __init__(self, world, progress_reporter=None):
        """Initialise the controller"""
        super(LevelController, self).__init__()
        #
        self.world = world
        self.progress_reporter = progress_reporter

    def scoreFitness(self, world, detail=False):
        """Return how good a level is"""
        #
        # Number of spaces
        if not world:
            return -1e6
        #
        # Generate a graph to test for pathing
        graph = networkx.Graph()
        w, h = world.width, world.height
        spaces = blocks = 0
        #
        # Build the graph
        for x in range(h):
            for y in range(w):
                cell = world.getCell(x, y)
                graph.add_node((x, y))
                if cell != '-':
                    spaces += 1
                if cell == 'B':
                    blocks += 1
                #
                # Look for places to move to
                for dx, dy in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
                    nx, ny = x + dx, y + dy
                    #
                    # Is the new place in the board?
                    if 0 <= nx < w and 0 <= ny < h:
                        to_cell = world.getCell(nx, ny)
                        #
                        # Calculate weight - allowing movement over walls
                        # lets the pathing algorithm spot close solutions
                        weight = 1.0
                        if to_cell == '-':
                            weight += 100
                        if to_cell == '-':
                            weight += 100
                        #
                        graph.add_node((nx, ny))
                        graph.add_edge((x, y), (nx, ny), weight=weight)
        #
        # Path lengths to the test cells
        test_points = [
            ((h - 1) / 2, 1, h * 1.2, -10),  # Vertical mid point
            ((h - 1) / 2, h - 2, h * 1.2, -10),  # Vertical mid point
            (1, (w - 1) / 2, w * 1.2, -10),  # Horizontal mid point
            (w - 2, (w - 1) / 2, w * 1.2, -10),  # Horizontal mid point
            ((h - 1) / 2, (w - 1) / 2, (w / 2 + h / 2) * 1.2, -10),  # Center point
            (h - 2, w - 2, (w + h) * 1.5, -100),  # Enemy
        ]
        total_score = 0
        for (dx, dy, distance, miss_cost) in test_points:
            try:
                path = networkx.shortest_path(
                    graph, (1, 1), (dx, dy), weight='weight')
            except (networkx.NetworkXError, networkx.NetworkXNoPath), err:
                # No path - have large score
                score = miss_cost
            else:
                #
                # Generate weighted distance
                path_length = 0
                for idx in range(len(path) - 1):
                    from_cell, to_cell = path[idx:idx + 2]
                    path_length += 1.0 + (graph.get_edge_data(from_cell, to_cell)['weight'] - 1) * miss_cost
                score = -abs(path_length - distance)
                if detail:
                    self.log.debug('Path: %s' % (path, ))
            total_score += score
            if detail:
                self.log.info('Path score to %d, %d, %s' % (dx, dy, score))

        #
        # Space score
        space_score = -abs(spaces - world.width * world.height * self.target_percent_space / 100.0) * self.percent_space_multiplier
        if detail:
            self.log.info('Space score is %s' % space_score)
        #
        # Blocks score
        blocks_score = -abs(blocks - self.target_blocks) * self.target_blocks_multiplier
        if detail:
            self.log.info('Blocks score is %s' % blocks_score)
        #
        return space_score + total_score + blocks_score

    def getCopy(self):
        """Return a new copy of the controller"""
        return LevelController(self.world, self.progress_reporter)

    def reportProgress(self, percent, best):
        """Report progress back"""
        if self.progress_reporter:
            self.progress_reporter._progress_percent = percent
            self.progress_reporter._progress_world = best
        return not self.progress_reporter._should_stop