"""Handles the sound and music"""

import os
import pygame

MUTED = False


class _Sounds(object):
    """Handle sounds"""

    def getSound(self, name):
        """Return a new sound"""
        if MUTED:
            return MutedSound()
        else:
            return pygame.mixer.Sound(os.path.join('data', 'sounds', name))

    def playMusic(self, name):
        """Return a new sound"""
        if not MUTED and False:
            pygame.mixer.music.load(os.path.join('data', 'music', name))
            pygame.mixer.music.play(-1)


Sounds = _Sounds()


class MutedSound:

    def play(self):
        """Do not play!"""
        pass