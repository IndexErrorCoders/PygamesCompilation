'''The main game module. One big event loop in the run function plus a few helper functions.'''

import pygame
from pygame.locals import *
import os
import random

from locals import *

from player import Player
from spider import Spider
from particle import Particle
from level import Level
from sound import play_sound
from edit_utils import Edit_utils
from util import *
from variables import Variables
from log import error_message
from trigger import Trigger
from visibleobject import flip_direction_from_position

import data

keys_released = {}

def render_edit_utilities(screen):
  return

#This function renders the in-game GUI on the screen.
def render_gui(screen, life, score, topleft):
  score_image = render_text("Score: " + str(score) )
  life_image = render_text("Life:")
  #life_bar_bg_image = Util.cached_images["health_bar_empty"]
  #life_bar_image = Util.cached_images["health_bar_fill"]
  version_image = render_text("0.7.9")

  rect = score_image.get_rect()
  rect.left = topleft[0]
  rect.top = topleft[1]
  screen.blit(score_image, rect)

  rect.left = topleft[0] + 26
  rect.top = topleft[1] + 26
  rect.width = 38
  rect.height = 8
  pygame.draw.rect(screen, COLOR_GUI_BG, rect)
  if life > 0:
    rect.left = topleft[0] + 27
    rect.top = topleft[1] + 27
    rect.width = life
    rect.height = 6
    pygame.draw.rect(screen, COLOR_BLOOD, rect)

  rect = life_image.get_rect()
  rect.left = topleft[0]
  rect.top = topleft[1] + 20
  screen.blit(life_image, rect)

  rect = version_image.get_rect()
  rect.right = SCREEN_WIDTH - 2
  rect.bottom = SCREEN_HEIGHT - 2
  screen.blit(version_image, rect)
  return

#This function parses inputs from the keyboard and returns them as an array
def parse_inputs(joystick = None):
  keys = pygame.key.get_pressed()
  inputs = {}

  if keys[K_LEFT]:
    inputs["LEFT"] = True
    if keys_released["K_LEFT"]:
      inputs["EDIT_LEFT"] = True
    keys_released["K_LEFT"] = False
  else:
    keys_released["K_LEFT"] = True

  if keys[K_RIGHT]:
    inputs["RIGHT"] = True
    if keys_released["K_RIGHT"]:
      inputs["EDIT_RIGHT"] = True
    keys_released["K_RIGHT"] = False
  else:
    keys_released["K_RIGHT"] = True

  if keys[K_DOWN]:
    if keys_released["K_DOWN"]:
      inputs["DOWN"] = True
      inputs["EDIT_DOWN"] = True
    keys_released["K_DOWN"] = False
  else:
    keys_released["K_DOWN"] = True

  if keys[K_z]:
    inputs["UP"] = True
    if keys_released["K_z"]:
      inputs["JUMP"] = True
    keys_released["K_z"] = False
  else:
    keys_released["K_z"] = True

  if keys[K_p]:
    if keys_released["K_p"]:
      inputs["PAUSE"] = True
    keys_released["K_p"] = False
  else:
    keys_released["K_p"] = True

  if keys[K_w]:
    inputs["ADD_TILE_WALL"] = True

  if keys[K_s]:
    if keys_released["K_s"]:
      inputs["ADD_TILE_SPIKES"] = True
      if (keys[K_RCTRL] or keys[K_LCTRL]):
        inputs["SAVE_TILES"] = True
        del inputs["ADD_TILE_SPIKES"]
    keys_released["K_s"] = False
  else:
    keys_released["K_s"] = True

  if keys[K_b]:
    inputs["ADD_TILE_BARS"] = True

  if keys[K_d]:
    inputs["REMOVE_TILE"] = True


  if keys[K_UP]:
    inputs["UP"] = True
    if keys_released["K_UP"]:
      inputs["JUMP"] = True
      inputs["EDIT_UP"] = True
    keys_released["K_UP"] = False
  else:
    keys_released["K_UP"] = True

  if keys[K_F10]:
    inputs["SPECIAL"] = True

  if joystick != None:   # Parse joystick input

    axis0 = joystick.get_axis(0)

    if axis0 < -0.1:
      inputs["LEFT"] = True
      inputs["ANALOG"] = -axis0

    if axis0 > 0.1:
      inputs["RIGHT"] = True
      inputs["ANALOG"] = axis0

    if joystick.get_numbuttons() > 1:
      if joystick.get_button(0):
        inputs["UP"] = True
        if keys_released["J_B0"]:
          inputs["JUMP"] = True
        keys_released["J_B0"] = False
      else:
        keys_released["J_B0"] = True

      if joystick.get_button(1):
        if keys_released["J_B1"]:
          inputs["DOWN"] = True
        keys_released["J_B1"] = False
      else:
        keys_released["J_B1"] = True
    else:
      axis1 = joystick.get_axis(1)

      if axis1 < -0.1:
        inputs["UP"] = True
        if keys_released["J_A1U"]:
          inputs["JUMP"] = True
        keys_released["J_A1U"] = False
      else:
        keys_released["J_A1U"] = True

      if axis1 > 0.1:
        if keys_released["J_A1D"]:
          inputs["DOWN"] = True
        keys_released["J_A1D"] = False
      else:
        keys_released["J_A1D"] = True

  return inputs


