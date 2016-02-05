"""The actor class"""

import pygame
import math

import common
import serialize
import geometry
import visual 
import events
import physical
import world
import engine
from common import pymunk 

class InvalidActor(Exception): """The actor supplied was not valid for the operation"""
class AlreadyMounted(Exception): """The actor was already mounted"""
class NotMounted(Exception): """The actor was not mounted at all"""
class PositionLocked(Exception): """The actor was locked in place"""
class NoPhysicalConditions(Exception): """An actor was expected to have some physical conditions"""


class PositionLock(object):
    """A lock that you can place on an actor to prevent it moving"""
    
    def __init__(self, reason):
        """Initialise the lock"""
        self.reason = reason
        
        
class Actor(common.Loggable, geometry.Rectangle, common.EventAware):
    """Represents an actor"""
    
    my_properties = (
        serialize.S('tag', 'actor', 'the actor\'s tag'),
        serialize.S('name', '', 'the actor\'s name'),
        serialize.B('active', True, 'whether the actor is active'),
        serialize.B('visible', True, 'whether the actor is visible'),
        serialize.S('sprite', '', 'the name of our sprite'),
        serialize.S('layer', '', 'the name of the layer we render to'),
        serialize.O('physical_conditions', '', 'the physical conditions for this object'),
        serialize.F('angle', 0.0, 'the angle for the actor'),
        serialize.O('lock', None, 'a lock object you can place to prevent an actor moving'),
    )
    
    def __init__(self, tag, name=''):
        """Initialise the actor"""
        self.addLogger()
        self.initEvents()
        super(Actor, self).__init__()
        # Whether we respond to updates or not
        self.active = True
        self.visible = True   
        # Class based tag to locate the actor by
        self.tag = tag
        # Unique name to locate by
        self.name = name
        # Our sprite
        self.sprite = ''
        self._visual = None
        # The layer we render to
        self.layer = ''    
        # Our zoom factor
        self.zoom = 1.0
        # Physics parameters - None means no physics
        self.physical_conditions = None
        # Angle
        self.angle = 0.0
        # Properties to lock an actor so it cannot be moved
        self.lock = None
        
    def init(self):
        """Initialize from serialized form"""
        self.addLogger()
        self.initEvents()
        self.log.info('Initializing actor %s:%s:%s' % (self, self.tag, self.name))
        super(Actor, self).init()
        if self.sprite:
            self.setSpriteName(self.sprite)
        else:
            self._visual = None
        self.setLayerName(self.layer)
        self.zoom = 1.0

    def getNiceName(self):
        """Return a nice name for this actor"""
        if self.name:
            name_part = '%s (%s)' % (self.name, self.tag)
        else:
            name_part = self.tag
        return '%s [%s] <%s>' % (self.__class__.__name__, name_part, hex(id(self)))
        
    def setSpriteName(self, name):
        """Set the sprite for this actor"""
        if name != self.sprite:
            self.visual = visual.Register.getItem(name).getCopy()
            self.sprite = name
        
    @property
    def visual(self): return self._visual
    @visual.setter
    def visual(self, value):
        """Set the visual item for this actor"""
        self._visual = value
        self._resetVisual()
        
    def _resetVisual(self):
        """Reset the visual item on the center point"""
        #
        # Adjust our location so that we are positioned and sized appropriately
        cx, cy, _, _ = self.getSpatialCentered()
        self.setSpatialCentered(cx, cy, self._visual.width, self._visual.height)
        #
        # Here is a hack - sometimes the visual width changes and we want to update our width
        # so we let the visual know about us so it can update our width. This is almost 
        # certainly the wrong thing to do, but we have some tests in there so hopefully
        # the right thing becomes obvious later!
        self._visual._actor_parent = self
        
    def getSpriteName(self):
        """Return our sprite"""
        return self.sprite
        
    def setLayerName(self, name):
        """Set the layer that we render to"""
        self.layer = name
    
    def getLayerName(self):
        """Return our layer name"""
        return self.layer
    
    def renderTo(self, renderer, interval):
        """Render ourself to the given renderer"""
        if self._visual and self.layer:       
            layer = renderer.getLayer(self.layer)
            camera = renderer.camera
            if layer.static:
                coords = self.getOrigin()
            elif camera.canSee(self):
                coords = camera.getRelativeLocation(self)
            else: 
                return # Cannot see me
            self._visual.renderTo(interval, layer.getSurface(), coords)
    
    def updateActor(self, interval, world):
        """Update the actor status"""

    def removedFromWorld(self, world):
        """Called when we are being removed from the world"""
        self.processEvent((events.E_REMOVED_FROM_WORLD, self))

    def addedToWorld(self, world):
        """Called when we are being added to the world"""
        self.processEvent((events.E_ADDED_TO_WORLD, self))
        
    def setZoom(self, zoom):
        """Zoom in on this actor"""
        if self._visual:
            self._visual.scaleBy(zoom/self.zoom)
            self.setSpatialCentered(self.x, self.y, self._visual.width, self._visual.height)
        self.zoom = zoom

    def setAngle(self, angle, sync_physical=False, override_lock=False):
        """Set the angle for the visual"""
        if self.lock and not override_lock:
            raise PositionLocked('Cannot rotate: %s' % self.lock.reason)
        if self._visual:
            self._visual.setAngle(angle)
            self._resetVisual()
        if sync_physical and self.physical_conditions:
            self.physical_conditions.body.angle = math.radians(-angle)
        self.angle = angle
        
    def getAngle(self):
        """Return the angle for the actor"""
        return self.angle
    

    ### Physics ###
    
    def setPhysical(self, physical_conditions):
        """Set the physical conditions"""
        #
        # Watch for if this object already has a shape
        if self.physical_conditions and self.physical_conditions.body:
            self.physical_conditions.updateFrom(physical_conditions)
        else:
            #
            # Check if we should be using the size of the visual element
            if physical_conditions.visual_size:
                if self.visual is None:
                    raise physical.InvalidDimensions(
                        'No visual element set for actor %s but visual_size requested' % self.getNiceName())
                else:
                    if physical_conditions.visual_size == geometry.CIRCLE:
                        # Circle
                        physical_conditions.setGeometry(radius=self.visual.radius)
                    elif physical_conditions.visual_size == geometry.RECTANGLE:
                        # Rectangle
                        physical_conditions.setGeometry(width=self.visual.width, height=self.visual.height)
                    else:
                        raise physical.InvalidDimensions('Visual size setting (%s) is not recognized' % physical_conditions.visual_size)
            #
            self.physical_conditions = physical_conditions
        
    def getPhysical(self):
        """Return the physical conditions"""
        return self.physical_conditions

    def syncPhysics(self, spatial_only=False):
        """Sync physics when the actors physical properties have been changed"""
        if self.physical_conditions:
            #self.log.debug('Syncing physics for %s to %s, %s' % (self.getNiceName(), self.x, self.y))
            self.physical_conditions.body.position = self.x, self.y
            if not spatial_only:
                self.physical_conditions.body.velocity = self.physical_conditions.velocity

    # Remap x, y properties to allow syncing with the physics engine

    def move(self, x, y):
        """Move by a certain amount"""
        super(Actor, self).move(x, y)
        self.syncPhysics(spatial_only=True)
        

    def moveTo(self, x, y, no_sync=False, override_lock=False):
        """Move the center of this actor to the given location, unless it is locked
        
        You can override the lock by passing True to override lock.
        
        """
        if self.lock and not override_lock:
            raise PositionLocked('The actor is locked in place: %s' % self.lock.reason)
        else:
            super(Actor, self).moveTo(x, y, override_lock=override_lock)
            if not no_sync:
                self.syncPhysics(spatial_only=True)


