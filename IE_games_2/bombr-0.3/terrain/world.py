"""The world"""

import array

import loggable


class BaseWorld(loggable.Loggable):
    """Represents a basic"""

    safe_access = False

    def __init__(self, width, height):
        """Initialise the world"""
        self.addLogger()
        #
        self.height = height
        self.width = width
        self.cells = self.initialiseCells()

    def initialiseCells(self):
        """Return a new set of cells"""
        raise NotImplementedError()

    def iterCells(self):
        """Iterate through all cells"""
        for row in range(self.height):
            for col in range(self.width):
                yield(self.cells[row][col])

    def iterCellsAndLocations(self):
        """Iterate through all cells returning row, col, cell"""
        for row in range(self.height):
            for col in range(self.width):
                yield((row, col, self.cells[row][col]))

    def isInRange(self, row, col):
        """Return true if the cell is in the range of the world"""
        return 0 <= row < self.height and 0 <= col < self.width

    def getCell(self, row, col):
        """Return the cell at the certain location"""
        if self.safe_access and not self.isInRange(row, col):
            raise IndexError('The cell (%d, %d) is not in the world' % (row, col))
        else:
            return self.cells[row][col]

    def setCell(self, row, col, value):
        """Set the cell at the certain location"""
        if self.safe_access and not self.isInRange(row, col):
            raise IndexError('The cell (%d, %d) is not in the world' % (row, col))
        else:
            self.assignCellValue(row, col, value)

    def assignCellValue(self, row, col, value):
        """Assign a value to a cell"""
        raise NotImplementedError

    def updateFrom(self, other):
        """Update our cells from another world"""
        for row in range(self.height):
            for col in range(self.width):
                self.assignCellValue(row, col, other.getCell(row, col))

    def getCopy(self):
        """Return a copy of this world"""
        return self.__class__(self.width, self.height)


class World(BaseWorld):
    """Represents the world"""

    def initialiseCells(self):
        """Return new cells"""
        cells = []
        for row in range(self.height):
            cells.append([])
            for col in range(self.width):
                cells[-1].append(Cell(row, col))
        return cells

    def assignCellValue(self, row, col, value):
        """Assign a value to a cell"""
        self.cells[row][col] = value


class Cell(object):
    """Represents a cell in the world"""

    def __init__(self, row, col):
        """Initialise the cell"""
        self.row = row
        self.col = col


class StringWorld(BaseWorld):
    """A world represented by strings"""

    def initialiseCells(self):
        """Initialise the cells"""
        return array.array('c', '-' * self.height * self.width)

    def getCell(self, row, col):
        """Return the value"""
        return self.cells[row * self.width + col]

    def setCell(self, row, col, value):
        """Assign a value to a cell"""
        self.cells[row * self.width + col] = value

    assignCellValue = setCell

    def iterCellsAndLocations(self):
        """Iterate through all cells returning row, col, cell"""
        for row in range(self.height):
            for col in range(self.width):
                yield((row, col, self.cells[row * self.width + col]))