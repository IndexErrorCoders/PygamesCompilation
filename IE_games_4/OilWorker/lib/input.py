# -*- coding: utf-8 -*-

#===================================================
# 
# input.py - a simple library to bind standard input into user defined actions to be 
# used in pygame applications
#
# Copyright (C) 2008  Wil Alvarez <wil_alejandro@yahoo.com>
#
# This library is free software; you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation; either version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# this library (see COPYING); if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#===================================================

import pygame, pygame.locals

MOUSE_MOTION 		= 0xFF20
MOUSE_BUTTON1 		= 0xFF21
MOUSE_BUTTON2 		= 0xFF22
MOUSE_BUTTON3 		= 0xFF23

JOY_BUTTON0			= 0xFF30
JOY_BUTTON1			= 0xFF31
JOY_BUTTON2			= 0xFF32
JOY_BUTTON3			= 0xFF33
JOY_BUTTON4			= 0xFF34
JOY_BUTTON5			= 0xFF35
JOY_BUTTON6			= 0xFF36
JOY_BUTTON7			= 0xFF37
JOY_BUTTON8			= 0xFF38
JOY_BUTTON9			= 0xFF39

JOY_AXIS_0_LEFT		= 0xFF3A
JOY_AXIS_0_RIGHT		= 0xFF3B
JOY_AXIS_1_UP			= 0xFF3C
JOY_AXIS_1_DOWN		= 0xFF3D
#JOY_AXIS_2_UP		= 0xFF3E
#JOY_AXIS_2_DOWN	= 0xFF3F
JOY_AXIS_3_LEFT		= 0xFF40
JOY_AXIS_3_RIGHT		= 0xFF41
JOY_AXIS_4_UP			= 0xFF42
JOY_AXIS_4_DOWN		= 0xFF43
JOY_AXIS_5_LEFT		= 0xFF44
JOY_AXIS_5_RIGHT		= 0xFF45
JOY_AXIS_6_UP			= 0xFF46
JOY_AXIS_6_DOWN		= 0xFF47

JOY_SENSITIVITY		= 0.05
JOY_OFFSET			= (0.0038, 0.0039)

