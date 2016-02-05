import pygame
import os

from pygame.locals import *

from locals import *

import data

from visibleobject import VisibleObject
from animation import Animation

from log import log_message

class Tile(VisibleObject):
  def __init__(self, screen, tilex, tiley, set = "brown", tileclass = "wall"):
    x = (tilex - (FULL_TILES_HOR - TILES_HOR) + 0.5) * TILE_DIM
    y = (tiley - (FULL_TILES_VER - TILES_VER) + 0.5) * TILE_DIM
    VisibleObject.__init__(self, screen, x, y)
    self.animations["default"] = Animation(set, tileclass)
    self.image = self.animations[self.current_animation].update_and_get_image()
    self.rect = self.image.get_rect()
    self.tilex = tilex
    self.tiley = tiley
    self.tileclass = tileclass
    self.aligned = True
    return

  def update(self, level = None):
    VisibleObject.update(self)
    if not self.flipping:
      self.realign()
    return

  def flip(self, flip_direction = CLOCKWISE):
    VisibleObject.flip(self, flip_direction)
    if flip_direction == CLOCKWISE:
      tempx = self.tilex
      self.tilex = FULL_TILES_VER - self.tiley - 1
      self.tiley = tempx
    else:
      tempy = self.tiley
      self.tiley = FULL_TILES_HOR - self.tilex - 1
      self.tilex = tempy


  def realign(self):
    self.rect.centerx = self.x
    self.rect.centery = self.y
    self.x = round((float(self.rect.right)/float(TILE_DIM)), 0)*TILE_DIM - self.rect.width / 2
    self.y = round((float(self.rect.bottom)/float(TILE_DIM)), 0)*TILE_DIM - self.rect.height / 2
    if self.rect.height % 2 == 1:
       self.y -= 1
    if self.rect.width % 2 == 1:
       self.x -= 1
    self.rect.centerx = self.x
    self.rect.centery = self.y
    return

  def is_aligned(self):
    aligned = self.rect.right % TILE_DIM == 0 and self.rect.bottom % TILE_DIM == 0
    if not aligned:
      log_message("tilepos " + str(self.rect.right) + " " + str(self.rect.bottom))
    return aligned