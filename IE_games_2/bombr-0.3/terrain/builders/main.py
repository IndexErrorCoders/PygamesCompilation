"""Builders to use to build the terrain"""

import random
import math

from terrain import loggable
from terrain import common


class Builder(loggable.Loggable):
    """A general builder"""

    reports_progress = False

    def __init__(self, configuration):
        """Initialise the builder"""
        self.addLogger()
        self.configuration = configuration
        self.name = common.getStrAttr(configuration, 'name')
        self.log.debug('Builder created')
        #
        self._progress_percent = 0
        self._progress_world = None
        self._should_stop = False

    def buildOnWorld(self, world):
        """Do our stuff - return the new world"""
        return world

    def getProgress(self):
        """Return a tuple of (current % done, current world)

        Implement this method to show periodic progress.

        """
        if self.reports_progress and self._progress_world:
            return self._progress_percent, self._progress_world
        else:
            return None

    def requestStop(self):
        """Request that we stop"""
        self._should_stop = True


class RockSubstrate(Builder):
    """Creates a rock substrate"""

    reports_progress = True

    def __init__(self, configuration):
        """Initialise the builder"""
        super(RockSubstrate, self).__init__(configuration)
        #
        self.mean_height = common.getInt(configuration, 'meanHeight')
        self.push_energy = common.getInt(configuration, 'pushEnergy')
        self.drop_off = common.getInt(configuration, 'dropOff')
        self.number_pushes = common.getInt(configuration, 'numberPushes')
        self.push_pull_probability = common.getFloat(configuration, 'pushPullProbability')

    def buildOnWorld(self, world):
        """Build the rock substrate"""
        #
        # Set the mean depth across the landscape
        self.log.debug('Setting mean rock depth')
        for cell in world.iterCells():
            cell.rock_depth = self.mean_height
        #
        # Now push a series of peaks in the land
        self.log.debug('Performing %d pushes' % self.number_pushes)
        max_distance = self.drop_off
        for idx in range(self.number_pushes):
            #
            # Progress reporting
            self._progress_percent = 100.0 * idx / self.number_pushes
            self._progress_world = world
            if self._should_stop:
                break
            #
            row = random.randrange(world.height)
            col = random.randrange(world.width)
            push_direction = 1 if random.random() <= self.push_pull_probability else -1
            for row_offset in range(-self.drop_off, self.drop_off + 1):
                for col_offset in range(-self.drop_off, self.drop_off + 1):
                    actual_row = row + row_offset
                    actual_col = col + col_offset
                    if world.isInRange(actual_row, actual_col):
                        distance = math.sqrt(row_offset ** 2 + col_offset ** 2)
                        push_amount = self.push_energy * max(0, (1.0 - distance / max_distance))
                        world.getCell(actual_row, actual_col).rock_depth += push_amount * push_direction
        return world


class BiomeTagger(Builder):
    """Tag areas as a certain Biome"""

    def __init__(self, configuration):
        """Initialise the builder"""
        super(BiomeTagger, self).__init__(configuration)
        #
        self.ranges = []
        for biome_range in configuration.find('heightRanges').findall('range'):
            self.ranges.append((
                common.getIntAttr(biome_range, 'low'),
                common.getIntAttr(biome_range, 'high'),
                common.getStrAttr(biome_range, 'tag')
            ))

    def buildOnWorld(self, world):
        """Tag the biomes"""
        for cell in world.iterCells():
            for low, high, tag in self.ranges:
                if low <= cell.rock_depth < high:
                    cell.biome = tag
                    break
            else:
                self.log.warn('No biome for depth %s' % cell.rock_depth)
        return world


class FillTagBuilder(Builder):
    """Fill the entire area with tags"""

    def __init__(self, configuration):
        """Initialise the builder"""
        super(FillTagBuilder, self).__init__(configuration)
        #
        self.tag_name = common.getString(configuration, 'attributeName')
        self.tag_value = common.getString(configuration, 'attributeValue')
        self.world_width = common.getInt(configuration, 'worldWidth', 0)
        self.world_height = common.getInt(configuration, 'worldHeight', 0)

    def buildOnWorld(self, world):
        """Tag the cells"""
        #
        # Resize the world if required
        if self.world_width is not None or self.world_height is not None:
            world.width = self.world_width if self.world_width else world.width
            world.height = self.world_height if self.world_height else world.height
            world = world.getCopy()
        #
        # Fill to size
        for cell in world.iterCells():
            setattr(cell, self.tag_name, self.tag_value)
        #
        return world


class StringBuilder(Builder):
    """Fill the entire area with tags"""

    def __init__(self, configuration):
        """Initialise the builder"""
        super(StringBuilder, self).__init__(configuration)
        #
        self.tag_value = common.getString(configuration, 'attributeValue')

    def buildOnWorld(self, world):
        """Tag the cells"""
        for row, col, cell in world.iterCellsAndLocations():
            world.setCell(row, col, self.tag_value)
        return world


