"""Player module. The guy with the stylish clothes and lots of
different animations. Moves and jumps, takes damage."""

import pygame
import os

from pygame.locals import *

from locals import *

import data

from object import DynamicObject
from sound import play_sound
from animation import Animation
from log import log_message

class Player(DynamicObject):

  def __init__(self, screen, x = None, y = None):
    DynamicObject.__init__(self, screen, x, y, PLAYER_LIFE, True, True)
    #Changing some of the values from DynamicObject, the animations should probably actually be parsed from a file:
    self.animations["default"] = Animation("guy", "standing")
    self.animations["walking"] = Animation("guy", "walking")
    self.animations["arrow"] = Animation("guy", "arrow")
    self.animations["dying"] = Animation("guy", "dying")
    self.animations["shouting"] = Animation("guy", "shouting")
    self.animations["jumping"] = Animation("guy", "standing")
    self.animations["exit"] = Animation("guy", "exit")
    self.animations["gone"] = Animation("guy", "gone")
    self.image = self.animations[self.current_animation].update_and_get_image()
    self.rect = self.image.get_rect()
    self.itemclass = "player"

    #Variables spesific to this class:
    self.inventory = []
    self.umbrella_on = False
    return

  def move(self, direction):
    if self.current_animation == "dying":
      return
    if not self.on_ground:
      direction = (direction[0] * PLAYER_ACC_AIR_MULTIPLIER, direction[1])

    if direction[0] > 0 and self.dx < PLAYER_MAX_SPEED:
      self.acc(direction)
      if self.dx > PLAYER_MAX_SPEED:
        self.dx = PLAYER_MAX_SPEED
    if direction[0] < 0 and self.dx > -PLAYER_MAX_SPEED:
      self.acc(direction)
      if self.dx < -PLAYER_MAX_SPEED:
        self.dx = -PLAYER_MAX_SPEED
    return

  def update(self, level = None):

    #Automatic animation selection:
    if self.animations[self.current_animation].finished:
      if self.current_animation == "dying":
        pass
      elif self.current_animation == "exit":
        self.current_animation = "gone"
      else:
        #Special animation has finished, falling back to automatic selection
        self.animations[self.current_animation].reset()
        self.current_animation = "default"
    if self.on_ground:
      if self.current_animation == "jumping":
        self.current_animation = "default"
      if self.dx != 0 and self.current_animation == "default":
        self.current_animation = "walking"
      if (self.dx == 0) and self.current_animation == "walking" :
        self.current_animation = "default"
    elif self.current_animation == "default" or self.current_animation == "walking":
      self.current_animation = "jumping"

    collision_type = DynamicObject.update(self, level)

    blood = []

    if collision_type > 0:
      blood = self.take_damage(collision_type)
      if self.current_animation != "dying":
        self.dy -= collision_type*PLAYER_JUMP_ACC / 4.5
    return blood

  def dec(self, direction):
    if not self.on_ground:
      direction = (direction[0] * PLAYER_ACC_AIR_MULTIPLIER, direction[1])
    DynamicObject.dec(self, direction)
    return

  def render(self, surface = None, topleft = None, static_render = False):
    self.rect.centerx = int(self.x)
    self.rect.centery = int(self.y)
    if self.rect.bottom > 0:
      DynamicObject.render(self, surface, topleft, static_render)
    else:
      self.arrowimage = self.animations["arrow"].update_and_get_image()
      self.arrowrect = self.arrowimage.get_rect()
      self.arrowrect.centerx = int(self.x)
      self.arrowrect.top = 5
      self.screen.blit(self.arrowimage, self.arrowrect)
    if self.umbrella_on:
      self.umbrella_on = False # This should be set again before next render by the jump function
    return

  def jump(self):
    if (self.on_ground):
      self.dy = -PLAYER_JUMP_ACC
      play_sound("boing", 0.5)
    else:
      self.dy -= PLAYER_AIR_JUMP
      self.umbrella_on = True
    return

  def flip(self, flip_direction = CLOCKWISE):
    #Position correction - Guy's collision shape isn't an exact square,
    #so this is needed to avoid unwanted collisions after flipping
    self.y += 2
    xmod = 20 - self.x % TILE_DIM
    if abs(xmod) < 6:
      #Guy hasn't crossed over to another (empty) tile, but isn't centered
      #- a chance of a post-flip collision
      self.x += xmod

    DynamicObject.flip(self, flip_direction)
    if self.current_animation == "arrow":
      self.current_animation = "default"
    return

  def take_damage(self, amount, x = None, y = None):
    last_life = self.life
    blood = DynamicObject.take_damage(self, amount, x, y)
    if self.current_animation != "dying":
      self.current_animation = "shouting"
      play_sound("augh")
    elif last_life > 0:
      play_sound("augh")
    return blood
    
  def exit(self):
    self.current_animation = "exit"
    return