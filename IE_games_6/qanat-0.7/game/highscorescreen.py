"""The high score screen"""


import pygame

import serge.actor
import serge.engine
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.visualeffects
import serge.blocks.onlinescores
import serge.blocks.layout
import serge.blocks.achievements

from theme import G, theme
import common


class HighScoreScreen(serge.blocks.actors.ScreenActor):
    """The logic for the main screen"""

    def __init__(self):
        """Initialise the screen"""
        super(HighScoreScreen, self).__init__('item', 'high-score-screen')

    def addedToWorld(self, world):
        """We were added to the world"""
        super(HighScoreScreen, self).addedToWorld(world)
        self.manager = world.findActorByName('behaviours')
        L = theme.getTheme('high-score-screen').getProperty
        #
        self.main_title = serge.blocks.utils.addSpriteActorToWorld(
            world, 'title', 'main-title', 'logo', 'ui', L('logo-position'))
        #
        self.title = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.StringText(
                'text', 'title', 'Web High Scores', colour=L('title-colour'),
                font_size=L('title-size'), justify='center',
            ),
            layer_name='ui',
            center_position=L('title-position')
        )
        #
        self.back = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.StringText(
                'text', 'back', 'Back', colour=L('back-colour'),
                font_size=L('back-font-size'), justify='center',
                font_name=L('back-font-name')
            ),
            layer_name='ui',
            center_position=L('back-position')
        )
        self.back.linkEvent(serge.events.E_LEFT_CLICK, serge.blocks.utils.backToPreviousWorld())
        #
        # The table
        player_name = serge.blocks.utils.getUniqueID()
        self.table = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.onlinescores.SimpleHSTableView(
                'hs-table', 'hs-table', L('app-url'), L('app-game'), L('app-category'),
                player_name, L('max-scores'),
                serge.blocks.layout.VerticalBar(
                    'vbar', 'vbar', L('table-width'), item_height=L('table-item-height')
                ),
                theme.getTheme('high-score-screen'),
                fmt='%(num)02d ... %(score)06d'
            ),
            layer_name='ui',
            center_position=L('table-position')
        )
        self.table.layout.setLayerName('ui')
        self.table.ensurePlayer()
        self.table.updateScores()
        common.HIGH_SCORE_TABLE = self.table
        #
        # Best
        self.best = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.NumericText(
                'text', 'best', 'Your best: %06d', colour=L('hs-font-player-colour'),
                font_size=L('best-font-size'), justify='center',
                font_name=L('best-font-name'),
                value=0
            ),
            layer_name='ui',
            center_position=L('best-position')
        )
        #
        # Refresh button
        self.refresh = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.StringText(
                'btn', 'refresh', 'Refresh', colour=L('refresh-colour'),
                font_size=L('refresh-size'), justify='center',
                font_name=L('refresh-name'),
            ),
            layer_name='ui',
            center_position=L('refresh-position')
        )
        self.refresh.linkEvent(serge.events.E_LEFT_CLICK, self.refreshScores)

    def updateActor(self, interval, world):
        """Update this actor"""
        self.best.value = common.CURRENT_HIGH_SCORE

    def refreshScores(self, obj, arg):
        """Refresh the scores"""
        self.refresh.value = 'Refreshing ...'
        self.table.updateScores(self.refreshDone)

    def refreshDone(self):
        """Called when the refresh operation is complete"""
        self.refresh.value = 'Refresh'


def main(options):
    """Create the main logic"""
    #
    # The behaviour manager
    world = serge.engine.CurrentEngine().getWorld('high-score-screen')
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # The screen actor
    s = HighScoreScreen()
    s.options = options
    world.addActor(s)
    #
    # Snapshots
    if options.screenshot:
        manager.assignBehaviour(
            None,
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshot')