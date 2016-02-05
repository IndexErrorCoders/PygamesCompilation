'''This class governs all visible, animateable game objects from ground tiles to the player.
The functionality is extended with the DynamicObject class.'''
import pygame
import os
import random

from math import *

from pygame.locals import *

from locals import *

import data

from animation import Animation
from log import log_message

class VisibleObject:

  def __init__(self, screen, x = None, y = None):
    self.screen = screen
    self.animations = {}
    self.animations["default"] = Animation("object", "idle")
    self.current_animation = "default"
    self.image = self.animations[self.current_animation].update_and_get_image()
    self.rect = self.image.get_rect()
    self.x = x
    self.y = y
    if (self.x == None):
      self.x = SCREEN_WIDTH / 2
    if (self.y == None):
      self.y = SCREEN_HEIGHT / 2

    self.flipping = False
    self.flipcounter = 0
    self.flip_init_angle = 0
    self.flip_finished = False
    self.flip_direction = CLOCKWISE #The object will move clockwise

    self.orientation = RIGHT
    self.itemclass = "not_item"

    self.pickable = False

    self.dead = False

    return

  def update(self, level = None):
    self.flip_finished = False

    if self.animations[self.current_animation].finished and self.current_animation == "dying":
      self.dead = True

    if self.flipping:

      if self.flipcounter == 0:
        rela_x = self.x - PLAY_AREA_CENTER_X
        rela_y = self.y - PLAY_AREA_CENTER_Y
        self.rad = sqrt(rela_x**2 + rela_y**2)
        self.flip_init_angle = atan2(rela_y, rela_x)

      self.flipcounter += 1
      self.flip_angle = self.flipcounter * (pi * 0.5 / (FLIP_FRAMES + 1)) * self.flip_direction
      self.angle = self.flip_angle + self.flip_init_angle
      self.x = PLAY_AREA_CENTER_X + cos(self.angle) * self.rad
      self.y = PLAY_AREA_CENTER_Y + sin(self.angle) * self.rad

      if self.flipcounter > FLIP_FRAMES:
        self.flipcounter = 0
        self.flipping = False
        self.dx = 0
        self.dy = 0
        self.flip_finished = True
    return

  def render(self, surface = None, center = None, static_render = False, alpha = 255):
    """Render the object - also flips or rotates it visually according to the orientation."""
    if (not static_render) or (self.image == None):
      self.image = self.animations[self.current_animation].update_and_get_image()
    if center == None:
      self.rect.centerx = int(self.x)
      self.rect.centery = int(self.y)
    else:
      self.rect.centerx = center[0]
      self.rect.centery = center[1]

    self.orientation = self.get_orientation()

    drawsurface = self.screen
    if surface != None:
      drawsurface = surface

    image = self.image

    if self.orientation == LEFT:
      image = pygame.transform.flip(image, True, False)
    elif self.orientation == UP:
      image = pygame.transform.rotate(image, 90)
    elif self.orientation == DOWN:
      image = pygame.transform.rotate(image, -90)

    image.set_alpha(alpha)

    drawsurface.blit(image, self.rect)

    if center != None:
      self.rect.centerx = int(self.x)
      self.rect.centery = int(self.y)
    return

  def get_orientation(self):
    return RIGHT

  def flip(self, flip_direction = CLOCKWISE):
    """Make the object flip with the level to either direction"""
    if not self.flipping:
      self.flipping = True
      self.flip_direction = flip_direction
      return True
    return False

  def die(self):
    """Make the object die - if the object has a death animation, it will be played first."""
    if self.animations.has_key("dying"):
      self.current_animation = "dying"
    else:
      self.dead = True
    return
    
  def to_str(self, verbose = True):
    string = self.itemclass
    tx, ty = screen_coords_to_tile_coords(self.x, self.y)
    string += " " + str(tx) + " " + str(ty)
    if verbose:
      log_message("Obj converted to string: " + string)
    return string

def flip_direction_from_position(flip_trigger_position):
  flip_direction = CLOCKWISE
  if flip_trigger_position[1] > flip_trigger_position[0] and flip_trigger_position[1] > 240:
    flip_direction = COUNTER_CLOCKWISE
  return flip_direction

def tile_coords_to_screen_coords(x, y):
  x = (float(x) - (FULL_TILES_HOR - TILES_HOR)) * TILE_DIM
  y = (float(y) - (FULL_TILES_VER - TILES_VER))* TILE_DIM
  return (x, y)

def screen_coords_to_tile_coords(x, y):
  x = float(x)/float(TILE_DIM) + float(FULL_TILES_HOR - TILES_HOR)
  y = float(y)/float(TILE_DIM) + float(FULL_TILES_VER - TILES_VER)
  return (x, y)