"""Evolve rooms"""

import random
import copy

from terrain import common
from terrain import loggable

import main
from terrain import evolution


class Door(object):
    """Represents a door"""

    def __init__(self, row, col):
        """Initialise the door"""
        self.row = row
        self.col = col
        self.active = True
        self.direction = None


class Room(loggable.Loggable):
    """Represents a room"""

    place_doors = True

    def __init__(self, name, room_type, configuration):
        """Initialise the room"""
        self.addLogger()
        #
        self.name = name
        self.room_type = room_type
        self.rows = []
        self.doors = []
        for row_idx, row in enumerate(configuration):
            self.rows.append(row)
            for col_idx, col in enumerate(row):
                if col == 'D':
                    self.doors.append(Door(row_idx, col_idx))
            if len(self.rows[-1]) != len(self.rows[0]):
                raise ValueError('Row %d of room %s has wrong number of items' % (row_idx, name))
        #
        # Determine door directions
        for door_id, door in enumerate(self.doors):
            if door.row == 0:
                door.direction = 'n'
            elif door.row == len(self.rows) - 1:
                door.direction = 's'
            elif door.col == 0:
                door.direction = 'w'
            elif door.col == len(self.rows[0]) - 1:
                door.direction = 'e'
            elif self.rows[door.row - 1][door.col] == '-':
                door.direction = 'n'
            elif self.rows[door.row + 1][door.col] == '-':
                door.direction = 's'
            elif self.rows[door.row][door.col - 1] == '-':
                door.direction = 'w'
            elif self.rows[door.row][door.col + 1] == '-':
                door.direction = 'e'
            else:
                raise ValueError('Unable to determine direction of door %d' % door_id)
        #
        self.log.debug('Room %s has %d doors' % (self.name, len(self.doors)))

    def getLinkedRoomRotation(self, other_room, my_door_id, other_door_id, my_rotation):
        """Return the rotation needed for another room to connect to a door when I am rotated"""
        difference = (180 + self._getRotationAngle(self.doors[my_door_id].direction) +
                      self._getRotationAngle(my_rotation) -
                      self._getRotationAngle(other_room.doors[other_door_id].direction))
        #
        if difference >= 360:
            difference -= 360
        #
        return {
            0: 'n',
            90: 'e',
            180: 's',
            -90: 'w',
            270: 'w',
            360: 'n',
        }[difference]

    def getLinkedRoomOffset(self, other_room, my_door_id, other_door_id, my_rotation):
        """Return the offset of a room origin when linking the two rooms"""
        other_rotation = self.getLinkedRoomRotation(other_room, my_door_id, other_door_id, my_rotation)
        r1, c1 = self.getDoorOffset(my_door_id, my_rotation)
        r2, c2 = other_room.getDoorOffset(other_door_id, other_rotation)
        return r1 - r2, c1 - c2

    def _getRotationAngle(self, rotation):
        """Return the rotation angle"""
        return 'nesw'.find(rotation) * 90

    def _getRowsWithRotation(self, rotation):
        """Return the rows as they will appear when we are rotated"""
        #
        # Find the actual rotation
        rows = self.rows
        if rotation == 's':
            rows = [row[::-1] for row in rows[::-1]]
        elif rotation == 'e':
            rows = [''.join(reversed(i)) for i in zip(*rows)]
        elif rotation == 'w':
            rows = reversed([''.join(i) for i in zip(*rows)])
        return rows

    def willFitAt(self, world, rotation, y, x):
        """Return True if the room will fit in a place - world is left in an undefined state"""
        actual_doors = [True] * len(self.doors)
        try:
            self.renderToWorld(world, rotation, y, x, actual_doors)
        except evolution.BadOrganism:
            return False
        else:
            return True

    def renderToWorld(self, world, rotation, y, x, actual_doors):
        """Render this room to the world"""
        rows = list(self._getRowsWithRotation(rotation))
        #
        # In range?
        if not world.isInRange(y + len(rows), x + len(rows[0])) or not world.isInRange(y, x):
            raise evolution.BadOrganism('Room "%s" would not fit at (%d, %d) - no room' % (self.name, y, x))
        #
        # Put in world
        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(row):
                cell = world.getCell(y + row_idx, x + col_idx)
                #
                # Check we can write here
                if cell != '-' and col != '-':
                    if not ((cell == 'W' and col == 'W') or (cell == 'D' and col == 'D')):
                        raise evolution.BadOrganism('Room "%s" would not fit at (%d, %d) - overlaps' % (self.name, y, x))
                if col not in '-.D':
                    world.setCell(y + row_idx, x + col_idx, col)
                elif col == '.':
                    world.setCell(y + row_idx, x + col_idx, 'F')
        #
        # Now put the doors on there where they exist.
        # If we do not have a door then we fill empty
        # space with a wall but if there is a door there
        # already then we leave it in place because it is likely
        # an entrance to this room
        if self.place_doors:
            for idx, exists in enumerate(actual_doors):
                row, col = self.getDoorOffset(idx, rotation)
                cell = world.getCell(y + row, x + col)
                if exists:
                    world.setCell(y + row, x + col, 'D')
                elif cell != 'D':
                    world.setCell(y + row, x + col, 'W')

    def getDoorOffset(self, door_num, rotation):
        """Return the row, col offset of a door"""
        door = self.doors[door_num]
        row, col = door.row, door.col
        #
        # Rotation
        if rotation == 's':
            row = len(self.rows) - 1 - row
            col = len(self.rows[0]) - 1 - col
        elif rotation == 'e':
            row, col = col, len(self.rows) - 1 - row
        elif rotation == 'w':
            row, col = len(self.rows[0]) - 1 - col, row
        #
        return row, col


