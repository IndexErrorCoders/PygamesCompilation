"""Dispatching events

This maybe should use pyglet's event framework but it isn't clear
how to do that cleanly in a short time!

TODO: fix event framework to be more pyglet-like

"""

import errors


# Common events
E_LEFT_CLICK = 'left-click'
E_RIGHT_CLICK = 'right-click'
E_MOUSE_RELEASE = 'mouse-release'
E_MOUSE_DRAG = 'mouse-drag'
E_MOUSE_SCROLL = 'mouse-scroll'
E_ACTOR_ADDED = 'actor-added'
E_ACTOR_REMOVED = 'actor-removed'
E_KEY_PRESS = 'key-press'
E_KEY_RELEASE = 'key-release'


class EventAware(object):
    """Event aware class"""

    def initEvents(self):
        """Initialise the event framework"""
        self.listening_for = {}

    def linkEvent(self, event, function, argument=None, important=False):
        """Link an event listener"""
        if not important:
            self.listening_for.setdefault(event, []).append((function, argument))
        else:
            self.listening_for.setdefault(event, []).insert(0, (function, argument))

    def processEvent(self, event, initiator):
        """Process an event"""
        if event in self.listening_for:
            for function, argument in self.listening_for[event]:
                #
                # Call handler and if handler returns a True then do not propagate any
                # more events
                if function(initiator, argument):
                    return True
            else:
                return False

    def unlinkEvent(self, event, function):
        """Unlink an event"""
        listeners = self.listening_for[event]
        for fn, arg in listeners[:]:
            if fn == function:
                listeners.remove((fn, arg))
                break
        else:
            raise errors.NotFound('Listener was not found for %s' % event)