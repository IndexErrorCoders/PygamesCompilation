import pygame

from pygame.locals import *

from locals import *

from util import render_text
from variables import Variables

from level import Change

class Edit_utils:

  def __init__(self):
    self.cursor = [0, 0]
    return

  def update(self, inputs):
    if inputs.has_key("REMOVE_TILE"):
      return Change("remove", self.cursor)
    if inputs.has_key("ADD_TILE_WALL"):
      return Change("W", self.cursor)
    if inputs.has_key("ADD_TILE_SPIKES"):
      return Change("S", self.cursor)
    if inputs.has_key("ADD_TILE_BARS"):
      return Change("B", self.cursor)
    if inputs.has_key("SAVE_TILES"):
      return Change("save", (0, 0))
    if inputs.has_key("EDIT_RIGHT") and self.cursor[0] < (TILES_HOR - 1):
      self.cursor[0] += 1
    if inputs.has_key("EDIT_LEFT") and self.cursor[0] > 0:
      self.cursor[0] -= 1
    if inputs.has_key("EDIT_DOWN") and self.cursor[1] < (TILES_VER - 1):
      self.cursor[1] += 1
    if inputs.has_key("EDIT_UP") and self.cursor[1] > 0:
      self.cursor[1] -= 1
    return None

  def render(self, screen):
    pygame.draw.rect(screen, COLOR_GUI_EDIT_HILIGHT, pygame.Rect(self.cursor[0]*TILE_DIM, self.cursor[1]*TILE_DIM, TILE_DIM, TILE_DIM), 2)
    return