class ActualRoom(list):
    """An actualized room"""

    def __init__(self, data=None, depth=None):
        """Initialise the room"""
        if data:
            super(ActualRoom, self).__init__(data)
            self.depth = depth


class EvolutionBased(main.Builder):
    """Evolves a set of rooms"""

    reports_progress = True

    def __init__(self, configuration):
        """Initialise the builder"""
        super(EvolutionBased, self).__init__(configuration)
        #
        # Find the rooms
        self.rooms = {}
        for room_configuration in configuration.find('rooms').findall('room'):
            room = Room(
                common.getStrAttr(room_configuration, 'name'),
                common.getStrAttr(room_configuration, 'type'),
                [line.strip() for line in room_configuration.text.strip().splitlines()]
            )
            self.rooms[room.name] = room
        #
        # Get properties
        self.initial_pool_size = common.getInt(configuration, 'initialPoolSize')
        self.tournament_size = common.getInt(configuration, 'tournamentSize')
        self.max_iterations = common.getInt(configuration, 'maxIterations')
        #
        # Tuning parameters
        RoomController.target_num_rooms = common.getFloat(configuration, 'targetRooms')
        RoomController.missed_corridor_penalty = common.getFloat(configuration, 'missedCorridorPenalty')
        RoomController.corridor_to_room_penalty = common.getFloat(configuration, 'corridorToRoomPenalty')
        RoomController.exit_longest_path_multiplier = common.getFloat(configuration, 'exitLongestPath')
        RoomController.missed_door_penalty = common.getFloat(configuration, 'missedDoorPenalty')
        #
        RoomController.target_room_types['event'] = common.getFloat(configuration, 'numEventRooms')
        RoomController.target_room_types['treasure'] = common.getFloat(configuration, 'numTreasureRooms')
        RoomController.target_room_types['corridor'] = common.getFloat(configuration, 'numCorridors')

    def buildOnWorld(self, world):
        """Build on the world"""
        dna = RoomDNA(
            ['start', 'n', None, [
            ]]
        )
        #
        Room.place_doors = False
        #
        new = dna
        controller = RoomController(self.rooms, self)
        controller.setDNA(RoomDNA)
        controller.createInitialPool(self.initial_pool_size)
        controller.performTournament(self.tournament_size, self.max_iterations, world, self.rooms)
        #
        Room.place_doors = True
        #
        #self.log.info('Score for the result is %s' % controller.scoreFitness(new, self.rooms))
        for item in controller.getPool():
            self.log.debug('Ranking for item is %s' % item.score)

        world.updateFrom(controller.getPool()[0].makeOrganism(world, self.rooms))
        return world


