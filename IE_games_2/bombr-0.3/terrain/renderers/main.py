"""Things that render output"""

import os
import pygame

from terrain import loggable
from terrain import common


class Renderer(loggable.Loggable):
    """A general renderer"""

    def __init__(self, configuration):
        """Initialise the renderer"""
        self.addLogger()
        self.configuration = configuration
        self.name = common.getStrAttr(configuration, 'name')
        self.confirmation_message = common.getStrAttr(configuration, 'confirmationMessage', '')
        self.log.debug('Renderer created')

    def renderToFile(self, filename, world):
        """Do our stuff"""


class PygameRenderer(Renderer):
    """Uses pygame to render a grid"""

    def __init__(self, configuration):
        """Initialise the renderer"""
        super(PygameRenderer, self).__init__(configuration)
        #
        self.cell_width = common.getInt(configuration, 'cellWidth')
        self.cell_height = common.getInt(configuration, 'cellHeight')
        self.surface = None

    def createSurface(self, world):
        """Create the underlying surface"""
        self.surface = pygame.Surface((world.width * self.cell_width, world.height * self.cell_height))

    def renderToFile(self, filename, world):
        """Render the output to a file"""
        actual_filename = '%s.png' % os.path.splitext(filename)[0]
        self.log.debug('Writing rendered output to "%s"' % actual_filename)
        pygame.image.save(self.surface, actual_filename)


class HeightRenderer(PygameRenderer):
    """Render a height field"""

    def __init__(self, configuration):
        """Initialise the renderer"""
        super(HeightRenderer, self).__init__(configuration)
        #
        self.base_height = common.getInt(configuration, 'baseHeight')
        self.auto_scale = common.getInt(configuration, 'autoScale')
        if not self.auto_scale:
            self.max_height = common.getInt(configuration, 'maxHeight')
            self.min_height = common.getInt(configuration, 'minHeight')
        self.lower_colour = common.getTuple(configuration, 'lowerColour')
        self.higher_colour = common.getTuple(configuration, 'higherColour')

    def renderToFile(self, filename, world):
        """Render the output to a file"""
        self.createSurface(world)
        #
        # Check for scaling
        if self.auto_scale:
            self.max_height = max(cell.rock_depth for cell in world.iterCells())
            self.min_height = min(cell.rock_depth for cell in world.iterCells())
        #
        for row in range(world.width):
            for col in range(world.height):
                #
                # Calculate the location
                x = col * self.cell_width
                y = row * self.cell_height
                cell = world.getCell(row, col)
                #
                # Get the colour
                if cell.rock_depth >= self.base_height:
                    fraction = min(1.0, (cell.rock_depth - self.base_height) / (self.max_height - self.base_height))
                    base_colour = self.higher_colour
                else:
                    fraction = min(1.0, (cell.rock_depth - self.base_height) / (self.min_height - self.base_height))
                    base_colour = self.lower_colour
                #
                colour = tuple(fraction * c for c in base_colour)
                pygame.draw.rect(self.surface, colour, (x, y, self.cell_width, self.cell_height))
        #
        super(HeightRenderer, self).renderToFile(filename, world)


class ColourEntry(object):
    """Details about a colour"""

    def __init__(self, values, index):
        """Initialise the entry"""
        self.values = values
        self.index = index


class StringRenderer(PygameRenderer):
    """Render biomes as different colours"""

    def __init__(self, configuration):
        """Initialise the renderer"""
        super(StringRenderer, self).__init__(configuration)
        #
        self.default_value = common.getString(configuration, 'defaultValue')
        self.values = {}
        for index, value in enumerate(configuration.find('attributeValues').findall('attributeValue')):
            self.values[common.getStrAttr(value, 'tag')] = ColourEntry(
                common.getTupleAttr(value, 'colour'),
                common.getIntAttr(value, 'index', index + 1)
            )

    def renderToFile(self, filename, world):
        """Render the output to a file"""
        self.createSurface(world)
        #
        for row in range(world.height):
            for col in range(world.width):
                #
                # Calculate the location
                x = col * self.cell_width
                y = row * self.cell_height
                cell_value = self.getCellValue(world.getCell(row, col))
                #
                colour = self.values[cell_value]
                pygame.draw.rect(self.surface, colour.values, (x, y, self.cell_width, self.cell_height))
        #
        super(StringRenderer, self).renderToFile(filename, world)

    def getCellValue(self, cell):
        """Return the value from a cell"""
        return cell


