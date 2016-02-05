from variables import Variables

from locals import *

import data

class World:

  def __init__(self, world_name = WORLDS[0]):
    self.index = 0
    self.levels = []
    self.name = world_name
    self.number = 1
    count = 0
    for w in WORLDS:
      count += 1
      if self.name == w:
        self.number = count

    #Parsing config:
    conffile = open(data.levelpath(world_name))
    for line in conffile:
      if line.strip() != "":
        values = line.split()
        if values[0] == "level":
          self.levels.append(values[1])

    self.level_count = len(self.levels)
    return

  def is_next_level(self):
    if self.index < len(self.levels):
      return True
    else:
      return False

  def get_level(self, index = None):
    level = ""

    if index != None:
      self.index = index
    level = self.levels[self.index]

    #Unlocking the next level of this world
    if Variables.vdict["unlocked" + self.name] < self.index:
      Variables.vdict["unlocked" + self.name] = self.index

    self.index += 1

    return level