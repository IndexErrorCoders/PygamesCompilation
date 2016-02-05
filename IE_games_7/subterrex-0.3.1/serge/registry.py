"""A general registry for objects

This is used as a base class for other concrete types.

"""

import os
import serialize

class DuplicateItem(Exception): """The item was already registered"""
class UnknownItem(Exception): """The item was not found"""
class BadPath(Exception): """The base path was not a valid directory"""


class GeneralStore(serialize.Serializable):
    """Stores things"""
    
    my_properties = (
        serialize.S('base_path', '', 'the base location to find files'),
        serialize.L('raw_items', [], 'the items we have registered'),
    )
    
    def __init__(self):
        """Initialize the store"""
        self.items = {}
        self.raw_items = []
        self.base_path = ''

    def init(self):
        """Initialise from serialized form"""
        self.items = {}
        old_items, self.raw_items = self.raw_items, []
        for item in old_items:
            self.registerItem(*item)
        
    def setPath(self, path):
        """Set our base path to locate images"""
        if not os.path.isdir(path):
            raise BadPath('The path %s is not a directory' % path)
        self.base_path = path
        
    def _resolveFilename(self, name):
        """Return the name to a file"""
        if os.path.isfile(name):
            return name
        else:
            return os.path.join(self.base_path, name)
        
    def registerItem(self, name, *args, **kw):
        """Register an item"""
        #
        # Make sure we only register once
        if name in self.items:
            raise DuplicateItem('The item named "%s" is already registered' % name)
        #
        return self._registerItem(name, *args, **kw)
        
    def getItems(self):
        """Return all the items"""
        return self.items.values()

    def getItemDefinitions(self):
        """Return all the item definitions"""
        return self.raw_items
    
    def clearItems(self):
        """Clear all the items"""
        self.items = {}
        self.raw_items = []
        
    def removeItem(self, name):
        """Remove the named item"""
        try:
            del(self.items[name])
        except KeyError:
            raise UnknownItem('The item "%s" was not in the collection' % name)
        self.raw_items = [item for item in self.raw_items if item[0] != name]
        
    def getNames(self):
        """Return the names of all the items"""
        return self.items.keys()

    def getItem(self, name):
        """Return an item"""
        try:
            return self.items[name]
        except KeyError:
            raise UnknownItem('The item called "%s" could not be found' % name)
        
    def duplicateItem(self, name, new_name):
        """Create a duplicate of the named item with a new name"""
        #
        # Find parameters of this item
        self.items[new_name] = self.getItem(name)
