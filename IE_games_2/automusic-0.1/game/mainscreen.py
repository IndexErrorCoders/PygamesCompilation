"""The main screen for the game"""

import pygame

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.layout
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

from theme import G, theme
import musicgrid
import soundinstrument
import instruments.piano


class MainScreen(serge.blocks.actors.ScreenActor):
    """The logic for the main screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(MainScreen, self).__init__('item', 'main-screen')
        self.options = options

    def addedToWorld(self, world):
        """Added to the world"""
        super(MainScreen, self).addedToWorld(world)
        #
        # The music grid
        self.grid = serge.blocks.utils.addActorToWorld(
            world,
            musicgrid.MusicGrid('grid', 'grid', G('grid-size'), G('grid-frequency'), None),
        )
        #
        # Play button
        self.play = serge.blocks.utils.addSpriteActorToWorld(
            world, 'button', 'play',
            'play',
            layer_name='ui',
            center_position=G('play-button-position'),
        )
        self.play.linkEvent(serge.events.E_LEFT_CLICK, self.playClick)
        #
        # Pause button
        self.pause = serge.blocks.utils.addSpriteActorToWorld(
            world, 'button', 'pause',
            'pause',
            layer_name='ui',
            center_position=G('pause-button-position'),
        )
        self.pause.linkEvent(serge.events.E_LEFT_CLICK, self.pauseClick)
        #
        # Stop the automaton
        self.pauseClick(None, None)
        #
        # Frequency options
        bar = serge.blocks.layout.HorizontalBar(
            'bar', 'hbar', width=G('frequencies-width')
        )
        self.frequencies = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.ToggledMenu(
                'menu', 'frequencies', map(str, G('grid-frequency-options')), bar,
                default=str(G('grid-frequency')),
                on_colour=G('frequencies-on-colour'),
                off_colour=G('frequencies-off-colour'),
                width=G('frequencies-item-width'),
                height=G('frequencies-height'),
                callback=self.frequenciesClick,
                font_size=G('frequencies-font-size')
            ),
            center_position=G('frequencies-position')
        )
        bar.setLayerName('ui')
        #
        serge.blocks.utils.addTextToWorld(
            world, 'Beats per minute', 'bpm', theme, 'ui'
        )
        #
        # Instrument options
        self.possible_instruments = dict(
            [(module.name, soundinstrument.Instrument.getFromModule(module)) for module in instruments.instrument_modules]
        )
        instrument_names = sorted(self.possible_instruments.keys())
        #
        bar = serge.blocks.layout.HorizontalBar(
            'bar', 'hbar', width=G('instruments-width')
        )
        self.instruments = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.ToggledMenu(
                'menu', 'instruments', instrument_names, bar,
                default=instrument_names[0],
                on_colour=G('instruments-on-colour'),
                off_colour=G('instruments-off-colour'),
                width=G('instruments-item-width'),
                height=G('instruments-height'),
                callback=self.instrumentsClick,
                font_size=G('instruments-font-size')
            ),
            center_position=G('instruments-menu-position')
        )
        bar.setLayerName('ui')
        #
        serge.blocks.utils.addTextToWorld(
            world, 'Instrument', 'instruments', theme, 'ui'
        )

        #
        # Cheating
        if self.options.cheat:
            fps = serge.blocks.utils.addActorToWorld(world,
                serge.blocks.actors.FPSDisplay(G('fps-x'), G('fps-y'), G('fps-colour'), G('fps-size')))

    def updateActor(self, interval, world):
        """Update this actor"""
        super(MainScreen, self).updateActor(interval, world)

    def playClick(self, obj, arg):
        """The play button was clicked"""
        if not self.grid.running:
            self.log.info('Play clicked')
            self.grid.setRunning(True)
            self.play.visual.setCell(0)
            self.pause.visual.setCell(1)
        else:
            self.pauseClick(None, None)

    def pauseClick(self, obj, arg):
        """The pause button was clicked"""
        if self.grid.running:
            self.log.info('Pause clicked')
            self.grid.setRunning(False)
            self.play.visual.setCell(1)
            self.pause.visual.setCell(0)
        else:
            self.playClick(None, None)

    def frequenciesClick(self, obj, new_value):
        """The frequencies menu was clicked"""
        self.log.info('Clicked on frequency %s' % new_value)
        #
        self.grid.setBeatsPerMinute(int(new_value))

    def instrumentsClick(self, obj, new_value):
        """The instruments menu was clicked"""
        self.log.info('Clicked on instrument %s' % new_value)
        #
        self.grid.setInstrument(self.possible_instruments[new_value])


def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = MainScreen(options)
    world = serge.engine.CurrentEngine().getWorld('main-screen')
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(), 'keyboard-quit')
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