class ActorCollection(list):
    """A list of actors
    
    This class implements some useful methods which help to 
    handle collections of actors.
    
    """
    
    def findActorsByTag(self, tag):
        """Return a collection of actors with the given tag"""
        return ActorCollection([actor for actor in self if actor.tag == tag])

    def findActorsByTags(self, tags):
        """Return a collection of actors with at least one of the tags"""
        collection = ActorCollection()
        for tag in tags:
            collection.extend(self.findActorsByTag(tag))
        return collection
                  
    def findActorByName(self, name):
        """Return then actor with the given name"""
        for actor in self:
            if actor.name == name:
                return actor
        else:
            raise InvalidActor('The actor with name "%s" was not found in %s' % (name, self))
        
    def numberOfActorsWithTag(self, tag):
        """Return the number of actors with the given tag"""
        return len(self.findActorsByTag(tag))        

    def numberOfActorsWithName(self, name):
        """Return the number of actors with the given name"""
        count = 0
        for actor in self:
            if actor.name == name:
                count += 1
        return count     
    
    def hasActorWithTag(self, tag):
        """Return True if the collection contains an actor with the given tag"""
        return self.numberOfActorsWithTag(tag) > 0
    
    def hasActorWithName(self, name):
        """Return True if the collection contains an actor with the given name"""
        return self.numberOfActorsWithName(name) > 0

    def hasActor(self, actor):
        """Return True if we have that actor"""
        return actor in self

    def forEach(self):
        """Returns an object suitable for mapping method calls to all the actors in the collection
        
        Use this like,
            collection.forEach().setAngle(12)
            
        """
        return ProxyLauncher(self)

