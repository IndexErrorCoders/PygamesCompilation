import pygame
import os

from pygame.locals import *

from locals import *

import data

from util import dir_from_str

from log import log_message

from variables import Variables

class Scripted_event_element:
  def __init__(self, event_type, text = "", orientation = RIGHT, animation = ""):
    self.event_type = event_type
    self.finished = False
    self.text = text
    self.orientation = orientation
    self.animation = animation
    return

  def to_str(self):
    if self.event_type == "dialogue":
      return self.event_type + " " + self.text
    if self.event_type == "player" and self.text == "orientation":
      string = self.event_type + " " + self.text + " "
      if self.orientation == RIGHT:
        string += "RIGHT"
      elif self.orientation == LEFT:
        string += "LEFT"
      elif self.orientation == DOWN:
        string += "DOWN"
      elif self.orientation == UP:
        string += "UP"
      return string
    if self.event_type == "player" and self.text == "animation":
      return self.event_type + " " + self.text + " " + self.animation
    else:
      return self.event_type

class Scripted_event:
  def __init__(self, trigger_type, times = 1):
    self.trigger_type = trigger_type
    self.elements = []
    self.counter = -1
    self.last_dir = RIGHT
    self.repeated = 0
    self.times = times
    return

  def add_element(self, text):
    values  = text.split(" ", 1)
    etype = values[0]
    etype = etype.strip()
    if etype == "dialogue":
      element = Scripted_event_element(etype, values[1].strip())
    else:
      if etype == "player":
        values = values[1].split()
        if values[0] == "orientation":
          self.last_dir = dir_from_str(values[1])
          element = Scripted_event_element(etype, values[0], self.last_dir)
        if values[0] == "animation":
          element = Scripted_event_element(etype, values[0], self.last_dir, values[1])
      else:
        element = Scripted_event_element(etype)
    self.elements.append(element)
    return

  def next_element(self):
    if self.repeated == self.times:
      #The event has repeated enough times
      return Scripted_event_element("end")

    #Returning one element
    self.counter += 1

    if self.counter < len(self.elements):
      return self.elements[self.counter]

    else:
      #Event finished
      self.repeated += 1
      self.counter = -1
      return Scripted_event_element("end")

  def to_str(self):
    string = "\ntrigger " + self.trigger_type + " " + str(self.times) + "\n"
    for el in self.elements:
      string += el.to_str() + "\n"
    string += "end trigger"
    return string