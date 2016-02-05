# -*- coding: utf-8 -*-
#Wizards Magic
#Copyright (C) 2011-2014  https://code.google.com/p/wizards-magic/
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# Documentation for this class available at the end of this code.
# __author__ = "mtsimoni"
# __date__ = "$25.05.2011 23:17:00$"

try: 
    import pygame
    yes_pygame = True
except ImportError:
    yes_pygame = False
import globals

animations_running = []
cards_attacking = []
cards_dying = []

class Animation():
    def __init__(self, image, origin = [0,0]):
        animations_running.append(self) #Adding to current running animations
        self.image = image.copy() #The source image
        self.origin = origin #The origin
        self.position = [self.origin[0],self.origin[1]]
        self.path = [(0,0)] #The path that must follow the animation
        self.path_trace = 0
        self.style = 'direct' #The style of movement (direct, curve)
        self.speed = 10 #The speed of animation
        self.speedmode = 'lineal' #May be lineal, progressive, random
        self.speedstep = 1 #For progressive speedmode
        self.maxspeed = 10 #For progressive speedmode
        self.mode = ''
        self.distance_x = self.path[0][0] - self.origin[0]
        self.distance_y = self.path[0][1] - self.origin[1]
        self.step_x = self.distance_x*1.0/self.speed
        self.step_y = self.distance_y*1.0/self.speed
        self.additional_groups = []
        self.alpha = 255
        self.fade_step = 5
    def move(self):
        self.mode = 'move'
        
        milestone = self.path_trace
        self.distance_x = self.path[milestone][0] - self.origin[0]
        self.distance_y = self.path[milestone][1] - self.origin[1]
        self.step_x = self.distance_x/self.speed
        self.step_y = self.distance_y/self.speed

        if self.step_x > 0:
            reach_target_x = (self.position[0] >= self.path[milestone][0])
        else:
            reach_target_x = (self.position[0] <= self.path[milestone][0])
        if self.step_y > 0:
            reach_target_y = (self.position[1] >= self.path[milestone][1])
        else:
            reach_target_y = (self.position[1] <= self.path[milestone][1])

        if not reach_target_x: self.position[0] = self.position[0] + self.step_x
        if not reach_target_y: self.position[1] = self.position[1] + self.step_y
        if reach_target_x and reach_target_y:
            if (self.position[0] != self.path[milestone][0]) or (self.position[1] != self.path[milestone][1]):
                self.position= [self.path[milestone][0],self.path[milestone][1]]            
            if milestone == len(self.path)-1:
                animations_running.remove(self)
                for item in self.additional_groups:
                    item.remove(self)
            else:
                self.origin = self.path[milestone]
                self.path_trace = self.path_trace + 1

    def evolution(self, image, origin):
        pass
    def rotation (self):
        pass

    def fade_out(self):
        self.mode = 'fade_out'
        self.alpha -= self.fade_step
        self.image.set_alpha(self.alpha)

        if self.alpha <= 0:
            animations_running.remove(self)
            for item in self.additional_groups:
                item.remove(self)

    def fade_in(self, image, origin):
        pass
    def zoom_in(self, image, origin, destiny, maxsize):
        pass
    def zoom_out(self, image, origin, destiny, minsize):
        pass
    def vibration(self, image, origin, aperture, rebounds, maxspeed):
        pass
    def frameshow(self, frames):
        pass
    def run(self):
        if self.mode == 'move':
            self.move()
        globals.screen.blit(self.image, self.position)


class CustomAnimation(Animation):
    def attacking(self):
        self.step = 40
        self.additional_groups = [globals.cards_attacking]
        globals.cards_attacking.append(self) 
        self.move()
    def dying(self):
        self.additional_groups = [globals.cards_dying]
        globals.cards_dying.append(self)
        self.fade_out()
# Class Animation:
# Implements a class for generics animations of objects.
# Properties:
# image: Required. Specifies the image object to animate.
# origin: Required. Origin point for animation.
# position: This property is used internally for track the position of the object.
# destiny: Optional. Specifies the destiny of the animation (where are you want that image go).
# speed: Optional. Specifies the speed of the animation (try the correct here, this in pixel per frame)
# speedmode: Optional. Specifies if the speed is constant, increases or is randomly selected.
# speedstep: Optional. You can use this only when speedmode = 'progressive' and this specifies the step that speed increases each frame.
# maxspeed: Optional. The maximun speed that the image can reach in progressive mode.
# mode: Used internally by the class for track what are doing the instance.

