"""Events that can occur

Use the constants rather than the text to avoid
breaking things in future releases.

"""

import sys
import re

import common
import serialize

# Occurs when one object collides with another
E_COLLISION = 'collision'

# Mouse events related to the left mouse button
#  - down is when the button is held down (fires continuously)
#  - up is when the button is released
#  - click is the mouse was down and then released
E_LEFT_MOUSE_DOWN = 'left-mouse-down'
E_LEFT_MOUSE_UP = 'left-mouse-up'
E_LEFT_CLICK = 'left-click'

# Mouse events related to the right mouse button
#  - down is when the button is held down (fires continuously)
#  - up is when the button is released
#  - click is the mouse was down and then released
E_RIGHT_MOUSE_DOWN = 'right-mouse-down'
E_RIGHT_MOUSE_UP = 'right-mouse-up'
E_RIGHT_CLICK = 'right-click'

# Mouse events related to the wheel
#  - wheel up the mouse wheel was moved up
#  - wheel down the mouse wheel was moved down
E_MOUSE_WHEEL_UP = 'wheel-up-click'
E_MOUSE_WHEEL_DOWN = 'wheel-down-click'

# Events related to actor and the world
E_ADDED_TO_WORLD = 'added-to-world'
E_REMOVED_FROM_WORLD = 'remove-from-world'

# Events related to the world or layers
#
# The world is activated when it 
# becomes the current world for the engine.
# The previously activated world is deactivated.
#
# Before and after render are triggered relative
# to rendering the whole world or the layer
E_ACTIVATE_WORLD = 'activate-world'
E_DEACTIVATE_WORLD = 'deactivate-world'
E_BEFORE_RENDER = 'before-render'
E_AFTER_RENDER = 'after-render'

# Events related to the keyboard
E_KEY_DOWN = 'key-down'
E_KEY_UP = 'key-up'
E_KEY_CLICKED = 'key-clicked'

# Events related to the engine
E_BEFORE_STOP = 'before-stop'  # The stop method has been called and the engine is about to quit
E_AFTER_STOP = 'after-stop'  # The stop method has been called and the engine is quiting

# Events related to movement
E_ACTOR_ARRIVED = 'actor-arrived'

# Events related to sound and music
E_TRACK_ENDED = 'track-ended'

# Drag and drop events
E_DRAG_START = 'drag-start'
E_DRAG_ENDED = 'drag-ended'
E_DROPPED_ON = 'dropped-on'

# Events related to entering information
E_ACCEPT_ENTRY = 'accept-entry'
E_GOT_FOCUS = 'got-focus'
E_LOST_FOCUS = 'lost-focus'

### The global event broadcasting system ###


class Broadcaster(common.EventAware):
    """The main event broadcaster"""
    
    strict = True
    
    def __init__(self):
        """Initialise the Broadcaster"""
        self.initEvents()
        

_broadcaster = Broadcaster()

def getEventBroadcaster():
    """Return the global broadcaster"""
    return _broadcaster


ALL_EVENTS = serialize.Bag()
finder = re.compile('E_[A-Z_]+$')
for name, obj in list(sys.modules[__name__].__dict__.iteritems()):
    if finder.match(name) and isinstance(obj, str):
        setattr(ALL_EVENTS, name, obj)
