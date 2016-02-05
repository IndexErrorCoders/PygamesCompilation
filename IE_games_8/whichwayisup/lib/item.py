import pygame
import os

from pygame.locals import *

from locals import *

import data

from visibleobject import VisibleObject
from animation import Animation
from trigger import Trigger
from log import log_message

class Item(VisibleObject):

  def __init__(self, screen, x = None, y = None, set = "brown", itemclass = "key", max_activations = 1, trigger_type = None):
    VisibleObject.__init__(self, screen, x, y)
    self.animations["default"] = Animation(set, itemclass)

    try:
      self.animations["broken"] = Animation(set, itemclass + "_broken")
    except:
      self.animations["broken"] = self.animations["default"]

    self.image = self.animations[self.current_animation].update_and_get_image()
    self.rect = self.image.get_rect()
    self.itemclass = itemclass
    self.activated_times = 0
    self.max_activations = max_activations
    self.trigger = None
    if trigger_type != None:
      self.trigger = Trigger(trigger_type, x, y)
    else:
      self.pickable = True
    return

  def activate(self):
    if self.itemclass == "lever":
      self.activated_times += 1
      if (self.activated_times <= self.max_activations) or (self.max_activations == -1):
        if (self.activated_times == self.max_activations):
          self.current_animation = "broken"
        self.trigger.x = self.x
        self.trigger.y = self.y
        return self.trigger

    return None

  def to_str(self, verbose = True):
    string = VisibleObject.to_str(self, False)
    if self.trigger != None:
      string += " " + str(self.max_activations) + " " + self.trigger.trigger_type
    if verbose:
      log_message("Obj converted to string: " + string)
    return string