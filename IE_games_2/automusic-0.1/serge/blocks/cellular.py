"""Implementations of various cellular automatons"""

import serge.actor


class OutOfRange(Exception):
    """A cell reference was out of range"""


class Otomata(serge.actor.Actor):
    """Implementation of an automaton based on the rules from Batuhan Bozkurt

    Source: http://www.earslap.com/projectslab/otomata

    """

    # States
    S_NULL = (0, 0)
    S_UP = (0, -1)
    S_DOWN = (0, 1)
    S_LEFT = (-1, 0)
    S_RIGHT = (1, 0)

    # Events
    E_BOUNCE = 'cell-bounce'

    rotations = {
        S_UP: S_RIGHT,
        S_RIGHT: S_DOWN,
        S_DOWN: S_LEFT,
        S_LEFT: S_UP,
    }

    def __init__(self, name, tag, size):
        """Initialise the automaton"""
        super(Otomata, self).__init__(name, tag)
        #
        self.frequency = 100.0
        self.size = size
        self.resetAutomaton()

    def resetAutomaton(self):
        """Set the automaton back to its initial state"""
        self.cells = {}
        self._time_to_go = self.frequency

    def setFrequency(self, frequency):
        """Set the update frequency"""
        self.frequency = frequency
        self._time_to_go = self.frequency

    def getFrequency(self):
        """Return the frequency"""
        return self.frequency

    def _inRange(self, (cx, cy)):
        """Return True if the cell is in range"""
        sx, sy = self.size
        return 0 <= cx < sx and 0 <= cy < sy

    def setState(self, (cx, cy), state):
        """Set the state of a cell"""
        if not self._inRange((cx, cy)):
            raise OutOfRange('The cell (%s, %s) is out of range' % (cx, cy))
        if state != self.S_NULL:
            self.cells[(cx, cy)] = [state]
        else:
            del(self.cells[(cx, cy)])

    def getState(self, (cx, cy)):
        """Return the state of a cell"""
        if not self._inRange((cx, cy)):
            raise OutOfRange('The cell (%s, %s) is out of range' % (cx, cy))
        return self.cells.get((cx, cy), [self.S_NULL])

    def updateState(self):
        """Update the state of the automaton"""
        self.log.debug('Updating state for %s' % self.getNiceName())
        new_cells = {}
        collisions = set()
        bounces = set()
        #
        # Go through all active cells and update their location
        for (cx, cy), states in self.cells.iteritems():
            for state in states:
                nx, ny = cx + state[0], cy + state[1]
                #
                # Watch for bouncing
                if not self._inRange((nx, ny)):
                    bounces.add((nx, ny))
                    nx, ny = cx, cy
                    state = state[0] * -1, state[1] * -1
                #
                try:
                    existing = new_cells[(nx, ny)]
                except KeyError:
                    new_cells[(nx, ny)] = [state]
                else:
                    collisions.add((nx, ny))
                    existing.append(state)
        #
        # Rotate all the cells that collided
        for cx, cy in collisions:
            #
            # Alter the cells to move clockwise
            items = new_cells[(cx, cy)]
            new_items = []
            for item in items:
                new_items.append(self.rotations[item])
            new_cells[(cx, cy)] = new_items
        #
        # Report bounces
        for bounce in bounces:
            self.processEvent((self.E_BOUNCE, bounce))
        #
        # Change the state to the new one
        self.cells = new_cells

    def updateActor(self, interval, world):
        """Update the automaton"""
        self._time_to_go -= interval
        while self._time_to_go <= 0:
            self._time_to_go += self.frequency
            self.updateState()