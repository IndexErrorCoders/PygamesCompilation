"""Handling text"""

import os
import pygame
import drawable


pygame.font.init()


class _Fonts(object):
    """Handle fonts"""

    def __init__(self):
        """Initialise the fonts"""
        self.font_cache = {}

    def getFont(self, name, size):
        """Load a font"""
        try:
            return self.font_cache[(name, size)]
        except KeyError:
            f = pygame.font.Font(os.path.join('data', 'fonts', name), size)
            self.font_cache[(name, size)] = f
            return f

Fonts = _Fonts()


class Text(drawable.Drawable):
    """Draws text on the screen"""

    def __init__(self, x, y, text, font, colour, line_height=0, pad_bottom=0, anchor=drawable.A_CENTER):
        """Initialise the text"""
        self.font = font
        self.colour = colour
        self.line_height = line_height
        self.pad_bottom = pad_bottom
        #
        self.setText(text)
        super(Text, self).__init__(x, y, surface=self.surface, name='Text (%s)' % text, anchor=anchor)

    def setText(self, text):
        """Return a surface with the text on it"""
        #
        # Account for multiple lines
        width = 0
        lines = text.splitlines()
        for line in lines:
            width = max(self.font.size(line)[0], width)
        height = self.line_height if self.line_height else self.font.get_height()
        #
        self.surface = pygame.Surface((width, height * len(lines) + self.pad_bottom), pygame.SRCALPHA, 32)
        for i, line in enumerate(lines):
            self.surface.blit(self.font.render(line, True, self.colour),
                              (width / 2 - self.font.size(line)[0] / 2, float(i) * height))