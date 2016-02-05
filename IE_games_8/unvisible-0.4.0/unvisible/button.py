"""Buttons to be clicked on"""

import os

import sprite


class Button(sprite.Sprite):
    """Represents a button"""

    def __init__(self, filename, x=0, y=0, callback=None, name=None):
        """Initialise the button"""
        super(Button, self).__init__(filename, x, y, name=name)
        #
        self.callback = callback

    def handleClick(self, event_type):
        """Handle that a click occurred"""
        self.log.info('%s button clicked' % self.name)
        if self.callback:
            return self.callback(self, event_type)
        else:
            return self


class OnOffButton(Button):
    """A button that can be toggled"""

    def __init__(self, *args, **kw):
        """Initialise the button"""
        super(OnOffButton, self).__init__(*args, **kw)
        #
        self.on_filename = '%s-on%s' % os.path.splitext(self.filename)

    def setState(self, state):
        """Set the state"""
        self.surface = self.loadImage(
            self.filename if not state else self.on_filename
        )