class RoomDNA(evolution.DNA):
    """DNA for creating a set of rooms

    Chromosome is
        [<room name>, <rotation nesw>, <door id (not used for root)>,
            List of door connections
            [
                [<room name>, <rotation (not used for non-root)>, <door id>],
                [<room name>, <rotation (not used for non-root)>, <door id>],
                [<room name>, <rotation (not used for non-root)>, <door id>],
            ]
        ]

    If room name is NULL then the door is blocked and not used

    """

    grow_nodes = 3
    trim_nodes = 1

    @classmethod
    def getRandomInitialChromosomes(cls):
        """Return some random chromosomes"""
        return ['square', 'n', None, []]

    def makeOrganism(self, world, rooms):
        """Make the world from this DNA"""
        new_world = world.getCopy()
        row, col = new_world.width / 2, new_world.height / 2
        self.makeRoom(new_world, rooms, row, col, *self.chromosomes)
        new_world.dna = self
        return new_world

    def makeRoom(self, world, rooms, row, col, room_name, rotation, door_id, doors, include_sub_rooms=True):
        """Make a particular room"""
        room = rooms[room_name]
        actual_doors = [item[0] is not None for item in doors]
        #
        # Pad out door flags if they were not all specified
        if len(actual_doors) < len(room.doors):
            actual_doors += [False] * (len(room.doors) - len(actual_doors))
        #
        room.renderToWorld(world, rotation, row, col, actual_doors)
        #
        # Render all the sub rooms
        if include_sub_rooms:
            for door_id, (new_room_name, new_rotation, new_door_id, new_doors) in enumerate(doors):
                if new_room_name is not None:
                    actual_new_rotation = room.getLinkedRoomRotation(rooms[new_room_name], door_id, new_door_id, rotation)
                    dr, dc = room.getLinkedRoomOffset(rooms[new_room_name], door_id, new_door_id, rotation)
                    self.makeRoom(world, rooms, row + dr, col + dc,
                                  new_room_name, actual_new_rotation, new_door_id, new_doors)

    def findAvailableDoorSlots(self, rooms):
        """Return all the available empty slots where we can place new rooms

        This means where there is a door missing. A None doorway is not missing
        and does not appear as a slot

        """
        return self._findAvailableSlotsIn(rooms, *self.chromosomes)

    def _findAvailableSlotsIn(self, rooms, room_name, rotation, door_id, doors):
        """Return the available room slots"""
        results = []
        #
        # Do we have empty door slots?
        if room_name is not None:
            actual_doors = len(rooms[room_name].doors)
            if actual_doors != len(doors):
                results.append(doors)
        #
        # Now look for empty slots in the rooms attached to us
        for sub_door in doors:
            results.extend(self._findAvailableSlotsIn(rooms, *sub_door))
        #
        return results

    def findRooms(self, item=None):
        """Return all the rooms"""
        if item is None:
            item = self.chromosomes
        rooms = [item]
        for door in item[3]:
            rooms.extend(self.findRooms(door))
        return rooms

    def findRoomsAndDepths(self, item=None, depth=0):
        """Return all the rooms"""
        if item is None:
            item = self.chromosomes
        rooms = [(item, depth)]
        for door in item[3]:
            rooms.extend(self.findRoomsAndDepths(door, depth=depth + 1))
        return rooms

    @evolution.mutator(0.5)
    def mutateGrow(self, world, rooms):
        """Mutate the DNA by growing new rooms at random points in the tree"""
        #
        # Get all available door slots
        new = self.getCopy()
        #
        # Add to required number of slots
        for _ in range(self.grow_nodes):
            possible_slots = new.findAvailableDoorSlots(rooms)
            if not possible_slots:
                raise evolution.CannotMutate('Cannot mutate by growing - no empty slots')
            #
            self._addToSlot(world, rooms, new, random.choice(possible_slots))
        #
        return new

    def _addToSlot(self, world, rooms, new, slot):
        """Try to add a room to a slot"""
        #
        # Find a room and a door
        room = random.choice(rooms.values())
        possible_doors = list(enumerate(room.doors))
        random.shuffle(possible_doors)
        #
        # Try to find a door
        for door_idx, door in possible_doors:
            slot.append([room.name, None, door_idx, []])
            #
            # Make sure this is a valid arrangement
            world = world.getCopy()
            try:
                _ = new.makeOrganism(world, rooms)
            except evolution.BadOrganism:
                # Ok, not good so remove this one and carry on looking
                slot.pop()
            else:
                return
        #
        # If we got to here then there are no rooms that will fit so blank off this ending
        slot.append(self.getNullRoom())

    def getNullRoom(self):
        """Return the null room"""
        return [None, 'n', None, []]

    @evolution.mutator(0.5)
    def mutateTrim(self, world, rooms):
        """Mutate the DNA by trimming a room"""
        new = self.getCopy()
        for _ in range(self.trim_nodes):
            rooms = new.findRooms()[1:]
            if rooms:
                room = random.choice(rooms)
                room[:] = new.getNullRoom()
        return new

    @evolution.mutator(0.5)
    def mutateChange(self, world, rooms):
        """Mutate the DNA by changing a room"""
        new = self.getCopy()
        #
        # Get all rooms and choose one to change
        all_rooms = new.findRooms()
        if not all_rooms:
            raise evolution.CannotMutate('No rooms available to change')
        changer = random.choice(all_rooms)
        #
        # Find new name
        room_names = rooms.keys()
        if changer[0] is not None:
            room_names.remove(changer[0])
        #
        # Switch name
        if room_names:
            new_name = random.choice(room_names)
            #
            # Truncate doors
            actual_door = rooms[new_name]
            changer[0] = new_name
            changer[3] = []
            #
            # Try to find a door that will work here
            available_doors = range(len(actual_door.doors))
            random.shuffle(available_doors)
            for door_number in available_doors:
                changer[2] = door_number
                #
                # See if this worked - if not then bail out
                try:
                    _ = new.makeOrganism(world, rooms)
                except evolution.BadOrganism:
                    pass
                else:
                    # OK - looks good
                    break
            else:
                # If we got here then we tried all the doors and none were working
                raise evolution.CannotMutate('Tried changing room but it didn\'t render')
        #
        return new


