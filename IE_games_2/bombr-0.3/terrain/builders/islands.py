"""Builders that help with generating island type environments"""

import random
import math

import serge.blocks.textgenerator
from terrain import common

import main


class IslandFinder(main.Builder):
    """Finds and creates islands from a terrain that has been biome tagged

    The builder needs to be told what are sea biomes

    """

    def __init__(self, configuration):
        """Initialise the builder"""
        super(IslandFinder, self).__init__(configuration)
        #
        self.sea_tags = common.getString(configuration, 'seaTags')
        self.smallest_island = common.getInt(configuration, 'smallestIsland')

    def buildOnWorld(self, world):
        """Find all the islands

        The algorithm is that you find all the land cells. Then
        you look for any cell that is next to another in any of
        the adjacent cells. If they are adjacent then they are
        part of the same island.

        Coastline is also identified. A coastal cell is a land cell that
        has at least on neighbouring cell that is water.

        """
        islands = world.islands = {}
        land_cells = []
        sea_tags = [item.strip() for item in self.sea_tags.split(',')]
        #
        for cell in world.iterCells():
            cell.island_number = None
            cell.is_coastline = False
            if cell.biome not in sea_tags:
                land_cells.append(cell)
                cell.is_land = True
            else:
                cell.is_land = False
        self.log.debug('Found %d land cells' % len(land_cells))
        #
        visited = set()
        island_counter = 0
        #
        while land_cells:
            #
            # Get the first land cell to process
            cell = land_cells.pop()
            visited.add(cell)
            #
            # Create an island if we need to
            if cell.island_number is None:
                cell.island_number = island_counter
                islands[island_counter] = [cell]
                island_counter += 1
            #
            # Now find all the connected cells
            for dx in (-1, 0, +1):
                for dy in (-1, 0, +1):
                    if dx != 0 or dy != 0:
                        new_row = cell.row + dy
                        new_col = cell.col + dx
                        try:
                            new_cell = world.getCell(new_row, new_col)
                        except IndexError:
                            # Not in the world
                            continue
                        #
                        # Is the connected cell location actually a land cell
                        if new_cell.is_land:
                            if not new_cell in visited:
                                #
                                # Add to the island and make this be processed next
                                new_cell.island_number = cell.island_number
                                islands[cell.island_number].append(new_cell)
                                land_cells.remove(new_cell)
                                land_cells.append(new_cell)
                        else:
                            cell.is_coastline = True
        #
        # Remove islands that are too small
        filtered = 0
        for key in list(world.islands.keys()):
            if len(world.islands[key]) < self.smallest_island:
                for cell in world.islands[key]:
                    cell.island_number = None
                del(world.islands[key])
                filtered += 1
        #
        self.log.debug('Found %d islands. Removed %d that were too small.' % (
            len(world.islands), filtered))
        #
        return world


class PortCreator(main.Builder):
    """Creates ports on the islands

    Ports are created based on the amount of coastline of the island.
    There is an average distance between ports which is used to
    determine the number of ports. They are then created at
    random locations.

    """

    def __init__(self, configuration):
        """Initialise the builder"""
        super(PortCreator, self).__init__(configuration)
        #
        # Basic properties of the port
        self.coast_per_port = common.getInt(configuration, 'averageCoastLinePerPort')
        self.island_must_have_port = common.getTrue(configuration, 'islandMustHavePort')
        self.min_port_separation = common.getInt(configuration, 'minimumPortSeparation')
        self.port_location_attempts = common.getInt(configuration, 'portLocationAttempts', 5)
        self.max_name_length = common.getInt(configuration, 'maxPortNameLength', 9)
        #
        # Resource properties
        properties = configuration.findall('resources/resourceProperties/*')
        root = configuration.find('resources/resourceProperties')
        self.property_ranges = dict(
            (element.tag, common.getFloatTuple(root, element.tag)) for element in properties
        )
        #
        self.name_generator = serge.blocks.textgenerator.MarkovNameGenerator(
            serge.blocks.textgenerator.EUROPE
        )
        #
        # Resource types
        self.resource_types = [
            common.getStrAttr(element, 'name')
            for element in configuration.findall('resources/resourceTypes/resource')
        ]

    def buildOnWorld(self, world):
        """Build the ports"""
        #
        for cell in world.iterCells():
            cell.is_port = False
        #
        world.ports = []
        num_skipped = 0
        for island in world.islands.values():
            #
            # Find all the coastline
            coastal_cells = [cell for cell in island if cell.is_coastline]
            #
            # Determine the number of ports to create
            number_ports = int(len(coastal_cells) / self.coast_per_port)
            if self.island_must_have_port:
                number_ports = max(1, number_ports)
            #
            # Now create the ports
            for port in range(number_ports):
                for _ in range(self.port_location_attempts):
                    port_cell = random.choice(coastal_cells)
                    #
                    # Make sure the cell is not too close to others
                    for other_cell in world.ports:
                        dist = abs(port_cell.row - other_cell.row) + abs(port_cell.col - other_cell.col)
                        if dist < self.min_port_separation:
                            break
                    else:
                        #
                        # Ok, port was in a good location
                        coastal_cells.remove(port_cell)
                        port_cell.is_port = True
                        world.ports.append(port_cell)
                        break
                else:
                    num_skipped += 1
        #
        # Create the properties of the ports
        for port in world.ports:
            self.addPortProperties(port)
        #
        self.log.info('Created %d ports. %d not created as would have violated constraints' % (
            len(world.ports), num_skipped))
        #
        return world

    def addPortProperties(self, port):
        """Add some properties to the port"""
        resources = {}
        for name in self.resource_types:
            resources[name] = {}
            for prop, rge in self.property_ranges.iteritems():
                if rge[0] == rge[1]:
                    value = rge[0]
                else:
                    value = random.uniform(*rge)
                resources[name][prop.replace('Range', '')] = value
        #
        port.properties = PortProperties(
            name=self.name_generator.getName(self.max_name_length),
            resources=resources,
        )


class PortProperties(object):
    """Holds properties of a port"""

    def __init__(self, name, resources):
        """Initialise the port"""
        self.name = name
        self.resources = resources