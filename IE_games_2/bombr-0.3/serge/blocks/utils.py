"""Some utilities that speed up common operations"""

import sys
import os
import pygame
import subprocess
import uuid
import random
import bisect

import serge
import serge.render
import serge.actor
import serge.world
import serge.zone
import serge.engine
import serge.visual
import serge.events
import serge.blocks.actors


def createLayers(engine, layers, cls):
    """Create a number of layers in the engine using the given class of layer"""
    renderer = engine.getRenderer()
    #
    # Find the right number of layers so that we can set the order correctly
    n = len(renderer.getLayers())
    for name in layers:
        layer = cls(name, n)
        renderer.addLayer(layer)
        n += 1


def createLayersForEngine(engine, layers):
    """Add a number of layers to the engine
    
    The layers parameter is a list of layer names. The layers are added to
    the renderer of the engine as successive layers in order.
    
    """
    createLayers(engine, layers, serge.render.Layer)


def createVirtualLayersForEngine(engine, layers):
    """Add a number of virtual layers to the engine
    
    The layers parameter is a list of layer names. The layers are added to
    the renderer of the engine as successive layers in order.
    
    The layers are created as virtual, meaning that this will render
    quicker than the real layers version, although compositing
    will not be possible.
    
    """
    createLayers(engine, layers, serge.render.VirtualLayer)        


def createWorldsForEngine(engine, worlds, world_class=serge.world.World):
    """Add a number of worlds to the engine
    
    The words parameter is a list of names of the worlds to create.
    Each world is created with a single active zone which is quite
    large.
    
    """
    for name in worlds:
        world = world_class(name)
        zone = serge.zone.Zone()
        zone.active = True
        zone.setSpatial(-2000, -2000, 4000, 4000)
        world.addZone(zone)
        engine.addWorld(world)
        

def addActorToWorld(world, actor, sprite_name=None, layer_name=None, center_position=None, physics=None, origin=None):
    """Create a new actor in the world
    
    If the center position is not specified then it is placed at the center of the screen.
    
    """
    #
    # If not position then put at the center
    if origin is None and center_position is None:
        renderer = serge.engine.CurrentEngine().getRenderer()
        center_position = (renderer.width / 2.0, renderer.height / 2.0)
    #
    # Create the new actor
    if sprite_name is not None:
        actor.setSpriteName(sprite_name)
    if layer_name is not None:
        actor.setLayerName(layer_name)
    if physics:
        actor.setPhysical(physics)
    if center_position is not None:
        actor.moveTo(*center_position)
    else:
        actor.setOrigin(*origin)
    world.addActor(actor)
    return actor


def addSpriteActorToWorld(world, tag, name, sprite_name, layer_name,
                          center_position=None, physics=None, actor_class=serge.actor.Actor):
    """Create a new actor in the world and set the visual to be the named sprite
    
    If the center position is not specified then it is placed at the center of the screen.
    
    """
    #
    # Create the new actor
    actor = actor_class(tag, name)
    return addActorToWorld(world, actor, sprite_name, layer_name, center_position, physics)


def addVisualActorToWorld(world, tag, name, visual, layer_name,
                          center_position=None, physics=None, actor_class=serge.actor.Actor):
    """Create a new actor in the world and set the visual 
    
    If the center position is not specified then it is placed at the center of the screen.
    
    """
    #
    # Create the new actor
    actor = actor_class(tag, name)
    actor.visual = visual
    return addActorToWorld(world, actor, None, layer_name, center_position, physics)


def addTextToWorld(world, text, name, theme, layer_name, actor_class=serge.actor.Actor):
    """Add some text to the world"""
    L = theme.getProperty
    actor = addVisualActorToWorld(
        world, 'text', name,
        serge.visual.Text(
            text, L('%s-colour' % name),
            font_size=L('%s-font-size' % name),
            font_name=theme.getPropertyWithDefault(('%s-font' % name), 'DEFAULT'),
            justify=theme.getPropertyWithDefault(('%s-justify' % name), 'center')),
        layer_name,
        center_position=L('%s-position' % name),
        actor_class=actor_class)
    return actor


def addTextItemsToWorld(world, items, theme, layer_name,  actor_class=serge.actor.Actor):
    """Add multiple text items to the world"""
    for item in items:
        text, name = item[0:2]
        callback = None if len(item) == 2 else item[2]
        actor = addTextToWorld(world, text, name, theme, layer_name, actor_class=actor_class)
        if callback:
            actor.linkEvent(serge.events.E_LEFT_CLICK, callback)    


def addMuteButtonToWorlds(button, center_position, world_names=None):
    """Add a particular mute button to various worlds
    
    If worlds is not specified then add to all the worlds currently in the engine.
    
    """
    engine = serge.engine.CurrentEngine()
    if world_names is None:
        world_names = [world.name for world in engine.getWorlds()]
    for name in world_names:
        world = engine.getWorld(name)
        addActorToWorld(world, button, center_position=center_position)


