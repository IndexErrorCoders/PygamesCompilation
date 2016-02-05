'''A game object class for almost everything - changed from Gameobject to DynamicObject after PyWeek.
Might still need some cleaning up.'''

import pygame
import os
import random

from math import *

from pygame.locals import *

from locals import *

import data

from variables import Variables
from particle import Particle
from visibleobject import VisibleObject, screen_coords_to_tile_coords

from sound import play_sound
from log import log_message

class DynamicObject(VisibleObject):

  #The last parameter "colliding" might be one of the stupidest hacks ever,
  #and has to do with objects moving while not having normal collision detection.
  #(Spider cannons use the parameter).
  #This probably should be reworked some time.
  def __init__(self, screen, x, y, life = -1, gravity = False, colliding = False):
    VisibleObject.__init__(self, screen, x, y)
    self.dx = 0.0
    self.dy = 0.0
    self.initial_x = x
    self.initial_y = y
    self.gravity = gravity
    self.colliding = colliding
    self.active = (self.x + self.rect.width / 2 > 0) and (self.y + self.rect.height / 2 > 0)

    self.on_ground = False

    self.life = life
    self.destructable = True
    if (self.life == -1):
      self.destructable = False

    return

  def acc(self, direction):
    self.dx += direction[0]
    self.dy += direction[1]
    return

  def dec(self, direction):
    if abs(self.dx) < direction[0]:
      self.dx = 0
    else:
      if self.dx > 0:
        self.dx -= direction[0]
      else:
        self.dx += direction[0]

    if abs(self.dy) < direction[1]:
      self.dy = 0
    else:
      if self.dy > 0:
        self.dy -= direction[1]
      else:
        self.dy += direction[1]
    return

  #A big-ass function for handling pretty much everything -
  #flipping, moving, collision detection, taking damage from spikes.
  #returns a list of particles for implementation of blood effects.
  def update(self, level = None):

    VisibleObject.update(self)

    if self.flip_finished and self.itemclass != "player":
      self.active = (self.x + self.rect.width / 2 > 0) and (self.y + self.rect.height / 2 > 0)

    if self.flipping:
      return

    if not self.active:
      return

    if self.gravity:
      self.dy += GRAVITY

    self.x += self.dx
    self.y += self.dy

    if not self.colliding or level == None:
      return

    collision_type = self.check_collisions(level)

    return collision_type

  def flip(self, flip_direction = CLOCKWISE):
    """Make the object flip with the level to either direction"""
    if VisibleObject.flip(self, flip_direction):
      if flip_direction == CLOCKWISE:
        self.initial_x, self.initial_y = -self.initial_y + PLAY_AREA_WIDTH / TILES_HOR * (TILES_HOR*2 - FULL_TILES_HOR), self.initial_x
      else:
        self.initial_x, self.initial_y = self.initial_y, -self.initial_x + PLAY_AREA_WIDTH / TILES_HOR * (TILES_HOR*2 - FULL_TILES_HOR)
    return

  def check_collisions(self, level):
    """Check for collisions and also change the object's position accordingly.
    If there isn't a collision, it returns -1, if there is one, it returns 0,
    And if the collision caused damage, it returns the amount of damage.
    The function also updates the object's self.on_ground variable."""

    collision_type = -1

    self.on_ground = False

    if self.x < 0 + self.rect.width / 2:
      self.x = 0 + self.rect.width  / 2
      self.dx = 0
      collision_type = 0

    if self.x > PLAY_AREA_WIDTH - self.rect.width  / 2:
      self.x = PLAY_AREA_WIDTH - self.rect.width  / 2
      self.dx = 0
      collision_type = 0

    # The commented block is the collision code for the upper edge of the screen.
    # The spiders and projectiles might need this, but they use simplified
    # collision detection for better performance anyway.
    '''if self.y < 0 + self.rect.height / 2:
      self.y = 0 + self.rect.height  / 2
      self.dy = 0'''

    if self.y > PLAY_AREA_HEIGHT - self.rect.height / 2:
      self.y = PLAY_AREA_HEIGHT - self.rect.height  / 2
      self.dy = 0
      self.on_ground = True
      collision_type = 0

    if (level != None):
      self.rect.centerx = int(self.x)
      self.rect.centery = int(self.y)
      if self.itemclass == "player":
        self.rect.top += PLAYER_COLLISION_ADJUST
        self.rect.height -= PLAYER_COLLISION_ADJUST
        level_collision = level.collide(self.rect, self.dy, self.dx, True)
        self.rect.height += PLAYER_COLLISION_ADJUST
        self.rect.top -= PLAYER_COLLISION_ADJUST
      else:
        level_collision = level.collide(self.rect, self.dy, self.dx, True)
      if (level_collision[RIGHT] != None):
        self.x = level_collision[RIGHT] - float(self.rect.width) / 2.0 - 1.0
        self.dx = 0
        collision_type = 0
      if (level_collision[LEFT] != None):
        self.x = level_collision[LEFT] + float(self.rect.width) / 2.0 + 1.0
        self.dx = 0
        collision_type = 0
      if (level_collision[DOWN] != None):
        self.y = level_collision[DOWN] - float(self.rect.height) / 2.0 - 1.0
        self.dy = 0
        self.on_ground = True
        collision_type = 0
      if (level_collision[UP] != None):
        if self.itemclass == "player":
          self.y = level_collision[UP] + float(self.rect.height) / 2.0 + 1.0 - PLAYER_COLLISION_ADJUST
        else:
          self.y = level_collision[UP] + float(self.rect.height) / 2.0 + 1.0
        self.dy = 0
        collision_type = 0

    if (level_collision[DAMAGE] > 0):
      collision_type = level_collision[DAMAGE]

    return collision_type

  def get_orientation(self):
    """Get the direction the object is facing"""
    if (self.dx < 0):
      orientation = LEFT
    if (self.dx > 0):
      orientation = RIGHT
    try:
      return orientation
    except:
      return self.orientation

  def render(self, surface = None, center = None, static_render = False):
    VisibleObject.render(self, surface, center, static_render)
    if Variables.vdict["devmode"] and not self.flipping:
      VisibleObject.render(self, surface, (self.initial_x, self.initial_y), static_render, 100)
    return
    
  def to_str(self, verbose = True):
    string = self.itemclass
    tx, ty = screen_coords_to_tile_coords(self.initial_x, self.initial_y)
    string += " " + str(tx) + " " + str(ty)
    if verbose:
      log_message("Obj converted to string: " + string)
    return string

  def take_damage(self, amount, x = None, y = None):
    """Make the object take the specified amount of damage.
    Returns a list of particles for blood effects"""
    blood = []
    if self.destructable:
      if (x == None):
        x = self.x
        y = self.y
      self.life -= amount
      count = 0
      if self.current_animation != "dying":
        while (count < amount):
          blood.append(Particle(self.screen, 15, x + random.uniform(-3, 3), y + random.uniform(-3, 3), self.dx, self.dy, 0.3, COLOR_BLOOD, 4, True))
          count += 1
      if self.life < 1:
        self.life = 0
        self.die()
    return blood