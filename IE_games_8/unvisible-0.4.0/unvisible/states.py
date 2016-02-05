"""Game states"""

import pygame

import loggable
import settings as S


class StateMachine(loggable.Loggable):
    """A state machine to use for handling the screen"""

    verbose = True

    def __init__(self, initial_state, speed_factor):
        """Initialise the machine"""
        self.addLogger()
        self.speed_factor = speed_factor
        self.method = None
        self.delay = 0
        self.clicked_on = None
        self.state = initial_state
        self.state_clock = pygame.time.Clock()
        #
        self.initUI()

    def initUI(self):
        """Initialise the user interface"""

    def updateState(self, clicked_on):
        """Update the game state"""
        self.state_clock.tick(S.Screen.fps)
        self.delay -= self.state_clock.get_time() * self.speed_factor
        #self.log.debug('Delay is now %s' % self.delay)
        self.clicked_on = clicked_on
        #
        if self.state and self.delay < 0:
            if self.method is None:
                self.method = getattr(self, self.state.lower())()
                if self.verbose:
                    self.log.debug('Calling state: %s' % self.state)
            try:
                self.delay = self.method.next()
            except StopIteration:
                self.method = None
        elif self.clicked_on:
            self.log.debug('Missed a click ("%s", %s)' % (self.state, self.delay))

    def processClick(self, event_type, (x, y)):
        """Process a click event"""

    def processKey(self, key):
        """Process a key press"""
        if key == pygame.K_ESCAPE:
            return pygame.QUIT