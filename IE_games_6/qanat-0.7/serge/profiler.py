"""Stores profiling information to help optimize game times"""

import time

class NullProfiler(object):
    """A profiler that does nothing at all.
    
    This is used as the default profiler as it is fast.
    
    """

    def __init__(self):
        """Initialise the NullProfiler"""
        
    def getNames(self):
        """Return the actor names we have data on"""
        return []

    def getTags(self):
        """Return the actor tags we have data on"""
        return []
        
    def start(self, actor, activity):
        """Start an activity with an actor"""

    def end(self):
        """Start an activity with an actor"""
        
    def byName(self, name):
        """Return data for action by the name"""

    def byTag(self, tag):
        """Return data for action by the tag"""
   
   
class Profiler(NullProfiler):
    """A profiler to collect statistics from the game execution"""

    def __init__(self):
        """Initialise the Profiler"""
        self._data = {
            'names':{},
            'tags':{},
        }
        self._activities = []

    def getNames(self):
        """Return the actor names we have data on"""
        return self._data['names'].keys()

    def getTags(self):
        """Return the actor tags we have data on"""
        return self._data['tags'].keys()
        
    def start(self, actor, activity):
        """Start an activity with an actor"""
        self._activities.append((time.time(), actor, activity))
        
    def end(self):
        """Start an activity with an actor"""
        started, actor, activity = self._activities.pop()
        duration = time.time()-started
        #
        # Name
        record = self._data['names'].setdefault(actor.name, {})
        times, total = record.get(activity, (0, 0))
        record[activity] = (times+1, duration+total)
        #
        # Tag
        record = self._data['tags'].setdefault(actor.tag, {})
        times, total = record.get(activity, (0, 0))
        record[activity] = (times+1, duration+total)
        
    def byName(self, name):
        """Return data for action by the name"""
        return self._data['names'][name]
        
    def byTag(self, tag):
        """Return data for action by the tag"""
        return self._data['tags'][tag]

        
PROFILER = Profiler()
