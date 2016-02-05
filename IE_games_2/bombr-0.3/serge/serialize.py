"""The serialization logic"""

import cPickle
import copy

class InvalidFile(Exception): """The file used to thaw an item was not a valid serialized file"""


class Bag(object):
    """Bag to hold properties"""

    def __init__(self, **kw):
        """Initialise the bag"""
        for name, value in kw.iteritems():
            setattr(self, name, value)

    
# Types

class Int(int):
    """An int"""

class Float(float):
    """An float"""

class String(str):
    """A str"""

class List(list):
    """A list"""
    
class Dict(dict):
    """A dict"""
    
class Bool(int):
    """A boolean"""

class Obj(object):
    """An object"""
    
def initType(item, name, description=None):
    """Initialize the type"""
    item.name = name
    item.description = description if description else name
        
def I(name, value, description=None):
    v = Int(value)
    initType(v, name, description)
    return v

def F(name, value, description=None):
    v = Float(value)
    initType(v, name, description)
    return v

def S(name, value, description=None):
    v = String(value)
    initType(v, name, description)
    return v
        
def L(name, value, description=None):
    v = List(value)
    initType(v, name, description)
    return v

def D(name, value, description=None):
    v = Dict(value)
    initType(v, name, description)
    return v

def B(name, value, description=None):
    v = Bool(value)
    initType(v, name, description)
    return v

def O(name, value, description=None):
    v = Obj()
    initType(v, name, description)
    return v


class Serializable(object):
    """A mixing class to help serialize and deserialize objects"""
    
    # This is where you put the properties that your object has
    # This should be a list of tuples
    #      name, default value, type, description
    my_properties = ()
    
    
    @classmethod    
    def createInstance(cls):
        """Return an instance of the class with all default properties set"""
        instance = cls()
        instance.__setstate__()
        return instance
    
    @classmethod
    def _getProperties(cls):
        """Get the properties all the way up the inheritance tree"""
        props = dict([(obj.name, obj) for obj in cls.my_properties])
        for the_cls in cls.__bases__:
            if issubclass(the_cls, Serializable):
                for key, value in the_cls._getProperties():
                    if key not in props:
                        props[key] = value
        return props.iteritems()

    def __getstate__(self):
        """Return the live properties suitable for pickling"""
        values = []
        for name, _ in self.__class__._getProperties():
            values.append((name, getattr(self, name)))
        return values 
    
    def __setstate__(self, state=None):
        """Initialize the object to the given state for unpickling"""
        self.initial_properties = Bag()
        #
        # Initialize first from the defaults and then from the live state
        for this_state in (self.__class__._getProperties(), state):
            if this_state:
                for name, value in this_state:
                    setattr(self, name, value)
                    setattr(self.initial_properties, name, value)
        
    def asString(self):
        """Return the properties of this object as a string"""
        return cPickle.dumps(self, protocol=2)

    def toFile(self, filename):
        """Store this object in a file"""
        with file(filename, 'wb') as f:
            f.write(self.asString())
                
    @classmethod
    def fromString(cls, text):
        """Return a new instance from a string"""
        obj = cPickle.loads(text)
        obj.init()
        return obj

    @classmethod
    def fromFile(cls, filename):
        """Return a new instance from a file"""
        with file(filename, 'rb') as f:
            try:
                return cls.fromString(f.read())
            except Exception, err:
                raise InvalidFile('Failed to load data from file "%s": %s' % (filename, err))
       
    def init(self):
        """Implement this method to do any object initialization after unpickling"""
        pass
    
    def copy(self):
        """Return another copy of this item"""
        return self.fromString(self.asString())
    
    
class SerializedBag(object):
    """A bag that can be serialized"""
    
    def __init__(self, **kw):
        """Initialise the bag"""
        for name, value in kw.iteritems():
            setattr(self, name, value)


    def init(self):
        """Initialise - here to meet the Serialized protocol"""
        pass
        
    def copy(self):
        """Return a copy"""
        return copy.deepcopy(self)
               