class MovieRecorder(object):
    """Will record a movie of the game"""

    def __init__(self, path, make_movie=False, rate=1, in_memory=False):
        """Initialise the MovieRecorder
        
        If make_movie is True then we will convert the frames to a movie
        
        """
        self.path = path
        self.basename = os.path.splitext(path)[0]
        self.engine = serge.engine.CurrentEngine()
        self.renderer = self.engine.getRenderer()
        self.frame_count = 1
        self.skip_frames = rate
        self.skipped_frames = 0
        self.clearFrames()
        #
        self.engine.linkEvent(serge.events.E_AFTER_RENDER, self.makeFrame)
        if make_movie:
            self.engine.linkEvent(serge.events.E_AFTER_STOP, self.makeMovie)
        #
        self.in_memory = in_memory
        self.frames = []
        
    def makeFrame(self, obj, arg):
        """Make a frame"""
        self.skipped_frames += 1
        if self.skipped_frames >= self.skip_frames:
            self.skipped_frames = 0
            if self.in_memory:
                self.frames.append(self.renderer.getSurface().copy())
            else:
                pygame.image.save(self.renderer.getSurface(), self._getName(self.frame_count))
            self.frame_count += 1
        
    def clearFrames(self):
        """Clear all current frames"""
        for i in xrange(1, 1000000):
            if os.path.isfile(self._getName(i)):
                os.remove(self._getName(i))
            else:
                break

    def makeMovie(self, obj, arg):
        """Convert the frames to movie"""
        if self.in_memory:
            self._dumpFiles()
        cmd = 'cd %s; mencoder mf://%s -mf w=%d:h=%d:fps=%d:type=png -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -o %s' % (
            os.path.dirname(self.path), 
            '*.png', 
            self.renderer.width, self.renderer.height, 
            60/self.skip_frames,
            os.path.basename(self.path)
        )
        subprocess.call(cmd, shell=True)
        self.clearFrames()
                   
    def _getName(self, idx):
        """Return the filename"""
        return '%s-%07d.png' % (self.basename, idx)
        
    def _dumpFiles(self):
        """Dump all files out from memory"""
        for idx, frame in enumerate(self.frames):
            pygame.image.save(frame, self._getName(idx+1))
            
            
class RecordDesktop(serge.common.Loggable):
    """Use record my desktop to record the action"""

    def __init__(self, filename):
        """Initialise the RecordDesktop"""
        self.addLogger()
        #
        # Highly system specific!
        #
        # Find our window
        self.log.info('Looking for the main window')
        engine = serge.engine.CurrentEngine()
        #
        windows = subprocess.check_output(['wmctrl', '-lG']).splitlines()
        for window in windows:
            parts = window.split()
            x, y, width, height = parts[2:6]
            name = ' '.join(parts[7:])
            if name == engine.title:
                break
        else:
            raise ValueError('Could not find the main window!')
        #import pdb; pdb.set_trace()
        #
        # Now start the recording
        self.log.info('Starting "recordmydesktop"')
        self.child = subprocess.Popen(['recordmydesktop', '--width', width, '--height', height,
            '-x', x, '-y', y, '-o', filename, '--fps', '60'])
        
        #
        # Hook completion so we can quit
        engine.linkEvent(serge.events.E_AFTER_STOP, self.stop)
        
    def stop(self, obj, arg):
        """Stop the recording"""
        self.log.info('Asking "recordmydesktop" to compile the video now')
        self.child.terminate()
        self.child.wait()


def checkPythonVersion():
    """Check a suitable Python version is installed"""
    if sys.version_info[0] == 3:
        print 'Python 3 is not supported'
        return False
    elif sys.version_info[1] <= 5:
        print 'Python 2.6+ is required'
        return False
    return True


def checkNetworkXVersion(need_version):
    """Check a suitable version of NetworkX is installed"""
    try:
        import networkx
    except ImportError:
        print 'networkx is required.\nTry "easy_install networkx" or visit http://networkx.lanl.gov/'
        return False
        
    # Attempt to check correct version
    try:
        version = float(networkx.__version__.rsplit('.', 1)[0])
    except:
        # Ok, this didn't work so probably we will fail later with a more direct error!
        pass
    else:
        if version < need_version:
            print '\n\nnetworkx >= version %s is required. Found %s.\n' % (need_version, version)
            print 'Try "easy_install networkx" or visit http://networkx.lanl.gov/' 
            print 'You may have to remove your version using synaptic first.\n\n'
            return False
    return True
    
