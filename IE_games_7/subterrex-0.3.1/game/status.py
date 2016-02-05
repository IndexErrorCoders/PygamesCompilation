"""Maintains the status of the player"""

import serge.actor

from theme import G, theme
import common 

class Status(serge.actor.Actor):
    """Represents the main player's status"""

    def __init__(self, tag, name):
        """Initialise the Status"""
        super(Status, self).__init__(tag, name)
        #
        self.time_left = G('player-initial-time')
        self.ropes = G('player-initial-ropes')
        self.blue_lights = G('initial-blue-lights')
        self.yellow_lights = G('initial-yellow-lights')
        self.green_lights = G('initial-green-lights')
        self.selected_light = G('initial-selected-light')
        self.camera_locked = False
        self.time_spent = 0
        self.total_crystals = 0
        self.collected_crystals = 0

    def updateActor(self, interval, world):
        """Update the actor"""
        super(Status, self).updateActor(interval, world)
        #
        self.time_left = max(0, self.time_left - interval / 1000.0)
        self.time_spent += interval / 1000.0
        
    def getNumberOfLights(self, colour):
        """Return the number of lights left for a colour"""
        return getattr(self, '%s_lights' % colour)
        
    def setNumberOfLights(self, colour, number):
        """Set the number of lights left for a colour"""
        return setattr(self, ('%s_lights' % colour), number)
        
