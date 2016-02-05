"""Classes to perform rendering"""

import os
import pygame

import common
import serialize
import camera
import visual
import events

class DuplicateLayer(Exception): """The layer was already present"""
class UnknownLayer(Exception): """The layer was not found"""
class NoLayer(Exception): """A layer was not found when one was expected"""


class Renderer(common.Loggable, serialize.Serializable, common.EventAware):
    """The main rendering component"""
    
    my_properties = (
        serialize.L('layers', [], 'the layers we render to'),
        serialize.I('width', 640, 'the width of the screen'),
        serialize.I('height', 480, 'the height of the screen'),
        serialize.S('title', 'Serge', 'the title of the main window'),
        serialize.L('backcolour', (0,0,0), 'the background colour'),
        serialize.O('camera', None, 'the camera for this renderer'),
        serialize.O('icon', None, 'the icon for the main window'),
        serialize.B('fullscreen', False, 'whether to display in full screen or not'),
    )
    
    def __init__(self, width=640, height=480, title='Serge', backcolour=(0,0,0), icon=None, fullscreen=False):
        """Initialise the Renderer"""
        self.addLogger()
        self.initEvents()
        self.width = width
        self.height = height
        self.title = title
        self.layers = []
        self.backcolour = backcolour
        self.fullscreen = fullscreen
        self.camera = camera.Camera()
        self.camera.setSpatial(0, 0, self.width, self.height)
        self.icon = icon
        self.init()
            
    ### Serializing ###
    
    def init(self):
        """Initialise from serialized state"""
        self.addLogger()
        self.initEvents()
        self._sort_needed = False
        pygame.display.set_caption(self.title)
        # 
        # Tried the following with flags but no impact pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.surface = pygame.display.set_mode((self.width, self.height), flags | pygame.HWSURFACE)
        for layer in self.layers:
            layer.setSurface(pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32))
            layer.init()
        self.camera.init()
        self.camera.resizeTo(self.width, self.height)
        if self.icon:
            if os.path.isfile(self.icon):
                pygame.display.set_icon(pygame.image.load(self.icon))
            else:
                pygame.display.set_icon(visual.Register.getItem(self.icon).raw_image)
        #
        self._render_layer_dict = None
        
    ### Layers ###
    
    def addLayer(self, layer):
        """Add a layer to the rendering"""
        self.log.info('Adding layer "%s" at %d' % (layer.name, layer.order))
        if layer in self.layers:
            raise DuplicateLayer('The layer %s is already in the renderer' % layer)
        else:
            self.layers.append(layer)
        self._sort_needed = True
        self.resetSurfaces()
        #
        # Update the layer dictionary cache
        self.getRenderingOrderDictionary()
        #
        return layer

    def getLayer(self, name):
        """Return the named layer"""
        for layer in self.layers:
            if layer.name == name:
                return layer
        else:
            raise UnknownLayer('No layer with name "%s" was found' % (name,))

    def getLayerBefore(self, layer):
        """Return the layer before the specified one in terms of rendering order"""
        for test_layer in reversed(self.getLayers()):
            if test_layer.order < layer.order:
                return test_layer
        else:
            raise NoLayer('There is no layer before %s' % layer.getNiceName())
        
    def resetSurfaces(self):
        """Recreate the surfaces for our layers
        
        When layers are added we sometimes need to reset the layers,
        for instance, virtual layers need to be shifted around so
        that they have the right order.
        
        """
        self._sortLayers()
        for layer in self.getLayers():
            layer.initSurface(self)

    def getLayers(self):
        """Return all the layers"""
        return self.layers

    def getBackgroundLayer(self):
        """Return the layer that is in the background"""
        return self.layers[0]

    def removeLayer(self, layer):
        """Remove the layer from the rendering"""
        try:
            self.layers.remove(layer)
        except ValueError:
            raise UnknownLayer('The layer %s was not found' % layer.getNiceName())
        #
        # Update the layer dictionary cache
        self.getRenderingOrderDictionary()

    def removeLayerNamed(self, name):
        """Remove the layer with the specific name"""
        layer = self.getLayer(name)
        self.removeLayer(layer)
        
    def clearLayers(self):
        """Clear all the layers"""
        self.layers = []
        
    def _sortLayers(self):
        """Sort the layers into the right order"""
        self.layers.sort(lambda l1, l2 : cmp(l1.order, l2.order))
        self._sort_needed = False

    def orderActors(self, actors):
        """Return the list of actors sorted by who should be processed first to correctly render
        
        The actors are checked to see which layer they reside on and then
        this is used to order the returned list.
        
        """
        #
        # Make a lookup table to quickly find layers
        layers = dict([(layer.name, layer.order) for layer in self.getLayers()])
        actor_list = [(layers.get(actor.getLayerName(), 0) * 10000 + actor.rendering_order, actor) for actor in actors]
        actor_list.sort()
        #
        return [actor for _, actor in actor_list]

    def getRenderingOrder(self, layer):
        """Return the order that a layer will be rendered in (0 = first)"""
        try:
            return self.layers.index(layer)
        except ValueError:
            raise UnknownLayer('The layer %s was not found' % layer)
        
    def getRenderingOrderDictionary(self):
        """Return a dictionary of the rendering orders of each layer by name ({name:0, name:1} etc)
        
        The dictionary is actually a live copy that will be updated if you 
        add layers to the renderer so it is safe for you to cache it and
        re-use it.
        
        Changing the dictionary results in undefined behaviour.
        
        """
        order = dict([(layer.name, idx) for idx, layer in enumerate(self.getLayers())])
        if self._render_layer_dict is None:
            #
            # Set the dictionary
            self._render_layer_dict = order
        else:
            #
            # Clear and reset the cached copy of the dictionary
            for k in self._render_layer_dict.keys():
                del(self._render_layer_dict[k])
            self._render_layer_dict.update(order)
        #
        return self._render_layer_dict
    
    ### Rendering ###

    def clearSurface(self):
        """Clear the surface"""
        self.surface.fill(self.backcolour)

    def preRender(self):
        """Prepare for new rendering"""
        self.clearSurface()
        for layer in self.getLayers():
            if layer.active:
                layer.clearSurface()
                layer.preRender()
                
    def render(self):
        """Render all the layers"""
        #
        # Post rendering events
        for layer in self.layers:
            if layer.active:
                layer.postRender()
        #
        # Put layers in the right order
        if self._sort_needed:
            self._sortLayers()
        #
        # Render all layers
        for layer in self.layers:
            if layer.active:
                layer.render(self.surface)
        #
        self.processEvent((events.E_AFTER_RENDER, self))            

    def getSurface(self):
        """Return the overall surface"""
        return self.surface  
    
    ### Camera stuff ###
    
    def setCamera(self, camera):
        """Set our camera"""
        self.camera = camera    
        
    def getCamera(self):
        """Return our camera"""
        return self.camera  

    def getScreenSize(self):
        """Returns the screen size"""
        return (self.width, self.height)
    

           
