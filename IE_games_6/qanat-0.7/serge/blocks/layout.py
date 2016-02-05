"""Blocks to help with laying out things on the screen"""

import serge.actor
import serge.engine

class OutOfRange(Exception): """Tried to find something outside the range of the container"""
class CellOccupied(Exception): """Tried to put an actor in an occupied cell"""
class CellEmpty(Exception): """The cell being accessed was empty"""
class UnknownActor(Exception): """The actor was not found"""
class AlreadyInCell(Exception): """The actor was already in this cell"""


class Container(serge.actor.MountableActor):
    """A layout container that contains actors"""

    def __init__(self, tag, name='', width=None, height=None, 
                 background_colour=None, background_layer=None, background_sprite=None,
                 item_width=None, item_height=None):
        """Initialise the Bar"""
        super(Container, self).__init__(tag, name)
        #
        # Item widths and heights - you cannot specify these and the overall
        # dimension
        if (item_width and width) or (item_height and height):
            raise ValueError('Cannot specify both item height/width and overall height/width')
        #
        self.item_height = item_height
        self.item_width = item_width
        #
        # Default sizes are the extent of the screen
        engine = serge.engine.CurrentEngine()
        if width is None:
            width = engine.getRenderer().getScreenSize()[0]
        if height is None:
            height = engine.getRenderer().getScreenSize()[1]
        #
        # Set our size
        self.resizeTo(width, height)
        #
        # Set background if needed
        if background_colour:
            self.setBackgroundColour(background_colour)
        if background_sprite:
            self.setBackgroundSprite(background_sprite)
        self.background_layer = background_layer if background_layer else None

    def setLayerName(self, name):
        """Set the layer name"""
        super(Container, self).setLayerName(self.background_layer if self.background_layer else name)
        for actor in self.getChildren():
            actor.setLayerName(name)    

    def _redoLocations(self):
        """Reloate items in case we have moved"""
        
    def reflowChildren(self):
        """Relocate all children"""
        self._redoLocations()
        for child in self.children:
            if hasattr(child, 'reflowChildren'):
                child.reflowChildren()

    def setBackgroundColour(self, colour):
        """Sets the background colour"""
        self.visual = serge.blocks.visualblocks.Rectangle((self.width, self.height), colour)

    def setBackgroundSprite(self, name):
        """Sets the background sprite"""
        self.visual = serge.visual.Sprites.getItem(name)

    def moveTo(self, x, y, no_sync=False, override_lock=True):
        """Move this actor"""
        super(Container, self).moveTo(x, y, no_sync=no_sync, override_lock=True)
        self.reflowChildren()
        
        
class Bar(Container):
    """A bar of actors - useful for user interfaces"""
    
    def addActor(self, actor, layer_name=None):
        """Add an actor to the bar"""
        self.addChild(actor)
        self._redoLocations()
        actor.setLayerName(self.getLayerName() if layer_name is None else layer_name)
        return actor

    def addBlanks(self, number):
        """Add blank entries into the bar"""
        for i in range(number):
            a = serge.actor.Actor('blank')
            self.addActor(a)


