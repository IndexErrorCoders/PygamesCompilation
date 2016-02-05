import pygame
import os

from pygame.locals import *

from locals import *

import data

from util import Util, Score, render_text, bool_to_str
from variables import Variables
from level import Level
from menu import Menu

class Mainmenu:

  def __init__(self, screen, score = None, world = None, bgscreen = None, time = None, levels = None):
    if bgscreen == None:
      self.bgscreen = Util.blackscreen.copy()
    else:
      self.bgscreen = bgscreen.copy()
    self.screen = screen
    self.score = score
    self.time = time
    self.levels = levels
    self.world = world
    return

  def run(self, menu_choice = 0):
    done = False

    #Static menu part

    menu_items = ["Quit", "Sound: " + bool_to_str(Variables.vdict["sound"]), "Dialogue: " + bool_to_str(Variables.vdict["dialogue"]), "Fullscreen mode: " + bool_to_str(Variables.vdict["fullscreen"]), "Choose world: " + str(self.world.number)]

    #Adds levels to the menu

    count = 0

    while (count <= Variables.vdict["unlocked" + self.world.name] and count < self.world.level_count):
      menu_items.append("Play level " + str(count + 1))
      count += 1

    #Hi score and best time text on the bgscreen

    if self.score != None:
      score_text = "Your final score: %s" % str(self.score)
      if self.levels == self.world.level_count:
        time_text = "Your final time: %s frames" % str(self.time)
      else:
        time_text = "Didn't pass all levels"

      if self.score > Variables.vdict["hiscore" + self.world.name]:
        score_text += " - NEW HIGH SCORE!"
        Variables.vdict["hiscore" + self.world.name] = self.score
      else:
        score_text += " - High score: %s" % Variables.vdict["hiscore" + self.world.name]

      if (self.time < Variables.vdict["besttime" + self.world.name] or Variables.vdict["besttime" + self.world.name] == 0) and (self.levels == self.world.level_count):
        time_text += " - NEW BEST TIME!"
        Variables.vdict["besttime" + self.world.name] = self.time
      elif Variables.vdict["besttime" + self.world.name] == 0:
        time_text += " - Best time: no best time"
      else:
        time_text += " - Best time: %s frames" % Variables.vdict["besttime" + self.world.name]
    else:
      score_text = "High score: %s" % Variables.vdict["hiscore" + self.world.name]
      if Variables.vdict["besttime" + self.world.name] == 0:
        time_text = "Best time: no best time"
      else:
        time_text = "Best time: %s frames" % Variables.vdict["besttime" + self.world.name]


    menu_image = render_text("World " + str(self.world.number) + ": " + self.world.name, COLOR_GUI)
    rect = menu_image.get_rect()
    rect.centerx = SCREEN_WIDTH / 2
    rect.top = GUI_MENU_TOP - 75
    self.bgscreen.blit(menu_image, rect)

    menu_image = render_text(score_text, COLOR_GUI)
    rect = menu_image.get_rect()
    rect.centerx = SCREEN_WIDTH / 2
    rect.top = GUI_MENU_TOP - 50
    self.bgscreen.blit(menu_image, rect)

    menu_image = render_text(time_text, COLOR_GUI)
    rect = menu_image.get_rect()
    rect.centerx = SCREEN_WIDTH / 2
    rect.top = GUI_MENU_TOP - 30
    self.bgscreen.blit(menu_image, rect)
    
    #Uses the menu class for the actual selection functionality

    menu = Menu(self.screen, menu_items, self.bgscreen, "Which way is up?")

    menu_choice = menu.run(menu_choice + MENU_OFFSET)

    #Quit (-3) gets special treatment, because it's returned as a constant when the player presses ESC
    #If offset would be applied to it, it would turn up -6

    if not (menu_choice == MENU_QUIT):
      menu_choice = menu_choice - MENU_OFFSET

    return menu_choice
