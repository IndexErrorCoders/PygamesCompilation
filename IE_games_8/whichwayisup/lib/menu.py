# A generic, keyboard- or joystick-controlled menu class.
# Draws a list of strings on the screen, and the user can select one of them.
#
# Key configuration is hard-coded:
# Up/down keys or the main vertical axis on the joystick change the selection
# Return, Z, Space or joystick keys 1 or 2 make the selection.
# Esc quits the menu.
#
# To use the module, initialize it with the following parameters:
# screen - standard pygame surface the menu is drawn on
# menu_items - a list of strings in the menu
#
# Optional initialization parameters:
# bgscreen - the menu background covering the entire screen, a pygame surface
# heading_text - a heading for the menu
#
# If the bgscreen isn't specified, the class uses a black screen instead.
#
# After initialization, use the run function. If you want some of the items
# pre-selected, you can supply it with the index of the selection in the
# menu_items list
#
# The run() function returns the index of the selection OR constant MENU_QUIT,
# if the user presses Esc while in the menu.
#
# Menu placement on the screen is controlled by constants in the locals.py.
# The use of the module also requires play_sound from the sound module,
# Util class and render_text from the util module
# and the Variables class from the variables module.

import pygame
import os

from pygame.locals import *

from locals import *

import data

from util import Util, render_text
from variables import Variables

from sound import play_sound

class Menu:

  def __init__(self, screen, menu_items, bgscreen = None, heading_text = None):
    self.bgscreen = bgscreen
    if self.bgscreen == None:
      self.bgscreen = Util.blackscreen
    self.screen = screen
    self.menu_items = menu_items
    self.heading_text = heading_text
    return

  def run(self, menu_choice = 0):
    done = False

    clock = pygame.time.Clock()

    self.screen.blit(self.bgscreen, (0, 0))      #Renders the menu background, usually the faded out game display
                                                 #Or a black screen
    #Menu loop

    while not done:

      # Pygame event and keyboard input processing
      for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
          menu_choice = MENU_QUIT
          done = True
        elif (event.type == KEYDOWN and event.key == K_DOWN) or (event.type == JOYAXISMOTION and event.axis == 1 and event.value > 0.7):
          if menu_choice + 1 < len(self.menu_items):
            menu_choice += 1
            play_sound("click")
        elif (event.type == KEYDOWN and event.key == K_UP) or (event.type == JOYAXISMOTION and event.axis == 1 and event.value < -0.7):
          if menu_choice > 0:
            menu_choice -= 1
            play_sound("click")
        elif (event.type == KEYDOWN and (event.key == K_z or event.key == K_SPACE or event.key == K_RETURN)) or (event.type == JOYBUTTONDOWN and (event.button == 0 or event.button == 1)):
          done = True

      #Menu rendering

      #Menu offset value centers the menu when the maximum amount of choices is not visible

      if len(self.menu_items) < MENU_MAX_VISIBLE:
        menu_offset = -(len(self.menu_items) - 5) * 10
      else:
        menu_offset = -(MENU_MAX_VISIBLE - 5) * 10

      menu_bg = pygame.image.load(data.picpath("menu", "bg")).convert_alpha()
      rect = menu_bg.get_rect()
      rect.centerx = SCREEN_WIDTH / 2
      rect.top = GUI_MENU_TOP
      self.screen.blit(menu_bg, rect)

      if self.heading_text != None:
        menu_head = render_text(self.heading_text)
        rect = menu_head.get_rect()
        rect.centerx = SCREEN_WIDTH / 2
        rect.top = GUI_MENU_TOP + 50 + menu_offset
        self.screen.blit(menu_head, rect)

      #If the menu choice is greater than the second last menu item on screen,
      #the menu must be scrolled:
      if menu_choice > (MENU_MAX_VISIBLE - 1):
        current_menu_index = menu_choice - MENU_MAX_VISIBLE
        if (menu_choice + 1) < len(self.menu_items):
          current_menu_index += 1
      else:
        current_menu_index = 0

      menu_visible = 0

      while (not (menu_visible > MENU_MAX_VISIBLE or (current_menu_index) == len(self.menu_items))):
        m = self.menu_items[current_menu_index]
        if (menu_choice == current_menu_index):
          menu_image = render_text(m, COLOR_GUI_HILIGHT, COLOR_GUI_DARK)
        else:
          menu_image = render_text(m, COLOR_GUI)
        rect = menu_image.get_rect()
        rect.centerx = SCREEN_WIDTH / 2
        rect.top = GUI_MENU_TOP + 60 + (menu_visible + 1) * 20 + menu_offset
        self.screen.blit(menu_image, rect)
        current_menu_index += 1
        menu_visible += 1

      #Display, clock

      pygame.display.flip()

      clock.tick(FPS)

    return menu_choice