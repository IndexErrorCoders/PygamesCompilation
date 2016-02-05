"""The game engine

The engine:
    Contains worlds
    Causes current world to render
    Causes current world to update its actors
    Can dispatch events like mouse click and keyboard

"""

import os
import pyglet

import common
import tween
import errors


class Engine(common.Loggable):
    """The main game engine"""

    max_screenshots = 1000

    def __init__(self, width, height, framerate=60.0, debug=False, fade_image_name=None):
        """Initialise the engine"""
        self.addLogger()
        self.worlds = {}
        self.current_world = None
        self.debug = debug
        self.paused = False
        if fade_image_name:
            self.world_fade = pyglet.sprite.Sprite(pyglet.resource.image(fade_image_name))
            self.world_fade.x, self.world_fade.y = 0, 0
            self.world_fade.scale = max(width, height) / self.world_fade.width * 2
        else:
            self.world_fade = None
        self.fading = False
        self.initialiseWindow(width, height, framerate)
        self.log.info('Engine created with window (%d, %d)' % (width, height))

    def initialiseWindow(self, width, height, framerate):
        """Create the main pyglet window"""
        self.window = pyglet.window.Window(width, height)
        self.window.on_draw = self.onDraw
        self.window.on_key_press = self.onKeyPress
        self.window.on_key_release = self.onKeyRelease
        self.window.on_mouse_press = self.onMouseDown
        self.window.on_mouse_release = self.onMouseRelease
        self.window.on_mouse_drag = self.onMouseDrag
        self.window.on_mouse_scroll = self.onMouseScroll
        pyglet.clock.schedule_interval(self.onUpdate, 1.0 / framerate)
        #
        if self.debug:
            self._fps_display = pyglet.clock.ClockDisplay(color=(1, 1, 1, 1))

    def addWorld(self, world):
        """Add a world to the engine"""
        if world.name in self.worlds:
            raise errors.AlreadyExists('A world named "%s" is already in the engine' % world.name)
        self.log.info('Added world "%s"' % world.name)
        self.worlds[world.name] = world
        world.engine = self

    def setCurrentWorld(self, name):
        """Sets the current world"""
        self.log.info('Switching to world "%s"' % name)
        if self.current_world:
            self.current_world.deactivateWorld(name)
        self.current_world = self.worlds[name]
        self.current_world.activateWorld()

    def fadeToWorld(self, name, duration):
        """Move to a new world using a fade"""
        if not self.world_fade:
            raise Exception('There is no world fade set for the engine')
        self.fading = True
        self.current_world.tweens.append(tween.Tween(self.world_fade, 'opacity', 0, 255, duration / 2.,
                                                     tween.Tween.sinOut, after=lambda: self._fadeIn(name, duration)))

    def _fadeIn(self, name, duration):
        """Fade in to the new world"""
        self.setCurrentWorld(name)
        self.current_world.tweens.append(tween.Tween(self.world_fade, 'opacity', 255, 0, duration / 2.,
                                                     tween.Tween.sinOut, after=self._fadeComplete))

    def _fadeComplete(self):
        """The fade is done"""
        self.fading = False

    def onDraw(self):
        """The main rendering loop from pyglet"""
        self.window.clear()
        if self.current_world:
            self.current_world.renderWorld()
        if self.fading:
            self.world_fade.draw()
        if self.debug:
            self._fps_display.draw()

    def onUpdate(self, dt):
        """Update the world logic"""
        if self.current_world and not self.paused:
            self.current_world.updateWorld(dt)

    def runEngine(self):
        """Run the main pyglet loop"""
        pyglet.app.run()

    def onKeyPress(self, symbol, modifier):
        """Hand off key presses to the world"""
        if self.current_world:
            self.current_world.onKeyPress(symbol, modifier)

    def onMouseDown(self, x, y, button, modifiers):
        """All mouse press events are routed here"""
        if self.current_world:
            self.current_world.onMouseDown(x, y, button, modifiers)

    def onMouseRelease(self, x, y, button, modifiers):
        """All mouse release events come here"""
        if self.current_world:
            self.current_world.onMouseRelease(x, y, button, modifiers)

    def onMouseDrag(self, x, y, dx, dy, button, modifiers):
        """All mouse drag events come here"""
        if self.current_world:
            self.current_world.onMouseDrag(x, y, dx, dy, button, modifiers)

    def onMouseScroll(self, x, y, scroll_x, scroll_y):
        """All mouse scroll events come here"""
        if self.current_world:
            self.current_world.onMouseScroll(x, y, scroll_x, scroll_y)

    def onKeyRelease(self, symbol, modifier):
        """Hand off key release to the world"""
        #
        # Watch for keys
        if modifier == pyglet.window.key.MOD_CTRL and symbol == pyglet.window.key.S:
            self.takeScreenShot()
        elif self.debug:
            if modifier == pyglet.window.key.MOD_CTRL and symbol == pyglet.window.key.P:
                self.paused = not self.paused
                self.log.info("Engine paused" if self.paused else "Engine un-paused")
        #
        # Pass keys onto current world
        if self.current_world:
            self.current_world.onKeyRelease(symbol, modifier)

    def stopEngine(self, reason='Stopping engine'):
        """Stop the engine"""
        self.log.info('Engine stopping: %s' % reason)
        pyglet.app.exit()

    def takeScreenShot(self):
        """Take a screenShot from the engine"""
        #
        # Find a free filename
        for i in range(self.max_screenshots):
            filename = os.path.join('screenshots', 'screenshot-%d.bmp' % i)
            if not os.path.exists(filename):
                break
        else:
            self.log.error('No free slot for screenshot. Increase max_screenshots on engine')
            return
        #
        # Record screenshot
        self.log.info('Creating screenshot "%s"' % filename)
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename)
