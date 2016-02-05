"""Representations of the dice"""

import time
import random

import sprite
import drawable
import slots
import settings as S


class Dice(drawable.Drawable):
    """Represents a dice"""

    def __init__(self, x=0, y=0, colour='white'):
        """Initialise the dice"""
        colour_text = '' if colour == 'white' else 'black-'
        #
        # TODO: Last minute hack to switch the colours around - this is only
        # allowed because it is 40 mins to go until the end of the competition!
        colour_text = 'black-' if colour_text == '' else ''
        #
        self.colour = colour
        self.images = []
        for i in range(6):
            self.images.append(sprite.Sprite('%sdice-%d.png' % (colour_text, i + 1)))
        #
        super(Dice, self).__init__(x, y, surface=self.images[0].surface)
        #
        self.value = 1
        self.rolling_duration = S.Dice.roll_duration
        self.current_rolled_for = 0
        self.roll_start = 0
        self.interval_timer = 0
        self.last_update = 0
        self.roll_interval = S.Dice.roll_interval
        self.rolling = False

    def rollDice(self):
        """Start rolling the dice"""
        self.roll_start = time.time() + random.uniform(*S.Dice.randomness)
        self.last_update = time.time()
        self.interval_timer = 0
        self.rolling = True

    def renderTo(self, surface, x=0, y=0):
        """Render this dice"""
        super(Dice, self).renderTo(surface, x, y)
        #
        if self.rolling:
            if time.time() - self.roll_start >= self.rolling_duration:
                self.rolling = False
            else:
                self.interval_timer += time.time() - self.last_update
                self.last_update = time.time()
                if self.interval_timer > self.roll_interval:
                    self.interval_timer = 0
                    self.value = random.randint(1, 6)
                    self.surface = self.images[self.value - 1].surface


class DiceSlots(slots.VerticalItemSlots):
    """Slots for dice"""

    def rollDice(self):
        """Roll all the dice"""
        for slot in self.slots:
            slot.item.rollDice()

    def isRolling(self):
        """Return True if any dice are still rolling"""
        for slot in self.slots:
            if slot.item.rolling:
                return True
        else:
            return False