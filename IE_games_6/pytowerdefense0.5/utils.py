# -*- coding: utf-8 -*-
from math import sqrt
def get_Percentage(Max, Value):
    fraction = float(Value) / Max
    return fraction
def get_Distance(v1, v2):
    x = v1[0] - v2[0]
    y = v1[1] - v2[1]
    return sqrt(x**2 + y**2)

class Timer(object):
    """ A Timer that can periodically call a given callback
        function.

        After creation, you should call update() with the
        amount of time passed since the last call to update()
        in milliseconds.

        The callback calls will result synchronously during these
        calls to update()
    """
    def __init__(self, interval, callback, oneshot=False):
        """ Create a new Timer.

            interval: The timer interval in milliseconds
            callback: Callable, to call when each interval expires
            oneshot: True for a timer that only acts once
        """
        self.interval = interval
        self.callback = callback
        self.oneshot = oneshot
        self.time = 0
        self.alive = True

    def update(self, time_passed):
        if not self.alive:
            return

        self.time += time_passed
        if self.time > self.interval:
            self.time -= self.interval
            self.callback()

            if self.oneshot:
                self.alive = False