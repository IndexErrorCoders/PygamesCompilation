"""Zones are part of worlds"""

import math

import common 
import serialize
import geometry
import profiler
pymunk = common.pymunk

class DuplicateActor(Exception): """An actor was already in the zone"""
class ActorNotFound(Exception): """Could not find the actor in the zone"""

# Use this to configure the Physics stepsize
PHYSICS_ITERATIONS = 10

class Zone(geometry.Rectangle, common.Loggable):
    """A zone
    
    A zone is part of a world. It is a container for objects
    and it controls whether objects will take part in world 
    updates.
    
    """
    
    my_properties = (
        serialize.B('active', False, 'whether the zone is active'),
        serialize.L('actors', set(), 'the actors in this zone'),
        serialize.F('physics_stepsize', 10.0, 'the size of physics steps in ms'),
        serialize.L('global_force', (0,0), 'the global force for physics'),
        serialize.F('_rtf', 1.0, 'debugging aid to slow down physics'),
    )
    
    def __init__(self):
        """Initialise the zone"""
        super(Zone, self).__init__()
        self.addLogger()
        self.physics_stepsize = 10.0
        self.global_force = (0,0)
        self.active = False
        self.setSpatial(-1000, -1000, 2000, 2000)
        self.clearActors()
        self._initPhysics()
        self._rtf = 1.0 # A debugging aid to slow down physics

    ### Serializing ###
    
    def init(self):
        """Initialise from serialized state"""
        self.addLogger()
        self.log.info('Initializing zone %s' % self)
        super(Zone, self).init()
        self._initPhysics()
        for actor in self.actors:
            actor.init()
            if actor.getPhysical():
                actor.getPhysical().init()
                self._addPhysicalActor(actor)
        

    ### Zones ###
    
    def updateZone(self, interval, world):
        """Update the objects in the zone"""
        #
        # Iterate through actors - use a list of the actors
        # in case the actor wants to update the list of
        # actors during this iteration
        for actor in list(self.actors):
            if actor.active:
                profiler.PROFILER.start(actor, 'updateActor')
                actor.updateActor(interval, world)
                profiler.PROFILER.end()
        #
        # Do physics if we need to
        if self._physics_objects:
            self.updatePhysics(interval)
    
    def wouldContain(self, actor):
        """Return True if this zone would contain the actor as it is right now
        
        The base Zone implementation uses spatial overlapping as the criteria but you
        can create custom zones that use other criteria to decide which actors should
        be in the zone.
        
        """
        return self.isOverlapping(actor)
    
    def addActor(self, actor):
        """Add an actor to the zone"""
        if actor in self.actors:
            raise DuplicateActor('The actor %s is already in the zone' % actor)
        else:
            self.actors.add(actor)
            if actor.getPhysical():
                self._addPhysicalActor(actor)

    def hasActor(self, actor):
        """Return True if the actor is in this zone"""
        return actor in self.actors
            
    def removeActor(self, actor):
        """Remove an actor from the zone"""
        try:
            self.actors.remove(actor)
        except KeyError:
            raise ActorNotFound('The actor %s was not in the zone' % actor)       
        else:
            if actor in self._physics_objects:
                self._physics_objects.remove(actor)
                p = actor.getPhysical()
                #
                # The try-catch here is probably not required but if the game
                # is playing around with the physics space then it might
                # remove something without alerting the zone so we catch it
                # here.
                try:
                    self.space.remove(p.body)
                    if p.shape:
                        self.space.remove(p.shape)
                except KeyError, err:
                    self.log.error('Actor %s already removed from physics space' % actor.getNiceName())
                
    def clearActors(self):
        """Remove all actors"""
        self.actors = set()
        
    ### Finding ###
    
    def findActorByName(self, name):
        """Return the actor with the given name"""
        for actor in self.actors:
            if actor.name == name:
                return actor
        else:
            raise ActorNotFound('Could not find actor "%s"' % name) 
    
    def findActorsByTag(self, tag):
        """Return all the actors with a certain tag"""
        return [actor for actor in self.actors if actor.tag == tag]
    
    def findFirstActorByTag(self, tag):
        """Return the first actor found with the given tag or raise an error"""
        for actor in self.actors:
            if actor.tag == tag:
                return actor
        else:
            raise ActorNotFound('Could not find actor with tag "%s"' % tag) 

    def getActors(self):
        """Return all the actors"""
        return self.actors

    ### Physics ###
    
    def _initPhysics(self):
        """Initialize the physics engine"""
        #
        # Pymunk may not be installed - if so then we skip creating any physics context
        if not common.PYMUNK_OK:
            self.log.debug('No pymunk - physics disabled')
            self._physics_objects = []
            return
        #
        # Create a context for the physics
        self.log.debug('Initializing physics engine with %d iterations' % PHYSICS_ITERATIONS)
        self.space = pymunk.Space(PHYSICS_ITERATIONS)
        self.space.add_collision_handler(2, 2, self._checkCollision, None, None, None)
        #
        # List of physics objects that we need to update
        self._physics_objects = []
        self._shape_dict = {}
                
    def _checkCollision(self, space, arbiter):
        """Return True if the collision should occur"""
        s1, s2 = arbiter.shapes[0], arbiter.shapes[1]
        self._collisions.append((s1, s2))
        return True 
    
    def _addPhysicalActor(self, actor):
        """Add an actor with physics to the zone"""
        p = actor.getPhysical()
        p.space = self.space
        if p.shape:
            self.space.add(p.body, p.shape)
            self._shape_dict[p.shape] = actor
        else:
            self.space.add(p.body)
        self._physics_objects.append(actor)
        actor.syncPhysics()
        
    def updatePhysics(self, interval):
        """Perform a step of the physics engine
        
        You do not normally need to call this method as it is called by the
        updateZone method. You may call this to advance the physics simulation
        along without affecting other game elements.
        
        """
        #
        # Globally applied forces
        self.space.gravity = self.global_force
        #
        # Do calculations
        self._collisions = []
        while interval > 0.0:
            togo = min(self.physics_stepsize, interval)
            self.space.step(togo/1000.0*self._rtf) # rtf is a debugging aid to go into slow motion mode
            interval -= togo
        #
        # Apply all the collisions
        for shape1, shape2 in self._collisions:
            actor1, actor2 = self._shape_dict[shape1], self._shape_dict[shape2]
            actor1.processEvent(('collision', actor2))
            actor2.processEvent(('collision', actor1))
        #
        # Now update all the tracked objects in world space
        for actor in self._physics_objects:
            p = actor.getPhysical()
            actor.moveTo(*p.body.position, no_sync=True, override_lock=True)
            p.velocity = tuple(p.body.velocity)
            if p.update_angle:
                actor.setAngle(-math.degrees(p.body.angle), override_lock=True)
            
    def setPhysicsStepsize(self, interval):
        """Set the maximum step size for physics calculations"""
        self.physics_stepsize = interval
        
    def setGlobalForce(self, force):
        """Set the global force for physics"""
        self.global_force = force

    def sleepActor(self, actor):
        """Tell the actor to go to sleep from a physics perspective
        
        The actor will still be visible and will still be updated but it
        will not update its physics. Useful for optimising when an actor
        does not need to interact with the physics simulation for a while.

        """
        actor.getPhysical().body.sleep()
        
    def wakeActor(self, actor):
        """Tell the actor to go to wake up from a physics perspective 
        
        An actor that was put to sleep (via sleepActor) will be woken
        up and take part in the physics simulation again.

        """
        actor.getPhysical().body.activate()


class TagIncludeZone(Zone):
    """A zone that includes any actor with a tag chosen from a list"""

    def __init__(self, tag_list):
        """Initialise the TagIncludeZone"""
        super(TagIncludeZone, self).__init__()
        self.tag_list = tag_list
            
    def wouldContain(self, actor):
        """Return True if this actor has the right tag"""
        return actor.tag in self.tag_list
        
        
class TagExcludeZone(Zone):
    """A zone that excludes any actor with a tag chosen from a list"""

    def __init__(self, tag_list):
        """Initialise the TagExcludeZone"""
        super(TagExcludeZone, self).__init__()
        self.tag_list = tag_list
            
    def wouldContain(self, actor):
        """Return True if this actor doesn't have a tag matching our list"""
        return actor.tag not in self.tag_list

