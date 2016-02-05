"""Implements an interface to Tiled files"""

import os
import copy
from xml.etree.ElementTree import ElementTree

import serge.common
import serge.visual
import serge.geometry


class BadTiledFile(Exception): """The tiled file could not be found"""
class NotFound(Exception): """The object was not found"""
class BadLayer(Exception): """The layer specification was invalid"""


LAYER_TYPES = (
    'visual',       # Sprites
    'adhoc-visual', # Object layer with sprite tiles placed on non-orthoganol grid
    'movement',     # Whether actors can move on this tile
    'visibility',   # Whether actors can see through this tile
    'object',       # Objects 
    'resistance',   # Resistance to movement
)


class TileMap(serge.common.Loggable):
    """A representation of a 2d map of tiles"""
    
    def __init__(self):
        """Initialise the Tiled"""
        self.addLogger()
        self.layers = []
        TileMap.resetLayerTypes()

    @classmethod    
    def resetLayerTypes(cls):
        """Reset the layer types to default"""
        cls.layer_types = list(LAYER_TYPES)

    @classmethod    
    def addLayerTypes(cls, layer_types):
        """Add more layer types"""
        cls.layer_types.extend(layer_types)

    def addLayer(self, layer):
        """Add a layer"""
        self.layers.append(layer)
        return layer
        
    def getLayers(self):
        """Return the layers of tiles"""
        return self.layers

    def getLayersByType(self, type_name):
        """Return the layer with a given type"""
        return [layer for layer in self.getLayers() if layer.layer_type == type_name]

    def getLayerByType(self, type_name):
        """Return the layer with a given type"""
        layers = self.getLayersByType(type_name)
        if not layers:
            raise NotFound('A layer with type "%s" was not found' % type_name)
        elif len(layers) > 1:
            raise BadLayer('Multiple layers with type "%s" were found' % type_name)
        else:
            return layers[0]
            
    def getLayer(self, name):
        """return the tile with a certain name"""
        for layer in self.getLayers():
            if layer.name == name:
                return layer
        raise NotFound('A layer named "%s" was not found' % name)

    def getTypeFrom(self, name, properties):
        """Return the layer type, checking validity which we do it"""
        try:
            layer_type = properties['type']
        except KeyError:
            raise BadLayer('Layer "%s" in file "%s" does not have a type property. Should be one of %s' % 
                (name, self.filename, LAYER_TYPES))
        #
        if layer_type in self.layer_types:
            return layer_type
        else:
            raise BadLayer('Layer "%s" in file "%s" has an invalid type property (%s). Should be one of %s' % 
                (name, self.filename, layer_type, LAYER_TYPES))

    def getPropertiesFrom(self, nodes):
        """Return a property disction from the node"""
        props = {}
        for node in nodes:
            text = node.attrib['value']
            try:
                value = float(text)
            except ValueError:
                if text.lower() == 'true':
                    value = True
                elif text.lower() == 'false':
                    value = False
                else:
                    value = text
            props[node.attrib['name']] = value
        return props
    
    def getSpriteName(self, idx):
        """Return the sprite name for an index"""
        last_end = 0
        for name, ending_at in self.tilesets:
            if idx < ending_at:
                return '%s-%d' % (name, idx-last_end)
            last_end = ending_at-1
        raise ValueError('Unknown sprite gid (%s)' % idx)

    def getLayersForTile(self, (x, y), excluding=None):
        """Return a list of the layers that the tile at x, y is set on"""
        if excluding is None:
            excluding = []
        return [layer for layer in self.getLayers() if layer.tiles[y][x] if layer.layer_type not in excluding]

    def getPropertyBagArray(self, sprite_layers, boolean_layers, property_layers, prototype=None, optional_layers=None):
        """Return an array of property bags for the tile array
        
        You pass a series of lists of layer types, which are treated like:
            sprite_layers = tile based layers to treat as identifying sprites
            boolean_layers = tile layers where if a tile is set (to anything) then a boolean flag is True
            property_layers = tile layers where if a tile is set then the item recieves all the properties of the layer
            
        """
        optional_layers = optional_layers if optional_layers is not None else [] 
        #
        # Set the default item
        if prototype is None:
            prototype = serge.serialize.SerializedBag()
        #
        # Create an array to store the results
        data = []
        for y in range(self.height):
            data.append([])
            for x in range(self.width):
                cell = prototype.copy()
                cell.init()
                cell.coords = (x, y)
                cell.sprites = []
                for boolean_type in boolean_layers:
                    setattr(cell, boolean_type, False)
                data[-1].append(cell)
        #
        # Add sprites
        for sprite_type in sprite_layers:
            for layer in self.getLayersByType(sprite_type):
                for (x, y) in layer.iterCellLocations():
                    if layer.tiles[y][x]:
                        data[y][x].sprites.append(self.getSpriteName(layer.tiles[y][x]))
        #
        # Add booleans
        for boolean_type in boolean_layers:
            try:
                layer = self.getLayerByType(boolean_type)
            except NotFound:
                if boolean_type in optional_layers:
                    continue
                else:
                    raise
            for (x, y) in layer.getLocationsWithTile():
                setattr(data[y][x], boolean_type, True)
        #
        # Add properties
        for property_type in property_layers:
            for layer in self.getLayersByType(property_type):
                for (x, y) in layer.getLocationsWithTile():
                    for name, value in layer.properties.iteritems():
                        setattr(data[y][x], name, value)
        #
        return data

    def getSize(self):
        """Return the size of the map using the first layer as a guide"""
        return self.getLayers()[0].getSize()        
        
        