class TagNameRenderer(StringRenderer):
    """Render biomes as different colours"""

    def __init__(self, configuration):
        """Initialise the renderer"""
        super(TagNameRenderer, self).__init__(configuration)
        #
        self.tag_name = common.getString(configuration, 'tagName')

    def getCellValue(self, cell):
        """Return the value from a cell"""
        return getattr(cell, self.tag_name, self.default_value)


class TiledRenderer(TagNameRenderer):
    """Render to a tiled file"""

    def __init__(self, configuration):
        """Initialise the renderer"""
        super(TiledRenderer, self).__init__(configuration)
        #
        self.tileset_filename = common.getString(configuration, 'tilesetFilename')
        self.layer_name = common.getString(configuration, 'layerName', 'Render')

    def renderToFile(self, filename, world):
        """Render to the tiled file"""
        #
        # Preamble
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<map version="1.0" orientation="orthogonal" width="%d" height="%d" tilewidth="%d" tileheight="%d">' % (
                world.width, world.height, self.cell_width, self.cell_height
            ),
        ]
        lines.extend(self.getTileset())
        lines.extend(self.getMapLines(world))
        lines.extend(self.getOtherLines(world))
        #
        # Close out tags
        lines.extend([
            '</map>',
        ])
        #
        # Render the tiled file
        actual_filename = '%s.xml' % os.path.splitext(filename)[0]
        with file(actual_filename, 'w') as f:
            f.write('\n'.join(lines))
        #
        # Now render the tile-set squares to a surface
        surface = pygame.Surface((self.cell_width, self.cell_height * len(self.values)))
        for i in range(len(self.values)):
            colour = self.values[self.values.keys()[i]]
            x = 0
            y = i * self.cell_height
            pygame.draw.rect(surface, colour.values, (x, y, self.cell_width, self.cell_height))
        #
        # And save the resulting file
        base_dir = os.path.split(filename)[0]
        pygame.image.save(surface, os.path.join(base_dir, self.tileset_filename))

    def getMapLines(self, world):
        """Get lines of text to add to the file representing the map"""
        lines = [
            '\t<layer name="%s" width="%d" height="%d">' % (
                self.layer_name, world.width, world.height
            ),
            '\t\t<properties>',
            '\t\t\t<property name="type" value="visual"/>',
            '\t\t</properties>',
            '\t\t<data encoding="csv">',
        ]
        #
        # Put the items in there
        for row in range(world.height):
            parts = []
            for col in range(world.width):
                cell = world.getCell(row, col)
                value = getattr(cell, self.tag_name, self.default_value) if self.tag_name != 'None' else cell
                index = self.values[value].index
                parts.append(index)
            lines.append('\t\t\t\t%s' % (','.join(map(str, parts))))
            #
            # Tiled expects a trailing comma except on the last line
            if row != world.height - 1:
                lines[-1] += ','
        lines.extend([
            '\t\t</data>',
            '\t</layer>',
        ])
        #
        return lines

    def getTileset(self):
        """Return the lines for the tileset spec"""
        lines = [
            '\t<tileset firstgid="1" name="tiles" tilewidth="%d" tileheight="%d">' % (
                self.cell_width, self.cell_height
            ),
            '\t\t<image source="%s" width="%d" height="%d"/>' % (
                self.tileset_filename,
                self.cell_width,
                self.cell_height * len(self.values),
            ),
            '\t</tileset>',
        ]
        return lines

    def getOtherLines(self, world):
        """Return any other extra lines for the file

        Override  this method to specialise the file"""
        return []