'''One of the enemies, the spider, which climbs along walls and shoots at the player.'''

import pygame

from pygame.locals import *

from locals import *

import data

from object import DynamicObject
from sound import play_sound
from animation import Animation
from projectile import Projectile

from util import cycle_clockwise, cycle_counter_clockwise, get_direction, str_from_dir
from sound import play_sound
from log import log_message

class Spider(DynamicObject):

  def __init__(self, screen, x = None, y = None, attached = RIGHT):
    DynamicObject.__init__(self, screen, x, y, 10, False, False)
    self.animations["default"] = Animation("spider", "standing")
    self.animations["walking"] = Animation("spider", "walking")
    self.image = self.animations[self.current_animation].update_and_get_image()
    self.rect = self.image.get_rect()
    self.itemclass = "spider"

    self.attached = attached
    self.move_target = STAY
    self.fire_delay = 0

    return

  def get_orientation(self):
    return self.attached

  def update(self, level = None):
    DynamicObject.update(self, level)

    if self.x < 0 or self.y < 0 or self.flipping:
      return

    if self.attached == RIGHT or self.attached == LEFT:
      self.top_collide_point = (self.rect.centerx, self.rect.top + SPIDER_TOO_WIDE - 2)
      self.bottom_collide_point = (self.rect.centerx, self.rect.bottom - SPIDER_TOO_WIDE + 2)
      if self.attached == RIGHT:
        self.top_leg_attach_point = (self.rect.right + 2, self.rect.top + SPIDER_TOO_WIDE)
        self.bottom_leg_attach_point = (self.rect.right + 2, self.rect.bottom - SPIDER_TOO_WIDE)
      else:
        self.top_leg_attach_point = (self.rect.left - 2, self.rect.top + SPIDER_TOO_WIDE)
        self.bottom_leg_attach_point = (self.rect.left - 2, self.rect.bottom - SPIDER_TOO_WIDE)
    else:
      self.top_collide_point = (self.rect.left + SPIDER_TOO_WIDE - 2, self.rect.centery)
      self.bottom_collide_point = (self.rect.right - SPIDER_TOO_WIDE + 2, self.rect.centery)
      if self.attached == DOWN:
        self.top_leg_attach_point = (self.rect.left + SPIDER_TOO_WIDE, self.rect.bottom + 2)
        self.bottom_leg_attach_point = (self.rect.right - SPIDER_TOO_WIDE, self.rect.bottom + 2)
      else:
        self.top_leg_attach_point = (self.rect.left + SPIDER_TOO_WIDE, self.rect.top - 2)
        self.bottom_leg_attach_point = (self.rect.right - SPIDER_TOO_WIDE, self.rect.top - 2)

    fire = True

    self.move_target = STAY
    if self.attached == RIGHT or self.attached == LEFT:
      if level.player.rect.top > (self.y - 2):
        fire = False
        if not level.ground_check(self.bottom_collide_point[0], self.bottom_collide_point[1]):
          self.move_target = DOWN
      if level.player.rect.bottom < (self.y + 2):
        fire = False
        if not level.ground_check(self.top_collide_point[0], self.top_collide_point[1]):
          self.move_target = UP
    else:
      if level.player.rect.left > (self.x - 2):
        fire = False
        if not level.ground_check(self.bottom_collide_point[0], self.bottom_collide_point[1]):
          self.move_target = RIGHT
      if level.player.rect.right < (self.x + 2):
        fire = False
        if not level.ground_check(self.top_collide_point[0], self.top_collide_point[1]):
          self.move_target = LEFT

    if not self.gravity:
      if self.fire_delay > 0:
        self.fire_delay -= 1
      self.dy = 0
      self.dx = 0
      if self.move_target == UP:
        if (level.ground_check(self.top_leg_attach_point[0], self.top_leg_attach_point[1] - 1)):
          self.dy = -1
      elif self.move_target == DOWN:
        if (level.ground_check(self.bottom_leg_attach_point[0], self.bottom_leg_attach_point[1] + 1)):
          self.dy = 1
      elif self.move_target == LEFT:
        if (level.ground_check(self.top_leg_attach_point[0] - 1, self.top_leg_attach_point[1])):
          self.dx = -1
      elif self.move_target == RIGHT:
        if (level.ground_check(self.bottom_leg_attach_point[0] + 1, self.bottom_leg_attach_point[1])):
          self.dx = 1
      elif fire and not level.player.dead:
        if (self.attached == RIGHT) and (level.player.x > self.x + 20):
          fire = False
        if (self.attached == LEFT) and (level.player.x < self.x - 20):
          fire = False
        if (self.attached == UP) and (level.player.y < self.y - 20):
          fire = False
        if (self.attached == DOWN) and (level.player.y > self.y + 20):
          fire = False
        if fire:
          self.fire(level)

    if self.animations[self.current_animation].finished and self.current_animation != "dying":
      self.animations[self.current_animation].reset()
      self.current_animation = "default"
    if self.dx != 0 or self.dy != 0 and self.current_animation == "default":
      self.current_animation = "walking"
    if self.dx == 0 and self.dy == 0 and self.current_animation == "walking":
      self.current_animation = "default"

    return

  def flip(self, flip_direction = CLOCKWISE):
    if flip_direction == CLOCKWISE:
      self.attached = cycle_clockwise(self.attached)
    else:
      self.attached = cycle_counter_clockwise(self.attached)
    DynamicObject.flip(self, flip_direction)
    return

  def fire(self, level):
    if self.fire_delay == 0:
      play_sound("fire")
      self.fire_delay = SPIDER_FIRE_DELAY
      fire_direction = get_direction(self.attached)
      level.objects.append(Projectile(self.screen, self.x, self.y, fire_direction[0]*-SPIDER_PROJECTILE_SPEED, fire_direction[1]*-SPIDER_PROJECTILE_SPEED, SPIDER_DAMAGE, "energy"))
    return
    
  def to_str(self, verbose = True):
    string = DynamicObject.to_str(self, False)
    try:
      string += " " + str_from_dir(self.attached)
    except:
      pass
    if verbose:
      log_message("Obj converted to string: " + string)
    return string