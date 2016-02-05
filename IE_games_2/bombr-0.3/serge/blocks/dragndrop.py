"""Implements drag and drop behaviour"""

import serge.actor
import serge.events
import serge.input
import serge.blocks.actors

class NotDragging(Exception): """No actor is being dragged"""
class DuplicateActor(Exception): """The actor is already controlled"""
class NotATarget(Exception): """The actor is not a target"""
class AlreadyATarget(Exception): """The actor is a target already"""
class DropNotAllowed(Exception): """Cannot drop here"""
class BadConstraint(Exception): """The constraint was invalid"""


class DragItem(object):
    """An item to be dragged"""

    def __init__(self, obj, start, stop, x_constraint, y_constraint):
        """Initialise the object"""
        self.obj = obj
        self.start = start
        self.stop = stop
        self.x_constraint = x_constraint
        self.y_constraint = y_constraint

    def getXYValue(self, dx, dy):
        """Return the new x and y value honoring the constraints"""
        if self.x_constraint:
            nx = max(min(self.obj.x + dx, self.x_constraint[1]), self.x_constraint[0])
        else:
            nx = self.obj.x + dx
        if self.y_constraint:
            ny = max(min(self.obj.y + dy, self.y_constraint[1]), self.y_constraint[0])
        else:
            ny = self.obj.y + dy
        #
        return nx, ny


class DragController(serge.blocks.actors.ScreenActor):
    """Controls objects which are draggable"""
    
    def __init__(self, tag='controller', name='controller', start=None, stop=None, hit=None, miss=None):
        """Initialise the controller"""
        super(DragController, self).__init__(tag, name)
        self.draggables = {}
        self.targets = {}
        self.dragging = self._last_dragged = None
        self.drag_x = self.drag_y = 0.0
        self.setCallbacks(start, stop)
        self.setDropCallbacks(hit, miss)

    def addActor(self, actor, start=None, stop=None, x_constraint=None, y_constraint=None):
        """Add an actor to be controlled and callback to be called when dragging start and stops"""
        #
        # Reality checks
        if actor in self.draggables:
            raise DuplicateActor('The actor %s is already controlled by %s' % (actor.getNiceName(), self.getNiceName()))
        if x_constraint is not None and not isinstance(x_constraint, tuple):
            raise BadConstraint('The x_constraint was not a tuple')
        if y_constraint is not None and not isinstance(y_constraint, tuple):
            raise BadConstraint('The y_constraint was not a tuple')
        #
        # Add the draggable
        self.draggables[actor] = DragItem(actor, start, stop, x_constraint, y_constraint)
        actor.linkEvent(serge.events.E_LEFT_MOUSE_DOWN, self.mouseDown, (actor, start))
        actor.linkEvent(serge.events.E_LEFT_CLICK, self.clickedActor, (actor, stop))

    def getDraggable(self, actor):
        """Return the draggable for the actor"""
        try:
            return self.draggables[actor]
        except KeyError:
            raise NotDragging('The actor %s is not tracked as a draggable' % actor.getNiceName())

    def removeActor(self, actor):
        """Remove an actor from being controlled"""
        del(self.draggables[actor])
        actor.unlinkEvent(serge.events.E_LEFT_MOUSE_DOWN, self.mouseDown)
        actor.unlinkEvent(serge.events.E_LEFT_CLICK, self.clickedActor)

    def addDropTarget(self, actor, fn=None):
        """Add a target to drop to"""
        if actor in self.targets.keys():
            raise AlreadyATarget('The target %s is already a drop target for %s' % (actor.getNiceName(), self.getNiceName()))
        else:
            self.targets[actor] = fn

    def removeDropTarget(self, actor):
        """Remove an actor as a drop target"""
        try:
            del(self.targets[actor])
        except KeyError:
            raise NotATarget('The actor %s was not a target in %s' % (actor.getNiceName(), self.getNiceName()))

    def isDragging(self):
        """Return True if we are dragging an object"""
        return self.dragging != None

    def getDraggedActor(self):
        """Return the actor being dragged"""
        if self.isDragging():
            return self.dragging
        else:
            raise NotDragging('No actor is being dragged')        
                
    def mouseDown(self, obj, (actor, fn)):
        """The mouse was down over an actor"""
        if self.active and not self.dragging:
            self.dragging = actor
            self.drag_x, self.drag_y = self.mouse.getScreenPos()
            #
            # We allow the callbacks to return an actor, which will be used
            # as the dragged object
            dragger = None
            if fn:
                dragger = fn(obj, actor)
            if self._start:
                dragger = dragger if dragger else self._start(obj, actor)
            #
            if dragger:
                self.dragging = dragger
            
    def clickedActor(self, obj, (actor, fn)):
        """The mouse was released over an actor"""
        if self.active and self.dragging:
            #
            # Check to see where we are dropping
            if self.checkForDrops(self.dragging):
                #
                # Dropping was allowed - so cancel drag and call any callbacks
                if fn:
                    fn(obj, self.dragging)
                if self._stop:
                    self._stop(obj, self.dragging)
                self.dragging = None
            else:
                #
                # The drop target would not allow us to be dropped
                self.log.debug('Drop not allowed')
            
    def checkForDrops(self, actor):
        """Check to see if we dropped our actor onto a target or not - return False if the drop is not allowed
        
        If we dropped on a target then we can call the callback. If
        we didn't drop on a target then we call the miss callback.
        
        The callback can raise DropNotAllowed to cause the drop not to occur
        
        """
        #
        # Go through all the targets looking for the one we dropped on (use the mouse
        # as the test point)
        hit = False
        allowed = True
        test = serge.geometry.Point(*self.mouse.getScreenPos())
        for target, fn in self.targets.iteritems():
            if actor != target and test.isInside(target):
                # Ok, dropped on this target
                hit = True
                for callback in (fn, self._hit):
                    if callback:
                        try:
                            callback(target, actor)
                        except DropNotAllowed:
                            allowed = False
        #
        # No targets were overlapped - so call the miss callback
        if not hit and self._miss:
            try:
                self._miss(actor)
            except DropNotAllowed:
                allowed = False
        #
        return allowed
        
        
    def updateActor(self, interval, world):
        """Update the controller"""
        super(DragController, self).updateActor(interval, world)
        #
        if self.active and self.dragging:
            #
            # Watch for mouse up - if this occurs with the mouse outside
            # of the object then we will not get the event
            if not self.mouse.isDown(serge.input.M_LEFT):
                self.log.debug('Mouse up outside actor - dropping now')
                self.clickedActor(self.dragging, (self.dragging, self.getDraggable(self.dragging).stop))
            else:
                mx, my = self.mouse.getScreenPos()
                nx, ny = self.getDraggable(self.dragging).getXYValue(mx-self.drag_x, my-self.drag_y)
                self.dragging.moveTo(nx, ny)
                self.drag_x, self.drag_y = self.mouse.getScreenPos()

    def setCallbacks(self, start, stop):
        """Set the callbacks to use when starting and stopping a drag"""
        self._start = start
        self._stop = stop           
    
    def setDropCallbacks(self, hit, miss):
        """Set the callback to use when dropping on a target"""
        self._hit = hit
        self._miss = miss