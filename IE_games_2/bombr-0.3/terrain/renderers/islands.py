"""Renderer for an island based terrain"""

import pygame
import random

import main
from .. import common


class IslandRenderer(main.PygameRenderer):
    """Renders islands"""

    def __init__(self, configuration):
        """Initialise the renderer"""
        super(IslandRenderer, self).__init__(configuration)
        #
        self.coastal_colour = common.getTuple(configuration, "coastalColour")
        self.port_colour = common.getTuple(configuration, "portColour")

    def renderToFile(self, filename, world):
        """Render the islands to a file"""
        self.createSurface(world)
        #
        # Create colours
        self.colours = {None: (0, 0, 0)}
        for idx, island_number in enumerate(world.islands):
            self.colours[island_number] = (
                random.randrange(50, 255),
                random.randrange(50, 255),
                random.randrange(50, 255)
            )
        #
        for row in range(world.height):
            for col in range(world.width):
                #
                # Calculate the location
                x = col * self.cell_width
                y = row * self.cell_height
                cell = world.getCell(row, col)
                colour = self.colours[cell.island_number]
                if cell.island_number is not None and cell.is_coastline:
                    colour = self.coastal_colour
                if cell.is_port:
                    colour = self.port_colour
                #
                pygame.draw.rect(self.surface, colour, (x, y, self.cell_width, self.cell_height))
        #
        super(IslandRenderer, self).renderToFile(filename, world)


class TiledIslandRenderer(main.TiledRenderer):
    """Render island information to a tiled-like file"""

    def __init__(self, configuration):
        """Initialise the renderer"""
        super(TiledIslandRenderer, self).__init__(configuration)
        #

    def getOtherLines(self, world):
        """Return the lines describing the island features"""
        lines = ['\t<ports>']
        for port in world.ports:
            lines.extend([
                '\t\t<port row="%d" col="%d">' % (port.row, port.col),
                '\t\t\t<name>%s</name>' % port.properties.name,
                '\t\t\t<resources>',
            ])
            #
            # All the resources
            for resource, params in port.properties.resources.iteritems():
                lines.append('\t\t\t\t<%s' % resource)
                for name, value in params.iteritems():
                    lines.append('\t\t\t\t\t%s="%f"' % (name, value))
                lines.append('\t\t\t\t/>')
            #
            lines.extend([
                '\t\t\t</resources>',
                '\t\t</port>',
            ])
        lines.append('\t</ports>')
        return lines