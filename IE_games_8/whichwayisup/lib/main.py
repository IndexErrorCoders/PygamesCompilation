'''Game main module.

Contains the entry point used by the run_game.py script.
The actual gameplay code is in game.py.
'''

import pygame
import os
import sys

from pygame.locals import *

from locals import *

import data
import game

from util import Score, parse_config, write_config, write_log, apply_fullscreen_setting
from variables import Variables
from log import error_message
from mainmenu import Mainmenu
from world import World

from sound import play_sound

def main():

    #Parsing level from parameters and parsing main config:

    level_name = None
    world_index = 0
    world = World(WORLDS[world_index])

    user_supplied_level = False

    parse_config()

    getlevel = False
    
    Variables.vdict["devmode"] = False

    if len(sys.argv) > 1:
        for arg in sys.argv:
          if getlevel:
            try:
              level_name = arg
              user_supplied_level = True
              end_trigger = END_NEXT_LEVEL
              menu_choice = MENU_QUIT
            except:
              error_message("Incorrect command line parameters")
              level_name = None
          elif arg == "-l":
            getlevel = True
          elif arg == "-dev":
            Variables.vdict["devmode"] = True
            Variables.vdict["verbose"] = True            
          elif arg == "-v":
            Variables.vdict["verbose"] = True

    #Initializing pygame and screen

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    caption = "Which way is up?"
    if (Variables.vdict["devmode"]):
      caption = caption + " - developer mode"
    pygame.display.set_caption(caption)

    apply_fullscreen_setting(screen)

    if (pygame.joystick.get_count() > 0):
      joystick = pygame.joystick.Joystick(0)
      joystick.init()
    else:
      joystick = None

    score = Score(0)

    done = False

    if not user_supplied_level:
      if (Variables.vdict["unlocked" + WORLDS[0]] == 0): # Nothing unlocked, go straight to the game
        end_trigger = END_NEXT_LEVEL
        menu_choice = MENU_QUIT
        level_name = world.get_level()
      else:                                      # Go to the menu first
        end_trigger = END_MENU
        menu_choice = 0

    bgscreen = None

    #Menu and level changing loop, actual game code is in game.py:

    while not done:
      if end_trigger == END_NEXT_LEVEL:
        if user_supplied_level:
          end_trigger = game.run(screen, level_name, world.index, score, joystick)
          if end_trigger == END_NEXT_LEVEL:
            user_supplied_level = False
            end_trigger = END_WIN
        else:
          end_trigger = game.run(screen, level_name, world.index, score, joystick)
          if end_trigger == END_NEXT_LEVEL:
            if world.is_next_level():
              level_name = world.get_level()
            else:
              end_trigger = END_WIN
          elif end_trigger == END_QUIT:
            display_bg("quit", screen)
            end_trigger = END_MENU
            bgscreen = screen.copy()
      if end_trigger == END_LOSE:
        display_bg("lose", screen)
        end_trigger = END_MENU
        menu_choice = world.index - 1
        bgscreen = screen.copy()
      elif end_trigger == END_WIN:
        display_bg("victory", screen)
        end_trigger = END_MENU
        menu_choice = 0
        bgscreen = screen.copy()
      elif end_trigger == END_QUIT or end_trigger == END_HARD_QUIT:
        done = True
      elif end_trigger == END_MENU:
        prev_score = score.score
        prev_time = score.time
        prev_levels = score.levels
        score = Score(0)
        if prev_score != 0:
          menu = Mainmenu(screen, prev_score, world, bgscreen, prev_time, prev_levels)
        else:
          menu = Mainmenu(screen, None, world, bgscreen)
        menu_choice = menu.run(menu_choice)
        if menu_choice == MENU_QUIT:
          end_trigger = END_QUIT
        elif menu_choice == MENU_SOUND:
          Variables.vdict["sound"] = not Variables.vdict["sound"]
          end_trigger = END_MENU
        elif menu_choice == MENU_DIALOGUE:
          Variables.vdict["dialogue"] = not Variables.vdict["dialogue"]
          end_trigger = END_MENU
        elif menu_choice == MENU_FULLSCREEN:
          Variables.vdict["fullscreen"] = not Variables.vdict["fullscreen"]
          end_trigger = END_MENU
          apply_fullscreen_setting(screen)
        elif menu_choice == MENU_WORLD:
          world_index += 1
          if world_index >= len(WORLDS):
            world_index = 0
          world = World(WORLDS[world_index])
          end_trigger = END_MENU
        else:
          level_name = world.get_level(menu_choice)
          end_trigger = END_NEXT_LEVEL

    write_config()
    write_log()

    return

def display_bg(key, screen):
  bg_image = pygame.image.load(data.picpath("bg", key))
  rect = bg_image.get_rect()
  screen.blit(bg_image, rect)
  return

if __name__ == "__main__":
  main()
