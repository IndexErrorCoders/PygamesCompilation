"""Some general utility functions"""

import random
import sys


class RandomGenerator(float):
    """Generates random numbers and can be used in place of a float

    You can pass this in place of a float and it will return the
    middle point. However if you call "float" on it then it will
    return a random number.

    """

    def __new__(cls, minimum, maximum, *args, **kwargs):
        """Create new instance"""
        return float.__new__(cls, 0.5 * (minimum + maximum))

    def __init__(self, minimum, maximum):
        """Initialise the value"""
        super(RandomGenerator, self).__init__(0.5 * (minimum + maximum))
        self.minimum = minimum
        self.maximum = maximum

    def __float__(self):
        """Return the value"""
        return random.uniform(self.minimum, self.maximum)


def getUID(text):
    """Return a unique ID, eg for an object name"""
    global _UID
    _UID += 1
    return text % _UID

_UID = 0