class Room(object):
    """Represents a base room"""

    def __init__(self, configuration):
        """Initialise the room"""
        self.min_row_multiplier = common.getIntAttr(configuration, 'minRowMultiplier')
        self.max_row_multiplier = common.getIntAttr(configuration, 'maxRowMultiplier')
        self.min_col_multiplier = common.getIntAttr(configuration, 'minColMultiplier')
        self.max_col_multiplier = common.getIntAttr(configuration, 'maxColMultiplier')
        self.rows = [
            (common.getIntAttr(row, 'repeat'), row.text) for row in configuration.findall('row')
        ]

    def getRows(self):
        """Return the rows of the room"""
        row_multiplier = random.randrange(self.min_row_multiplier, self.max_row_multiplier + 1)
        col_multiplier = random.randrange(self.min_col_multiplier, self.max_col_multiplier + 1)
        #
        # Generate the rows
        actual_rows = []
        for repeat, items in self.rows:
            for _ in range(row_multiplier if repeat else 1):
                actual_rows.append([])
                for item in items:
                    actual_rows[-1].extend(item.upper() * (col_multiplier if item != ' ' and item == item.lower() else 1))
        #
        # Flip it around
        if random.random() < 0.5:
            actual_rows.reverse()
        if random.random() < 0.5:
            for row in actual_rows:
                row.reverse()
        #
        return actual_rows


class RandomRoomPlacer(Builder):
    """Put random rooms in a landscape"""

    def __init__(self, configuration):
        """Initialise the builder"""
        super(RandomRoomPlacer, self).__init__(configuration)
        #
        self.number_rooms = common.getInt(configuration, 'numberOfRooms')
        self.wall_width = common.getInt(configuration, 'wallWidth')
        self.max_room_tries = common.getInt(configuration, 'maxRoomTries')
        #
        self.rooms = []
        for room in configuration.find('rooms').findall('room'):
            self.rooms.append(Room(room))

    def buildOnWorld(self, world):
        """Build the rooms"""
        world.rooms = []
        for room_id in range(self.number_rooms):
            for _ in range(self.max_room_tries):
                #
                # Pick room
                room = random.choice(self.rooms)
                rows = room.getRows()
                width = len(rows[0])
                height = len(rows)
                #
                # Pick room location
                x = random.randrange(0, world.width - width)
                y = random.randrange(0, world.height - height)
                #
                # Create tiles and also check room will fit without overlapping
                walls = []
                floor = []
                room_ok = True
                for row in range(height):
                    for col in range(width):
                        xp = x + col
                        yp = y + row
                        cell = world.getCell(yp, xp)
                        if cell.tag == "ROCK":
                            if rows[row][col] == 'W':
                                walls.append(cell)
                            elif rows[row][col] == 'F':
                                floor.append(cell)
                        else:
                            room_ok = False
                #
                # If we got a full room - set the cells
                if room_ok:
                    for cell in walls:
                        cell.tag = "WALL"
                        cell.room = room_id
                    for cell in floor:
                        cell.tag = "FLOOR"
                        cell.room = room_id
                    #
                    # Remember room
                    center_cell = random.choice(floor)
                    world.rooms.append((center_cell.row, center_cell.col))
                    #
                    # Next room
                    break
                else:
                    #
                    # Didn't get a room, try again
                    continue
            else:
                #
                # Ok, tried and failed to find a complete room
                raise BufferError('Unable to find a place to put room %d after %d attempts' % (room_id + 1, self.max_room_tries))
        return world


