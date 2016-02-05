"""Common parts of the framework"""

import logging
import sys

LEVEL = logging.DEBUG

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(relativeCreated)6d] :: %(levelname)7s %(name)20s :: %(message)s')
handler.setFormatter(formatter)


def getLogger(name):
    """Create a named logger"""
    l = logging.getLogger(name)
    l.addHandler(handler)
    l.setLevel(LEVEL)
    l.propagate = False
    return l


class Loggable(object):
    """A base class to use for logging etc"""

    def addLogger(self):
        """"Add a logger"""
        self.log = getLogger(self.__class__.__name__)