class ProxyLauncher(object):
    
    def __init__(self, items):
        """Intialise the proxy"""
        self._items = items
        
    def __getattr__(self, name):
        """Return a mapped attribute call"""
        return MapperList(self._items, name)

    def __setattr__(self, name, value):
        """Set an attribute of the list"""
        if name.startswith('_'):
            self.__dict__[name] = value
        else:
            for item in self._items:
                setattr(item, name, value)

class MapperList(object):
    
    def __init__(self, items, method_name):
        """Intialise the mapper"""
        self._items = items
        self._method_name = method_name
        
    def __call__(self, *args, **kw):
        """Make the call"""
        results = []
        for item in self._items:
            try:
                result = getattr(item, self._method_name)(*args, **kw)
            except StopIteration:
                break
            else:
                results.append(result)
        return results

                    
          
class CompositeActor(Actor):
    """An actor that can have children, which are also actors
    
    World operations on the parent, like adding and removing,
    will also apply to the children.
    
    If the children are removed from the parent then they are
    also removed from the world.
    
    """
    
    # When serializing the children property can be needed (eg for the active and visible
    # properties)
    children = tuple()
        
    my_properties = (
        serialize.L('children', [], 'the child actors that we own'),
        serialize.L('_world', [], 'the world that we belong to'),
    )
    
    def __init__(self, *args, **kw):
        """Initialise the actor"""
        self.children = ActorCollection()
        self._active = True
        self._visible = True
        self._world = None
        super(CompositeActor, self).__init__(*args, **kw)

    ### World events ###
    
    def removedFromWorld(self, world):
        """Called when we are being removed from the world"""
        super(CompositeActor, self).removedFromWorld(world)
        for child in self.getChildren()[:]:
            world.removeActor(child)
        self._world = None
        
    def addedToWorld(self, world):
        """Called when we are being added to the world"""
        super(CompositeActor, self).addedToWorld(world)
        for child in self.getChildren():
            world.addActor(child)
        self._world = world
            
    ### Children ###
            
    def addChild(self, actor):
        """Add a child actor"""
        self.children.append(actor)
        actor.linkEvent(events.E_REMOVED_FROM_WORLD, self._childRemoved)
        #
        # If we are already in the world then add this actor to the world also
        if self._world:
            try:
                self._world.addActor(actor)
            except world.DuplicateActor:
                # Ok if the actor is already there
                pass
                   
    def removeChild(self, actor, leave_in_world=False):
        """Remove a child actor"""
        try:
            self.children.remove(actor)
        except ValueError:
            raise InvalidActor('The actor %s was not a child of %s' % (actor.getNiceName(), self.getNiceName()))
        #
        # Remove the child from the world
        if self._world and not leave_in_world:
            self._world.removeActor(actor)

    def removeChildren(self):
        """Remove all the children"""
        for actor in self.getChildren()[:]:
            self.removeChild(actor)
            
    def hasChild(self, actor):
        """Return True if this actor already has this actor as a child"""
        return actor in self.children

    def hasChildren(self):
        """Return True if this actor has children"""
        return len(self.children) != 0
            
    def getChildren(self):
        """Return the list of children"""
        return self.children

    def getChildrenWithTag(self, tag):
        """Return all the children with a certain tag"""
        return [actor for actor in self.getChildren() if actor.tag == tag]
    
    def _childRemoved(self, child, arg):
        """A child was removed from the world"""
        if child in self.children:
            self.children.remove(child)

    # The active attribute should cascade to our children
    @property
    def active(self): return self._active
    @active.setter
    def active(self, value):
        """Set the active"""
        self._active = value
        for child in self.getChildren():
            child.active = value
            
    # The visible attribute should cascade to our children
    @property
    def visible(self): return self._visible
    @visible.setter
    def visible(self, value):
        """Set the visible"""
        self._visible = value
        for child in self.getChildren():
            child.visible = value
        
    
