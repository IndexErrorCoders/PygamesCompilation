"""Sprite that can be drawn on the screen and receives click events"""

import os
import pygame
import drawable


class Sprite(drawable.Drawable):
    """Represents a sprite on the screen"""

    def __init__(self, filename, x=0, y=0, name=None):
        """Initialise the sprite"""
        self.filename = filename
        surface = self.loadImage(filename)
        actual_name = name if name else os.path.splitext(filename)[0]
        super(Sprite, self).__init__(x, y, surface=surface, name=actual_name)

    def loadImage(self, filename):
        """Load an image from a file"""
        surface = pygame.image.load(os.path.join('data', 'graphics', filename))
        return surface


