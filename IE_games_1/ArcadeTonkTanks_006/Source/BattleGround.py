# BattleGround 
#
# Arcade Tonk Tanks 0.0.6
#
# Module created on 2009-11-05 by Koen Lefever. License: GPL v.3
###################################################################

import pygame
from pygame.locals import *
import cPickle as pickle

#####################################################################
class BattleGround():
    """Battle Ground: background, buildings, scenery..."""
    def __init__(self, name, background, walls_list, water_list, respawn_list, draw_walls = False, draw_water = False):
        self.name=name                      # name as displayed in the options screen
        self.background=background          # file with background picture
        self.walls=walls_list               # a list of Rect() objects
        self.water=water_list               # a list of Rect() objects
        self.respawnpoints=respawn_list     
        self.draw_walls = draw_walls        # put to false if the walls are already painted in the background picture
        self.draw_water = draw_water        # put to false if the water is already painted in the background picture
