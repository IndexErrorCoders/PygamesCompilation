import sys
import traceback
import logging
import re

version = '0.4.4.2'

#
# Number of channels of audio - pygame default is 8 but
# it looks like this can easily be reached and causes
# some sounds to cut out. The following number is large 
# enough to avoid that.
NUM_AUDIO_CHANNELS = 32

#
# Look for Pymunk
try:
    import pymunk
    #
    # Looks like the following is not needed on pymunk 2.1
    if hasattr(pymunk, 'init_pymunk'):
        pymunk.init_pymunk()
    PYMUNK_OK = True
except ImportError:
    import simplevecs as pymunk
    PYMUNK_OK = False

# The following needed for pygame and py2exe
try:
    import pygame._view
except ImportError:
    pass
    
DETAIL = 5

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

def addFileLogging():
    """Add file logging"""
    global LOG_TO_FILE, fhdlr
    LOG_TO_FILE = True
    fhdlr = logging.FileHandler('log.txt', 'w')
    fhdlr.setFormatter(formatter)
    
#logger.setLevel(logging.DEBUG)
logger.setLevel(DETAIL)
#logger.setLevel(logging.ERROR)

def tb():
    """Return the traceback as a string"""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return traceback.format_tb(exc_traceback)

def info(type, value, tb):
   if hasattr(sys, 'ps1') or not sys.stderr.isatty():
      # we are in interactive mode or we don't have a tty-like
      # device, so we call the default hook
      sys.__excepthook__(type, value, tb)
   else:
      import traceback, pdb
      # we are NOT in interactive mode, print the exception...
      traceback.print_exception(type, value, tb)
      print
      # ...then start the debugger in post-mortem mode.
      pdb.pm()

def installDebugHook():
    sys.excepthook = info
    
class BaseError(Exception):
    """A useful base class for errors"""
    
    def __init__(self, text):
        """Initialialise and add traceback"""
        super(BaseError, self).__init__(text + '\n' + ''.join(tb()))

LOG_TO_FILE = False
        
def getLogger(name):
    """Return a new logger with the name"""
    l = logging.getLogger(name)
    l.addHandler(hdlr)
    l.setLevel(logger.level)
    l.addFilter(filterer)
    if LOG_TO_FILE:
        l.addHandler(fhdlr)
    l.propagate = False
    return l


class Loggable(object):
    """A helper class that adds a logger to a class
    
    Each instance of the class will have a *log* attribute and can
    use this to log output. The `log` attrbute is a logger with the
    usual *debug*, *warn*, *info*, and *error* methods.
    
    """

    log = None

    def addLogger(self):
        """Add a logger"""
        if not 'log' in self.__class__.__dict__:
            self.__class__.log = getLogger(self.__class__.__name__)


class EventNotLinked(Exception): """The event was not linked to a callback"""
class EventNotFound(Exception): """The event was not a registered event"""
class DuplicateEvent(Exception): """An event was registered twice"""


class EventAware(object):
    """A mixin class that allows objects to respond to events"""

    # Legacy flag - set to True to enforce only registered events
    strict = False

    def initEvents(self):
        """Initialise the events system"""
        self._event_handlers = {}
        self._registered_events = set()

    def registerEvent(self, event):
        """Register an event"""
        if event in self._registered_events:
            raise DuplicateEvent('The event "%s" is already registered' % event)
        self._registered_events.add(event)
        
    def registerEvents(self, events):
        """Register a number of events"""
        for event in events:
            self.registerEvent(event)

    def registerEventsFromModule(self, module):
        """Register all events found in the module
        
        Events must be strings and their name must be of the 
        form E_THE_NAME
        
        ie: Begins with an 'E' and is all uppercase
        
        """
        finder = re.compile('E_[A-Z_]+$')
        for name, obj in module.__dict__.iteritems():
            if finder.match(name) and isinstance(obj, str):
                self.registerEvent(obj)
                          
    def processEvent(self, event):
        """Process an incoming event"""
        name, obj = event
        if self.strict and name not in self._registered_events:
            raise EventNotFound('The event "%s" was not registered' % name)
        #
        # Try to pass this off to a handler
        inhibits = set()
        try:
            links = self._event_handlers[name]
        except KeyError:
            new_inhibits = self.handleEvent(event)
            # Watch for new events to inhibit
            if new_inhibits:
                inhibits.add(new_inhibits)
        else:
            #
            # Process all the handler functions
            for callback, arg in links:
                new_inhibits = callback(obj, arg)
                # Watch for new events to inhibit
                if new_inhibits:
                    inhibits.add(new_inhibits)
        return inhibits
        
    def handleEvent(self, event):
        """Handle an incoming event"""
        pass
    
    def linkEvent(self, name, callback, arg=None):
        """Link an event to a callback"""
        if self.strict and name not in self._registered_events:
            raise EventNotFound('The event "%s" was not registered' % name)
        self._event_handlers.setdefault(name, []).append((callback, arg))
        
    def unlinkEvent(self, name, callback=None):
        """Unlink an event from a callback"""
        if self.strict and name not in self._registered_events:
            raise EventNotFound('The event "%s" was not registered' % name)
        if callback is None:
            try:
                del(self._event_handlers[name])
            except KeyError:
                raise EventNotLinked('No links to event "%s"' % name)
        else:
            #
            # Look for items with the same name and callback
            try:
                old_items, new_items = self._event_handlers[name], []
            except KeyError:
                raise EventNotLinked('No links to event "%s"' % name)
            #                
            for the_callback, arg in old_items:
                if the_callback != callback:
                    # This one is ok
                    new_items.append((the_callback, arg))
            #
            # Were any changed?
            if old_items == new_items:
                raise EventNotLinked('No links for event "%s" with callback "%s"' % (name, callback))
            #
            # Reset events
            self._event_handlers[name] = new_items