class Tiled(TileMap):
    """An interface to tiled files"""
    
    layer_types = list(LAYER_TYPES)
    
    def __init__(self, filename):
        """Initialise the Tiled"""
        super(Tiled, self).__init__()
        self.filename = filename
        self._registerSprites()
        self._parseLayers()
        self._parseObjectLayers()
                    
    def _registerSprites(self):
        """Register all the sprites"""
        self.log.info('Parsing sprites from %s' % self.filename)
        try:
            tree = ElementTree().parse(self.filename)
        except Exception, err:
            raise BadTiledFile('Unable to load XML file "%s": %s' % (self.filename, err))
        #
        # Find all tilesets in the file
        self.tilesets = []
        for tileset in tree.findall('.//tileset'):
            self.log.debug('Found tileset "%s"' % tileset.attrib['name'])
            width, height = int(tileset.attrib['tilewidth']), int(tileset.attrib['tileheight'])
            image = tileset.find('image')
            source = os.path.join(os.path.dirname(self.filename), image.attrib['source'])
            source_width, source_height = int(image.attrib['width']), int(image.attrib['height'])
            #
            # Create all images
            number = ((source_width*source_height)/(width*height))
            names = ['%s-%d' % (tileset.attrib['name'], idx) for idx in range(1, number+1)]
            serge.visual.Sprites.registerMultipleItems(names, source, source_width/width, source_height/height)
            self.log.debug('Created %d tiles' % number)
            #
            self.tilesets.append((tileset.attrib['name'], number+int(tileset.attrib['firstgid'])))

    def _parseLayers(self):
        """Parse the layers"""
        self.log.info('Parsing layers from %s' % self.filename)
        self.layers = layers = []
        #
        try:
            tree = ElementTree().parse(self.filename)
        except Exception, err:
            raise BadTiledFile('Unable to load XML file "%s": %s' % (self.filename, err))
        #
        self.width, self.height = int(tree.attrib['width']), int(tree.attrib['height'])
        #
        # Find all layers
        for layer in tree.findall('.//layer'):
            name = layer.attrib['name']
            self.log.debug('Found layer "%s"' % name)
            width, height = int(layer.attrib['width']), int(layer.attrib['height'])                    
            #
            # Get all data
            data = []
            for r, row in enumerate(layer.find('data').text.strip().split('\n')):
                data.append([])
                for c, col in enumerate(row.rstrip(',').split(',')):
                    data[-1].append(int(col))
            #
            properties = self.getPropertiesFrom(layer.findall('properties/property'))
            layer_type = self.getTypeFrom(name, properties)
            self.addLayer(Layer(self, name, layer_type, width, height, data, properties))

    def _parseObjectLayers(self):
        """Return the layers of objects"""
        self.log.info('Parsing object layers from %s' % self.filename)
        self.object_layers = []
        #
        try:
            tree = ElementTree().parse(self.filename)
        except Exception, err:
            raise BadTiledFile('Unable to load XML file "%s": %s' % (self.filename, err))
        #
        # Find all layers
        for layer in tree.findall('.//objectgroup'):
            name = layer.attrib['name']
            self.log.debug('Found layer "%s"' % name)
            properties = self.getPropertiesFrom(layer.findall('properties/property'))
            width, height = int(layer.attrib['width']), int(layer.attrib['height'])                    
            new_layer = Layer(self, name, properties.get('type', 'object'), width, height, None, properties)
            #
            # Look for ad-hoc visual layer
            if properties.get('type', '') == 'adhoc-visual':
                self.layers.append(new_layer)
                # 
                # Find sprites in this layer
                for obj in layer.findall('object'):
                    new_layer.addObject(TileObject(
                        'tile', 'sprite', int(obj.attrib['x']), int(obj.attrib['y']), 
                        int(obj.attrib.get('width', 0)), int(obj.attrib.get('height', 0)), 
                        {}, self.getSpriteName(int(obj.attrib['gid']))))
            else:
                self.object_layers.append(new_layer)
                #
                # Find objects in this layer
                for obj in layer.findall('object'):
                    #
                    # Watch out for polygon objects
                    children = obj.getchildren()
                    if children and children[0].tag == 'polygon':
                        try:
                            point_string = children[0].attrib['points']
                        except Exception, err:
                            raise BadLayer('Object "%s" on layer "%s" not recognized: %s' % (
                                obj.attrib.get('name', 'unknown'), name, err))
                        #
                        # Convert points to integers and find the extent
                        points = [map(int, coords.split(',')) for coords in point_string.split(' ')]
                        x, y = zip(*points)
                        min_x, max_x = min(x), max(x)
                        min_y, max_y = min(y), max(y)
                        x_pos, y_pos = int(obj.attrib['x']) + min_x, int(obj.attrib['y']) + min_y
                        width = max_x - min_x
                        height = max_y - min_y
                    else:
                        #
                        # Just get the width and height from the specified object
                        width = int(obj.attrib.get('width', 0))
                        height = int(obj.attrib.get('height', 0))
                        x_pos, y_pos = int(obj.attrib['x']), int(obj.attrib['y'])
                    #
                    # Create the new object
                    new_layer.addObject(TileObject(
                        obj.attrib['name'], obj.attrib['type'], x_pos, y_pos,
                        width, height,
                        self.getPropertiesFrom(obj.findall('properties/property'))))

    def getObjectLayers(self):
        """Return the object layers"""
        return self.object_layers
        

            
