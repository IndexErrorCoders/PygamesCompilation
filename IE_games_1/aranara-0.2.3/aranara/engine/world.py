"""Represents a world in the engine

A world is a collection of actors that should be rendered and updated
in any one pyglet cycle. The engine has only one active world and so
switching between world switches between active sets of actors.

This is typically used to represent different game states (eg screens)

A world
    Has collection of batches of actors
    Has a physics space
    Has methods to handle mouse clicks and keyboard

"""

import collections
import pyglet
import pymunk

import common
import events
import errors


class World(common.Loggable, events.EventAware):
    """A collection of actors that should be updated and rendered"""

    def __init__(self, name, options):
        """Initialise the world"""
        self.addLogger()
        self.initEvents()
        self.name = name
        self.options = options
        self.actors = {}
        self.batches = collections.OrderedDict()
        self.space = pymunk.Space()
        self.tweens = []
        self.engine = None
        self.bounds = None
        self._shape_cache = {}
        self._actors_for_removal = []
        self._actors_for_addition = []
        self.worldCreated()
        self.log.info('World "%s" created' % name)

    def worldCreated(self):
        """Create the world items - override this"""

    def renderWorld(self):
        """Render the actors using pyglet"""
        for batch in self.batches.values():
            batch.draw()

    def activateWorld(self):
        """The world was activated"""

    def deactivateWorld(self, next_world_name):
        """The world was deactivated"""

    def updateWorld(self, dt):
        """Update the actor logic"""
        #
        # Add forces from previous timestep and then clear them
        for actor in self.actors.values():
            if actor.hasPhysics() and actor.force:
                actor.body.apply_impulse(actor.force)
                actor.resetForces()
        #
        # Physics update
        self.space.step(dt)
        #
        # Individual actor updates
        for_removal = []
        for actor in self.actors.values():
            actor.updateActor(self, dt)
            #
            # Watch for actor going out of bounds - we should
            # remove these actors
            if self.bounds and not self.bounds.contains_vect(actor.getCenter()):
                for_removal.append(actor)
        #
        # Ongoing tweens
        for tween in self.tweens[:]:
            tween.doTween(dt)
            if tween.complete:
                self.tweens.remove(tween)
        #
        # Remove actors that went out of bounds
        for actor in for_removal:
            self.removeActor(actor)
        #
        # Remove actors that we requested to be removed
        for actor in self._actors_for_removal:
            try:
                self.removeActor(actor)
            except errors.NotFound:
                # Ok, not a big deal - some other process probably removed it before
                # we got to it
                self.log.error('Scheduled actor %s was already removed' % actor)
        self._actors_for_removal = []
        #
        # Add actors
        for actor in self._actors_for_addition:
            self.addActor(actor)
        self._actors_for_addition = []

    def addActor(self, actor):
        """Add an actor to the world"""
        if actor.name in self.actors:
            raise errors.AlreadyExists('An actor named "%s" is already in the world' % actor.name)
        self.actors[actor.name] = actor
        #
        # Add physics objects to the physical simulation if needed
        if actor.hasPhysics():
            if actor.isStatic():
                self.space.add(actor.shape)
            else:
                self.space.add(actor.body, actor.shape)
            self._shape_cache[actor.shape] = actor
        #
        # Notify the actor that they were added to the world
        actor.addedToWorld(self)
        self.processEvent(events.E_ACTOR_ADDED, actor)
        #
        return actor

    def removeActor(self, actor):
        """Remove an actor from the world"""
        self.log.debug('Removing actor "%s"' % actor)
        #
        if not actor.name in self.actors:
            raise errors.NotFound('Actor "%s" was not in world "%s"' % (actor.name, self.name))
        #
        # Remove from physics simulation
        if actor.hasPhysics():
            self.space.remove(actor.shape)
            if not actor.isStatic():
                self.space.remove(actor.body)
            del(self._shape_cache[actor.shape])
        #
        del(self.actors[actor.name])
        #
        # Notify the world
        actor.removedFromWorld(self)
        self.processEvent(events.E_ACTOR_REMOVED, actor)

    def scheduleActorRemoval(self, actor):
        """Schedule the removal of an actor when next convenient

        This should be used rather than the normal removeActor because
        that can cause problems when you are iterating over the actors
        or in the middle of the physics time-step

        """
        self._actors_for_removal.append(actor)

    def scheduleActorAddition(self, actor):
        """Add an actor when next convenient"""
        self._actors_for_addition.append(actor)

    def addBatch(self, name):
        """Add a batch to the world"""
        batch = pyglet.graphics.Batch()
        self.batches[name] = batch
        return batch

    def onKeyPress(self, symbol, modifier):
        """All key presses are routed here"""
        return self.processEvent(events.E_KEY_PRESS, (symbol, modifier))

    def onKeyRelease(self, symbol, modifier):
        """All key releases are routed here"""
        return self.processEvent(events.E_KEY_RELEASE, (symbol, modifier))

    def onMouseDown(self, x, y, button, modifiers):
        """All mouse press events are routed here"""
        self.log.debug('The mouse was down')
        #
        # Try to find who was clicked on
        for actor in self.actors.values():
            if actor.visible:
                width, height = actor.getSize()
                ax, ay = actor.x, actor.y
                #
                # Was the click inside the actor
                if ax - width / 2 <= x <= ax + width / 2 and ay - height / 2 <= y <= ay + height / 2:
                    actor.processEvent((events.E_LEFT_CLICK if button == 1 else events.E_RIGHT_CLICK), (x, y, button, modifiers))

    def onMouseRelease(self, x, y, button, modifiers):
        """All mouse release events come here"""
        self.processEvent(events.E_MOUSE_RELEASE, (x, y, button, modifiers))

    def onMouseDrag(self, x, y, dx, dy, button, modifiers):
        """All mouse drag events are routed here"""
        self.processEvent(events.E_MOUSE_DRAG, (x, y, dx, dy, button, modifiers))

    def onMouseScroll(self, x, y, scroll_x, scroll_y):
        """All mouse scroll events come here"""
        self.processEvent(events.E_MOUSE_SCROLL, (x, y, scroll_x, scroll_y))

    def setBounds(self, left, bottom, top, right):
        """Set the bounds of the world

        Actors outside the bounds will be automatically removed
        from the simulation

        """
        self.bounds = pymunk.BB(left, bottom, top, right)

    def getActorByShape(self, shape):
        """Return the actor with a given shape"""
        try:
            return self._shape_cache[shape]
        except KeyError:
            raise errors.NotFound('No actor with shape %s found in %s' % (shape, self.name))

    def getPhysicsActors(self):
        """Return all the physics actors"""
        return [actor for actor in self.actors.values() if actor.hasPhysics()]