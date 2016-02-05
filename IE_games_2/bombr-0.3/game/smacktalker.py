"""Talks smack back to the player during the game"""

import os
import textwrap
import random

import serge.actor
import serge.events
import serge.blocks.utils
import serge.blocks.textgenerator
import serge.blocks.actors

from theme import G, theme
import common


class SmackTalker(serge.actor.CompositeActor):
    """Talks smack back to the player"""

    def __init__(self, tag, name, theme_name):
        """Initialise the talker"""
        super(SmackTalker, self).__init__(tag, name)
        #
        self.theme_name = theme_name

    def addedToWorld(self, world):
        """Added to the world"""
        super(SmackTalker, self).addedToWorld(world)
        #
        the_theme = theme.getTheme(self.theme_name)
        L = the_theme.getProperty
        self.line_length = L('smack-line-length')
        #
        self.icon = serge.blocks.utils.addSpriteActorToWorld(
            world, 'icon', 'smack-icon', 'head',
            center_position=L('smack-icon-position'),
            layer_name='ui',
        )
        self.addChild(self.icon )
        #
        self.bubble = serge.blocks.utils.addSpriteActorToWorld(
            world, 'icon', 'smack-bubble', 'speech-bubble',
            center_position=L('smack-bubble-position'),
            layer_name='ui',
        )
        self.addChild(self.bubble)
        #
        self.text = serge.blocks.utils.addTextToWorld(
            world, 'Some text that is potentially long\nwith line breaks', 'smack-text', the_theme,
            layer_name='ui-front',
        )
        self.addChild(self.text)
        #
        self.generator = serge.blocks.textgenerator.TextGenerator()
        self.generator.addExamplesFromFile(os.path.join('game', 'smack-talk.txt'))
        #
        self.hide_timer = self.addChild(serge.blocks.actors.Timer(
            'timer', '%s-hide-timer' % self.name,
            L('smack-hide-interval'),
            callback=self.hideNow,
            started=False,
        ))
        #
        # Clear smack talker when leaving the screen
        world.linkEvent(serge.events.E_DEACTIVATE_WORLD, lambda o, a: self.hideNow())

    def makeVisible(self, sentence):
        """Make the smack visible"""
        self.processEvent((common.E_SMACK_APPEAR, self))
        text = self.generator.getRandomSentence('@{%s}@' % sentence)
        wrapped_text = '\n'.join(textwrap.wrap(text, self.line_length))
        self.text.visual.setText(wrapped_text)
        self.visible = True
        self.hide_timer.resetTimer()
        self.hide_timer.startTimer()

    def hideNow(self):
        """Hide the talk now"""
        self.processEvent((common.E_SMACK_HIDE, self))
        self.visible = False
        self.hide_timer.resetAndStopTimer()

    def deathOfAI(self):
        """The AI died"""
        self.makeVisible('ai-death')

    def deathOfPlayer(self):
        """The player died"""
        self.makeVisible('player-death')


class RandomlyAppearingSmacker(SmackTalker):
    """A smack talker that appears randomly"""

    def __init__(self, tag, name, theme_name, conversation, random_on=True):
        """Initialise the smacker"""
        super(RandomlyAppearingSmacker, self).__init__(tag, name, theme_name)
        #
        self.conversation = conversation
        self._random_on = random_on

    def addedToWorld(self, world):
        """Added to the world"""
        super(RandomlyAppearingSmacker, self).addedToWorld(world)
        #
        the_theme = theme.getTheme(self.theme_name)
        L = the_theme.getProperty
        #
        # Parameters
        self.timer = self.addChild(serge.blocks.actors.Timer(
            'timer', 'timer-%s' % self.name,
            L('smack-delay'), L('smack-delay') + L('smack-offset'),
            self._showRandom
        ))
        if self._random_on:
            self.enableRandomShowing()

    def _showRandom(self):
        """Show based on random time trigger"""
        self.makeVisible(self.conversation)
        self.timer.stopTimer()

    def enableRandomShowing(self):
        """Enable the random showing"""
        self.timer.startTimer()

    def disableRandomShowing(self):
        """Disable the random showing"""
        self.timer.resetAndStopTimer()

    def hideNow(self):
        """Hide the talker"""
        super(RandomlyAppearingSmacker, self).hideNow()
        self.timer.resetAndStartTimer()