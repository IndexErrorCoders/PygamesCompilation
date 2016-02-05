"""Blocks to make handling settings very easy"""

import sys
import os
import cPickle

import serge.common
import serge.serialize

class Bag(object):
    """A bag to store objects in"""
    
    def init(self, defaults=None):
        """Initialise the bag"""
        self.__defaults = defaults

    def __getattr__(self, name):
        """Get a value from the values Bag and if it is not there return it from the defaults instead"""
        try:
            return self.__dict__[name]
        except KeyError:
            if not name.startswith('__') and self.__defaults:
                try:
                    return self.__defaults.__dict__[name]
                except KeyError:
                    pass
        raise AttributeError
        
        
                
class Settings(serge.common.Loggable):
    """Handles settings"""

    def __init__(self, name):
        """Initialise the Settings"""
        self.addLogger()
        #
        self.name = name
        self.defaults = Bag()
        self.defaults.init()
        self.values = Bag()
        self.values.init(self.defaults)
        #
        # Set the default location
        var = 'HOME' if not sys.platform.startswith('win') else 'HOMEPATH'
        self._location = os.getenv(var)
        
    def setLocation(self, location):
        """Set the location to store and retrieve files from"""
        self._location = location
        
    def getLocation(self):
        """Return the location to store and retrieve files from"""
        return self._location
        
    def saveValues(self):
        """Serialize all the values to a file"""
        with file(os.path.join(self.getLocation(), '%s.%s' % (self.name, 'settings')), 'w') as f:
            cPickle.dump(self.values, f)
            
    def restoreValues(self):
        """Restore all the values from a file"""
        with file(os.path.join(self.getLocation(), '%s.%s' % (self.name, 'settings')), 'r') as f:
            self.values = cPickle.load(f)
            self.values.init(self.defaults)
    
    def safeRestoreValues(self):
        """Restore values if the file is there. If not just restore a blank set"""
        try:
            self.restoreValues()
        except (OSError, IOError):
            self.values = Bag()
            self.values.init(self.defaults)

