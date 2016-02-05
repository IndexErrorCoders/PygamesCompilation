# A more simplified game object class to make special effects with less performance cost

import pygame
import os
import random
from math import *

from pygame.locals import *

from locals import *

import data

class Particle:
  def __init__(self, screen, life = 30, x = None, y = None, dx = None, dy = None, random_move = 0, color = COLOR_DUST, radius = 3, gravity = False):
    self.screen = screen
    self.init_life = life
    self.life = life
    self.dead = False
    self.color = color
    self.init_radius = radius
    self.radius = radius
    self.random_move = random_move
    self.x = x
    self.y = y
    self.dx = dx
    self.dy = dy
    self.radius = radius
    self.gravity = gravity
    if (self.x == None):
      self.x = SCREEN_WIDTH / 2
    if (self.y == None):
      self.y = SCREEN_HEIGHT / 2
    if (self.dx == None):
      self.dx = 0.0
    if (self.dy == None):
      self.dy = 0.0
    return


  def update(self):
    self.radius = (float(self.life) / float(self.init_life)) * self.init_radius
    self.x += self.dx
    self.y += self.dy
    if self.gravity:
      self.dy = self.dy + GRAVITY_PARTICLE
    self.dx += self.random_move * random.uniform(-0.5, 0.5)
    self.dy += self.random_move * random.uniform(-0.5, 0.5)
    self.life -= 1
    if self.life < 0:
      self.dead = True
    return

  def render(self, drawsurface = None):
    pygame.draw.circle(self.screen, self.color, (int(self.x), int(self.y)), int(self.radius))
    return

  def flip(self):
    self.life = -1
    self.dead = True
    return