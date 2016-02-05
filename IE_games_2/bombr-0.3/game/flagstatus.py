"""Displays the status of the capture the flag aspect of the game"""

import serge.actor
import serge.sound
import serge.events

from theme import G
import common


class FlagStatus(serge.actor.CompositeActor):
    """Shows the status of the capture the flag game"""

    def __init__(self, tag, name):
        """Initialise the status"""
        super(FlagStatus, self).__init__(tag, name)
        #
        self.setSpriteName('flag-status')
        self.flag_position = 0
        self.time_limit = G('flag-time-limit')
        self.currently_carrying = None
        self.flag_position_width = G('flag-position-width')
        self.flag_offset_x = G('flag-position-offset-x')
        self.flag_offset_y = G('flag-position-offset-y')
        self.broadcaster = serge.events.getEventBroadcaster()
        self._updating = True

    def addedToWorld(self, world):
        """Added to the world"""
        super(FlagStatus, self).addedToWorld(world)
        #
        self.flag = self.addChild(
            serge.actor.Actor('flag', 'flag')
        )
        self.flag.setSpriteName(G('flag-sprite-name'))
        self.flag.setLayerName('ui-front')
        self.flag.setZoom(G('flag-zoom'))
        #
        self.broadcaster.linkEvent(common.E_FLAG_CAPTURED, self.flagCaptured)

    def updateActor(self, interval, world):
        """Update the status"""
        super(FlagStatus, self).updateActor(interval, world)
        #
        # Update the position
        if self._updating:
            if self.currently_carrying:
                multiplier = -1 if self.currently_carrying == 'player' else 1
                self.flag_position = min(1.0, max(-1.0, self.flag_position + multiplier * interval / 1000.0 / self.time_limit))
                #
                # Check for winner
                if self.flag_position == 1:
                    self.processEvent((common.E_FLAG_WON, 'ai'))
                elif self.flag_position == -1:
                    self.processEvent((common.E_FLAG_WON, 'player'))
            #
            # Move the flag indicator
            self.flag.moveTo(
                self.x + self.flag_offset_x + self.flag_position * self.flag_position_width,
                self.y + self.flag_offset_y
            )

    def flagCaptured(self, capturer, arg):
        """The flag was captured"""
        self.log.info('Flag has been captured by %s' % capturer.getNiceName())
        self.currently_carrying = capturer.name
        serge.sound.Sounds.play('flag-taken')

    def stopUpdating(self):
        """Stop updating"""
        self._updating = False

    def resetAndStart(self):
        """Start updating"""
        self.flag_position = 0
        self.currently_carrying = None
        self._updating = True