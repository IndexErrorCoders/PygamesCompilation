"""Utilities to do with cardinal directions"""

from serge.simplevecs import Vec2d

N = 'n'
S = 's'
E = 'e'
W = 'w'
NE = 'ne'
NW = 'nw'
SE = 'se'
SW = 'sw'

_directions = {
    '': (0, 0),
    'n': (0, -1),
    'ne': (1, -1),
    'e': (1, 0),
    'se': (1, 1),
    's': (0, 1),
    'sw': (-1, 1),
    'w': (-1, 0),
    'nw': (-1, -1),
}

_angles = {
    N: 0,
    E: -90,
    W: +90,
    S: 180,
    NE: -45,
    NW: +45,
    SE: 135,
    SW: 225,
}

_reverse_directions = dict((v, e) for e, v in _directions.iteritems())


def getVectorFromCardinal(direction):
    """Return the vector for a cardinal direction"""
    return Vec2d(_directions[direction])


def getCardinalFromVector(vector):
    """Return the cardinal name from the vector"""  
    normalized = (vector[0]/abs(vector[0]) if vector[0] else 0, vector[1]/abs(vector[1]) if vector[1] else 0)
    return _reverse_directions[normalized]


def getCardinals():
    """Return the cardinal directions by name"""
    return _directions.keys()


def getOppositeVector(vector):
    """Return the opposite vector"""
    return vector[0]*-1, vector[1]*-1


def getOppositeCardinal(cardinal):
    """Return the opposite cardinal direction"""
    return getCardinalFromVector(getOppositeVector(getVectorFromCardinal(cardinal)))


def getAngleFromCardinal(direction):
    """Return the angle for a cardinal direction"""
    return _angles[direction]


def getAngleFromVector(vector):
    """Return the angle for a vector"""
    return getAngleFromCardinal(getCardinalFromVector(vector))


def getCardinalFromAngle(angle):
    """Return the cardinal for an angle"""
    for c, a in _angles.iteritems():
        if angle == int(a) or angle-360 == int(a) or angle+360 == int(a):
            return c
    raise KeyError('Angle not a cardinal: %s' % angle)

