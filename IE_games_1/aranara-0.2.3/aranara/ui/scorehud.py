"""HUD for the score"""

"""The palette of objects that the player can put on the screen"""

import pymunk
import pyglet

from .. import engine
from .. import settings
from .. import sound
# TODO: fix this import - this is ugly
from .. import common as gamecommon
import common

# TODO: add text to show the number of objects to the palette


class ScoreHUD(common.HideableComponent):
    """Represents the head up display for the score"""

    def __init__(self, name, *args, **kw):
        """Initialise the palette"""
        super(ScoreHUD, self).__init__(name, 'score-hud.png', *args, **kw)
        #
        # Hideable properties
        self.on_screen_position = settings.S.ScoreHUD.on_screen_position
        self.off_screen_position = settings.S.ScoreHUD.off_screen_position
        self.hide_duration = settings.S.ScoreHUD.hide_duration
        #
        self.opacity = settings.S.ScoreHUD.opacity

    def addedToWorld(self, world):
        """We were added to the world"""
        super(ScoreHUD, self).addedToWorld(world)
        #
        # Name
        name_label = engine.TextActor(
            'name-label',
            pyglet.text.decode_attributed('{font_name "Sci Fied 2002"}{font_size 20}%s' % world.name),
            batch=self.batch,
            group=self.world.ui_front
        )
        name_label.anchor_x = 'left'
        self.mountActor(name_label, (settings.S.ScoreHUD.name_label_x, settings.S.ScoreHUD.name_label_y))
        #
        # Time
        self.time_label = engine.TextActor(
            'time-label',
            pyglet.text.decode_attributed('{font_name "Sci Fied 2002"}{font_size 14}Level Time'),
            batch=self.batch,
            group=self.world.ui_front
        )
        self.time_label.anchor_x = 'left'
        self.mountActor(self.time_label, (settings.S.ScoreHUD.time_label_x, settings.S.ScoreHUD.time_label_y))
        #
        # Total Time
        self.total_time_label = engine.TextActor(
            'total-time-label',
            pyglet.text.decode_attributed('{font_name "Sci Fied 2002"}{font_size 14}Total Time'),
            batch=self.batch,
            group=self.world.ui_front
        )
        self.total_time_label.anchor_x = 'left'
        self.mountActor(self.total_time_label, (settings.S.ScoreHUD.total_time_label_x, settings.S.ScoreHUD.total_time_label_y))
        #
        self.level_time = 0

    def updateActor(self, world, dt):
        """Update the display"""
        super(ScoreHUD, self).updateActor(world, dt)
        #
        # Only update if the level is not complete
        if not world.level_complete:
            #
            # Update level time
            self.level_time += dt
            self.time_label.document.text = 'Level Time - %02d:%02d' % (self.level_time // 60, self.level_time % 60)
            #
            # Update total game time
            gamecommon.total_time += dt
            self.total_time_label.document.text = 'Total Time - %02d:%02d' % (gamecommon.total_time // 60, gamecommon.total_time % 60)
