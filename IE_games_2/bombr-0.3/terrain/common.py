"""Some common utils"""

import re
import loggable

log = loggable.getLogger('evolution')


class ParsingFailed(Exception):
    """Parsing the input file failed"""


class BuilderError(Exception):
    """An error occurred while building"""


def getResult(root, tag, result_type, default=None):
    """Return an integer from a tag"""
    try:
        return result_type(root.find(tag).text)
    except Exception, err:
        if default is None:
            raise ParsingFailed("Failed parsing input for a '%s' tag: %s" % (tag, err))
        else:
            return default


def getInt(root, tag, default=None):
    """Return an integer from a tag"""
    return getResult(root, tag, int, default)


def getFloat(root, tag, default=None):
    """Return a float from a tag"""
    return getResult(root, tag, float, default)


def getString(root, tag, default=None):
    """Return a string from a tag"""
    return getResult(root, tag, str, default)


def getTuple(root, tag, default=None):
    """Return a tuple from a tag"""
    return tuple(map(int, re.findall('[\d.]+', getString(root, tag, default))))


def getFloatTuple(root, tag, default=None):
    """Return a tuple from a tag"""
    return tuple(map(float, re.findall('[\d.]+', getString(root, tag, default))))


def getTrue(root, tag, default=None):
    """Return True or False value of tag"""
    return getResult(root, tag, getTruthValue, default)


def getAttr(root, name, result_type, default=None):
    """Return an attribute from a tag"""
    try:
        return result_type(root.attrib[name])
    except Exception, err:
        if default is None:
            raise ParsingFailed("Failed parsing input for a '%s' attribute: %s" % (name, err))
        else:
            return default


def getIntAttr(root, name, default=None):
    """Return an integer attribute"""
    return getAttr(root, name, int, default)


def getStrAttr(root, name, default=None):
    """Return an string attribute"""
    return getAttr(root, name, str, default)


def getTupleAttr(root, tag, default=None):
    """Return a tuple from an attribute"""
    return tuple(map(int, re.findall('\d+', getStrAttr(root, tag, default))))


def getTrueAttr(root, name, default=None):
    """Return an truth attribute"""
    return getAttr(root, name, getTruthValue, default)


def getTruthValue(string):
    """Return True if the string represents Yes, True, On"""
    return string.strip().lower() in ('yes', 'true', 'on')