class AbstractMountableActor(CompositeActor):
    """An base class for actors that you can mount other actors to
    
    The other actors are located at a certain position
    relative to the position of this actor. You can
    use this actor to create clusters either visually
    or functionally.
    
    """        

    my_properties = (
        serialize.L('children', [], 'the child actors that we own'),
        serialize.L('_world', [], 'the world that we belong to'),
        serialize.D('_offsets', {}, 'the offsets to our children'),
    )
    
    def __init__(self, *args, **kw):
        """Initialize the MountableActor"""
        super(AbstractMountableActor, self).__init__(*args, **kw)
        self._offsets = {}
        
    def mountActor(self, actor, (x, y), original_rotation=False):
        """Mount the actor with the given offset
        
        If original_rotation is True then the mount offset is taken as
        working against the original rotation (ie angle = 0) of the
        actor.
        
        """
        if self.hasChild(actor):
            raise AlreadyMounted('The actor %s is already mounted to %s' % (actor.getNiceName(), self.getNiceName()))
        #
        # Handle original rotation
        if original_rotation:
            old_angle = self.getAngle()
            self.setAngle(0.0)
        #
        self.addChild(actor)
        self._offsets[actor] = (x, y)
        actor.moveTo(self.x + x, self.y + y)
        #
        if original_rotation:
            self.setAngle(old_angle)
        #
        actor.lock = PositionLock('is mounted to %s' % self.getNiceName())
        return actor
        
    def unmountActor(self, actor):
        """Unmount the actor"""
        if not self.hasChild(actor):
            raise NotMounted('The actor %s is not mounted to %s' % (actor.getNiceName(), self.getNiceName()))
        self.removeChild(actor)
        del(self._offsets[actor])
        actor.lock = None

   
            
class MountableActor(AbstractMountableActor):
    """An actor that you can mount other actors to
    
    The other actors are located at a certain position
    relative to the position of this actor. You can
    use this actor to create clusters either visually
    or functionally.
    
    """        

    def moveTo(self, x, y, no_sync=False, override_lock=False):
        """Move this actor"""
        super(AbstractMountableActor, self).moveTo(x, y, no_sync=no_sync, override_lock=override_lock)
        for actor, (dx, dy) in self._offsets.iteritems():
            actor.moveTo(x+dx, y+dy, no_sync=no_sync, override_lock=True)
            
    def setAngle(self, angle, sync_physical=False, override_lock=False):
        """Set the angle for the visual"""
        if self.lock and not override_lock:
            raise PositionLocked('Cannot rotate: %s' % self.lock.reason)
        old_angle = self.getAngle()
        super(AbstractMountableActor, self).setAngle(angle, sync_physical=sync_physical, override_lock=override_lock)
        for actor, (dx, dy) in self._offsets.iteritems():
            actor.setAngle(angle, sync_physical=sync_physical, override_lock=True)
            #
            # Now also rotate the position
            off = pymunk.Vec2d(dx, dy)
            off.rotate(math.radians(-(angle-old_angle))) # Pymunk's angles reversed compared to pygame
            nx, ny = off
            actor.moveTo(self.x + nx, self.y + ny, override_lock=True)
            #
            # Update the offsets so we stay in position
            self._offsets[actor] = (nx, ny)

        


