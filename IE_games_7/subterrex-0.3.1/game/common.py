"""Common elements"""

import pygame
import os
import sys

import serge.engine
import serge.common
import serge.blocks.scores

log = serge.common.getLogger('Game')
from theme import G, theme

version = '0.3.1' 

#
# Events
#
# Put events here with names E_MY_EVENT
# and they will be registered automatically
#
# E_GAME_STARTED = 'game-started'
E_ROCK_CLICKED = 'rock-clicked'
E_ROCK_RIGHT_CLICKED = 'rock-right-clicked'
E_ADD_LIGHT = 'add-light'
E_CAVE_SELECTED = 'cave-selected'
E_PLAYER_DIED = 'player-died'
E_CAVE_SOLVED = 'cave-solved'
E_BANNER_SHOW = 'banner-show'

#
# Progress constants
P_NO_CAVE = 'no-cave'
P_IN_CAVE = 'in-cave'
P_DIED_IN_CAVE = 'died-in-cave'


def info(type, value, tb):
   if hasattr(sys, 'ps1') or not sys.stderr.isatty():
      # we are in interactive mode or we don't have a tty-like
      # device, so we call the default hook
      sys.__excepthook__(type, value, tb)
   else:
      import traceback, pdb
      # we are NOT in interactive mode, print the exception...
      traceback.print_exception(type, value, tb)
      print
      # ...then start the debugger in post-mortem mode.
      pdb.pm()

sys.excepthook = info


def getOverlays(world, text, visible=False):
    """Return some overlays to display when creating the main rendering"""
    overlay = serge.blocks.utils.addVisualActorToWorld(world, 'overlay', 'overlay', 
        serge.blocks.visualblocks.Rectangle((G('screen-width'), G('screen-height')), (0, 0, 0)),
        'overlay', 
        center_position=(G('screen-width')/2, G('screen-height')/2))
    overlay_text = serge.blocks.utils.addTextToWorld(world, text, 'overlay', theme.getTheme('overlay-screen'), 'overlay')
    overlays = serge.actor.ActorCollection([overlay, overlay_text])
    overlays.forEach().visible = visible
    #
    return overlays



