'''A class for storing triggers affecting gameplay.
Flip triggers and also level editing triggers in the future.'''

class Trigger:

    def __init__(self, trigger_type, x, y, tilex = None, tiley = None):
        self.trigger_type = trigger_type
        self.x = x
        self.y = y
        self.tilex = tilex
        self.tiley = tiley
        return
