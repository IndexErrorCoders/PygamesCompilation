"""Implements a grid that shows the state of the automaton and plays sounds"""

import serge.actor
import serge.events
import serge.sound
import serge.blocks.layout
import serge.blocks.cellular
import serge.blocks.utils

from theme import G


class MusicGrid(serge.actor.Actor):
    """Implements the grid that shows the automaton and plays music"""

    def __init__(self, tag, name, size, frequency, instrument):
        """Initialise the grid"""
        super(MusicGrid, self).__init__(tag, name)
        #
        self.size = size
        self.frequency = frequency
        self.instrument = instrument
        self.running = True
        #
        # Set up the automaton
        self.automaton = serge.blocks.cellular.Otomata('automaton', 'automaton', size)
        self.automaton.setFrequency(frequency)
        self.automaton.linkEvent(self.automaton.E_BOUNCE, self.bounceOccurred)
        #
        self.sprites = {
            self.automaton.S_LEFT: 'left',
            self.automaton.S_RIGHT: 'right',
            self.automaton.S_UP: 'up',
            self.automaton.S_DOWN: 'down',
            self.automaton.S_NULL: 'null',
        }

    def addedToWorld(self, world):
        """Added to the world"""
        super(MusicGrid, self).addedToWorld(world)
        #
        # Set up the grid to show the state
        self.layout = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.layout.Grid(
                'grid', 'grid', self.size, G('grid-width'), G('grid-height'),
                background_colour=G('grid-background-colour'), background_layer='background',
            ),
            layer_name='main',
            center_position=G('grid-position'),
        )
        #
        # Add actors
        for ix in range(self.size[0]):
            for iy in range(self.size[1]):
                actor = serge.actor.Actor('cell', 'cell-%d-%d' % (ix, iy))
                actor.setSpriteName('null')
                actor.setLayerName('main')
                actor.linkEvent(serge.events.E_LEFT_CLICK, self.cellClick, (ix, iy))
                self.layout.addActor((ix, iy), actor)
        #
        world.addActor(self.automaton)

    def updateActor(self, interval, world):
        """Update the actor"""
        #
        # Redraw the grid
        for ix in range(self.size[0]):
            for iy in range(self.size[1]):
                actor = self.layout.getActorAt((ix, iy))
                state = self.automaton.getState((ix, iy))
                actor.setSpriteName(self.sprites[state[0]])

    def cellClick(self, obj, (cx, cy)):
        """A cell was clicked on"""
        self.log.info('Clicked on cell %s, %s' % (cx, cy))
        #
        if self.automaton.getState((cx, cy)) == [self.automaton.S_NULL]:
            self.automaton.setState((cx, cy), self.automaton.S_UP)
        else:
            self.automaton.setState((cx, cy), self.automaton.S_NULL)

    def setRunning(self, state):
        """Update the running state"""
        self.running = state
        self.automaton.active = state

    def setBeatsPerMinute(self, bpm):
        """Set the beats per minute"""
        self.frequency = 60.0 / bpm * 1000.0 / self.size[0]
        self.automaton.setFrequency(self.frequency)

    def bounceOccurred(self, (cx, cy), arg):
        """A bounce occurred"""
        self.log.debug('Bounce occurred at %d, %d' % (cx, cy))
        #
        self.instrument.playCell((cx, cy))

    def setInstrument(self, instrument):
        """Set the current instrument"""
        self.instrument = instrument