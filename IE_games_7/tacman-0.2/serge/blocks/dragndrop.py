"""Implements drag and drop behaviour"""

import serge.actor
import serge.events
import serge.blocks.actors

class NotDragging(Exception): """No actor is being dragged"""
class DuplicateActor(Exception): """The actor is already controlled"""
class NotATarget(Exception): """The actor is not a target"""
class AlreadyATarget(Exception): """The actor is a target already"""
class DropNotAllowed(Exception): """Cannot drop here"""


class DragController(serge.blocks.actors.ScreenActor):
    """Controls objects which are draggable"""
    
    def __init__(self, tag='controller', name='controller', start=None, stop=None, hit=None, miss=None):
        """Initialise the controller"""
        super(DragController, self).__init__(tag, name)
        self.draggables = serge.actor.ActorCollection()
        self.targets = {}
        self.dragging = self._last_dragged = None
        self.drag_x = self.drag_y = 0.0
        self.setCallbacks(start, stop)
        self.setDropCallbacks(hit, miss)

    def addActor(self, actor, start=None, stop=None):
        """Add an actor to be controlled and callback to be called when dragging start and stops"""
        if actor in self.draggables:
            raise DuplicateActor('The actor %s is already controlled by %s' % (actor.getNiceName(), self.getNiceName()))
        self.draggables.append(actor)
        actor.linkEvent(serge.events.E_LEFT_MOUSE_DOWN, self.mouseDown, (actor, start))
        actor.linkEvent(serge.events.E_LEFT_CLICK, self.clickedActor, (actor, stop))

    def removeActor(self, actor):
        """Remove an actor from being controlledd"""
        self.draggables.remove(actor)
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
            mx, my = self.mouse.getScreenPos()
            self.dragging.move(mx-self.drag_x, my-self.drag_y)
            self.drag_x, self.drag_y = self.mouse.getScreenPos()
            
    def setCallbacks(self, start, stop):
        """Set the callbacks to use when starting and stopping a drag"""
        self._start = start
        self._stop = stop           
    
    def setDropCallbacks(self, hit, miss):
        """Set the callback to use when dropping on a target"""
        self._hit = hit
        self._miss = miss

                
