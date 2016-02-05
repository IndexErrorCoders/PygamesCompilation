"""Slots for putting cards in on the screen"""

import loggable


class Slot(loggable.Loggable):
    """A placeholder for something on the screen which can be clicked"""

    def __init__(self, x, y, width, height, name=None):
        """Initialise the drawable"""
        self.addLogger()
        self.x = x
        self.y = y
        self.name = name if name else '%s[%s]' % (self.__class__.__name__, id(self))
        self.width = width
        self.height = height
        self.visible = True
        self.active = True

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


class ItemSlot(Slot):
    """A slot to put a card in"""

    def __init__(self, *args, **kw):
        """Initialise the slot"""
        super(ItemSlot, self).__init__(*args, **kw)
        #
        self.item = None

    def addItem(self, item):
        """Add a item to this slot"""
        item.x, item.y = self.x, self.y
        item.visible = True
        self.item = item

    def removeItem(self):
        """Remove the item from this slot"""
        self.item.visible = False
        self.item = None

    def isOccupied(self):
        """Return True if we are occupied"""
        return self.item is not None


class BaseItemSlots(loggable.Loggable):
    """A set of slots that are arranged in a certain way"""

    def __init__(self, x, y, width, height, number, gap, name):
        """Initialise the slots"""
        self.addLogger()
        self.name = name
        self.x = x
        self.y = y
        self.visible = True
        #
        self.slots = []
        for i in range(number):
            xp, yp = self.getPositionForIndex(i, number, gap)
            slot = ItemSlot(xp, yp, width, height)
            self.slots.append(slot)

    def getPositionForIndex(self, i, number, gap):
        """Return the position for the given slot index"""
        raise NotImplementedError

    def addItem(self, item):
        """Add an item to a free slot"""
        self.log.debug('Adding item "%s" to %s' % (item.name, self.name))
        for slot in self.slots:
            if not slot.isOccupied():
                slot.addItem(item)
                return
        else:
            raise IndexError('No free slots')

    def removeItem(self, item):
        """Remove an item"""
        self.log.debug('Removing item "%s" to %s' % (item.name, self.name))
        for slot in self.slots:
            if slot.item == item:
                slot.removeItem()
                return
        else:
            raise IndexError('Item not found in any slot')

    def removeAll(self):
        """Remove all items"""
        for slot in self.slots:
            if slot.isOccupied():
                slot.removeItem()

    def renderTo(self, surface, x=0, y=0):
        """Render these slots to the surface"""
        if self.visible:
            for slot in self.slots:
                if slot.isOccupied():
                    slot.item.renderTo(surface, x, y)

    def hasFreeSlot(self):
        """Return True if there is a free slot"""
        for slot in self.slots:
            if not slot.isOccupied():
                return slot
        else:
            return False

    def hasItem(self, of_type=None):
        """Return True if there is at least one item in here"""
        for slot in self.slots:
            if slot.isOccupied():
                if of_type is None or slot.item.card_type == of_type:
                    return True
        else:
            return False

    def getItem(self):
        """Return the first item"""
        for slot in self.slots:
            if slot.isOccupied():
                return slot.item
        else:
            raise IndexError('No items present')

    def processClick(self, event_type, (x, y)):
        """Process clicks"""
        if self.visible:
            for slot in self.slots:
                if slot.isOccupied():
                    handled = slot.item.processClick(event_type, (x, y))
                    if handled:
                        return handled


class HorizontalItemSlots(BaseItemSlots):
    """Show slots horizontally"""

    def getPositionForIndex(self, i, number, gap):
        """Return the position for the given slot index"""
        return self.x + (i - number / 2) * gap, self.y


class VerticalItemSlots(BaseItemSlots):
    """Show slots vertically"""

    def getPositionForIndex(self, i, number, gap):
        """Return the position for the given slot index"""
        return self.x, self.y + (i - number / 2) * gap


class PositionedSlots(BaseItemSlots):
    """A series of slots with individual positions"""

    def __init__(self, positions, width, height, name):
        """Initialise the slots"""
        self.positions = positions
        #
        super(PositionedSlots, self).__init__(0, 0, width, height, len(positions), 0, name)

    def getPositionForIndex(self, i, number, gap):
        """Return the position for a certain index"""
        return self.positions[i]