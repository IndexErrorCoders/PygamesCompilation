"""Some effects which can alter properties of actors or visuals"""

import time
import math
import pygame
import random

import serge.serialize
import serge.actor
import serge.events


class InvalidMotion(Exception):
    """The motion type was not recognized"""


class Effect(serge.actor.Actor):
    """A generic effect"""

    my_properties = (
        serge.serialize.B('loop', False, 'whether we are looping or not'),
        serge.serialize.B('paused', False, 'whether we are paused or not'),
        serge.serialize.B('done', False, 'whether we are complete or not'),
        serge.serialize.B('persistent', False, 'whether we are retained after completing'),
    )

    def __init__(self, done=None, persistent=False):
        """Initialise the Effect"""
        super(Effect, self).__init__('effect')
        self.persistent = persistent
        self.done = done
        self.init()

    def init(self):
        """Initialise the effect"""
        self.paused = False
        self.done_recorded = False
        
    def pause(self):
        """Pause the effect"""
        self.paused = True
        
    def unpause(self):
        """Unpause the effect"""
        self.paused = False
        
    def restart(self):
        """Restart the effect"""
        self.current = self.start
        
    def finish(self):
        """End the effect"""
        self.current = self.end

    def _effectComplete(self, world):
        """Record the fact that we are done"""
        if self.done and not self.done_recorded:
            self.log.debug('Actor %s is calling the done method (%s)' % (self.getNiceName(), self.done))
            self.done_recorded = True
            self.done(self)
            self.log.debug('Actor %s completed the done method' % self.getNiceName())
        if not self.persistent:
            world.removeActor(self)
        

class Pause(Effect):
    """A simple pause
    
    Used in conjunction with other effects. Calls the done method when
    the pause has completed.
    
    """
    
    def __init__(self, time, done, persistent=False):
        """Initialise the Pause"""
        super(Pause, self).__init__(done, persistent)
        self.time = time
        self.time_passed = 0.0
        
    def updateActor(self, interval, world):
        """Update this effect"""
        #
        # Do not do anything if we are paused
        if self.paused:
            return
        #
        # Record passing of time
        self.time_passed += interval/1000.0
        if self.time_passed >= self.time:
            self._effectComplete(world)
            

class MethodCallFade(Effect):
    """Repeated call a method linearly changing the parameter over time
    
    The attribute changes between a start and an end with a decay.
    The decay is the length of time taken to get from the start to the end.
    
    If persistent is set to true then the effect remains in the world to be
    re-used. If false then it will be removed when completed.
    
    A method can be provided through the done parameter which will be called
    when the effect has completed.
    
    The way the variable is moved is dependent on the motion type. This can
    be 'linear' or 'accelerated'.
    
    """    

    def __init__(self, method, start, end, decay, persistent=False, done=None, motion='linear'):
        """Initialise the AttributeFade"""
        super(MethodCallFade, self).__init__(done, persistent)
        self.method = method
        self.start = start
        self.end = end
        self.decay = decay
        self.current = self.start
        if motion not in ('linear', 'accelerated'):
            raise InvalidMotion('The motion type "%s" was not understood. Should be "linear" or "accelerated"' % motion)
        self.motion = motion
        self.acceleration = float(self.end - self.start)/((self.decay/2.0)**2)
        self.velocity = 0.0
        self.gone = 0.0
        
    def updateActor(self, interval, world):
        """Update this effect"""
        #
        # Do not do anything if we are paused
        if self.paused:
            return
        #
        # Update the current 
        initial = self.current
        if self.motion == 'linear':
            self.current -= float(interval)/(self.decay*1000.0) * (self.start - self.end)
        else:
            #
            # Are we accelerating or decelerating
            if self.gone >= self.decay/2.0:
                factor = -1
            else:
                factor = +1
            self.current += self.velocity*(float(interval)/1000.0) + 0.5*self.acceleration*(float(interval)/1000.0)**2
            self.velocity += factor*self.acceleration*(float(interval)/1000.0)
        self.gone += interval/1000.0
        #
        # Watch for the end
        if (self.start > self.end) and (self.current <= self.end) or \
           (self.start < self.end) and (self.current >= self.end):        
            self.current = self.end 
            self._effectComplete(world)
        #
        self.method(self.current)
        