class HorizontalBar(Bar):
    """A horizontal bar of actors"""

    def _redoLocations(self):
        """Reset the locations of the objects within us"""
        self.log.debug('Resetting locations')
        if self.children:
            for i, actor in enumerate(self.children):
                actor.moveTo(*self.getCoords(i))
                self.log.debug('Set %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))

    def getCoords(self, i):
        """Return the coordinates of our ith location"""
        width = self.item_width if self.item_width else float(self.width) / len(self.children)
        left = self.x if self.item_width else self.getSpatial()[0]
        top = self.getSpatial()[1]
        return left + width * (i + 0.5), top + self.height * 0.5


class VerticalBar(Bar):
    """A vertical bar of actors"""

    def _redoLocations(self):
        """Reset the locations of the objects within us"""
        self.log.debug('Resetting locations')
        if self.children:
            height = self.item_height if self.item_height  else float(self.height) / len(self.children)
            left = self.getSpatial()[0]
            top = self.y if self.item_height else self.getSpatial()[1]
            for i, actor in enumerate(self.children):
                actor.moveTo(left + self.width * 0.5, top + height * (i + 0.5))
                self.log.debug('Set %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))


class BaseGrid(Container):
    """A grid of actors"""
    
    def __init__(self, tag, name='', size=(1,1), width=None, height=None, background_colour=None, background_layer=None):
        """Initialise the Grid"""
        super(BaseGrid, self).__init__(tag, name, width, height, background_colour, background_layer)
        self._grid = []
        self.setGrid(size)
        
    def setGrid(self, (w, h)):
        """Set the size of the grid
        
        This also removes all the current actors from the world. Note that
        this can be tricky if you want to re-add some of the actors since
        the actors are not actually removed until the next world update
        and so you cannot re-add them before this or you will get a duplicate
        actor error from the world.
        
        """
        self.clearGrid()
        self._grid = []
        for row in range(w):
            self._grid.append([])
            for col in range(h):
                self._grid[-1].append(self._getEmptyCell())
        self.rows, self.cols = h, w
        self._added = 0
        
    def _getEmptyCell(self):
        """Return an empty grid cell"""
        return None

    def clearGrid(self):
        """Clear the entire grid"""
        for x, row in enumerate(self._grid):
            for y, actor in enumerate(row):
                if actor is not None:
                    self.removeActor((x, y))

    def removeActor(self, (x, y)):
        """Remove the actor at a certain location"""
        try:
            occupant = self.getActorAt((x, y))
        except:
            raise
        else:
            self._grid[x][y] = self._getEmptyCell()
            self.removeChild(occupant)
        
    def getCoords(self, (x, y)):
        """Return the coordinates of a location"""
        my_x, my_y, w, h = self.getSpatial()
        return (my_x + (x+0.5)*w/self.cols, my_y + (y+0.5)*h/self.rows)
       
    def getLocation(self, (x, y)):
        """Return the location in the grid based on coordinates"""
        my_x, my_y, w, h = self.getSpatial()
        cx = round((x - my_x) * self.cols / w - 0.5)
        cy = round((y - my_y) * self.rows / h - 0.5)
        return max(0, int(cx)), max(0, int(cy))

    def removeChildren(self):
        """Remove all the children"""
        self.setGrid((len(self._grid), len(self._grid[0])))
               
class Grid(BaseGrid):
    """A grid where a cell can only contain a single actor"""

    def addActor(self, (x, y), actor, layer_name=None):
        """Add an actor to the grid"""
        #
        # Make sure that there isn't something already there
        try:
            occupant = self.getActorAt((x, y))
        except CellEmpty:
            pass
        else:
            raise CellOccupied('The cell %s is already occupied by %s in grid %s' % ((x, y), occupant.getNiceName(), self.getNiceName()))
        #
        # Add to the grid
        try:
            self._grid[x][y] = actor
        except IndexError:
            raise OutOfRange('%s is out of the range of this grid (%s)' % ((x, y), self.getNiceName()))
        #
        # Now make sure that we update everything
        self.addChild(actor)
        actor.setLayerName(self.getLayerName() if layer_name is None else layer_name)
        actor.moveTo(*self.getCoords((x, y)))
        self.log.debug('Set coords for %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))
        return actor

    def autoAddActor(self, actor):
        """Automatically add an actor to the next cell in the grid
        
        This fills horizontally and then vertically
        
        """
        self.addActor((self._added % len(self._grid), self._added // len(self._grid)), actor)
        self._added += 1
        return actor
    
    def moveActor(self, (x, y), actor):
        """Move an actor from wherever it is to the new location"""
        #
        # Check that this is a valid cell
        try:
            _ = self.getActorAt((x, y))
        except CellEmpty:
            pass
        #
        ox, oy = self.findActorLocation(actor)
        self._grid[x][y] = actor
        self._grid[ox][oy] = self._getEmptyCell()
        actor.moveTo(*self.getCoords((x, y)))
        self.log.debug('Set coords for %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))
        
    def getActorAt(self, (x, y)):
        """Return the actor at a certain location"""
        if x < 0 or y < 0:
            raise OutOfRange('Grid coordinates must be >= 0 (%s, %s)' % ((x, y), self.getNiceName()))            
        try:
            occupant = self._grid[x][y]
        except IndexError:
            raise OutOfRange('%s is out of the range of this grid (%s)' % ((x, y), self.getNiceName()))
        else:
            if occupant is None:
                raise CellEmpty('The cell %s in grid %s is empty' % ((x, y), self.getNiceName()))
            else:
                return occupant

    def findActorLocation(self, actor):
        """Find the location of an actor"""
        for x, row in enumerate(self._grid):
            for y, test_actor in enumerate(row):
                if actor == test_actor:
                    return (x, y)
        else:
            raise UnknownActor('The actor %s was not found in grid %s' % (actor.getNiceName(), self.getNiceName()))


class MultiGrid(BaseGrid):
    """A grid where each cell can contain multiple actors"""
    
    def addActor(self, (x, y), actor, layer_name=None):
        """Add an actor to the grid"""
        #
        # Make sure that there isn't something already there
        try:
            occupants = self.getActorsAt((x, y))
        except CellEmpty:
            pass
        else:
            if actor in occupants:
                raise AlreadyInCell('The cell %s is already occupied by %s in grid %s' % 
                    ((x, y), actor.getNiceName(), self.getNiceName()))
        #
        # Add to the grid
        try:
            self._grid[x][y].append(actor)
        except IndexError:
            raise OutOfRange('%s is out of the range of this grid (%s)' % ((x, y), self.getNiceName()))
        #
        # Now make sure that we update everything
        self.addChild(actor)
        actor.setLayerName(self.getLayerName() if layer_name is None else layer_name)
        actor.moveTo(*self.getCoords((x, y)))
        self.log.debug('Set coords for %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))
        return actor

    def moveActor(self, (x, y), actor):
        """Move an actor from wherever it is to the new location"""
        #
        # Check that this is a valid cell
        _ = self.getActorsAt((x, y))
        #
        ox, oy = self.findActorLocation(actor)
        self._grid[x][y].append(actor)
        self._grid[ox][oy].remove(actor)
        actor.moveTo(*self.getCoords((x, y)))
        self.log.debug('Set coords for %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))

    def _getEmptyCell(self):
        """Return an empty grid cell"""
        return serge.actor.ActorCollection()

    def getActorsAt(self, (x, y)):
        """Return the actors at a certain location"""
        if x < 0 or y < 0:
            raise OutOfRange('Grid coordinates must be >= 0 (%s, %s)' % ((x, y), self.getNiceName()))            
        try:
            actors = self._grid[x][y]
        except IndexError:
            raise OutOfRange('%s is out of the range of this grid (%s)' % ((x, y), self.getNiceName()))
        #
        # We need to make a copy of the list of actors to avoid this list
        # changing by adding and removing actors from the grid
        r = self._getEmptyCell()
        r.extend(actors)
        return r

    def findActorLocation(self, actor):
        """Find the location of an actor"""
        for x, row in enumerate(self._grid):
            for y, occupants in enumerate(row):
                if actor in occupants:
                    return (x, y)
        else:
            raise UnknownActor('The actor %s was not found in grid %s' % (actor.getNiceName(), self.getNiceName()))

    def removeActor(self, (x, y), actor):
        """Remove the actor at a certain location"""
        try:
            self._grid[x][y].remove(actor)
        except (ValueError, CellEmpty):
            raise UnknownActor('The actor %s was not in cell (%d, %d)' % (actor.getNiceName(), x, y))
        else:
            self.removeChild(actor)
            
    def removeActors(self, (x, y)):
        """Remove all the actor from a certain location"""
        for occupant in self.getActorsAt((x, y)):
            self.removeChild(occupant)
        self._grid[x][y][:] = self._getEmptyCell()
            
        