class RoomController(evolution.Controller):
    """A controller for judging controlling the evolution process"""

    target_num_rooms = 30
    missed_corridor_penalty = 2
    corridor_to_room_penalty = 0.5
    missed_door_penalty = .2
    exit_longest_path_multiplier = 1.5
    target_room_types = {
        'start': 1,
        'event': 2,
        'treasure': 2,
        'exit': 1,
        'corridor': 5,
    }
    target_depths = {
        'event': 10,
        'treasure': 4,
    }

    def __init__(self, rooms, progress_reporter=None):
        """Initialise the controller"""
        super(RoomController, self).__init__()
        #
        self.rooms = rooms
        self.progress_reporter = progress_reporter

    def scoreFitness(self, item):
        """Score the fitness for an item"""
        all_rooms = item.dna.findRoomsAndDepths()
        #
        return sum([
            self.targetRoomScore(all_rooms),
            self.targetRoomTypes(all_rooms, self.rooms) * 10,
            self.targetDepths(all_rooms, self.rooms) * 2,
            self.properCorridors(all_rooms, self.rooms),
            self.properDoors(all_rooms, self.rooms),
            self.exitIsLongestPath(all_rooms, self.rooms),
        ])

    def targetRoomScore(self, rooms):
        """Return the score based on the room totals"""
        actual_rooms = [room for room, _ in rooms if room[0] is not None]
        return -abs(self.target_num_rooms - len(actual_rooms))

    def targetRoomTypes(self, all_rooms, rooms):
        """Return the score based on the room totals"""
        scores = {}
        scores.update(self.target_room_types)
        for room, _ in all_rooms:
            name = room[0]
            if name is not None:
                actual_room = rooms[name]
                if actual_room.room_type in scores:
                    scores[actual_room.room_type] -= 1
        #
        return -sum(map(abs, scores.values()))

    def targetDepths(self, all_rooms, rooms):
        """Return the score based on the room depths"""
        score = 0
        for room, depth in all_rooms:
            name = room[0]
            if name is not None:
                actual_room = rooms[name]
                if actual_room.room_type in self.target_depths:
                    score += -abs(depth - self.target_depths[actual_room.room_type])
        #
        return score

    def properCorridors(self, all_rooms, rooms):
        """Return score based on whether corridors are fully working"""
        penalty = 0
        for room, _ in all_rooms:
            name = room[0]
            doors = len(room[3])
            if name is not None:
                actual_room = rooms[name]
                #
                # Corridors should have all doors occupied
                if actual_room.room_type == 'corridor' and doors < len(actual_room.doors):
                    penalty += self.missed_corridor_penalty
                #
                # All doors should lead to rooms that are not corridors
                for through_door_name, _, _, _ in room[3]:
                    if through_door_name is None:
                        penalty += self.corridor_to_room_penalty
                    else:
                        through_door_room = rooms[through_door_name]
                        if through_door_room.room_type == 'corridor':
                            penalty += self.corridor_to_room_penalty
        #
        return -penalty

    def properDoors(self, all_rooms, rooms):
        """Return score based on whether all doors are being used or not"""
        penalty = 0
        for room, _ in all_rooms:
            name = room[0]
            if name is None:
                penalty += self.missed_door_penalty
        #
        return -penalty

    def exitIsLongestPath(self, all_rooms, rooms):
        """Return score based on whether exit is on the longest path"""
        exits = []
        for room, depth in all_rooms:
            if room[0] is not None and rooms[room[0]].room_type == 'exit':
                exits.append((room, depth))
        longest_path = max(depth for _, depth in all_rooms)
        if exits:
            exist_dist = [abs(longest_path - depth) for _, depth in exits]
            return -max(exist_dist) * self.exit_longest_path_multiplier
        else:
            return 0

    def getCopy(self):
        """Return a copy of ourself"""
        return self.__class__(self.rooms)

    def reportProgress(self, percent, best):
        """Report progress back"""
        if self.progress_reporter:
            self.progress_reporter._progress_percent = percent
            self.progress_reporter._progress_world = best
        return not self.progress_reporter._should_stop