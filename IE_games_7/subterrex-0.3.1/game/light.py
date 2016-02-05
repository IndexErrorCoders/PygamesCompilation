"""Implements a light mask"""

import pygame
from scipy import signal, ndimage
import Queue
import random
import time

import serge.visual
import serge.actor
import serge.blocks.visualblocks
import serge.blocks.visualeffects
import serge.blocks.worker

from theme import G, theme
import common 

# Update needed flag
U_NOT_NEEDED = 0
U_NEED_FAST = 1
U_NEED_RIGOROUS = 2

class LightMask(serge.actor.Actor):
    """A light mask"""

    def __init__(self, tag, name, base_colour):
        """Initialise the LightMask"""
        super(LightMask, self).__init__(tag, name)
        #
        self.base_colour = base_colour
        self.mask = serge.blocks.visualblocks.Rectangle((G('cave-horizontal-screens')*G('screen-width'), 
                G('cave-vertical-screens')*G('screen-height')), base_colour)
        self.visual = serge.blocks.visualblocks.Rectangle((G('cave-horizontal-screens')*G('screen-width'), 
                G('cave-vertical-screens')*G('screen-height')), base_colour)
        self.blur = G('light-blur')
        #
        # Worker to do our hard work - define this worker at the class
        # level to make sure we only have one
        if not hasattr(LightMask, 'queue_todo'):
            LightMask.queue_todo, LightMask.queue_done, _ = \
                serge.blocks.worker.getSurfaceProcessingPipeline(doWork)
        #
        self.light_guid = 0
        self.light_images = []
        #
        self.clearSources()        
        
    def updateActor(self, interval, world):
        """Update the mask"""
        super(LightMask, self).updateActor(interval, world)
        #
        new_image = False
        #
        if self._update_needed != U_NOT_NEEDED:
            self.log.info('Requesting new surface (need is %s)' % self._update_needed)
            self.updateVisual(self._update_needed)
        #
        try:
            result, guid, fast_calculate, report = self.queue_done.get(False)
        except Queue.Empty:
            pass
        else:
            if guid == self.light_guid:
                self.log.info('Got new surface (%s) [guid %s]' % (report, guid))
                self.light_images.append(serge.blocks.worker.unmarshallSurface(*result))
                new_image = True
            else:
                self.log.debug('Rejecting old surface with guid %s' % guid)
        #
        if new_image or (self.light_images and random.random() < G('light-refresh-probability')):
            self.updateSurfaceDisplay()
        #
        # Watch for the fast calculated one - if we got it then ask
        # for the better one
        if new_image and fast_calculate:
            self.log.info('Surface was fast-calculated. Requesting rigorous one now')
            self.updateVisual(U_NEED_RIGOROUS)
                    
    def updateSurfaceDisplay(self):
        """Update the actual visual we are using"""
        self.visual.setSurface(random.choice(self.light_images))
    
        
    def addSource(self, (x, y), sprite):
        """Add a light source"""
        self.sources.append(((x, y), sprite))
        if self._update_needed == U_NOT_NEEDED:
            self._update_needed = U_NEED_FAST
        
    def setSources(self, sources):
        """Set all light sources"""
        self.clearSources()
        for source in sources:
            self.addSource(*source)
            
    def clearSources(self, need=U_NEED_FAST):
        """Clear all sources"""
        self.sources = []
        self._update_needed = need
        
    def updateVisual(self, need=U_NEED_FAST):
        """Update the visual representation"""
        self.light_guid += 1
        self.light_images = []
        use_rigorous = (need == U_NEED_RIGOROUS)
        self.queue_todo.replace((serge.blocks.worker.marshallSurface(self.mask.getSurface()), 
                self.sources, self.blur, self.light_guid, use_rigorous))
        for idx in range(G('light-number-renders')-1):
            self.queue_todo.put((serge.blocks.worker.marshallSurface(self.mask.getSurface()), 
                self.sources, self.blur, self.light_guid, use_rigorous))
        self._update_needed = U_NOT_NEEDED

    def isReady(self):
        """Return True if the light evaluation is ready"""
        return len(self.light_images) != 0
        


