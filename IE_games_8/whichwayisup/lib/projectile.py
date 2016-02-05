'''A straight-flying projectile capable of damaging the player.'''

import pygame
import os

from pygame.locals import *

from locals import *

import data

from object import DynamicObject
from sound import play_sound
from animation import Animation

class Projectile(DynamicObject):

  def __init__(self, screen, x, y, dx, dy, damage = 5, set = "energy"):
    DynamicObject.__init__(self, screen, x, y, -1, False, False)
    self.animations["default"] = Animation(set, "flying")
    self.animations["dying"] = Animation(set, "dying")
    self.image = self.animations[self.current_animation].update_and_get_image()
    self.rect = self.image.get_rect()
    self.dx = dx
    self.dy = dy
    self.saveddx =  None
    self.damage = damage
    self.itemclass = "projectile"
    return

  def update(self, level = None):
    DynamicObject.update(self, level)

    if self.dx == 0 and self.dy == 0 and self.saveddx != None: #Restores values saved on flipping
      self.dx = self.saveddx
      self.dy = self.saveddy
      self.saveddx = None

    if level.ground_check(self.x - 1, self.y - 1) or level.ground_check(self.x + 1, self.y + 1): #Simplified collision detection
      self.die()
      self.dx = 0
      self.dy = 0
    return

  def flip(self, flip_direction = CLOCKWISE):
    if flip_direction == CLOCKWISE:
      self.saveddx = -self.dy
      self.saveddy = self.dx
    else:
      self.saveddx = self.dy
      self.saveddy = -self.dx
    DynamicObject.flip(self, flip_direction)
    return