class TunnelBuilder(Builder):
    """Builds tunnels between rooms"""

    reports_progress = True

    def __init__(self, configuration):
        """Initialse the builder"""
        super(TunnelBuilder, self).__init__(configuration)
        #
        self.tunnel_optimiser_iterations = common.getInt(configuration, 'tunnelOptimiserIterations')

    def buildOnWorld(self, world):
        """Build tunnels between rooms"""
        self.log.debug('Creating tunnels for %d rooms' % len(world.rooms))
        #
        # Find closest rooms
        room_distances = []
        for room_id, (my_row, my_col) in enumerate(world.rooms):
            room_distances.append([])
            for num, (row, col) in enumerate(world.rooms):
                dist = abs(my_row - row) + abs(my_col - col)
                room_distances[-1].append((dist, num))
            room_distances[-1].sort()
        #
        # Find the optimal arrangement of tunnels
        tunnel_arrangements = []
        for idx in range(self.tunnel_optimiser_iterations):
            #
            # Progress reporting
            self._progress_percent = 100.0 * idx / self.tunnel_optimiser_iterations
            self._progress_world = world
            if self._should_stop:
                break
            #
            # Start creating tunnels
            tunnels = set()
            while True:
                #
                # Choose start room
                disconnected = self.isDisconnected(world.rooms, tunnels)
                if not disconnected:
                    break
                self.log.debug('Still to connect %s' % disconnected)
                #
                start_num = random.choice(disconnected)
                start = room_distances[start_num]
                #
                # Choose end room as closest room that we have not yet connected
                for _, end_num in start[1:]:
                    if (start_num, end_num) not in tunnels and (end_num, start_num) not in tunnels:
                        self.log.debug('Creating tunnel from %d to %d' % (start_num, end_num))
                        tunnels.add((start_num, end_num))
                        break
                else:
                    #
                    # Cannot connect this room - try again
                    continue
            #
            # Add to list
            tunnel_arrangements.append((len(tunnels), tunnels))
        #
        # Find the best
        tunnel_arrangements.sort()
        self.log.debug('Best tunnel arrangement has %d tunnels, worst is %d' % (
            tunnel_arrangements[0][0], tunnel_arrangements[-1][0]))
        #
        _, tunnels = tunnel_arrangements[0]
        for start_num, end_num in tunnels:
            #
            # Find path
            path = self.getPath(world, world.rooms[start_num], world.rooms[end_num])
            #
            # Dig path
            if path:
                self.log.debug('Digging path of length %d' % len(path))
                for cell in path:
                    if cell.tag == 'ROCK':
                        cell.tag = 'TUNNEL'
                    elif cell.tag == 'WALL':
                        cell.tag = 'DOOR'
            else:
                self.log.debug('No path found')
        return world

    def isDisconnected(self, rooms, tunnels):
        """Return a list of rooms that are not connected at all"""
        #
        # Start with all disconnected
        disconnected = set(range(len(rooms)))
        if not tunnels:
            return list(disconnected)
        #
        # Start with the first connections
        connected = set()
        tunnel_list = list(tunnels)
        connected.add(tunnel_list[0][0])
        connected.add(tunnel_list[0][1])
        #
        # Find the connected rooms
        for start, end in tunnel_list[1:]:
            if start in connected or end in connected:
                connected.add(start)
                connected.add(end)
        #
        # Now invert this
        return list(disconnected - connected)

    def getPath(self, world, start, end):
        """Return the path between two points in the world"""
        visited = set()
        queue = [(0, self.getDistance(start, end), start, [])]
        distances = {
            'FLOOR': -0.1,
            'ROCK': .1,
            'WALL': .1,
            'TUNNEL': 0,
            'DOOR': 0,
        }
        #
        # Start the iteration
        while queue:
            distance_travelled, distance_to_go, (y, x), path = queue.pop(0)
            visited.add((y, x))
            #
            # Find new locations
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                px, py = x + dx, y + dy
                if not world.isInRange(py, px) and not (py, px) in visited:
                    continue
                visited.add((py, px))
                new_cell = world.getCell(py, px)
                new_path = path[:]
                new_path.append(new_cell)
                #
                # Got to end?
                if (py, px) == end:
                    return new_path
                    #
                queue.append((
                    distance_travelled + distances[new_cell.tag],
                    self.getDistance((py, px), end),
                    (py, px),
                    new_path
                ))
                #
            # Re-sort
            queue.sort(lambda p1, p2: cmp(p1[0] + p1[1], p2[0] + p2[1]))
        #
        # Oops
        self.log.error('Could not find path')
        return None

    @staticmethod
    def getDistance(start, end):
        """Return the distance from start to end"""
        return abs(end[0] - start[0]) + abs(end[1] - start[1])


class WorldClipper(Builder):
    """Clips a world to remove dead space"""

    def __init__(self, configuration):
        """Initialise the builder"""
        super(WorldClipper, self).__init__(configuration)
        #
        self.tag_name = common.getString(configuration, 'tagName')
        self.tag_value = common.getString(configuration, 'tagValue')

    def buildOnWorld(self, world):
        """Build on the world"""
        #
        # Setup
        getter = (lambda x: x) if self.tag_name == 'None' else (lambda y: getattr(y, self.tag_name, None))
        min_x = min_y = 1e6
        max_x = max_y = 0
        #
        # Scan through the space finding the empty spots
        for x in range(world.width):
            for y in range(world.height):
                cell = world.getCell(y, x)
                if getter(cell) != self.tag_value:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        #
        self.log.info('Bounds of world are (%d, %d) to (%d, %d)' % (min_x, min_y, max_x, max_y))
        #
        # Now create a smaller world
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        new = world.__class__(width, height)
        #
        # Write the old cells to the new world
        for x in range(width):
            for y in range(height):
                new.setCell(y, x, world.getCell(y + min_y, x + min_x))
        #
        # And replace
        return new