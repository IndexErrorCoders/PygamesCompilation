"""The main engine for Serge"""

import time
import common
import pygame
import serialize
import render
import visual
import threading
import input
import sound
import events
import profiler

class WorldNotFound(Exception): """The world was not in the worlds collection"""
class DuplicateWorld(Exception): """The world already exists in the worlds collection"""
class NoCurrentWorld(Exception): """There was no current world present"""

import pygame
pygame.init()

class Engine(common.Loggable, serialize.Serializable, common.EventAware):
    """The main Serge engine
    
    The engine manages a set of worlds and allows
    a single :doc:`world`, the current world, to be automatically
    updated on a certain time frequency.
    
    """
    
    my_properties = (
        serialize.L('_worlds', [], 'the worlds in this engine'),
        serialize.O('renderer', None, 'the renderer for this engine'),
        serialize.O('sprites', None, 'the sprite registry'),
        serialize.S('_current_world_name', '', 'the name of the current world'),
        serialize.L('_recent_worlds', [], 'the list of worlds recently visited'),
        serialize.B('fullscreen', False, 'whether to display in full screen or not'),
    )
    
    def __init__(self, width=640, height=480, title='Serge', backcolour=(0,0,0), icon=None, fullscreen=False):
        """Initialise the engine
        
        :param width: width of the screen
        :param height: height of the screen
        
        """
        self.title = title
        self.fullscreen = fullscreen
        self.addLogger()
        self.initEvents()
        self.log.info('Starting serge engine (v%s)' % common.version)
        SetCurrentEngine(self)
        super(Engine, self).__init__()
        self.clearWorlds()
        self.renderer = render.Renderer(width, height, title, backcolour, icon, fullscreen)
        self.sprites = visual.Register
        self._stop_requested = False
        self._current_world_name = ''
        self._builder = None
        self._keyboard = input.Keyboard()
        self._mouse = input.Mouse(self)
        self._stats = EngineStats()
        self._recent_worlds = []
        self._profiler = profiler.NullProfiler()
                    
    def init(self):
        """Initialise ourself"""
        self.addLogger()
        self.log.info('Initializing serge engine (v%s)' % common.version)
        SetCurrentEngine(self)
        #
        # Prepare all the worlds
        for world in self._worlds.values():
            world.init()
        self._current_world = None
        self._snapshots_enabled = True
        self._snapshot_count = 0
        #
        # Recover the sprite registry from our own
        self.sprites.init()
        visual.Register = self.sprites
        self.setCurrentWorldByName(self._current_world_name)
        #
        self.renderer.init()
        #
        self._builder = None
        self._keyboard = input.Keyboard()
        self._mouse = input.Mouse(self)
            
    def addWorld(self, world):
        """Add a world to the engine
        
        :param world: the world instance to add
        
        """
        if world.name in self._worlds:
            raise DuplicateWorld('A world named "%s" already exists' % world.name)
        if world in self._worlds.values():
            raise DuplicateWorld('This world (named "%s") already exists' % world.name)
        self._worlds[world.name] = world
        world.setEngine(self)
        
    def removeWorld(self, world):
        """Remove a world from the engine
        
        :param world: the world instance to remove

        """
        self.removeWorldNamed(world.name)
        
    def removeWorldNamed(self, name):
        """Remove a world with a given name
        
        :param name: the name of the world to remove

        """
        try:
            del(self._worlds[name])
        except KeyError:
            raise WorldNotFound('No world named "%s" in the worlds collection' % name)

    def clearWorlds(self):
        """Clear all the worlds"""
        self._worlds = {}
        self._current_world = None
        
    def getWorld(self, name):
        """Return the named world
        
        :param name: the name of the world to return

        """
        try:
            return self._worlds[name]
        except KeyError:
            raise WorldNotFound('No world named "%s" in the worlds collection' % name)

    def getWorlds(self):
        """Return all the worlds"""
        return self._worlds.values()

    def getCurrentWorld(self):
        """Return the currently selected world"""
        if self._current_world:
            return self._current_world
        else:
            raise NoCurrentWorld('There is no current world')
        
    def setCurrentWorld(self, world):
        """Set the current world
        
        :param world: the world to set as the current world

        """
        self.setCurrentWorldByName(world.name)
        
    def setCurrentWorldByName(self, name):
        """Set the current world to the one with the given name
        
        :param name: the name of the world to set as the current world

        """
        self.log.info('Setting current world to %s' % name)
        if self._current_world_name:
            self._recent_worlds.append(self._current_world_name)
        new_world = self.getWorld(name)
        #
        # Send activation and deactivation callbacks to worlds to allow them to do
        # any housekeeping
        if new_world != self._current_world:
            if self._current_world:
                self._current_world.deactivateWorld()
            new_world.activateWorld()
        #
        self._current_world = new_world
        self._current_world_name = name
        return new_world

    def goBackToPreviousWorld(self, obj=None, arg=None):
        """Return to the world we were in before this one
        
        The arguments are never used and are just here to allow you to use
        this method as an event callback.
        
        """
        try:
            name = self._recent_worlds.pop()
        except IndexError:
            raise WorldNotFound('There are no previous worlds')
        self.setCurrentWorldByName(name)
        # We will have pushed the current world onto the stack, which we don't want
        # so take it off again
        self._recent_worlds.pop()
        
    def updateWorld(self, interval):
        """Update the current world"""
        if self._current_world:
            self._current_world.updateWorld(interval)
        else:
            raise NoCurrentWorld('Cannot update when there is no current world')
        
    def run(self, fps, endat=None):
        """Run the updates at the specified frames per second until the optional endtime
        
        :param fps: the target frames per second (integer)
        :param endat: a time to stop the engine at (long), eg time.time()+60 to run for a minute
        
        """
        self.log.info('Engine starting (requested fps=%d)' % fps)
        clock = pygame.time.Clock()
        self._stop_requested = False
        while True:
            #
            # Watch for ending conditions
            if self._stop_requested or (endat and time.time() >= endat):
                break
            #
            # Main render activity
            try:
                #
                # Pause
                clock.tick(fps)
                #
                # Do the update for our actors
                interval = clock.get_time()
                if self._current_world:
                    self.updateWorld(interval)
                #
                # Quit now if someone requested we stop
                if self._stop_requested:
                    break
                #
                # Do builder work if needed
                if self._builder:
                    self._builder.updateBuilder(interval)
                #
                # Events that may have happened
                self._handleEvents()
                # Inputs
                self._mouse.update(interval)
                self._keyboard.update(interval)
                pygame.event.clear()
                # Sound
                sound.Music.update(interval)
                sound.Sounds.update(interval)                
                if self._current_world:
                    self.processEvents()
                #
                # Get ready to render
                self._stats.beforeRender()
                self.renderer.preRender()
                #
                # Render the active world
                if self._current_world:
                    self._current_world.renderTo(self.renderer, interval)
                #
                # Render the builder if needed
                if self._builder:
                    self._builder.renderTo(self.renderer, interval)
                #
                # And render all of our layers
                self.renderer.render()
                self.processEvent((events.E_AFTER_RENDER, self))
                self._stats.afterRender()
                #
                # Show the screen
                pygame.display.flip()
                self._stats.recordFrame()
                #
            except NotImplementedError, err:
                self.log.error('Failed in main loop: %s' % err)
        #
        self.log.info('Engine stopping')
        self.processEvent((events.E_AFTER_STOP, self))
        self.log.info('Engine info: %s' % (self._stats,))
        
    def runAsync(self, fps, endat=None):
        """Run the engine asynchronously
        
        :param fps: the target frames per second (integer)
        :param endat: a time to stop the engine at (long), eg time.time()+60 to run for a minute
        
        """
        self.runner = threading.Thread(target=self.run, args=(fps, endat))
        self.runner.setDaemon(True)
        self.runner.start()

    def stop(self, process_events=True):
        """Stop the engine running"""
        if process_events:
            self.processEvent((events.E_BEFORE_STOP, self))
        self._stop_requested = True

    def getRenderer(self):
        """Return the renderer"""
        return self.renderer
    
    def getSprites(self):
        """Return the sprite registry"""
        return self.sprites
        
    def save(self, filename):
        """Store the engine state in a file suitable for loading again in the furture
        
        :param filename: the name of the file to save into
        
        """
        with file(filename, 'w') as f:
            f.write(self.asString())
            
    def attachBuilder(self, builder):
        """Attach a builder"""
        self._builder = builder
        
    def detachBuilder(self):
        """Detach the builder"""
        self._builder = None
        
    def getKeyboard(self):
        """Return the keyboard"""
        return self._keyboard
    
    def getMouse(self):
        """Return the mouse"""
        return self._mouse
    
    def getStats(self):
        """Return the stats for the engine"""
        return self._stats
    
       
    ### Events ###
    
    def _handleEvents(self):
        """Handle all events"""
        events = pygame.event.get(pygame.QUIT)
        if events:
            self.stop()
    
    def processEvents(self):
        """Process all the events for the current world"""
        events = self._mouse.getActorEvents(self._current_world, layer_order=self.renderer.getRenderingOrderDictionary())
        to_do = [((event, self._mouse), actor) for event, actor in events]
        self._current_world.processEvents(to_do)

    ### Profiling ###
    
    def profilingOn(self):
        """Turn the profiling on"""
        self._profiler = profiler.PROFILER
        
    def getProfiler(self):
        """Return the current profiler"""
        return self._profiler
        

