'''Blob. Jumps when the player jumps, and damages the player and dies when it hits the player.'''

import pygame
import random

from pygame.locals import *

from locals import *

import data

from object import DynamicObject
from sound import play_sound
from animation import Animation
from particle import Particle

class Blob(DynamicObject):

  def __init__(self, screen, x, y, player):
    DynamicObject.__init__(self, screen, x, y, 10, True, True)
    self.animations["default"] = Animation("blob", "standing")
    self.animations["dying"] = Animation("blob", "dying")
    self.animations["jumping"] = Animation("blob", "jumping")
    self.animations["falling"] = Animation("blob", "falling")
    self.image = self.animations[self.current_animation].update_and_get_image()
    self.rect = self.image.get_rect()
    self.rect.centerx = int(self.x)
    self.rect.centery = int(self.y)
    self.jump_queue = False
    self.itemclass = "blob"
    self.player = player
    return

  def update(self, level = None):
    DynamicObject.update(self, level)

    blood = []

    if not self.active:
      return blood

    if self.on_ground:
      if self.current_animation != "dying":
        self.current_animation = "default"
      if self.jump_queue:
        self.true_jump()
        count = 0
        while (count < 5):
          count += 1
          blood.append(Particle(self.screen, 10, self.rect.centerx + random.uniform(-7, 7), self.rect.bottom, 0.0, -0.5, 0.3, level.dust_color, 4))
    else:
      self.dy = self.dy - BLOB_AIR_JUMP
      if self.dy > 0 and self.current_animation == "jumping":
        self.current_animation = "default"
      if self.dy > 2 and self.current_animation == "default":
        self.current_animation = "falling"
      self.jump_queue = False

    if self.current_animation != "dying" and self.rect.colliderect(self.player.rect):
      self.die()
      blood = self.player.take_damage(BLOB_DAMAGE)

    return blood

  def true_jump(self):
    if self.on_ground and self.current_animation != "dying":
      self.current_animation = "jumping"
      self.jump_queue = False
      self.dy = -BLOB_JUMP_ACC

  def jump(self):
    if self.active:
      self.jump_queue = True
    return
    
