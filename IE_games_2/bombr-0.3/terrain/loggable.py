"""Copy of the serge logger so that this module can be independent of serge"""

import logging
import sys


class Filtering(logging.Filter):
    """A nice filtering formatter than can show certain types of log"""

    not_allowed = set([
    ])

    def filter(self, record):
        """Format the record"""
        return record.name not in self.not_allowed

filterer = Filtering()
log = logger = logging.getLogger('serge')
hdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(relativeCreated)6d] :: %(levelname)7s %(name)20s :: %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.addFilter(filterer)

DETAIL = 5

logger.setLevel(log.level)


def getLogger(name):
    """Return a new logger with the name"""
    l = logging.getLogger(name)
    l.addHandler(hdlr)
    l.setLevel(logger.level)
    l.addFilter(filterer)
    l.propagate = False
    return l


class Loggable(object):
    """A helper class that adds a logger to a class

    Each instance of the class will have a *log* attribute and can
    use this to log output. The `log` attribute is a logger with the
    usual *debug*, *warn*, *info*, and *error* methods.

    """

    log = None

    def addLogger(self):
        """Add a logger"""
        if not 'log' in self.__class__.__dict__:
            self.__class__.log = getLogger(self.__class__.__name__)