"""Handles in-betweening (tweening) of properties in the simulation"""

import random
import math


class Tween(object):
    """Tween a variable"""

    def __init__(self, obj, attribute, start, end, duration, function=None,
                 delay=0, after=None, repeat=False, ping_pong=True, integer=False,
                 set_immediately=True):
        """Initialise the tween"""
        self.obj = obj
        self.attribute = attribute
        self.start = start
        self.end = end
        self.function = function if function else Tween.linearTween
        self.duration = self.to_go = duration
        self.complete = False
        self.delay = delay
        self.after = after
        self.repeat = repeat
        self.ping_pong = ping_pong
        self.integer = integer
        if set_immediately:
            self.setValue(self.start)

    def doTween(self, dt):
        """Perform the tween"""
        #
        # Handle the delay
        if self.delay:
            self.delay -= dt
            if self.delay >= 0:
                return
            dt = abs(dt)
        #
        # Calculate the new value
        self.to_go -= dt
        if self.to_go <= 0:
            value = self.end
            self.complete = True
        else:
            value = self.function(1.0 - self.to_go / self.duration, self.start, self.end)
        #
        self.setValue(value)
        if self.complete and self.after:
            self.after()
        if self.complete and self.repeat:
            self.to_go = float(self.duration)
            self.complete = False
            if self.ping_pong:
                self.start, self.end = self.end, self.start

    def setValue(self, value):
        """Set the value"""
        setattr(self.obj, self.attribute, value if not self.integer else int(value))

    @staticmethod
    def linearTween(fraction, start, end):
        """Linear tween from start to end"""
        return fraction * (end - start) + start

    @staticmethod
    def sinOut(fraction, start, end):
        """Sine out tween"""
        return Tween.linearTween(math.sin(fraction * math.pi / 2.0), start, end)

    @staticmethod
    def sinInOut(fraction, start, end):
        """Sine out tween"""
        return Tween.linearTween((math.sin((fraction - 0.5) * math.pi) + 1.0) / 2, start, end)

    @staticmethod
    def colourTween(fraction, start, end):
        """Tween a colour"""
        return [Tween.linearTween(fraction, start[i], end[i]) for i in range(3)]

    @staticmethod
    def randomColour(fraction, start, end):
        """Tween a random colour"""
        colour = []
        for s, e in zip(start, end):
            if s == e:
                colour.append(s)
            else:
                if s > e:
                    s, e = e, s
                colour.append(random.randrange(s, e))
        return colour