class AttributeFade(MethodCallFade):
    """Linearly move an attribute
    
    The attribute changes between a start and an end with a decay.
    The decay is the length of time taken to get from the start to the end.
    
    If persistent is set to true then the effect remains in the world to be
    re-used. If false then it will be removed when completed.
    
    """
    
    def __init__(self, obj, attribute_name, *args, **kw):
        """Initialise the AttributeFade"""
        super(AttributeFade, self).__init__(self._doIt, *args, **kw)
        self.obj = obj
        self.attribute_name = attribute_name
                
    def _doIt(self, value):
        """Set the value"""
        setattr(self.obj, self.attribute_name, value)



class ColourPhaser(Effect):
    """An effect that causes colours on the whole screen to fade in and out"""
    
    def __init__(self, red, green, blue, *args, **kw):
        """Initialise the effect
        
        Red, green and blue are parameters of the fading. They are three element tuples
        comprising,
            (low_amount, high_amount, period)
            
        The colour amount will cycle between the low amount and high amount over
        the given period (in seconds). The amounts are 0-255. 255 means no change in colour
        0 means the colour will dissapear.
        
        """
        super(ColourPhaser, self).__init__(*args, **kw)
        self.red = red
        self.green = green  
        self.blue = blue
        self._do_effect = False
        self.start_time = time.time()

    def addedToWorld(self, world):
        """We were added to a wolrd"""
        super(ColourPhaser, self).addedToWorld(world)
        #
        # Link up to events so we can control the effect
        self.renderer = serge.engine.CurrentEngine().getRenderer()
        self.renderer.linkEvent(serge.events.E_AFTER_RENDER, self.postRender)   
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.worldChange, True)     
        world.linkEvent(serge.events.E_DEACTIVATE_WORLD, self.worldChange, False)
        self._do_effect = True

    def worldChange(self, obj, active):
        """The world changed its state
        
        Since we are linked to a renderer event we will be called from all worlds
        but we only want to be active when our world is the ative one. We use
        the world activation events to toggle our state.
        
        """
        self._do_effect = active

    def postRender(self, obj, arg):
        """Update this effect"""
        #
        # Do not do anything if we are paused
        if self.paused or not self._do_effect:
            return
        #
        time_pos = time.time()-self.start_time
        self.renderer.getSurface().fill((
            self._effectAmount(self.red),
            self._effectAmount(self.green),
            self._effectAmount(self.blue)),
            special_flags=pygame.BLEND_RGBA_SUB)

    def _effectAmount(self, colour):
        """Return the amount of the effect"""
        low, high, period = colour
        return 255-0.5*(high + low) + (high - low)/2.0*math.cos(2*math.pi*(time.time()-self.start_time)/period)


class PanActor(Effect):
    """Pan an actor across the screen"""
    
    def __init__(self, actor, speed, done=None, persistent=False, linear=True):
        """Pan an actor across the screen"""
        super(PanActor, self).__init__(done, persistent)
        self.actor = actor
        self.speed = speed
        self.linear = linear
        self.sx, self.sy = actor.x, actor.y
    
    def restart(self):
        """Restart the panning"""
        renderer = serge.engine.CurrentEngine().getRenderer()
        x_gap = -(renderer.width - self.actor.width)/2
        self.low_x = renderer.width/2 - x_gap
        self.high_x = renderer.width/2 + x_gap
        y_gap = -(renderer.height - self.actor.height)/2
        self.low_y = renderer.height/2 - y_gap
        self.high_y = renderer.height/2 + y_gap
        #
        if self.low_x >= self.high_x:
            self.end_x = self.actor.x
        else:
            self.end_x = random.randrange(self.low_x, self.high_x)
        #        
        if self.low_y >= self.high_y:
            self.end_y = self.actor.y
        else:
            self.end_y = random.randrange(self.low_y, self.high_y)
        #
        self.done_recorded = False
        self.current_speed = 0.0
        
    def updateActor(self, interval, world):
        """Update the panning"""
        super(PanActor, self).updateActor(interval, world)
        #
        if self.paused:
            return
        #        
        v = serge.common.pymunk.Vec2d
        to_go = v(self.end_x, self.end_y) - v(self.actor.x, self.actor.y)
        #
        if self.linear:
            movement = self.speed*interval/1000.0
        else:
            if to_go.length < 100:
                self.current_speed = max(5.0, min(to_go.length, self.current_speed))
            else:
                self.current_speed = min(self.speed, self.current_speed+0.1)
            movement = self.current_speed*interval/1000.0  
        #
        # Can we get there in one go?
        if to_go.length < movement:
            movement = to_go.length
            finished = True
        else:
            finished = False
        #
        #
        # Work out how much to go
        this_move = to_go.normalized()*movement
        self.actor.move(*this_move)
        #
        if finished:
            self._effectComplete(world)
