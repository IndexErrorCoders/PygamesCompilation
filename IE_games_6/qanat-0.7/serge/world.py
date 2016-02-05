"""The main world definition"""

import common
import zone
import serialize
import geometry
import events 
import actor
import profiler

class UnknownActor(Exception): """Could not find the actor"""
class DuplicateActor(Exception): """The actor was already in the world"""
class DuplicateZone(Exception): """The zone was already in the world"""

class World(common.Loggable, serialize.Serializable, common.EventAware):
    """The main world object
    
    The :doc:`engine` will control main worlds. Each world has a number
    of :doc:`zone` which contain :doc:`actor`.
    
    """

    my_properties = (
        serialize.S('name', '', 'the name of this world'),
        serialize.L('zones', set(), 'the zones in this world'),
        serialize.L('unzoned_actors', set(), 'the actors not in any zone in this world'),
    )    
        
    def __init__(self, name):
        """Initialise the World"""
        self.addLogger()
        self.initEvents()
        self.name = name
        self.engine = None
        self.zones = set()
        self.unzoned_actors = set() # Actors get put here if then end up in no zone
        self.event_handlers = {}
        self.init()
        
    ### Serializing ###
    
    def init(self):
        """Initialise from serialized state"""
        self.addLogger()
        self.initEvents()
        self.log.info('Initializing world %s' % self.name)
        super(World, self).__init__()
        self.engine = None
        #
        # This list is used to order the processing of actors in rendering. The 
        # flag is used to tell us when we need to resort them
        self._sorted_actors = []
        self._actors_need_resorting = False
        self._scheduled_deletions = set()
        #
        # Now process actors
        for zone in self.zones:
            zone.init()
        for actor in self.unzoned_actors:
            actor.init()

    ### Zones ###
    
    def addZone(self, zone):
        """Add a zone to the world"""
        if zone in self.zones:
            raise DuplicateZone('The zone %s is already in the world' % zone)
        else:
            self.zones.add(zone)
        self._actors_need_resorting = True
        
    def clearZones(self):
        """Remove all the zones"""
        self.zones = set()
        
    ### Main ###
                
    def updateWorld(self, interval):
        """Update the objects in the world"""
        for zone in self.zones:
            if zone.active:
                zone.updateZone(interval, self)
        #
        # Process any scheduled actor deletions
        while self._scheduled_deletions:
            try:
                self.removeActor(self._scheduled_deletions.pop())
            except UnknownActor:
                # Ok, the actor must have been removed directly
                pass

    def setEngine(self, engine):
        """Set the engine that we are owned by"""
        self.engine = engine

    def getEngine(self):
        """Return the engine that we are owned by"""
        return self.engine
        
    def findActorsByTag(self, tag):
        """Return all the actors in all zones based on the tag"""
        results = actor.ActorCollection()
        for z in self.zones:
            results.extend(z.findActorsByTag(tag))
        return results    
    
    def findActorByName(self, name):
        """Return the actor with the give name in all zones"""
        for z in self.zones:
            try:
                return z.findActorByName(name)
            except zone.ActorNotFound:
                pass
        else:
            raise zone.ActorNotFound('Unable to find actor named "%s" in any zone' % name)

    def findActorsAt(self, x, y):
        """Return the actors at a certain location"""
        actors = actor.ActorCollection()
        test = geometry.Point(x, y)
        for the_actor in self.getActors():
            if test.isInside(the_actor):
                actors.append(the_actor)
        return actors
        
    def getActors(self):
        """Return all the actors"""
        actors = actor.ActorCollection(self.unzoned_actors)
        for z in self.zones:
            actors.extend(z.getActors())
        return actors
      
    def rezoneActors(self):
        """Move actors to the right zone based on their spatial location"""
        #
        # Start with a list of actors to find homes for based on any that
        # were not in any zones at all
        moved = self.unzoned_actors
        self.unzoned_actors = set()
        #
        # Find all the actors that are no longer in the right zone
        # and remove them from their current zone
        for z in self.zones:
            for actor in z.actors.copy():
                if not actor.isOverlapping(z):
                    z.removeActor(actor)
                    moved.add(actor)
        #
        # Now find the place for the moved actors
        for actor in moved:
            self.addActor(actor)
            
    def clearActors(self):
        """Clear all the actors"""
        self.clearActorsExceptTags([])

    def clearActorsExceptTags(self, tags):
        """Clear all actors except the ones with a tag in the list of tags"""
        for actor in self.getActors():
            if actor.tag not in tags:
                try:
                    self.removeActor(actor)
                except UnknownActor:
                    # Can be called if a composite actor removes their own children
                    pass
        for actor in list(self.unzoned_actors):
            if actor.tag not in tags:
                self.unzoned_actors.remove(actor)

    def clearActorsWithTags(self, tags):
        """Clear all actors with a tag in the list of tags"""
        for actor in self.getActors():
            if actor.tag in tags:
                try:
                    self.removeActor(actor)
                except UnknownActor:
                    # Can be called if a composite actor removes their own children
                    pass
        for actor in list(self.unzoned_actors):
            if actor.tag not in tags:
                self.unzoned_actors.remove(actor)
       
        
    def addActor(self, actor):
        """Add an actor to the world"""
        #
        self.log.debug('Adding %s to world %s' % (actor.getNiceName(), self.name))
        #
        # Make sure the actor isn't already here
        if self.hasActor(actor):
            raise DuplicateActor('The actor %s is already in the world' % actor.getNiceName())
        #
        # Try to put the actor in the right zone
        for z in self.zones:
            if z.wouldContain(actor):
                z.addActor(actor)
                break
        else:
            # The actor is not in any zones, store for later
            self.unzoned_actors.add(actor)
        #
        # Tell the actor about it
        actor.addedToWorld(self)
        #
        self._actors_need_resorting = True
        #
        return actor
        
    def removeActor(self, actor):
        """Remove the actor from the world"""
        self.log.debug('Removing "%s" actor (%s)' % (actor.tag, actor.getNiceName()))
        #
        self._actors_need_resorting = True
        #
        # Try to remove from zones
        for z in self.zones:
            if z.hasActor(actor):
                z.removeActor(actor)
                break
        else:
            #
            # We didn't find it in the zone - maybe in the unzoned
            if actor in self.unzoned_actors:
                self.unzoned_actors.remove(actor)
            else:
                raise UnknownActor('The actor %s was not found in the world' % actor)
        #
        # Tell the actor about it
        actor.removedFromWorld(self)

    def scheduleActorRemoval(self, actor):
        """Remove an actor at the end of the next update for the world
        
        This method can be used to safely remove an actor from the world
        during the execution of the world update. It can sometimes be
        useful to do this when inside logic that is iterating over actors
        or inside the updateWorld event loop.
        
        """
        self._scheduled_deletions.add(actor)

    def hasActor(self, actor):
        """Return True if this actor is in the world"""
        #
        # Try to remove from zones
        for z in self.zones:
            if z.hasActor(actor):
                return True
        #
        # We didn't find it in the zone - maybe in the un-zoned
        return actor in self.unzoned_actors

    def requestResortActors(self):
        """Request that actors are resorted the next time we render

        Call this if you have adjusted the rendering order of actors

        """
        self._actors_need_resorting = True

    def renderTo(self, renderer, interval):
        """Render all of our actors in active zones"""
        #
        # Watch out in case we need to reorder our actors
        if self._actors_need_resorting:
            self.log.debug('Sorting actors now')
            self._sorted_actors = renderer.orderActors(self.getActors())
            self._actors_need_resorting = False
        #
        camera = renderer.getCamera()
        self.processEvent((events.E_BEFORE_RENDER, self))
        #
        # Render all of the actors
        for actor in self._sorted_actors:
            if actor.active and actor.visible:
                profiler.PROFILER.start(actor, 'renderActor')
                try:
                    actor.renderTo(renderer, interval)
                except Exception, err:
                    self.log.error('Failed rendering "%s" actor "%s": %s' % (actor.tag, actor, err))
                    raise
                profiler.PROFILER.end()
        #
        self.processEvent((events.E_AFTER_RENDER, self))

    def setZoom(self, zoom, x, y):
        """Set the visual zoom on this world to zoom centered on x, y"""
        for actor in self.getActors():
            actor.setZoom(zoom) 
            
    ### Events ###
    
    def processEvents(self, events):
        """Handle the events"""
        inhibited = set()
        for (event, obj), actor in events:
            if actor.active and not event in inhibited:
                # Process the event
                new_inhibits = actor.processEvent((event, obj))
                # Record if we need to inhibit further events of a certain type
                if new_inhibits:
                    inhibited.update(new_inhibits)

    def activateWorld(self):
        """Called when the world is set as the current world"""
        self.processEvent((events.E_ACTIVATE_WORLD, self))
                
    def deactivateWorld(self):
        """Called when the world is deactivated"""
        self.processEvent((events.E_DEACTIVATE_WORLD, self))
        
    ### Physics ###
    
    def setPhysicsStepsize(self, interval):
        """Set the maximum step size for physics calculations"""
        for z in self.zones:
            z.setPhysicsStepsize(interval)
            
    def setGlobalForce(self, force):
        """Set the global force for physics"""
        for z in self.zones:
            z.setGlobalForce(force)
    
    def sleepPhysicsForActors(self, actors):
        """Tell the actors to go to sleep from a physics perspective
        
        The actors will still be visible and will still be updated but they
        will not update their physics. Useful for optimising when an actor
        does not need to interact with the physics simulation for a while.
        
        If an actor is unzoned then this will have no impact on them
        
        """
        for actor in actors:
            for z in self.zones:
                if z.hasActor(actor):
                    z.sleepActor(actor)

    def wakePhysicsForActors(self, actors):
        """Tell the actors to go to wake up from a physics perspective 
        
        Actors that were put to sleep (via sleepPhysicsForActors) will be woken
        up and take part in the physics simulation again.
        
        """
        for actor in actors:
            for z in self.zones:
                if z.hasActor(actor):
                    z.wakeActor(actor)
        
        