class Layer(serge.common.Loggable):
    """A layer in a tilemap"""

    def __init__(self, tiled, name, layer_type, width=None, height=None, tiles=None, properties=None):
        """Initialise the Layer"""
        self.addLogger()
        self.tiled = tiled
        self.name = name
        self.layer_type = layer_type
        #
        # Set initial size
        if width and height:
            self.width = width
            self.height = height
        elif tiles:
            self.width, self.height = len(tiles[0]), len(tiles)
        else:
            raise ValueError('Must initialise Layer with either width, height or tiles')
        #
        # Set the tiles
        if not tiles:
            self.tiles = []
            for row in range(self.height):
                self.tiles.append([])
                for col in range(self.width):
                    self.tiles[-1].append(False)
        else:
            self.tiles = tiles
        #
        self.objects = []
        #
        # Set properties
        self.properties = properties if properties is not None else {}
        for name, value in self.properties.iteritems():
            setattr(self, name, value)
            
    def getSize(self):
        """Return the size of the layer"""
        return (self.width, self.height)

    def addObject(self, obj):
        """Add an object

        :param obj: the object to add to the layer

        """
        self.objects.append(obj)
        
    def getObjects(self):
        """Return all the objects"""
        return self.objects

    def getObject(self, name):
        """Return the named object

        :param name: the name of the object to return

        """
        for obj in self.getObjects():
            if obj.name == name:
                return obj
        else:
            raise NotFound('Could not find object "%s" in layer "%s"' % (name, self.name))

    def getSpriteFor(self, (x, y)):
        """Return the sprite for a certain location"""
        item = self.tiles[y][x]
        return serge.visual.Sprites.getItem(self.tiled.getSpriteName(item))

    def getLocationsWithTile(self):
        """Return all tile locations with a tile"""
        matches = []
        for y, row in enumerate(self.tiles):
            for x, item in enumerate(row):
                if item != 0:
                    matches.append((x, y))
        return matches

    def getLocationsWithSpriteName(self, sprite_name):
        """Return all tile locations with a specific tile

        :param sprite_name: the name of the sprite you are looking for

        """
        matches = []
        for y, row in enumerate(self.tiles):
            for x, item in enumerate(row):
                if item and self.tiled.getSpriteName(item) == sprite_name:
                    matches.append((x, y))
        return matches

    def getLocationsWithoutTile(self):
        """Return all tile locations without a tile"""
        matches = []
        for y, row in enumerate(self.tiles):
            for x, item in enumerate(row):
                if item == 0:
                    matches.append((x, y))
        return matches
       

    def iterCellLocations(self):
        """Return an interation of the cell locations"""
        for y, row in enumerate(self.tiles):
            for x, item in enumerate(row):
                yield (x, y)        




                  
class TileObject(serge.geometry.Rectangle, serge.common.Loggable):
    """A tile"""
    
    def __init__(self, name, object_type, x, y, width, height, properties, sprite_name=None):
        """Initialise the tile"""
        self.name = name
        self.object_type = object_type
        self.setSpatial(x, y, width, height)
        self.sprite_name = sprite_name
        #
        # Set properties
        self.properties = properties
        for name, value in properties.iteritems():
            setattr(self, name, value)
        