class EngineStats(object):
    """Statistic for the engine"""
    
    def __init__(self):
        """Initialise the stats"""
        self.start_time = time.time()
        self.average_frame_rate = 0.0
        self.current_frame_rate = 0.0
        self.last_frame = None
        self.last_render = None
        self.average_render_time = 0.0
        
    def recordFrame(self):
        """Record a frame"""
        now = time.time()
        if self.last_frame:
            try:
                self.current_frame_rate = 1.0/(now - self.last_frame)
            except ZeroDivisionError:
                # Sometimes happens on Windows
                return
            self.average_frame_rate = (59*self.average_frame_rate + self.current_frame_rate)/60.0
            
        self.last_frame = time.time()

    def beforeRender(self):
        """Record we are before a rendering cycle"""
        self.last_render = time.time()
        
    def afterRender(self):
        """Record that we are after a rendering cycle"""
        self.average_render_time = (59*self.average_render_time + (time.time() - self.last_render))/60.0

    def __repr__(self):
        """Nice representation"""
        return '(current fps=%f, ave fps=%f, ave render=%fs)' % (
            self.current_frame_rate, self.average_frame_rate, self.average_render_time)
        
        
### Allow people to find the current engine ###

_current_engine = None

def CurrentEngine():
    """Return the current (last created) engine"""
    global _current_engine
    return _current_engine

def SetCurrentEngine(engine):
    """Set the current engine"""
    global _current_engine
    _current_engine = engine