class Input:
	def __init__(self, parseall=False, sensitivity=JOY_SENSITIVITY):
		self.parseall=parseall		# Do nothing so far
		self.actions=[]
		self.bindings={}
		self.axis={}
		self.holds={}
		JOY_SENSITIVITY=sensitivity	# Do nothing so far too
		
		for i in range(pygame.joystick.get_count()):
			joy=pygame.joystick.Joystick(i)
			joy.init()
			print 'axis', joy.get_numaxes()
			print 'axispos', joy.get_axis(0)
			
	def __absAxisValue(self, value):
		'''if abs(value) <= JOY_SENSITIVITY: return 0
		elif value < 0: return -1
		else: return 1
		'''
		if value > JOY_OFFSET[1]: return 1
		elif value < JOY_OFFSET[0]: return -1
		else: return 0
			
	def bindKey(self, action, key, hold=True):
		self.bindings[key]=action
		self.holds[action]=hold
	
	def bindMouseButton(self, action, key, hold=False):
		self.bindings[key]=action
		self.holds[action]=hold
		
	def bindJoyButton(self, action, key, hold=True):
		self.bindings[key]=action
		self.holds[action]=hold
		
	def bindJoyAxis(self, action, joy_axis, hold=True):
		self.bindings[joy_axis]=action
		self.holds[action]=hold
		
	def clear(self):
		self.actions.clear()
	
	def lookup(self, action):
		if action in self.actions:
			if not self.holds[action]: self.actions.remove(action)
			return True
		return False
		
	def handleInput(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key in self.bindings: 
					self.actions.append(self.bindings[event.key])
			
			if event.type == pygame.KEYUP:
				if event.key in self.bindings: 
					if self.bindings[event.key] in self.actions: 
						self.actions.remove(self.bindings[event.key])
						
			if (event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.MOUSEBUTTONUP):
				button=None
				if (event.button==1) and (MOUSE_BUTTON1 in self.bindings): button=self.bindings[MOUSE_BUTTON1]
				if (event.button==2) and (MOUSE_BUTTON2 in self.bindings): button=self.bindings[MOUSE_BUTTON2]
				if (event.button==3) and (MOUSE_BUTTON3 in self.bindings): button=self.bindings[MOUSE_BUTTON3]
				
				if (button != None) and (event.type == pygame.MOUSEBUTTONDOWN): self.actions.append(button)
				if (button in self.actions) and (event.type == pygame.MOUSEBUTTONUP): self.actions.remove(button)
			
			if (event.type == pygame.MOUSEMOTION):
				if (MOUSE_MOTION in self.bindings): self.actions.append(self.bindings[MOUSE_MOTION])
			
			if (event.type==pygame.JOYBUTTONDOWN) or (event.type==pygame.JOYBUTTONUP):
				button=None
				if (event.button==0) and (JOY_BUTTON0 in self.bindings): button=self.bindings[JOY_BUTTON0]
				if (event.button==1) and (JOY_BUTTON1 in self.bindings): button=self.bindings[JOY_BUTTON1]
				if (event.button==2) and (JOY_BUTTON2 in self.bindings): button=self.bindings[JOY_BUTTON2]
				if (event.button==3) and (JOY_BUTTON3 in self.bindings): button=self.bindings[JOY_BUTTON3]
				if (event.button==4) and (JOY_BUTTON4 in self.bindings): button=self.bindings[JOY_BUTTON4]
				if (event.button==5) and (JOY_BUTTON5 in self.bindings): button=self.bindings[JOY_BUTTON5]
				if (event.button==6) and (JOY_BUTTON6 in self.bindings): button=self.bindings[JOY_BUTTON6]
				if (event.button==7) and (JOY_BUTTON7 in self.bindings): button=self.bindings[JOY_BUTTON7]
				if (event.button==8) and (JOY_BUTTON8 in self.bindings): button=self.bindings[JOY_BUTTON8]
				if (event.button==9) and (JOY_BUTTON9 in self.bindings): button=self.bindings[JOY_BUTTON9]
				
				if (button != None) and (event.type==pygame.JOYBUTTONDOWN): self.actions.append(button)
				if (button in self.actions) and (event.type==pygame.JOYBUTTONUP): self.actions.remove(button)
			
			if event.type==pygame.JOYAXISMOTION:
				if event.axis==2: continue
				axisvalue=self.__absAxisValue(event.value)
				
				# Axis 0
				if (event.axis==0) and (axisvalue == -1) and (JOY_AXIS_0_LEFT in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_0_LEFT])
				elif (event.axis==0) and (axisvalue == 1) and (JOY_AXIS_0_RIGHT in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_0_RIGHT])
				elif (event.axis==0) and (axisvalue == 0):
					if JOY_AXIS_0_LEFT in self.bindings: 
						if self.bindings[JOY_AXIS_0_LEFT] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_0_LEFT])
					if JOY_AXIS_0_RIGHT in self.bindings: 
						if self.bindings[JOY_AXIS_0_RIGHT] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_0_RIGHT])
				
				# Axis 1
				if (event.axis==1) and (axisvalue == -1) and (JOY_AXIS_1_UP in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_1_UP])
				elif (event.axis==1) and (axisvalue == 1) and (JOY_AXIS_1_DOWN in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_1_DOWN])
				elif (event.axis==1) and (axisvalue == 0):
					if JOY_AXIS_1_UP in self.bindings: 
						if self.bindings[JOY_AXIS_1_UP] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_1_UP])
					if JOY_AXIS_1_DOWN in self.bindings: 
						if self.bindings[JOY_AXIS_1_DOWN] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_1_DOWN])
				
				# Axis 3
				if (event.axis==3) and (axisvalue == -1) and (JOY_AXIS_3_LEFT in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_3_LEFT])
				elif (event.axis==3) and (axisvalue == 1) and (JOY_AXIS_3_RIGHT in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_3_RIGHT])
				elif (event.axis==3) and (axisvalue == 0):
					if JOY_AXIS_3_LEFT in self.bindings: 
						if self.bindings[JOY_AXIS_3_LEFT] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_3_LEFT])
					if JOY_AXIS_3_RIGHT in self.bindings: 
						if self.bindings[JOY_AXIS_3_RIGHT] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_3_RIGHT])
						
				# Axis 4
				if (event.axis==4) and (axisvalue == -1) and (JOY_AXIS_4_UP in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_4_UP])
				elif (event.axis==4) and (axisvalue == 1) and (JOY_AXIS_4_DOWN in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_4_DOWN])
				elif (event.axis==4) and (axisvalue == 0):
					if JOY_AXIS_4_UP in self.bindings:
						if self.bindings[JOY_AXIS_4_UP] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_4_UP])
					if JOY_AXIS_4_DOWN in self.bindings: 
						if self.bindings[JOY_AXIS_4_DOWN] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_4_DOWN])
				
				# Axis 5
				if (event.axis==5) and (axisvalue == -1) and (JOY_AXIS_5_LEFT in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_5_LEFT])
				elif (event.axis==5) and (axisvalue == 1) and (JOY_AXIS_5_RIGHT in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_5_RIGHT])
				elif (event.axis==5) and (axisvalue == 0):
					if JOY_AXIS_5_LEFT in self.bindings: 
						if self.bindings[JOY_AXIS_5_LEFT] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_5_LEFT])
					if JOY_AXIS_5_RIGHT in self.bindings: 
						if self.bindings[JOY_AXIS_5_RIGHT] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_5_RIGHT])
				
				# Axis 6
				if (event.axis==6) and (axisvalue == -1) and (JOY_AXIS_6_UP in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_6_UP])
				elif (event.axis==6) and (axisvalue == 1) and (JOY_AXIS_6_DOWN in self.bindings): 
					self.actions.append(self.bindings[JOY_AXIS_6_DOWN])
				elif (event.axis==6) and (axisvalue == 0):
					if JOY_AXIS_6_UP in self.bindings: 
						if self.bindings[JOY_AXIS_6_UP] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_6_UP])
					if JOY_AXIS_6_DOWN in self.bindings: 
						if self.bindings[JOY_AXIS_6_DOWN] in self.actions: self.actions.remove(self.bindings[JOY_AXIS_6_DOWN])
			
		
		pygame.event.pump()
