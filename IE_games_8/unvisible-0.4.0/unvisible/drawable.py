"""Base class for drawable objects"""

import loggable
import slots

# Anchoring
A_TOP_MIDDLE = 'top-middle'
A_CENTER = 'center'
A_LEFT_MIDDLE = 'left-middle'


class Drawable(slots.Slot):
    """Something that can be drawn on the screen"""

    def __init__(self, x, y, width=None, height=None, surface=None, name=None, anchor=A_CENTER):
        """Initialise the drawable"""
        self.addLogger()
        self.x = x
        self.y = y
        self.anchor = anchor
        self.name = name if name else '%s[%s]' % (self.__class__.__name__, id(self))
        #
        # Set the surface and dimensions
        if not surface:
            self.surface = None
        else:
            self.surface = surface
            width, height = surface.get_size()
        #
        super(Drawable, self).__init__(x, y, width, height, name)

    def renderTo(self, surface, x=0, y=0):
        """Render this drawable onto the surface"""
        if self.surface and self.visible:
            if self.anchor == A_CENTER:
                pos = x + self.x - self.width / 2, y + self.y - self.height / 2
            elif self.anchor == A_TOP_MIDDLE:
                pos = x + self.x - self.width / 2, y + self.y
            elif self.anchor == A_LEFT_MIDDLE:
                pos = x + self.x, y + self.y - self.height / 2
            else:
                raise ValueError('Unknown anchor: %s' % self.anchor)
            surface.blit(self.surface, pos)

    def processClick(self, event_type, (x, y)):
        """Process a click event"""
        if self.active and self.visible:
            if (self.x - self.width / 2 <= x <= self.x + self.width / 2 and
                    self.y - self.height / 2 <= y <= self.y + self.height / 2):
                handled = self.handleClick(event_type)
                if handled:
                    return handled

    def handleClick(self, event_type):
        """Handle a click event"""
        self.log.debug('%s received click event %s' % (self.name, event_type))
        return False


class DrawableGroup(list, loggable.Loggable):
    """A group of drawables"""

    def __init__(self, items=None, x=0, y=0):
        """Initialise the group"""
        super(DrawableGroup, self).__init__(items if items else [])
        #
        self.addLogger()
        self.x = x
        self.y = y
        self.visible = True
        self.active = True

    def renderTo(self, surface, x=0, y=0):
        """Render the group"""
        if self.visible:
            for item in self:
                item.renderTo(surface, x + self.x, y + self.y)

    def processClick(self, event_type, (x, y)):
        """Process clicks"""
        if self.active and self.visible:
            for item in reversed(self):
                handled = item.processClick(event_type, (x + self.x, y + self.y))
                if handled:
                    return handled