def doWork(surface, sources, blur, guid, use_rigorous):
    """A worker thread to do work"""
    start_time = time.time()
    #
    pos_jitter = G('light-position-jitter')
    alpha_jitter = G('light-opacity-jitter')
    alpha_jitter_min = G('light-opacity-jitter-min')
    #
    # We are going to keep track of the dirty rectangle so that we can optimize the
    # speed of the gaussian filter (its speed is very dependendent on the size of
    # the region you are bluring)
    dirty_x = []
    dirty_y = []
    mx, my = surface.get_size()
    #
    # Now put all the sources on there
    for (x, y), ((w, h), (r, g, b, alpha)) in sources:
        #
        # Look for dirty parts of the image
        lr, lg, lb, la = doWork.last_sources.get((x,y), (None,None,None,None))
        if la is not None:
            if abs(lr-r)+abs(lg-g)+abs(lb-b)+abs(la-alpha) > 10:
                dirty_x.append(x)
                dirty_y.append(y)
        else:
            dirty_x.append(x)
            dirty_y.append(y)
        #
        # Get the light for the current square
        if alpha > alpha_jitter_min:
            alpha = max(0, min(255, random.uniform(alpha-alpha_jitter, alpha+alpha_jitter)))
        sprite_surf = serge.blocks.visualblocks.Rectangle((w, h), (r, g, b, 255-alpha)).getSurface()
        #
        # Include some jitter in the lights
        ax = random.uniform(x-pos_jitter, x+pos_jitter)
        ay = random.uniform(y-pos_jitter, y+pos_jitter)
        #
        # Place on the surface
        surface.blit(
                sprite_surf,    
                (ax-sprite_surf.get_width()/2, ay-sprite_surf.get_height()/2),
                special_flags=pygame.BLEND_RGBA_ADD)
        #
        doWork.last_sources[(x,y)] = (r,g,b,alpha)
    #
    render_time = time.time() - start_time
    #
    # Evaluate dirty area
    if dirty_x:
        # New dirty area
        bw = bh = G('light-dirty-boundary')
        partly_dirty, lx, ly, hx, hy = True, max(0,min(dirty_x)-bw), max(0,min(dirty_y)-bh),  \
            min(mx, max(dirty_x)+bw), min(my, max(dirty_y)+bh)
        doWork.last_dirty = lx, ly, hx, hy
        dirty = '%s, %s, %s, %s' % (lx, ly, hx, hy)
    elif doWork.last_dirty:
        # Same as last time
        partly_dirty = True
        lx, ly, hx, hy = doWork.last_dirty
        dirty = '%s, %s, %s, %s (cached)' % (lx, ly, hx, hy)
    else:
        # Whole screen is dirty
        partly_dirty = False
        dirty = 'all'
    #
    fast_calculate = False
    #
    # Blur the surface
    if blur:
        ablur = random.uniform(blur-G('light-blur-jitter'), blur+G('light-blur-jitter'))
        #
        # Blur all or just the dirty area
        if use_rigorous or not partly_dirty or not doWork.last_result or doWork.last_dirty is None or not G('light-use-dirty-algorithm'):
            # Blur the whole surface
            surface = serge.blocks.visualeffects.gaussianBlur(surface, ablur)
        else:
            # Partial blur
            section = surface.subsurface((lx, ly, hx-lx, hy-ly))
            #pygame.image.save(section, 'sandbox/section-%d.png' % doWork.count)
            part = serge.blocks.visualeffects.gaussianBlur(section, ablur)
            #pygame.image.save(part, 'sandbox/part-%d.png' % doWork.count)
            surface = doWork.last_result
            #pygame.image.save(surface, 'sandbox/last-result-%d.png' % doWork.count)
            surface.fill(G('light-mask-colour'), (lx, ly, hx-lx, hy-ly))
            surface.blit(part, (lx, ly))
            #pygame.image.save(surface, 'sandbox/surface-%d.png' % doWork.count)
            #
            fast_calculate = True
            doWork.count += 1
    #
    blur_time = time.time() - start_time - render_time
    #
    # Cache the results to short circuit evaluation
    doWork.last_result = surface
    #
    return (surface, guid, fast_calculate, 'render %s, blur %s, dirty %s' % (render_time, blur_time, dirty))

doWork.last_sources = {}
doWork.last_result = None
doWork.last_dirty = None
doWork.count = 0

class Light(object):
    """Represents a light"""

        
class ColouredLight(object):
    """Represents a light source that is coloured"""
    
    def __init__(self, x, y, strength, colour, distance, light_type='light'):
        """Initialise the light"""
        self.x = x
        self.y = y
        self.strength = strength
        self.colour = colour
        self.distance = distance
        self.light_type = light_type
        
        
