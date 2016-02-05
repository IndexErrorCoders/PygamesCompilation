"""Main generator"""

import xml.etree.cElementTree as ET
import importlib
import sys

import loggable
import common
import world


class Generator(loggable.Loggable):
    """The main class to generate a landscape"""

    def __init__(self):
        """Initialise"""
        self.addLogger()
        #
        # Set instance attributes to blank values
        self.width = self.height = 0
        self.world = None
        self.builders = {}
        self.renderers = {}
        self.root = None
        self.inputfile = None
        self.renderfile = None
        self.rendername = None
        self.current_builder = None

    def generateLandscape(self, inputfile, renderfile, rendername):
        """Generate a landscape"""
        self.setOptions(inputfile, renderfile, rendername)
        self.createBuilders()
        self.createRenderers()
        self.doGeneration()
        self.renderOutput(self.rendername)

    def setOptions(self, inputfile, renderfile, rendername):
        """Set the options"""
        self.root = self.getOptions(inputfile)
        self.inputfile = inputfile
        self.renderfile = renderfile
        self.rendername = rendername

    def createBuilders(self):
        """Create the builders"""
        #
        # Go through all the builders
        for builder in self.root.find('builders').findall('builder'):
            if not common.getTrueAttr(builder, "active", True):
                self.log.debug('Skipping inactive builder "%s"' % builder.attrib['name'])
            else:
                self.log.debug('Processing builder "%s"' % builder.attrib['name'])
                module = importlib.import_module(builder.attrib['module'])
                #
                # Create the builder
                try:
                    cls = self.resolveName(module, builder.attrib['class'])
                    builder_item = cls(builder)
                except Exception, err:
                    raise common.ParsingFailed('Failed when trying to create builder: %s' % err)
                #
                self.builders[builder_item.name] = builder_item
                builder_item.order = len(self.builders)

    def getOptions(self, inputfile):
        """Set options based on the input file"""
        self.log.debug('Parsing %s' % inputfile)
        #
        # Get the XML
        try:
            tree = ET.parse(inputfile)
        except Exception, err:
            raise common.ParsingFailed("Could not parse XML file '%s': %s" % (inputfile, err))
        root = tree.getroot()
        if root.tag != 'generator':
            raise common.ParsingFailed("Input file '%s' doesn't start with a generator tag" % inputfile)
        #
        # Get size
        self.width = common.getInt(root, 'width')
        self.height = common.getInt(root, 'height')
        #
        world_class_name = common.getString(root, 'worldClass')
        world_class = getattr(world, world_class_name)
        self.world = world_class(self.width, self.height)
        #
        return root

    def getSortedBuilders(self):
        """Return a list of the builders in the order they are defined"""
        sorted_builders = self.builders.values()
        sorted_builders.sort(lambda a, b: cmp(a.order, b.order))
        return sorted_builders

    def getSortedRenderers(self):
        """Return a list of the renderers in the order they are defined"""
        sorted_renderers = self.renderers.values()
        sorted_renderers.sort(lambda a, b: cmp(a.order, b.order))
        return sorted_renderers

    def doGeneration(self):
        """Do the actual generation"""
        sorted_builders = self.getSortedBuilders()
        for builder in sorted_builders:
            #
            # Make it build
            builder.buildOnWorld(self.world)

    def runBuilderNamed(self, name):
        """Run the builder with a certain name"""
        self.log.info('Running builder %s' % name)
        self.current_builder = self.builders[name]
        self.world = self.current_builder.buildOnWorld(self.world)
        self.current_builder = None

    def getProgress(self):
        """Return the progress from the current builder"""
        if self.current_builder:
            return self.current_builder.getProgress()
        else:
            return None

    def requestStop(self):
        """Request that the current builder stop"""
        if self.current_builder:
            self.current_builder.requestStop()

    def resolveName(self, module, attribute_name):
        """Return the attribute in the module"""
        return getattr(module, attribute_name)

    def writeOutput(self, outfile, root):
        """Write the output"""
        with file(outfile, 'w') as f:
            for row in range(self.world.height):
                for col in range(self.world.width):
                    f.write(str(self.world.getCell(row, col).rock_depth) + ',')
                f.write('\n')

    def renderOutput(self, rendername, world=None):
        """Render the output to some kind of image"""
        renderer = self.renderers[rendername]
        renderer.renderToFile(
            self.renderfile,
            world if world else self.world
        )
        #
        # Return a message if there was one
        if renderer.confirmation_message:
            return renderer.confirmation_message


    def createRenderers(self):
        """Create the renderers"""
        #
        # Go through all the renderers
        for renderer in self.root.find('renderers').findall('renderer'):
            self.log.debug('Processing renderer "%s"' % renderer.attrib['name'])
            module = importlib.import_module(renderer.attrib['module'])
            #
            # Create the renderer
            try:
                cls = self.resolveName(module, renderer.attrib['class'])
                renderer_item = cls(renderer)
            except Exception, err:
                raise common.ParsingFailed('Failed when trying to create renderer: %s' % err)
            #
            self.renderers[renderer_item.name] = renderer_item
            renderer_item.order = len(self.renderers)