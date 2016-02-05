import pygame
import os
import codecs

from pygame.locals import *

from locals import *

import data
from util import dir_from_str

from log import error_message, log_message

from tile import Tile
from spikes import Spikes
from item import Item
from player import Player
from spider import Spider
from blob import Blob
from scripted_event import Scripted_event
from animation import Animation
from trigger import Trigger
from visibleobject import tile_coords_to_screen_coords

class Change:

  def __init__(self, tile_change, coords):
    self.tile_change = tile_change
    self.coords = coords
    return

class Level:

  def __init__(self, screen, level_name = "w0-l0"):
    self.screen = screen
    self.image = None
    self.flipping = False
    self.flipcounter = 0
    self.set = "brown"  #The default tileset, can be changed through level configuration

    self.tiles = []
    self.objects = []

    self.scripted_events = []

    self.cached_ground_check = {}

    self.dust_color = COLOR_DUST["brown"]

    self.level_name = level_name

    self.orientation = 0

    conffile = codecs.open(data.levelpath(self.level_name), "r", "utf_8")

    tiley = 0
    values = []

    trigger = False
    current_event = None

    parse_tiles = False

    for line in conffile:

      if parse_tiles:
        if tiley < FULL_TILES_VER:
          tilex = 0
          while tilex < FULL_TILES_VER:
            if (line[tilex] == "W") or (line[tilex] == "B") or (line[tilex] == "S"):
              self.add_tile(line[tilex], (tilex, tiley))
            tilex += 1
          tiley += 1
          continue
        else:
          parse_tiles = False
          continue

      elif line.strip() != "":
          values = line.split()

          #Parsing special commands

          if trigger:
            if values[0] == "end" and values[1] == "trigger":
              trigger = False
            else:
              current_event.add_element(line)
            continue
          elif values[0] == "trigger":
            trigger = True
            current_event = Scripted_event(values[1], int(values[2]))
            self.scripted_events.append(current_event)
            continue
          elif values[0] == "tiles":
            parse_tiles = True
            continue
          elif values[0] == "set":
            self.set = values[1]
            continue

          #Parsing objects
          x, y = tile_coords_to_screen_coords(values[1], values[2])
          if values[0] == "player":
            self.player = Player(self.screen, x, y)
            continue
          elif values[0] == "spider":
            self.objects.append(Spider( self.screen, x, y, dir_from_str(values[3]) ))
            continue
          elif values[0] == "blob":
            self.objects.append(Blob(self.screen, x, y, self.player))
            continue
          elif values[0] == "lever":
            trigger_type = TRIGGER_FLIP
            if values[4] == "TRIGGER_FLIP":
              trigger_type = TRIGGER_FLIP
            self.objects.append( Item(self.screen, x, y, self.set, values[0], int(values[3]), trigger_type) )
            continue
          else:
            try:
              self.objects.append(Item(self.screen, x, y, self.set, values[0]))
            except:
              error_message("Couldn't add object '" + values[0] + "'")
            continue

    self.dust_color = COLOR_DUST[self.set]

    self.bg_animations = {}
    self.bg_animations["default"] = Animation(self.set + "_background", "static")
    self.current_animation = "default"
    self.rect = (self.bg_animations[self.current_animation].update_and_get_image()).get_rect()
    self.rect.centerx = SCREEN_WIDTH / 2
    self.rect.centery = SCREEN_HEIGHT / 2

    self.reset_active_tiles()
    return

  def update(self):
    return_trigger = None
    if self.flipping:
      self.flipcounter += 1
      if self.flipcounter > FLIP_FRAMES:
        self.flipcounter = 0
        self.flipping = False
        self.reset_active_tiles()
        return_trigger = TRIGGER_FLIPPED
        self.image = None
      for t in self.tiles:
        t.update()
    return return_trigger

  def reset_active_tiles(self):
    self.active_tiles = []
    for t in self.tiles:
      if (t.x > 0 and t.y > 0):
        self.active_tiles.append(t)
    return

  def get_objects(self):
    return self.objects

  def get_player(self):
    return self.player

  def get_scripted_events(self):
    return self.scripted_events

  #Renders the background and the tiles
  def render(self):
    if self.flipping or self.image == None or self.edited:
      self.image = pygame.Surface((self.rect.width, self.rect.height))
      bg = self.bg_animations[self.current_animation].update_and_get_image()
      self.image.blit(bg, self.rect)
      for t in self.tiles:
        t.render(self.image)
      self.edited = False

    #Blits the cached background
    self.screen.blit(self.image, self.rect)
    return

  #Starts the flipping of the level
  def flip(self, flip_direction = CLOCKWISE):
    if self.flipping:
      return
    else:
      self.cached_ground_check = {}
      self.flipping = True
      if (flip_direction == CLOCKWISE):
        self.orientation += 1
      if (flip_direction == COUNTER_CLOCKWISE):
        self.orientation -= 1
      for t in self.tiles:
        t.flip(flip_direction)
      return

  #Triggers an object in the position specified
  def trigger(self, x, y):
    for o in self.objects:
      if o.rect.collidepoint(x, y):
        if o.itemclass == "lever":
          trigg = o.activate()
          if trigg != None:
            return trigg
    return None


  #Gives an object from the level (also removes it from the level)
  def pick_up(self, x, y):
    for o in self.objects:
      if o.rect.collidepoint(x, y):
        if o.pickable:
          self.objects.remove(o)
          return o
    return None


  #Checks the point for solid ground
  def ground_check(self, x, y):
    if self.cached_ground_check.has_key(str(x) + "_" +  str(y)):
      return self.cached_ground_check[str(x) + "_" +  str(y)]
    else:
      if x > SCREEN_WIDTH or y > SCREEN_HEIGHT or x < 0 or y < 0:
        return True
      for t in self.active_tiles:
        if t.rect.collidepoint(x, y):
          self.cached_ground_check[str(x) + "_" +  str(y)] = True
          return True
      self.cached_ground_check[str(x) + "_" +  str(y)] = False
      return False

  #This functions tests (approximately) if a rect collides with another and from which direction.
  #It's one of the most performance-heavy functions in the game, and thus should be optimized.
  #indexing: right left bottom top
  def collide(self, rect, dy, dx, topcollision = True):
    collision = [None, None, None, None, 0]
    for t in self.active_tiles:
      if not t.is_aligned():
        #Sometimes collisions were misdetected just after the level was flipped,
        #so this is an extra check to avoid that.
        #Should look into the order things are done when flipping finishes
        #to fix the problem properly
        continue
      if t.rect.collidepoint(rect.right + 1, rect.centery - dy) and dx > 0:
        collision[RIGHT] = t.rect.left
      if (t.rect.collidepoint(rect.right + 1, rect.bottom - dy - 1) or t.rect.collidepoint(rect.right + 1, rect.top - dy + 1)) and dx > 0:
        collision[RIGHT] = t.rect.left
      if t.rect.collidepoint(rect.left - 1, rect.centery - dy) and dx < 0:
        collision[LEFT] = t.rect.right
      if (t.rect.collidepoint(rect.left - 1, rect.bottom - dy - 1) or t.rect.collidepoint(rect.left - 1, rect.top - dy + 1)) and dx < 0:
        collision[LEFT] = t.rect.right
      if (t.rect.collidepoint(rect.centerx - dx, rect.bottom + 1) or t.rect.collidepoint(rect.right - dx - 1, rect.bottom + 1) or t.rect.collidepoint(rect.left - dx + 1, rect.bottom + 1)) and dy > 0:
        if (t.itemclass == "spikes"):
          if (collision[DOWN] == None):
            collision[DAMAGE] = 5
            collision[DOWN] = t.rect.top
        else:
          collision[DOWN] = t.rect.top
          if collision[DAMAGE] > 0:
            collision[DAMAGE] = 0
      if t.rect.collidepoint(rect.centerx - dx, rect.top - 1) and dy < 0:
        collision[UP] = t.rect.bottom
      if (t.rect.collidepoint(rect.right - dx - 1, rect.top - 1) or t.rect.collidepoint(rect.left - dx + 1, rect.top - 1)) and dy < 0:
        collision[UP] = t.rect.bottom

    return collision


  def change(self, change):
    """Apply a change to the level data according to a Change class object."""
    if change == None:
      return

    log_message("Made change " + change.tile_change + " to coords " + str(change.coords[0]) + ", " + str(change.coords[1]))

    if (change.tile_change == "remove"):
      self.remove_tile(change.coords)

    elif (change.tile_change == "save"):
      self.save()

    elif (change.tile_change == "W") or (change.tile_change == "B") or (change.tile_change == "S"):
      self.remove_tile(change.coords)
      change.coords = (change.coords[0] + FULL_TILES_HOR - TILES_HOR, change.coords[1] + FULL_TILES_VER - TILES_VER)
      self.add_tile(change.tile_change, change.coords)
      self.reset_active_tiles()

    return


  #Uses to_str to convert the level to string form and then saves the level
  #to a file, overwrites the old level file.
  def save(self):
    conffile = codecs.open(data.levelpath(self.level_name), "w", "utf_8")
    string = self.to_str()
    log_message('Level data to save:')
    log_message(string)
    log_message('Saving level to ' + data.levelpath(self.level_name))
    conffile.write(string)
    conffile.close()
    log_message('Level saved.')
    return


  #Converts the level to a string with all the original level data
  def to_str(self):
    string = "set " + self.set + "\n\n"

    string += "tiles" + "\n"

    tilemap = [[] for i in range(FULL_TILES_VER)]
    for row in tilemap:
      for i in range(FULL_TILES_HOR):
        row.append(' ')

    for t in self.tiles:
      tilemap[t.tiley][t.tilex] = t.tileclass[0].upper()

    for row in tilemap:
      for t in row:
        string += t
      string += "\n"
    string += "\n"

    for o in self.objects:
      string += o.to_str(False) + "\n"

    for s in self.scripted_events:
      string += s.to_str() + "\n"
    return string


  def remove_tile(self, coords):
    """Remove a tile from the level with coordinates relative to the corner of the area currently visible."""
    for t in self.active_tiles:
      if t.rect.collidepoint(coords[0]*TILE_DIM + TILE_DIM / 2, coords[1]*TILE_DIM + TILE_DIM / 2):
        self.active_tiles.remove(t)
        self.tiles.remove(t)
        self.edited = True
    return


  def add_tile(self, tile_type, coords):
    """Add a tile to the level with absolute coordinates in the current rotation state."""
    new_tile = None
    if tile_type == "W":
      new_tile = Tile(self.screen, coords[0], coords[1], self.set)
    elif tile_type == "B":
      new_tile = Tile(self.screen, coords[0], coords[1], self.set, "bars")
    elif tile_type == "S":
      new_tile = Spikes(self.screen, coords[0], coords[1], self.set)
    if new_tile != None:
      self.tiles.append(new_tile)
    self.edited = True
    return