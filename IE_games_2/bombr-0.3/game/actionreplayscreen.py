"""The action-replay screen for the game"""

import os
import time
import pygame


import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.layout
import serge.blocks.dragndrop

from theme import G, theme
import common


class ActionReplayScreen(serge.blocks.actors.ScreenActor):
    """The logic for the action-replay screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(ActionReplayScreen, self).__init__('item', 'action-replay-screen')
        self.options = options
        self.current_level = G('start-level')
        self._take_screenshots = G('auto-screenshots')
        self._screenshot_path = G('screenshot-path')
        self._screenshot_interval = G('screenshot-interval')
        self._last_screenshot = time.time() - self._screenshot_interval + 1.0
        #
        self._current_frame = 0
        self._framerate = 0
        self.frames = common.ACTION_REPLAY_FRAMES
        self.dragging = False

    def addedToWorld(self, world):
        """Added to the world"""
        super(ActionReplayScreen, self).addedToWorld(world)
        the_theme = theme.getTheme('action-replay-screen')
        L = the_theme.getProperty
         #
        # Background
        self.bg = serge.blocks.utils.addSpriteActorToWorld(
            world, 'bg', 'bg', 'replay-background',
            layer_name='background',
            center_position=(G('screen-width') / 2, G('screen-height') / 2),
        )
        #
        # A grid to hold the transport buttons
        self.transport_grid = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.layout.HorizontalBar('hbar', 'hbar', L('bar-width'), L('bar-height'),
                                              background_colour=L('bar-background-colour'),
                                              background_layer='main'),
            center_position=L('bar-position'),
            layer_name='ui',
        )
        #
        # The transport buttons themselves
        self.buttons = serge.actor.ActorCollection()
        for name in ('backward-btn-end', 'backward-btn-fast', 'backward-btn-normal', 'backward-btn-slow',
                     'forward-btn-stop', 'forward-btn-slow', 'forward-btn-normal', 'forward-btn-fast',
                     'forward-btn-end'):
            btn = self.transport_grid.addActor(serge.actor.Actor('btn', name))
            btn.setSpriteName(name)
            btn.setLayerName('ui')
            btn.linkEvent(serge.events.E_LEFT_CLICK, self.buttonClick, name)
            self.buttons.append(btn)
        #
        self.buttonClick(None, 'forward-btn-stop')
        #
        # Current frame
        self.frame_counter = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.FormattedText(
                'text', 'frame-counter',
                '%(current)d of %(total)d',
                L('current-colour'),
                font_name=L('current-font'), font_size=L('current-font-size'),
                current=0, total=len(self.frames), justify='center'
            ),
            layer_name='ui',
            center_position=L('current-position')
        )
        #
        # Slider for scrubbing
        self.slider_back = serge.blocks.utils.addSpriteActorToWorld(
            world, 'bg', 'slide-back', 'slider-back',
            center_position=L('slider-back-position'),
            layer_name='main'
        )
        self.slider = serge.blocks.utils.addSpriteActorToWorld(
            world, 'slider', 'slider', 'slider',
            center_position=L('slider-back-position'),
            layer_name='ui'
        )
        self.drag = serge.blocks.dragndrop.DragController()
        self.drag.addActor(
            self.slider, self.dragSlider, self.dropSlider,
            x_constraint=(self.slider_back.x - self.slider_back.width / 2, self.slider_back.x + self.slider_back.width / 2),
            y_constraint=(self.slider_back.y, self.slider_back.y)
        )
        world.addActor(self.drag)
        #
        # The main display of the replay
        self.replay = serge.blocks.utils.addActorToWorld(
            world, serge.actor.Actor('window', 'replay-window'),
            center_position=L('replay-position'),
            layer_name='main',
        )
        self.replay.visual = serge.visual.SurfaceDrawing(L('replay-width'), L('replay-height'))
        #
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.activateWorld)
        #
        # Cheating
        if self.options.cheat:
            fps = serge.blocks.utils.addActorToWorld(world,
                serge.blocks.actors.FPSDisplay(G('fps-x'), G('fps-y'), G('fps-colour'), G('fps-size')))

    def updateActor(self, interval, world):
        """Update this actor"""
        super(ActionReplayScreen, self).updateActor(interval, world)
        #
        # Update current frame
        frames_to_advance = interval * self._framerate / 1000.0
        self._current_frame += frames_to_advance
        if self._current_frame <= 0:
            self._current_frame = 0
            self.buttonClick(None, 'forward-btn-stop')
        elif self._current_frame >= len(self.frames):
            self._current_frame = len(self.frames) - 1
            self.buttonClick(None, 'forward-btn-stop')
        #
        # Current frame display
        self.frame_counter.setValue('current', self._current_frame)
        self.frame_counter.setValue('total', len(self.frames) - 1)
        #
        # Slider position
        self.slider.y = self.slider_back.y
        if self.dragging:
            px = (float(self.slider.x) - self.slider_back.x) / self.slider_back.width + 0.5
            px = min(1.0, max(0.0, px))
            self._current_frame = px * (len(self.frames) - 1)
        else:
            self.slider.x = self.slider_back.width * (self._current_frame / len(self.frames) - 0.5) + self.slider_back.x
        #
        # Set current frame to display
        self.replay.visual.setSurface(self.frames[int(self._current_frame)])
        #
        if self._take_screenshots:
            if time.time() - self._last_screenshot > self._screenshot_interval:
                filename = '%s-%s' % (self.name, time.strftime('%m-%d %H:%M:%S.png'))
                serge.blocks.utils.takeScreenshot(os.path.join(self._screenshot_path, filename))
                self._last_screenshot = time.time()
                self.log.debug('Taking screenshot - %s', filename)

    def buttonClick(self, obj, name):
        """A button was clicked"""
        #
        # Unselect all buttons
        for btn in self.buttons:
            btn.visual.setAlpha(0.5 if btn.name != name else 1.0)
        #
        # Set properties based on button
        if name == 'forward-btn-stop':
            self._framerate = 0
        elif name == 'forward-btn-end':
            self._current_frame = len(self.frames)
            self._framerate = 0
        elif name == 'backward-btn-end':
            self._current_frame = 0
            self._framerate = 0
        elif name == 'forward-btn-slow':
            self._framerate = G('replay-slow-fps', 'action-replay-screen')
        elif name == 'forward-btn-normal':
            self._framerate = G('replay-normal-fps', 'action-replay-screen')
        elif name == 'forward-btn-fast':
            self._framerate = G('replay-fast-fps', 'action-replay-screen')
        elif name == 'backward-btn-slow':
            self._framerate = -G('replay-slow-fps', 'action-replay-screen')
        elif name == 'backward-btn-normal':
            self._framerate = -G('replay-normal-fps', 'action-replay-screen')
        elif name == 'backward-btn-fast':
            self._framerate = -G('replay-fast-fps', 'action-replay-screen')

    def activateWorld(self, obj, arg):
        """The world was activated"""
        self._current_frame = len(self.frames) - 1
        self.buttonClick(None, 'forward-btn-stop')

    def dragSlider(self, obj, arg):
        """We started dragging the slider"""
        self.log.debug('Dragging the slider')
        self.dragging = True

    def dropSlider(self, obj, arg):
        """We dropped the slider"""
        self.log.debug('Stopped dragging the slider')
        self.dragging = False
        

def main(options):
    """Create the action-replay logic"""
    #
    # The screen actor
    s = ActionReplayScreen(options)
    world = serge.engine.CurrentEngine().getWorld('action-replay-screen')
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    manager.assignBehaviour(
        None,
        serge.blocks.behaviours.KeyboardBackWorld(sound_name='click'),
        'keyboard-back')
    if options.cheat:
        manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(pygame.K_q), 'keyboard-quit')
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

