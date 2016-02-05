'''A very simple sound module. Handles opening .ogg sound files,
playing sounds at different volumes and caching.

Use the play_sound function. It fetches and caches .ogg sound files
from the "sounds" subdirectory of the data directory and plays them.
Prints error messages if the sound file is not found or the sound
can't be played. Doesn't throw exceptions.

Usage of the module requires the Variables class from the variables module
and the data module.'''

import pygame
from pygame.locals import *
import os

import data

from variables import Variables

from log import error_message

sounds = {}

def play_sound(sound_id, volume = 1.0):
  if not Variables.vdict["sound"]:
    return
  snd = None
  if (not sounds.has_key(sound_id)):
    try:
      sound_path = data.filepath(os.path.join("sounds", sound_id + ".ogg"))
      snd = sounds[sound_id] = pygame.mixer.Sound(sound_path)
    except:
      error_message("No sound device available or sound file not found: " + sound_id + ".ogg")
      return
  else:
    snd = sounds[sound_id]
  try:
    snd.set_volume(volume)
    snd.play()
  except:
    error_message("Could not play sound")
  return
