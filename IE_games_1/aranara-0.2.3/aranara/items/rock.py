"""Represents a rock

Rocks are used to block the way and need to be cleared out

"""

from .. import engine
import item


class Rock(item.BaseItem):
    """Represents a rock"""

    def __init__(self, name, sprite_name, *args, **kw):
        """Initialise the rock"""
        super(Rock, self).__init__(name, sprite_name, *args, **kw)
