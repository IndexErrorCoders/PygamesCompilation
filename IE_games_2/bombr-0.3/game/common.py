"""Common elements"""

import pygame
import os
import sys

import serge.engine
import serge.common
import serge.blocks.scores
import serge.blocks.screentween

log = serge.common.getLogger('Game')
from theme import G

version = '0.3'

#
# Events
#
# Put events here with names E_MY_EVENT
# and they will be registered automatically
#
E_MAN_DIED = 'man-died'
E_FLAG_CAPTURED = 'flag-captured'
E_FLAG_WON = 'flag-won'
E_SMACK_APPEAR = 'smack-appear'
E_SMACK_HIDE = 'smack-hide'

#
# Action replay frames
ACTION_REPLAY_FRAMES = []

#
# Main music
MAIN_MUSIC = None

#
# Whether a level is in progress
LEVEL_IN_PROGRESS = False

#
# Tween between worlds
TWEENER = serge.blocks.screentween.ScreenTween('tweener')


def tweenWorlds(to_world):
    """Move between worlds"""
    def tweener(obj=None, arg=None):
        TWEENER.tweenToWorld(to_world, G('tween-world-time'), serge.blocks.screentween.SplitScreen, 'click')
    return tweener


def tweenBackWorlds(to_world):
    """Move between worlds"""
    def tweener(obj=None, arg=None):
        TWEENER.tweenToWorld(to_world, G('tween-world-time'), serge.blocks.screentween.ReverseSplitScreen, 'click')
    return tweener