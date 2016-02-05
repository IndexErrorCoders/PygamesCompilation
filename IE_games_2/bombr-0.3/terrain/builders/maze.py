"""Builder to build a maze"""

import random

from terrain import common
from terrain import loggable

import main


class MazeBuilder(main.Builder):
    """Builds a maze"""

    def __init__(self, configuration):
        """Initialise the builder"""
        super(MazeBuilder, self).__init__(configuration)
        #
        self.tag_name = common.getString(configuration, 'attributeName')
        self.wall = common.getString(configuration, 'wallValue')
        self.floor = common.getString(configuration, 'floorValue')
        self.door = common.getString(configuration, 'doorValue')
        self.entrances = common.getInt(configuration, 'numberEntrances')

    def buildOnWorld(self, world):
        """Build the maze"""
        #
        # Put all cells in a queue
        cells = []
        for row in range(1, world.height, 2):
            for col in range(1, world.width, 2):
                cell = world.getCell(row, col)
                setattr(cell, self.tag_name, self.floor)
                cells.append(cell)
        random.shuffle(cells)
        #
        # Now dig the maze
        start = random.choice(cells)
        self.digMaze([start], [], world)
        self.findEntrances(world)
        #
        return world

    def digMaze(self, cells, visited, world):
        """Recursively dig a maze"""
        while cells:
            current_cell = cells.pop()
            visited.append(current_cell)
            destinations = []
            for d_row, d_col in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                #
                # Positions of wall and new cell
                new_row = current_cell.row + d_row * 2
                new_col = current_cell.col + d_col * 2
                wall_row = current_cell.row + d_row
                wall_col = current_cell.col + d_col
                #
                # Inside the world?
                if new_col >= 1 and new_row >= 1 and new_col < world.width -1 and new_row < world.width - 1:
                    wall = world.getCell(wall_row, wall_col)
                    destination = world.getCell(new_row, new_col)
                    #
                    # Destination is not already a tunnel
                    if destination not in visited:
                        destinations.append((wall, destination))
            #
            # Anywhere to go?
            if not destinations:
                continue
            #
            wall, destination = random.choice(destinations)
            if len(destinations) > 1:
                cells.append(current_cell)
            #
            # Dig tunnel
            setattr(wall, self.tag_name, self.floor)
            #
            # Move to the new cell
            cells.append(destination)

    def findEntrances(self, world):
        """Find two entrances"""
        #
        # Find all valid positions
        valid_positions = []
        for row in range(1, world.height, 2):
            valid_positions.append(world.getCell(row, 0))
            valid_positions.append(world.getCell(row, world.width - 1))
        for col in range(1, world.width, 2):
            valid_positions.append(world.getCell(0, col))
            valid_positions.append(world.getCell(world.height - 1, col))
        #
        # Choose locations
        for entrances in range(self.entrances):
            cell = random.choice(valid_positions)
            setattr(cell, self.tag_name, self.door)
