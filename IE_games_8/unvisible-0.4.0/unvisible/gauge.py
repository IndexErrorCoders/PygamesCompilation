"""A vertical guage"""

import pygame

import sprite
import drawable
import slots


class Gauge(slots.VerticalItemSlots):
    """A vertical gauge to count up"""

    def __init__(self, x, y, width, height, blank_image, fill_image, grey_image,
                 target_image, target_image_filled, number, gap, name):
        """Initialise the gauge"""
        super(Gauge, self).__init__(x, y, width, height, number, gap, name=name)
        #
        self.blank_image = blank_image
        self.fill_image = fill_image
        self.grey_image = grey_image
        self.target_image = target_image
        self.target_image_filled = target_image_filled
        self.number = number
        self.gap = gap
        self.template = None
        self.target = 0
        self.value = 0
        #
        self.initImage()

    def initImage(self):
        """Initialise the image"""
        for i in range(1, self.number + 1):
            self.showSlot(i)

    def showSlot(self, number):
        """Show a certain slot"""
        if number <= 0:
            self.log.info('Showing slot "Negative" (%d) slot ignored' % number)
        else:
            slot = self.slots[self.number - number]
            if slot.isOccupied():
                slot.removeItem()
            if number == self.target:
                image = self.target_image if self.value < self.target else self.target_image_filled
                self.log.debug('Showing target row: %s, %s, %s' % (self.value, self.target, image))
            elif number <= self.value:
                image = self.fill_image
            elif number <= self.target:
                image = self.blank_image
            else:
                image = self.grey_image
            self.log.debug('Showing %s cell %d as %s (value=%s, target=%s)' % (
                self.name, number, image, self.value, self.target))

            slot.addItem(sprite.Sprite(image))