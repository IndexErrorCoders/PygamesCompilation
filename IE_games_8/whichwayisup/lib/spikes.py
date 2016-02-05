import pygame
import os

from pygame.locals import *

from locals import *

import data

from tile import Tile
from animation import Animation

class Spikes(Tile):
  def __init__(self, screen, tilex, tiley, set = "brown"):
    Tile.__init__(self, screen, tilex, tiley, set, "spikes")
    self.itemclass = "spikes"
    self.realign()
    return
