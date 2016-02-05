"""A world that simulates the real world but can run quicker"""

import time
import pygame

import serge.engine
import serge.world

from theme import G
import common


class SimulationWorld(serge.world.World):
    """A simulated world that can run quicker than real time"""

    def __init__(self, name, rtf, fps, options):
        """Initialise the world"""
        super(SimulationWorld, self).__init__(name)
        #
        self.log.info('Initialising simulation with rtf %d and fps as %d' % (rtf, fps))
        self.rtf = rtf
        self.fps = fps
        self.options = options
        self._last_render = 0.0
        self.paused = False
        self.store_action_replay = G('store-action-replay')
        self._action_replay = common.ACTION_REPLAY_FRAMES
        self._action_replay_rect = G('board-replay-rectangle')
        self._max_replay_frames = G('board-replay-max-frames')
        #
        # Stop the renderer from clearing each frame
        self.engine = serge.engine.CurrentEngine()
        self.renderer = self.engine.getRenderer()
        self.keyboard = self.engine.getKeyboard()
        self.clear_frame = self.renderer.preRender
        self._old_pre_render = self.renderer.preRender
        self.renderer.preRender = self.preRender

    def updateWorld(self, interval):
        """Update the world"""
        if not self.paused:
            super(SimulationWorld, self).updateWorld(interval * self.rtf)
        #
        # Cheating options
        if self.options.cheat:
            if self.keyboard.isClicked(pygame.K_p):
                self.paused = not self.paused
                self.log.info('Game %s' % 'paused' if self.paused else 'unpaused')

    def renderTo(self, renderer, interval):
        """Render the world if needed"""
        #
        # Do rendering if needed
        if time.time() - self._last_render >= 1.0 / self.fps:
            super(SimulationWorld, self).renderTo(renderer, interval)
            self._last_render = time.time()
        #
        # Store action replay
        if self.store_action_replay:
            self._action_replay.append(self.renderer.getSurface().subsurface(self._action_replay_rect).copy())
            if len(self._action_replay) > self._max_replay_frames:
                del(self._action_replay[:-self._max_replay_frames:])

    def preRender(self):
        """Pre-rendering"""
        if self.engine.getCurrentWorld().name in ('main-screen', 'action-replay-screen'):
            return
        self._old_pre_render()