class RenderingLayer(common.Loggable, serialize.Serializable, common.EventAware):
    """A layer on which to render things
    
    This is the abstract version of the layer. Create
    subclasses of this to do useful things.
    
    """
    
    my_properties = (
        serialize.S('name', '', 'the name of the layer'),
        serialize.I('order', 0, 'the order to render (0=low)'),
        serialize.B('active', True, 'whether this layer is active'),
        serialize.B('static', False, 'whether this layer is static with respect to the camera'),
    )
    
    def __init__(self, name, order):
        """Initialise the Layer"""
        super(RenderingLayer, self).__init__()
        self.initEvents()
        self.name = name
        self.order = order
        self.surface = None
        self.active = True
        self.static = False

    def setSurface(self, surface):
        """Set our surface"""
        self.surface = surface

    def getSurface(self):
        """Return the surface"""
        return self.surface  

    def initSurface(self, renderer):
        """Create the surface that we need to draw on"""
        raise NotImplementedError

    def getNiceName(self):
        """Return the nice name for this layer"""
        return '<Layer %d: %s - order %d>' % (id(self), self.name, self.order)
    
    def setStatic(self, static):
        """Determine whether this layer is static with respect to camera movements or not"""
        self.static = static
        
    ### Serializing ###
    
    def init(self):
        """Initialise from serialized state"""
        self.initEvents()
        
    ### Rendering ###
          
    def clearSurface(self):
        """Clear our surface"""
        raise NotImplementedError
    
    def preRender(self):
        """Called before the layer has anything rendered to"""
        self.processEvent((events.E_BEFORE_RENDER, self))
        
    def render(self, surface):
        """Render to a surface"""
        raise NotImplementedError
        
    def postRender(self):
        """Called after the layer has has had everything rendered on it"""
        self.processEvent((events.E_AFTER_RENDER, self))
    
    
class Layer(RenderingLayer):
    """A rendering layer with its own surface
    
    This type of layer is useful for compositing because
    you can do things to this layer once it has been
    rendered (eg shadows, glows, blurs etc).
    
    """

    def initSurface(self, renderer):
        """Create the surface that we need to draw on
        
        We create a surface that is identical to the background for the
        main renderer.
        
        """
        self.setSurface(pygame.Surface((renderer.width, renderer.height), pygame.SRCALPHA, 32))
     
    def clearSurface(self):
        """Clear our surface"""
        self.surface.fill((0,0,0,0))

    def render(self, surface):
        """Render to a surface"""
        surface.blit(self.surface, (0,0))
    
class VirtualLayer(RenderingLayer):
    """A rendering layer that doesn't have its own surface
    
    This layer will render to the layer immediately
    before it in the rendering cycle.
    
    """
    
    def initSurface(self, renderer):
        """Create the surface that we need to draw on
        
        We do not want a surface ourself but we need the next surface
        in line as far as the renderer is concerned.
        
        """
        try:
            self.setSurface(renderer.getLayerBefore(self).getSurface())
        except NoLayer:
            self.setSurface(renderer.getSurface())
            
    def clearSurface(self):
        """Clear our surface
        
        Nothing to do here - handled by the real owner of the surface.
        
        """
        pass

    def render(self, surface):
        """Render to a surface
        
        Nothing to do here - handled by the real owner of the surface.
        
        """
        pass    