class PhysicallyMountableActor(AbstractMountableActor):
    """An physical actor that you can mount other physical actors to
    
    The other actors are located at a certain position
    relative to the position of this actor. You can
    use this actor to create clusters either visually
    or functionally.
    
    All actors must be under the control of the physics engine.
    
    """        

    my_properties = (
        serialize.L('children', [], 'the child actors that we own'),
        serialize.L('_world', [], 'the world that we belong to'),
        serialize.D('_offsets', {}, 'the offsets to our children'),
    )
    
    def __init__(self, tag, name='', mass=0.0, **kw):
        """Initialize the MountableActor"""
        if not mass:
            raise NoPhysicalConditions('Mass needs to be specified for mountable actor')
        super(PhysicallyMountableActor, self).__init__(tag, name, **kw)
        self.setPhysical(physical.PhysicalBody(mass=mass, update_angle=True))
        self._joints = []

    def init(self):
        """Initialise from serialized form"""
        self._joints = []
        super(PhysicallyMountableActor, self).init()
        
    def mountActor(self, actor, (x, y), original_rotation=False):
        """Mount the actor with the given offset"""
        if not actor.getPhysical():
            raise NoPhysicalConditions('Actor %s does not have any physical conditions. Cannot mount to %s' % (
                actor.getNiceName(), self.getNiceName()))
        super(PhysicallyMountableActor, self).mountActor(actor, (x, y), original_rotation)

        
    def unmountActor(self, actor):
        """Unmount the actor"""
        super(PhysicallyMountableActor, self).unmountActor(actor)

    def addedToWorld(self, world):
        """The actor was added to the world"""
        super(PhysicallyMountableActor, self).addedToWorld(world)
        self._createJoints()
        
    def _createJoints(self):
        """Create the joints to hold the children together"""
        #
        # Create a joints to link the actors
        if len(self.children) == 0 or not self.getPhysical().space:
            return
        #
        # First link
        actor = self.children[0]
        joint = pymunk.PivotJoint(self.getPhysical().body, actor.getPhysical().body, self.getPhysical().body.position)
        self.getPhysical().space.add(joint)
        self._joints.append(joint)
        #
        # Make the main body rotate with the first child
        joint = pymunk.RotaryLimitJoint(self.getPhysical().body, actor.getPhysical().body, 0, 0)
        self.getPhysical().space.add(joint)
        self._joints.append(joint)
        #
        # Link all the children
        self.log.debug('Added mounting joint between %s and %s' % (actor.getNiceName(), self.getNiceName()))
        if len(self.children) > 1:
            children = self.children[:]
            while children:
                if len(children) > 1:
                    actor, other, children = children[0], children[1], children[1:]
                else:
                    actor, other, children = self.children[0], children[0], []
                #
                joint = pymunk.PivotJoint(other.getPhysical().body, actor.getPhysical().body, (0,0), 
                        -(actor.getPhysical().body.position - other.getPhysical().body.position))
                self.getPhysical().space.add(joint)
                self._joints.append(joint)
                self.log.debug('Added mounting joint between %s and %s' % (actor.getNiceName(), other.getNiceName()))
            #
            # Constrain the last child to rotate at the same rate as the first
            actor, other = self.children[0], self.children[-1]
            joint = pymunk.RotaryLimitJoint(actor.getPhysical().body, other.getPhysical().body, 0, 0)
            self.getPhysical().space.add(joint)
            self._joints.append(joint)
            
    def setAngle(self, angle, sync_physical=False, override_lock=False):
        """Set the angle for the visual"""
        if self.lock and not override_lock:
            raise PositionLocked('Cannot rotate: %s' % self.lock.reason)
        if sync_physical:
            self._clearJoints()
            old_angle = self.getAngle()
            for actor, (dx, dy) in self._offsets.iteritems():
                #
                # Now also rotate the position
                off = actor.getPhysical().body.position - self.getPhysical().body.position
                off.rotate(math.radians(-(angle-old_angle))) # Pymunk's angles reversed compared to pygame
                nx, ny = off
                actor.moveTo(self.x + nx, self.y + ny, no_sync=False, override_lock=True)
                actor.setAngle(angle, sync_physical=sync_physical, override_lock=True)
                actor.getPhysical().body.angular_velocity = 0.0
                #
                # Update the offsets so we stay in position
                self._offsets[actor] = (nx, ny)
        super(PhysicallyMountableActor, self).setAngle(angle, sync_physical=sync_physical, override_lock=override_lock)
        self.getPhysical().body.angular_velocity = 0.0
        if sync_physical:
            self._createJoints()

    def _clearJoints(self):
        """Clear all the joints"""
        if self.getPhysical().space:
            self.getPhysical().space.remove(*self._joints)
            self._joints = []
        
    def moveTo(self, x, y, no_sync=False, override_lock=False):
        """Move this actor"""
        if not no_sync:
            self._clearJoints()
        for actor in self.getChildren():
            dx, dy = actor.getPhysical().body.position - self.getPhysical().body.position
            actor.moveTo(x+dx, y+dy, no_sync=no_sync, override_lock=True)
            actor.getPhysical().body.velocity = (0,0)
        super(PhysicallyMountableActor, self).moveTo(x, y, no_sync=no_sync, override_lock=override_lock)
        self.getPhysical().body.velocity = (0,0)
        if not no_sync:
            self._createJoints()
           

