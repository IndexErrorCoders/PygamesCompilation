import pygame
import os

from pygame.locals import *

from locals import *

from log import error_message

import data

class Frame:

  def __init__(self, object, anim_name, frameno, frame_length):
    try:
      self.image = pygame.image.load(data.picpath(object, anim_name, frameno)).convert()
    except:
      try:
        self.image = pygame.image.load(data.picpath("brown", anim_name, frameno)).convert() #Fallback to brown tileset
      except:
        self.image = pygame.image.load(data.picpath("object", "idle", 0)).convert() #Fallback to default object image
        error_message("Object graphic missing: " + object + "_" +  anim_name + "_" + str(frameno))
    self.frame_length = frame_length
    self.image.set_colorkey((255,0,255))
    return

  def get_image(self):
    return self.image

  def get_time(self):
    return self.frame_length