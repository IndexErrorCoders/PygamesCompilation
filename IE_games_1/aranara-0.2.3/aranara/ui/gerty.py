"""Represents the visual persona of Gerty"""

import pyglet

from .. import engine
from .. import settings
import common

S_HAPPY = 'gerty-happy.png'
S_CONCERNED = 'gerty-concerned.png'
S_WORRIED = 'gerty-worried.png'
S_SAD = 'gerty-sad.png'

STATES = (S_HAPPY, S_CONCERNED, S_WORRIED, S_SAD)

# World states
W_INITIAL = 'world-initial'
W_LAST_SPOKE = 'last-spoke'
W_SCORED = 'scored'
W_SCORED_NEGATIVE = 'scored-negative'
W_LAST_SCORE = 'last-score'
W_TOTAL_SCORE = 'total-score'
W_GERTY = 'gerty'
W_HAD_BAD_SCORE = 'had-bad-score'
W_CLICKED_PALETTE = 'clicked-palette'
W_TOTAL_TIME = 'total-time'
W_LEVEL_COMPLETE = 'level-complete'
W_TIME_SINCE_COMPLETE = 'time-since-complete'
W_ROTATION_OCCURRED = 'rotation-occurred'
W_ITEMS_IN_PALETTE = 'items-in-palette'
W_LEVELS_SOLVED = 'levels-solved'
W_TIME_LEVEL_SOLVED = 'time-level-solved'
W_TIME_LEVEL_ENTERED = 'time-level-entered'


class GertyUI(common.HideableComponent):
    """The UI for Gerty"""

    def __init__(self, name, *args, **kw):
        """Initialise Gerty"""
        super(GertyUI, self).__init__(name, S_HAPPY, *args, **kw)
        #
        self.states = {}
        for state in STATES:
            img = self.states[state] = pyglet.resource.image(state)
            img.anchor_x = img.width / 2
            img.anchor_y = img.height / 2
        #
        self.setState(S_HAPPY)
        self.world_state = None
        self.conversation = []
        pyglet.clock.schedule_interval(self.checkConversation, settings.S.gerty_conversation_check_interval)
        #
        # Hideable properties
        self.on_screen_position = settings.S.gerty_on_screen_position
        self.off_screen_position = settings.S.gerty_off_screen_position
        self.hide_duration = settings.S.gerty_hide_duration

    def setWorldState(self, dct):
        """Set the dictionary of states of the world - used to control conversation"""
        self.world_state = dct

    def setConversation(self, conversation):
        """Set the conversation logic"""
        self.conversation = conversation

    def addedToWorld(self, world):
        """We were added to the world"""
        super(GertyUI, self).addedToWorld(world)
        #
        self.bg = self.mountActor(
            engine.SpriteActor('gerty-bg', 'gerty-background.png', batch=self.batch, group=world.gerty_back),
            settings.S.gerty_bg_offset
        )
        #
        self.text = self.mountActor(
            engine.TextActor(
                'gerty-text',
                pyglet.text.decode_html('<b>Hello Sam</b>. How are you doing today?'),
                batch=self.batch,
                group=world.gerty_text
            ),
            settings.S.gerty_text_offset
        )
        #
        # Add all the buttons
        self.buttons = []
        for idx in range(settings.S.gerty_number_buttons):
            btn = self.mountActor(
                engine.TextActor(
                    'gerty-btn-%d' % idx,
                    pyglet.text.decode_text(''),
                    batch=self.batch,
                    group=world.ui_front
                ),
                settings.S.gerty_button_origin_offset + idx * settings.S.gerty_button_offset
            )
            btn.linkEvent(engine.events.E_LEFT_CLICK, self.buttonClick, idx)
            self.buttons.append(btn)
        #
        self.position = settings.S.gerty_off_screen_position
        #
        self.showing = False

    def updateActor(self, world, dt):
        """Update the actor"""
        super(GertyUI, self).updateActor(world, dt)

    def setState(self, state):
        """Set Gerty's state"""
        self.image = self.states[state]

    def say(self, text):
        """Say some text"""
        #
        # Make sure we are showing
        if not self.showing:
            self.show()
        #
        self.text.document = pyglet.text.decode_html('<b>Gerty:</b><i><br><br>' + text)
        self.text.width = settings.S.gerty_width
        self.text.multiline = True
        self.clearButtons()

    def clearButtons(self):
        """Remove text from buttons"""
        for button in self.buttons:
            button.document.text = ''

    def buttonClick(self, actor, index):
        """A button was clicked"""
        self.log.info('Gerty button %d was clicked' % index)

    def askQuestion(self, text, buttons):
        """Ask a question"""
        #
        # Put up the question
        self.say(text)
        #
        # And set the right buttons
        for text, button in zip(buttons, self.buttons):
            button.document.text = text

    def checkConversation(self, dt):
        """Check for new conversation states"""
        #
        for idx, (name, remove, states, actions) in enumerate(self.conversation[:]):
            for state in states:
                if not state(self.world_state):
                    break
            else:
                # The state was True
                self.log.debug('State for "%s" matched' % name)
                for action in actions:
                    apply(action[0], action[1:] + (self.world_state, self))
                if remove:
                    del(self.conversation[idx])
                break