def checkPyOpenGLVersion(need_version):
    """Check a suitable PyOpenGL is installed"""
    try:
        import OpenGL
    except ImportError:
        print 'PyOpenGL is not installed\nTry "pip install PyOpenGL PyOpenGL_accelerate'
        return False
    else:
        return True
        

def worldCallback(name, sound=None):
    """Return an event callback to switch to a certain world"""
    def callback(obj, arg):
        if sound:
            serge.sound.Sounds.play(sound)
        serge.engine.CurrentEngine().setCurrentWorldByName(name)
    #
    return callback


def backToPreviousWorld(sound=None):
    """Return an event callback to switch back to the previous world"""
    def callback(obj, arg):
        if sound:
            serge.sound.Sounds.play(sound)
        serge.engine.CurrentEngine().goBackToPreviousWorld()
    #
    return callback


def getGamePath(*parts):
    """Return a path based on the main game folder"""
    return os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(serge.__file__)), '..', *parts))
    
    
def getSimpleSetup(width, height):
    """Return an engine with a single world, zone and a few layers"""
    #
    # Engine
    e = serge.engine.Engine(width=width, height=height)
    #
    # World
    createWorldsForEngine(e, ['lab'])
    #
    # Rendering
    createVirtualLayersForEngine(e, ['back', 'middle', 'front'])
    #
    e.setCurrentWorldByName('lab')
    #
    return e


def debugMethod(obj, method_name, logger=None, fmt=''):
    """Create a debug logged method"""
    def fn(*args, **kw):
        """Debugged method"""
        if fmt:
            logger.debug(fmt % args)
        else:
            logger.debug('Debug %s::%s: %s, %s' % (obj.getNiceName(), method_name, args, kw))
        return method(*args, **kw)
    #    
    if logger is None:
        logger = obj.log
    method = getattr(obj, method_name)
    setattr(obj, method_name, fn)


def getUniqueID():
    """Returns a unique ID string for this computer"""
    return str(uuid.getnode())


class LoadingScreen(serge.world.World):
    """Implements a loading screen"""

    def __init__(self, font_colour, font_size, font_name, position, layer_name,
                 justify='center', background=None, background_position=None, background_layer=None,
                 icon_name=None, icon_position=None):
        """Initialise the loading screen"""
        super(LoadingScreen, self).__init__('loading-screen')
        #
        # Background
        if background:
            addSpriteActorToWorld(
                self, 'bg', 'bg', background, background_layer if background_layer else layer_name,
                center_position=background_position if background_position else position
            )
        #
        # Add the actor to show the loading progress
        self.text = serge.blocks.actors.StringText(
            'txt', 'txt', 'Loading ...', colour=font_colour, font_name=font_name,
            font_size=font_size, justify=justify
        )
        self.addActor(self.text)
        self.text.moveTo(*position)
        self.text.setLayerName(layer_name)
        #
        # If there is an icon then show it
        if icon_name:
            icon = serge.actor.Actor('icon')
            icon.setSpriteName(icon_name)
            icon.moveTo(*icon_position)
            icon.setLayerName(layer_name)
            self.addActor(icon)
        #
        # Get the engine
        self.engine = serge.engine.CurrentEngine()
        self.renderer = self.engine.getRenderer()

    def showScreen(self, text='Loading ...'):
        """Show the loading screen"""
        self.log.info('Rendering loading screen')
        self.text.value = text
        self.renderer.clearSurface()
        self.renderTo(self.renderer, 1000)
        self.renderer.render()
        pygame.display.flip()


class ProbabilityChooser(object):
    """Returns choices from a list of possibilities with probabilities"""

    def __init__(self, options):
        """Initialise the chooser"""
        self.total_probability = sum(options.values())
        self.items = [(value, key) for key, value in options.iteritems()]
        self.items.sort()
        self.values = []
        #
        # Get cumulative values
        total = 0
        for item, _ in self.items:
            total += item
            self.values.append(total)

    def choose(self):
        """Return an item chosen at random from our list"""
        value = random.random() * self.total_probability
        idx = bisect.bisect(self.values, value)
        return self.items[idx][1]


class BidirectionalDict(dict):
    """A dictionary that can access items by key or by value"""

    def __init__(self):
        """Initialise the dict"""
        super(BidirectionalDict, self).__init__()
        self._reverse = {}

    def __setitem__(self, key, value):
        """Set an item"""
        super(BidirectionalDict, self).__setitem__(key, value)
        self._reverse[value] = key

    def getReverse(self, value):
        """Return the key from the value"""
        return self._reverse[value]

    def deleteReverse(self, value):
        """Delete the item from the value"""
        key = self._reverse[value]
        del(self[key])
        del(self._reverse[value])


def takeScreenshot(filename):
    """Take a screenshot"""
    surface = serge.engine.CurrentEngine().getRenderer().getSurface()
    pygame.image.save(surface, filename)