def run(screen, level_name = "w0-l0", score_mod = 0, score = None, joystick = None):

  if (Variables.vdict["devmode"]):
    edit_utils = Edit_utils()

  done = False
  objects = []
  particles = []

  if score == None:
    score = Score(0)

  #try:
  level = Level(screen, level_name)
  #except:
  #  error_message("Couldn't open level '" + level_name + "'")
  #  return END_QUIT

  objects = level.get_objects()
  player = level.get_player()
  objects.append(player)

  player.life = score.life

  clock = pygame.time.Clock()

  end_trigger = END_NONE
  scripted_event_on = False

  #There's no music at the moment:
  #pygame.mixer.music.load( data.filepath(os.path.join("music", "music.ogg")) )
  #pygame.mixer.music.play(-1)

  scripted_events = level.get_scripted_events()
  current_scripted_event = None

  scripted_event_trigger = TRIGGER_LEVEL_BEGIN

  flip_wait = -1

  keys_released["K_z"] = True
  keys_released["K_p"] = True
  keys_released["K_s"] = True
  keys_released["K_DOWN"] = True
  keys_released["K_LEFT"] = True
  keys_released["K_RIGHT"] = True
  keys_released["K_UP"] = True
  keys_released["J_B0"] = True
  keys_released["J_B1"] = True

  fading = True
  fade_target = FADE_STATE_NONE
  Util.fade_state = FADE_STATE_BLACK

  flip_trigger_position = (0, 0)

  changing_level = False

  paused = False

  #Main game loop

  while (end_trigger == END_NONE or fading):

    # Pygame event and keyboard input processing
    for event in pygame.event.get():
      if event.type == QUIT:
        end_trigger = END_HARD_QUIT
      if (event.type == KEYDOWN and event.key == K_ESCAPE):
        end_trigger = END_QUIT
        if fading == False:
          fading = True
        fade_target = FADE_STATE_HALF

    inputs = parse_inputs(joystick)

    trigger = None

    if scripted_event_on:
      if inputs.has_key("JUMP") or inputs.has_key("DOWN"):
        cleared = True

    moved = False

    add_time = False #The ingame time counter toggle - this is False when the player can't control the character

    if not scripted_event_on and not level.flipping and not fading and not paused \
    and player.current_animation != "dying" and player.current_animation != "exit":
      #There isn't anything special going on: player can control the character
      #Translates input to commands to the player object
      add_time = True
      if inputs.has_key("LEFT"):
        player.move((-PLAYER_MAX_ACC, 0))
        moved = True

      if inputs.has_key("RIGHT"):
        player.move((PLAYER_MAX_ACC, 0))
        moved = True

      if inputs.has_key("JUMP"):
        if (player.on_ground):
          count = 0
          while (count < 5):
            count += 1
            particles.append(Particle(screen, 10, player.rect.centerx - player.dx / 4 + random.uniform(-3, 3), player.rect.bottom, -player.dx * 0.1, -0.5, 0.3, level.dust_color, 4))
          player.jump()

          #The blobs always try to jump when the player jumps

          for o in objects:
            if o.itemclass == "blob":
              o.jump()

      if inputs.has_key("UP") and not player.on_ground:
        player.jump()

      if inputs.has_key("DOWN"):
        pick_up_item = level.pick_up(player.x, player.y)
        if pick_up_item != None:
          play_sound("coins")
          player.inventory.append(pick_up_item)
          scripted_event_trigger = pick_up_item.itemclass

        #If the level is not flipping at the moment, the player can trigger stuff in the level
        if flip_wait == -1:
          trigger = level.trigger(player.x, player.y)

      #Debug command for flipping:
      if inputs.has_key("SPECIAL"):
        trigger = Trigger(TRIGGER_FLIP, player.x, player.y)

    if inputs.has_key("PAUSE") and player.current_animation != "dying":
      paused = not paused

    #Decelerates the player, if he doesn't press any movement keys or when he is dead and on the ground
    if ((player.current_animation != "dying" and not moved) or (player.current_animation == "dying" and player.on_ground)) and not paused:
      player.dec((PLAYER_MAX_ACC, 0))

    if trigger != None and trigger.trigger_type == TRIGGER_FLIP:
      if flip_wait == -1:
        flip_wait = 0
        flip_trigger_position = (trigger.x, trigger.y)
        play_sound("woosh")

    if flip_wait != -1 and not paused:
      flip_wait += 1
      if flip_wait > FLIP_DELAY:
        flip_direction = flip_direction_from_position(flip_trigger_position)
        flip_wait = -1
        level.flip(flip_direction)
        for o in objects:
          o.flip(flip_direction)
        for p in particles:
          p.flip()

    #Dust effect rising from the character's feet:

    if (player.current_animation == "walking"):
      particles.append(Particle(screen, 10, player.rect.centerx - player.dx / 2 + random.uniform(-2, 2), player.rect.bottom, -player.dx * 0.1, 0.1, 0.3, level.dust_color))

    #Updating level and objects:

    if scripted_event_trigger == None:
      scripted_event_trigger = level.update()
    else:
      level.update()

    #Objects are only updated when there's not a scripted event going on

    normal_updating = not scripted_event_on and not fading and not paused

    if changing_level:
      player.update(level)
    elif normal_updating:
      for o in objects:
        if o.dead and o.itemclass != "player":
          objects.remove(o)
          continue
        new_particles = o.update(level)
        if o.itemclass == "projectile":
          if player.rect.collidepoint(o.x, o.y) and o.current_animation == "default":
            new_particles = player.take_damage(o.damage)
            o.die()
        if type(new_particles) == list: #Sometimes the type of the return value is int (hackity hack)
          if new_particles != None:
            for p in new_particles:
              particles.append(p)

    if normal_updating or changing_level:
      for p in particles:
        p.update()
        if p.dead:
          particles.remove(p)

    #Rendering level - background and tiles
    level.render()

    #Rendering objects and particles
    for o in objects:
      if o.itemclass == "player":
        o.render(None, None, (fading or paused) )
      else:
        o.render(None, None, (scripted_event_on or fading or paused) )
      #On special conditions the animations aren't updated. The player is updated on a scripted event, others are not.

    for p in particles:
      p.render()

    #Rendering GUI on top of game graphics:
    if (not paused) or (not Variables.vdict["devmode"]):
      render_gui(screen, player.life, score.score, (5, 5))

    # Scripted event triggering:

    if scripted_event_trigger != None:
      if player.on_ground:
        for ev in scripted_events:
          if ev.trigger_type == scripted_event_trigger:
            scripted_event_on = True
            current_scripted_event = ev
            current_scripted_event_element = None
            text = None
            phase = 0
            cleared = False        # Clearing dialog boxes
            player.dy = 0
            player.dx = 0
            player.update()
            scripted_event_trigger = None

    # Scripted event processing:

    if scripted_event_on and not fading and not paused:
      if (current_scripted_event_element == None) or (current_scripted_event_element.finished):

        current_scripted_event_element = current_scripted_event.next_element()

        if current_scripted_event_element.event_type == "end":
          scripted_event_on = False
          current_scripted_event_element = None

      else:

        if not Variables.vdict["dialogue"]:  #Dialogue skipping
          while (current_scripted_event_element.event_type == "dialogue" or current_scripted_event_element.event_type == "player"):
            current_scripted_event_element.finished = True
            current_scripted_event_element = current_scripted_event.next_element()
            if current_scripted_event_element.event_type == "end":
              current_scripted_event_element.finished = True

        if current_scripted_event_element.event_type == "wait":
          current_scripted_event_element.finished = True
        elif current_scripted_event_element.event_type == "dialogue":
          if text == None:
            text = current_scripted_event_element.text
            phase = 0
          phase = render_text_dialogue(screen, text, phase)
          if (phase == -1) and cleared:
            current_scripted_event_element.finished = True
            phase = 0
            cleared = False
            text = None
          if cleared:
            phase = -1
            cleared = False
        elif current_scripted_event_element.event_type == "player":
          if current_scripted_event_element.text == "orientation":
            player.orientation = current_scripted_event_element.orientation
          current_scripted_event_element.finished = True
        elif current_scripted_event_element.event_type == "change_level":
          score.score += (5 + score_mod) * ((player.life + 4) / 5 + 12)
          score.levels += 1
          current_scripted_event_element.finished = True
          if player.current_animation != "gone":
            player.exit()

    if player.current_animation == "exit":
      changing_level = True
    elif changing_level:
      end_trigger = END_NEXT_LEVEL
      fading = True
      fade_target = FADE_STATE_BLACK


    if player.dead:
      end_trigger = END_LOSE
      fading = True
      fade_target = FADE_STATE_HALF

    #And finally, rendering the pause button:

    if paused:
      if (Variables.vdict["devmode"]):
        change = edit_utils.update(inputs)
        level.change(change)
        edit_utils.render(screen)
      else:
        render_text_dialogue(screen, "Game paused. Press P to continue.", -1, "p")

    #Render fading on top of everything else:

    if (fading or Util.fade_state != FADE_STATE_NONE):
      if fade_to_black(screen, fade_target):
        #Fading finished
        fading = False

    if(add_time):
      score.time += 1

    #Display, clock

    pygame.display.flip()

    clock.tick(FPS)

  #Main game loop finished

  score.life = player.life #To make the player's health stay the same to the next level

  return end_trigger
