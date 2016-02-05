#! /usr/bin/python
# -*- coding: utf-8 -*-
#===================================================
# 
# Oil Worker - An addictive and challenging arcade puzzle game developed in 
# PyGame. You've been contracted by an oil company and your goal is to build a 
# long pipe to carry the oil from the oil well to the refinery
#
# Copyright (C) 2008  Wil Alvarez <wil_alejandro@yahoo.com>
#
# This game is free software; you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation; either version 3 of the License, or (at your option) any later version.
#
# This game is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# this library (see COPYING); if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#===================================================
import sys
sys.path.append('lib')
import pygame, os, random, util, input, objects, levelparser
from pygame.locals import *

# KEY BINDINGS (Defined by user)
UP 		= 0x11
DOWN 	= 0x12
LEFT 	= 0x13
RIGHT 	= 0x14
ENTER	= 0x15
TURBO 	= 0x16
PAUSE 	= 0x17
BGMUSIC  = 0x18
EXIT 	= 0xFF

#MOUSE BINDINGS
MOTION 	= 0x20
BUTTON1	= 0x21

class HowtoScreen:
	def __init__(self, screen):
		self.screen=screen
		self.clock = pygame.time.Clock()
		self.fps=60
		self.quit=False
		
		self.input=input.Input()
		self.input.bindKey(ENTER, pygame.K_RETURN, False)
		self.input.bindKey(ENTER, pygame.K_ESCAPE, False)
		
		fontsize=11
		fontcolor=(0xff,0xff,0xff)
		self.text=[util.loadText('You have been contracted by Pixoil, an Oil Company. They need you', fontsize, fontcolor, 'vera'),
		util.loadText('build oil pipelines to transport oil from oil wells to their refineries.', fontsize, fontcolor, 'vera'),
		util.loadText('', fontsize, fontcolor, 'vera'),
		util.loadText('You must use at least the minimum number of pipes demanded by', fontsize, fontcolor, 'vera'),
		util.loadText('the company, otherwise you will lose the contract. If the oil is', fontsize, fontcolor, 'vera'),
		util.loadText('spilled you will lose the contract too.', fontsize, fontcolor, 'vera'),
		util.loadText('', fontsize, fontcolor, 'vera'),
		util.loadText('For each pipe installed successfully you will earn a money bonus', fontsize, fontcolor, 'vera'),
		util.loadText('and if oil is transported successfully to the refinery you will receive', fontsize, fontcolor, 'vera'),
		util.loadText('the payment.', fontsize, fontcolor, 'vera'),
		util.loadText('', fontsize, fontcolor, 'vera'),
		util.loadText('Use the MOUSE to place the cursor at any part of the map and LEFT', fontsize, fontcolor, 'vera'),
		util.loadText('CLICK to build the first pipe in the pipes queue. Use SPACEBAR to', fontsize, fontcolor, 'vera'),
		util.loadText('accelerate the oil flow. In the main screen press F11 to turn on/off', fontsize, fontcolor, 'vera'),
		util.loadText('the background music', fontsize, fontcolor, 'vera'),
		util.loadText('', fontsize, fontcolor, 'vera'),
		util.loadText('GOOD LUCK!', fontsize, fontcolor, 'vera'),]
		
		back=util.loadText("Press 'ENTER/ESCAPE' to return menu", 10, fontcolor, 'vera')
		
		image = pygame.Surface((416, 340))
		image.fill((0x43,0x43,0x43))
		pygame.draw.rect(image, (0x0,0x0,0x0), (0,0,416,340), 1)
		image.set_alpha(128, pygame.locals.RLEACCEL)
		
		while not self.quit:
			self.clock.tick(self.fps)
			self.__gameInput()
			offset=100
			
			self.screen.blit(image, (40,80))
			for i in range(len(self.text)):
				self.screen.blit(self.text[i], (60, offset+i*16))
			
			cx, cy = back.get_size()
			self.screen.blit(back, ((512-cx)/2, 384))
			
			pygame.display.flip()
			
	def __gameInput(self):
		self.input.handleInput()
		
		if self.input.lookup(ENTER):
			self.quit=True
			return
			
class HighScoreScreen:
	def __init__(self, screen, highscore):
		self.screen=screen
		self.highscore=highscore
		self.clock = pygame.time.Clock()
		self.fps=60
		self.quit=False
		
		self.input=input.Input()
		self.input.bindKey(ENTER, pygame.K_RETURN, False)
		#self.input.bindKey(ENTER, pygame.K_ESCAPE, False)
		
		fontsize=14
		fontcolor=(0xff,0xff,0xff)
		
		title=util.loadText('Best Workers', 20, fontcolor, 'vera')
		text=[]
		for i in range(len(self.highscore.topscore)):
			name=util.loadText(str(self.highscore.topscore[i][0]), fontsize, fontcolor, 'vera')
			money=util.loadText('$'+str(self.highscore.topscore[i][1]), fontsize, fontcolor, 'vera')
			text.append((name, money))
		
		back=util.loadText("Press 'ENTER' to return menu", 10, fontcolor, 'vera')
		
		image = pygame.Surface((300, 300))
		image.fill((0x43,0x43,0x43))
		pygame.draw.rect(image, (0x0,0x0,0x0), (0,0,300,300), 1)
		
		while not self.quit:
			self.clock.tick(self.fps)
			self.__gameInput()
			offset=50
			
			cx, cy = title.get_size()
			image.blit(title, ((image.get_width()-cx)/2, 16))
			for i in range(len(text)):
				image.blit(text[i][0], (50, offset+i*20))
				cx, cy = text[i][1].get_size()
				image.blit(text[i][1], (150+((150-cx)/2), offset+i*20))
			
			cx, cy = back.get_size()
			image.blit(back, ((image.get_width()-cx)/2, 270))
			
			self.screen.blit(image, ((self.screen.get_width()-image.get_width())/2, 100))
			pygame.display.flip()
			
	def __gameInput(self):
		self.input.handleInput()
		
		if self.input.lookup(ENTER):
			self.quit=True
			return
			
class AskNameScreen:
	def __init__(self, screen):
		self.screen=screen
		self.clock = pygame.time.Clock()
		self.fps=60
		self.blink_delay = self.fps/2
		self.show=True
		self.quit=False
		
		white=(0xff,0xff,0xff)
		black=(0x0,0x0,0x0)
		bg=(0x9a,0x89,0x2b) #(0x43,0x43,0x43)
		
		title=util.loadText('Enter your name:', 20, white, 'vera')
		footer=util.loadText('and press \'ENTER\'', 11, white, 'vera')
		
		self.name=''
		image = pygame.Surface((200, 110))
		
		while not self.quit:
			self.clock.tick(self.fps)
			
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN: 
						self.quit=True
					elif (32 <= event.key < 127) or (256 <= event.key < 266):
						self.name += event.unicode
					elif (event.key == K_BACKSPACE):
						self.name=self.name[:-1]
					
					if (len(self.name)>15): self.name=self.name[:15]
			
			image.fill(bg)
			pygame.draw.rect(image, black, (0,0,200,110), 1)
			
			image.blit(title, (10, 16))
			cx, cy = footer.get_size()
			image.blit(footer, ((image.get_width()-cx)/2, 90))
			
			pygame.draw.rect(image, white, (10,52,180,25), 0)
			pygame.draw.rect(image, black, (10,52,180,25), 1)
			
			name=util.loadText(self.name, 16, black, 'vera')
			cx, cy = name.get_size()
			image.blit(name, (11, 54))
			
			self.blink_delay -= 1
			if (self.blink_delay == 0): 
				self.show=not self.show
				self.blink_delay = self.fps/2
			
			if self.show:
				cx, cy = name.get_size()
				pygame.draw.line(image, black, (cx+11, 56), (cx+11, 71), 1)
				
			self.screen.blit(image, ((self.screen.get_width()-image.get_width())/2, (self.screen.get_height()-image.get_height())/2))				
			pygame.display.flip()
			
class EndScreen:
	def __init__(self, screen):
		self.screen=screen
		self.clock = pygame.time.Clock()
		self.fps=60
		self.quit=False
		
		self.input=input.Input()
		self.input.bindKey(ENTER, pygame.K_RETURN, False)
		self.input.bindKey(ENTER, pygame.K_ESCAPE, False)
		
		fontsize=11
		fontcolor=(0xff,0xff,0xff)
		
		self.title=util.loadText('CONGRATULATIONS!', 24, fontcolor, 'vera')
		self.text=[
		util.loadText('Well done!  You have done a great job. Now, you are prepared to ', fontsize, fontcolor, 'vera'),
		util.loadText('conquer the world of the Oil Industries.', fontsize, fontcolor, 'vera'),
		util.loadText('', fontsize, fontcolor, 'vera'),
		util.loadText('Next step will be to found your oil company and try to rule the', fontsize, fontcolor, 'vera'),
		util.loadText('oil bussiness, the world and the whole universe! (In', fontsize, fontcolor, 'vera'),
		util.loadText('', fontsize, fontcolor, 'vera'),
		util.loadText('', fontsize, fontcolor, 'vera'),
		util.loadText('Design, graphics and development by:', fontsize, fontcolor, 'vera'),
		util.loadText('Wil A. Alvarez', fontsize, fontcolor, 'vera'),
		util.loadText('<wil_alejandro@yahoo.com>', fontsize, fontcolor, 'vera'),
		util.loadText('', fontsize, fontcolor, 'vera'),
		util.loadText('THANKS FOR PLAYING!', 18, fontcolor, 'vera'),
		]
		back=util.loadText("Press 'ENTER/ESCAPE' to exit", 10, fontcolor, 'vera')
		
		image = pygame.Surface((416, 340))
		image.fill((0x43,0x43,0x43))
		pygame.draw.rect(image, (0x0,0x0,0x0), (0,0,416,340), 1)
		#image.set_alpha(128, pygame.locals.RLEACCEL)
		
		while not self.quit:
			self.clock.tick(self.fps)
			self.__gameInput()
			offset=150
			
			self.screen.blit(image, (40,80))
			cx, cy = self.title.get_size()
			self.screen.blit(self.title, ((512-cx)/2, 100))
			for i in range(len(self.text)):
				cx, cy = self.text[i].get_size()
				self.screen.blit(self.text[i], ((512-cx)/2, offset+i*16))
			
			cx, cy = back.get_size()
			self.screen.blit(back, ((512-cx)/2, 384))
			
			pygame.display.flip()
			
	def __gameInput(self):
		self.input.handleInput()
		
		if self.input.lookup(ENTER):
			self.quit=True
			return

class ContractScreen:
	def __init__(self, screen, level, pipes, terrain, pumping,pay):
		self.screen=screen
		self.clock = pygame.time.Clock()
		self.fps=60
		self.accept=False
		quit=False
		
		self.input=input.Input()
		self.input.bindKey(ENTER, pygame.K_RETURN, False)
		self.input.bindKey(EXIT, pygame.K_ESCAPE, False)
		
		fontsize=11
		fontcolor=(0x0,0x0,0x0)
		
		if (terrain==0): type='Plain'
		elif (terrain==1): type='Rocky'
		elif (terrain==2): type='Wooded'
		elif (terrain==3): type='Mixed'
			
		if (300 < pumping <= 448): pump='Slow'
		elif (150 < pumping <= 300): pump='Medium'
		else: pump='Fast'		
		
		back=util.loadText("Press 'ENTER' to Accept, 'ESCAPE' to Quit", 10, (0x0,0x0,0x0), 'vera')
		contracttxt=util.loadText("Contract  "+str(level), 20, (0x0,0x0,0x0), 'vera')
		mintxt=util.loadText("Minimun Pipes: "+str(pipes), 10, (0x0,0x0,0x0), 'vera')
		terraintxt=util.loadText("Terrain: "+type, 10, (0x0,0x0,0x0), 'vera')
		temptxt=util.loadText("Pumping: "+pump, 10, (0x0,0x0,0x0), 'vera')
		paytxt=util.loadText("Payment: $"+str(pay), 20, (0x0,0x0,0x0), 'vera')
		leveltxt=util.loadText("A", 20, (0xff,0xff,0xff), 'vera')
		
		image=util.loadPng('contract.png')
		
		bgmPlayer('play', 'bgm-contract.ogg')
		
		while not quit:
			self.clock.tick(self.fps)
			quit=self.__gameInput()
			
			xoffset=95
			yoffset=32
			self.screen.fill((0xa7,0xa7,0xa7))
			self.screen.blit(image, (95,32))
			
			self.screen.blit(contracttxt, (23+xoffset,95+yoffset))
			self.screen.blit(mintxt, (42+xoffset,275+yoffset))
			self.screen.blit(terraintxt, (42+xoffset,295+yoffset))
			self.screen.blit(temptxt, (42+xoffset,315+yoffset))
			self.screen.blit(paytxt, (42+xoffset,340+yoffset))
			self.screen.blit(leveltxt, (290+xoffset,40+yoffset))
			cx, cy = back.get_size()
			self.screen.blit(back, ((512-cx)/2, 420))
			
			pygame.display.flip()
			
		bgmPlayer('stop')
			
	def __gameInput(self):
		self.input.handleInput()
		
		if self.input.lookup(EXIT):
			self.accept=False
			return True
		elif self.input.lookup(ENTER):
			self.accept=True
			return True
			
		return False
	

class MainScreen:
	def __init__(self, screen):
		self.screen=screen
		self.clock = pygame.time.Clock()
		self.fps=60
		self.menu=0
		self.askname=False
		
		self.lvl=levelparser.LevelParser()
		
		self.input=input.Input()
		self.input.bindKey(EXIT, pygame.K_ESCAPE)
		self.input.bindKey(UP, pygame.K_UP, False)
		self.input.bindKey(DOWN, pygame.K_DOWN, False)
		self.input.bindKey(LEFT, pygame.K_LEFT, False)
		self.input.bindKey(RIGHT, pygame.K_RIGHT, False)
		self.input.bindKey(ENTER, pygame.K_RETURN, False)
		self.input.bindKey(BGMUSIC, pygame.K_F11, False)
		
		menucolor=(0xff,0xff, 0xff)
		hgcolor=(0xff,0xf6,0x0)
		self.start=util.loadText('New Game', 16, menucolor, 'modernab')
		self.hlstart=util.loadText('New Game', 16, hgcolor, 'modernab')
		self.cont=util.loadText('Continue   <-  1  ->', 16, menucolor, 'modernab')
		self.hlcont=util.loadText('Continue   <-  1  ->', 16, hgcolor, 'modernab')
		self.howto=util.loadText('How to play', 16, menucolor, 'modernab')
		self.hlhowto=util.loadText('How to play', 16, hgcolor, 'modernab')
		self.high=util.loadText('High Scores', 16, menucolor, 'modernab')
		self.hlhigh=util.loadText('High Scores', 16, hgcolor, 'modernab')
		self.quit=util.loadText('Quit', 16, menucolor, 'modernab')
		self.hlquit=util.loadText('Quit', 16, hgcolor , 'modernab')
		
		self.bg = util.loadPng('mainscreen.png')
		self.menuicon = util.loadPng('menuicon.png')
		self.copyright=util.loadText('Created by Wil Alvarez (C) Copyright 2008', 10, (0xA,0xA,0xA), 'vera')
		
		self.highscore=objects.HighScore(top=100000, nonames=False)
		
		self.__reset()
		
		while True:
			self.clock.tick(self.fps)
			self.__gameInput()
		
			self.screen.blit(self.bg, (0, 0))
			cx, cy = self.copyright.get_size()
			self.screen.blit(self.copyright, ((512-cx)/2, 140))
			self.__updateMenu()
			
			pygame.display.flip()
	
	def __updateMenu(self):
		xicon=30
		xtxt=50
		self.screen.blit(self.start, (xtxt, 230))
		self.screen.blit(self.cont, (xtxt, 260))
		self.screen.blit(self.high, (xtxt, 290))
		self.screen.blit(self.howto, (xtxt, 320))
		self.screen.blit(self.quit, (xtxt, 350))
		
		if (self.menu==0): 
			self.screen.blit(self.menuicon, (xicon, 226))
			self.screen.blit(self.hlstart, (xtxt, 230))
		elif (self.menu==1): 
			self.screen.blit(self.menuicon, (xicon, 256))
			self.screen.blit(self.hlcont, (xtxt, 260))
		elif (self.menu==2): 
			self.screen.blit(self.menuicon, (xicon, 286))
			self.screen.blit(self.hlhigh, (xtxt, 290))
		elif (self.menu==3): 
			self.screen.blit(self.menuicon, (xicon, 316))
			self.screen.blit(self.hlhowto, (xtxt, 320))
		elif (self.menu==4): 
			self.screen.blit(self.menuicon, (xicon, 346))
			self.screen.blit(self.hlquit, (xtxt, 350))
			
	def __gameInput(self):
		self.input.handleInput()
		
		menucolor=(0xff,0xff, 0xff)
		hgcolor=(0xff,0xf6,0x0)
		
		if self.input.lookup(UP):
			self.menu -= 1
			if self.menu < 0: self.menu=4
		if self.input.lookup(DOWN):
			self.menu += 1
			if self.menu > 4: self.menu=0
		if self.input.lookup(LEFT):
			if self.menu == 1:
				if (self.level > 1): self.level -= 1
				else: self.level=self.maxlevel
				self.cont=util.loadText('Continue  <-  '+str(self.level)+'  ->', 16, menucolor, 'modernab')
				self.hlcont=util.loadText('Continue  <-  '+str(self.level)+'  ->', 16, hgcolor, 'modernab')
		if self.input.lookup(RIGHT):
			if self.menu == 1:
				if (self.level < self.maxlevel): self.level += 1
				else: self.level=1
				self.cont=util.loadText('Continue  <-  '+str(self.level)+'  ->', 16, menucolor, 'modernab')
				self.hlcont=util.loadText('Continue  <-  '+str(self.level)+'  ->', 16, hgcolor, 'modernab')
		if self.input.lookup(ENTER):
			if(self.menu == 0): 
				self.__run()
			elif(self.menu == 1):  
				self.__run()
			elif(self.menu == 2):  
				HighScoreScreen(self.screen, self.highscore)
				#AskNameScreen(self.screen)
			elif(self.menu == 3):  
				HowtoScreen(self.screen)
			elif(self.menu == 4):  
				exit(0)
		if self.input.lookup(EXIT): 
			exit(0)
		if self.input.lookup(BGMUSIC): 
			if pygame.mixer.music.get_volume() == 0:
				pygame.mixer.music.set_volume(1.0)
			else:
				pygame.mixer.music.set_volume(0.0)
		
		
	def __reset(self):
		bgmPlayer('play', 'main.ogg')
		self.level=1
		self.score=0
		self.maxlevel=self.lvl.readMaxLevel()
		
		self.cont=util.loadText('Continue  <-  '+str(self.level)+'  ->', 16, (0xff,0xff, 0xff), 'modernab')
		self.hlcont=util.loadText('Continue  <-  '+str(self.level)+'  ->', 16, (0xff,0xf6,0x0), 'modernab')
		
	def __run(self):
		while True:
			game=Game(self.screen, self.level, self.score, self.highscore)
			self.level, self.score, quit=game.getStatus()
			#print self.level, self.score, quit
			if (quit==1): 
				self.__reset()
				break
		#pygame.mixer.music.load(os.path.join(sys.path[0],'data','sounds', "intro.ogg"))
		#pygame.mixer.music.play(-1)
		
class Game:
	def __init__(self, screen, level, score, highscore):
		self.screen=screen
		self.__loadingScreen()
		self.level=level
		self.score=score
		self.quit=0
		self.FPS=60
		self.rdy_delay=self.FPS*1.5
		self.win_delay=self.FPS*3
		self.win=None
		self.pause=False
		self.fast=False
		self.clock = pygame.time.Clock()
		self.highscore=highscore
		self.gamingZone=pygame.Rect(0,0,448,448)
		
		self.__loadSfx()
		
		self.PAYMENT=500*self.level
		self.MIN_PIPES= self.__calculateMinPipes()
		self.TERRAIN=0							# Loaded from level
		self.MAX_START_DELAY=1632-(self.level*72)		# (192 - 1632)
		self.MAX_FLOW_VALUE=456-(self.level*18)		# (96 - 456)
		self.MIN_FLOW_VALUE=32
		
		self.limit_flow_value=self.MAX_FLOW_VALUE
		self.num_pipes=self.MIN_PIPES
		self.usedpipes=0
		self.currentpipe=None
		self.alarm=False
		self.pumpframe=0
		self.pumpcount=0
		self.pipetypes=['rightup', 'leftup', 'rightdown', 'leftdown', 'horizontal', 'vertical', 'cross', 'horizontal', 'vertical']
		self.bartiles=[util.loadPng('lateral0.png'), util.loadPng('lateral1.png'),util.loadPng('scorebar.png')]
		self.stack=[]
		
		self.input=input.Input()
		self.input.bindKey(EXIT, pygame.K_ESCAPE)
		self.input.bindKey(TURBO, pygame.K_SPACE)
		self.input.bindKey(PAUSE, pygame.K_RETURN, False)
		self.input.bindKey(MOTION, input.MOUSE_MOTION)
		self.input.bindKey(BUTTON1, input.MOUSE_BUTTON1, False)
		
		
		cursorGroup=pygame.sprite.RenderUpdates()
		pipeGroup=pygame.sprite.RenderUpdates()
		uiGroup=pygame.sprite.RenderUpdates()
		self.messageGroup=pygame.sprite.RenderUpdates()
		
		objects.Cursor.containers=cursorGroup
		objects.Oil.containers=cursorGroup
		objects.StackBar.containers=uiGroup
		objects.ScoreBar.containers=uiGroup
		objects.Pipe.containers=pipeGroup
		objects.Well.containers=pipeGroup
		objects.Refinery.containers=pipeGroup
		objects.Obstacle.containers=pipeGroup
	
		
		self.cursor=objects.Cursor((self.screen.get_width()/2, self.screen.get_height()/2))#(0,0))
		self.stackbar=objects.StackBar((self.screen.get_width()-64,0))
		self.scorebar=objects.ScoreBar((0,self.screen.get_height()-32))
		
		textcolor=(0xff,0xff,0xff) #(0x02,0x4e,0x02)
		self.leveltxt=util.loadText('Level '+str(self.level), 18,textcolor , 'engex')
		self.readytxt=util.loadText('Ready!', 36, textcolor, 'engex')
		self.pausetxt=util.loadText('Pause', 36, textcolor, 'engex')
		
		losearray=[util.loadText('You have failed', 26, textcolor, 'engex'),
		util.loadText('You lost the contract', 26, textcolor, 'engex'),
		util.loadText('You\'re fired!', 26, textcolor, 'engex'), 
		util.loadText('What are you doing?', 26, textcolor, 'engex'),
		util.loadText('Next!', 26, textcolor, 'engex'),
		util.loadText('You\'re a mess!', 26, textcolor, 'engex'),
		]
		
		self.morepipestxt=util.loadText('You needed more pipes', 26, textcolor, 'engex')
		
		winarray=[util.loadText('Good job!', 26, textcolor, 'engex'),
		util.loadText('Mission accomplished!', 26, textcolor, 'engex'),
		util.loadText('You did it!', 26, textcolor, 'engex'),
		util.loadText('Way to go!', 26, textcolor, 'engex'),
		util.loadText('Well done!', 26, textcolor, 'engex'),
		util.loadText('You\'re the boss!', 26, textcolor, 'engex'),
		util.loadText('You rock!', 26, textcolor, 'engex'),
		]
		
		self.losetxt=random.choice(losearray)
		self.wintxt=random.choice(winarray)
		self.dialog = util.loadPng("dialog.png")
		
		for i in range(4): self.__pushStack()
		
		tile = util.loadPng("grounds.png")
		self.bg = pygame.Surface((448, 448))
		
		lvl=levelparser.LevelParser()
		lvl.saveMaxLevel(self.level)
		level=lvl.parseLevel(self.level)
		offset=0
		for i in range(14):
			for j in range(14):
				if(level[i][j]==(0xb8,0x16,0x16,0xff)): 
					self.oil=objects.Oil((j*32,i*32), 'right')
					self.well=objects.Well((j*32,i*32))
					self.bg.blit(tile, (j*32,i*32), (0,0,32,32))
				elif(level[i][j]==(0xff,0xff,0xff,0xff)): 
					self.refinery=objects.Refinery((j*32,i*32))
					self.bg.blit(tile, (j*32,i*32), (32,0,32,32))
				elif(level[i][j]==(0x81,0x81,0x81,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,32]),0,32,32))
					objects.Obstacle((j*32,i*32), 'rock1')
				elif(level[i][j]==(0x60,0x4a,0x20,0xff)):
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,32]),0,32,32))
					objects.Obstacle((j*32,i*32), 'rock2')
				elif(level[i][j]==(0x18,0x67,0x00,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,32]),0,32,32))
					objects.Obstacle((j*32,i*32), 'cactus1')
				elif(level[i][j]==(0x3f,0x9c,0x22,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,32]),0,32,32))
					objects.Obstacle((j*32,i*32), 'cactus2')
				elif(level[i][j]==(0xc6,0xc1,0xb0,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,32]),0,32,32))
					objects.Obstacle((j*32,i*32), 'bones')
				elif(level[i][j]==(0x18,0x85,0x51,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,32]),0,32,32))
					objects.Obstacle((j*32,i*32), 'palmtree')
				elif(level[i][j]==(0x0,0x27,0x08,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,64]),0,32,32))
					objects.Obstacle((j*32,i*32), 'shrub1')
				elif(level[i][j]==(0xcc,0xaf,0x4d,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,64]),offset,32,32))
				elif(level[i][j]==(0xbf,0xa4,0x48,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (random.choice([0,64]),offset,32,32))
				elif(level[i][j]==(0xb2,0x99,0x43,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (96,offset,32,32))
				elif(level[i][j]==(0xa6,0x8e,0x3f,0xff)): 
					self.bg.blit(tile, (j*32,i*32), (128,offset,32,32))
				else: 
					continue
		
		contract=ContractScreen(self.screen, self.level, self.MIN_PIPES, self.TERRAIN, self.MAX_FLOW_VALUE, self.PAYMENT)
		self.quit=not contract.accept
		
		bgm=random.choice(['bgm-1.ogg', 'bgm-2.ogg', 'bgm-3.ogg', 'bgm-4.ogg'])
		bgmPlayer('play', bgm)
		
		while not self.quit:
			self.clock.tick(self.FPS)
			self.screen.blit(self.bg, (0,0))
			
			val=self.__prepareGame(pipeGroup, uiGroup, cursorGroup)
			if val == -1: continue
			elif val == 1: return
			
			self.__gameInput()
			
			if (self.oil.state=='next'):
				list=pygame.sprite.spritecollide(self.oil, objects.Pipe.containers, False)
				if (len(list) > 0):
					self.currentpipe=list[0]
					if self.oil.dir in self.currentpipe.inarray:
						if (self.num_pipes > 0): self.num_pipes -= 1
						self.usedpipes += 1
						self.moneysnd.play()
						self.score += 50
						#self.highscore.appendScore('', self.score)
						self.messageGroup.add(util.Message(self.currentpipe.rect.center, "+50",(0x12,0x3d,0x15), 15)) #(0x02,0x4e,0x02)
						self.currentpipe.startFlow()
						i=self.currentpipe.inarray.index(self.oil.dir)
						self.oil.dir=self.currentpipe.outarray[i]
						self.oil.flowing()
					else:
						self.__spillOil()
				else:
					self.__spillOil()
			elif (self.oil.state=='flowing') and not self.pause:
				#print 'flow',self.oil.flow_value, self.limit_flow_value
				self.oil.flow_value += self.oil.speed
				if (self.currentpipe != None): self.currentpipe.update(self.oil.flow_value, self.limit_flow_value, self.oil.dir)
				if (self.oil.flow_value >= self.limit_flow_value): self.oil.moveNext()
			
			# Check Win (Refinery)
			if (self.oil.rect == self.refinery.rect): 
				if (self.num_pipes == 0): 
					bgmPlayer('stop')
					self.winsnd.play()
					self.win=True
				else: 
					self.losesnd.play()
					self.losetxt=self.morepipestxt
					self.win=False
			
			if not self.pause:
				cursorGroup.update()
				self.messageGroup.update()
				pipeGroup.draw(self.screen)
				cursorGroup.draw(self.screen)
				self.messageGroup.draw(self.screen)
			else:
				cx, cy = self.pausetxt.get_size()
				dx, dy = self.dialog.get_size()
				
				self.screen.blit(self.dialog, ((448-dx)/2, (448-dy)/2))
				self.screen.blit(self.pausetxt, ((448-cx)/2, (416-cy)/2+16))
				
			uiGroup.update(self)
			uiGroup.draw(self.screen)			
			
			pygame.display.flip()
		
	def __gameInput(self):
		self.input.handleInput()
		
		self.fast=False
		if self.input.lookup(MOTION) and not self.pause:
			self.cursor.move(pygame.mouse.get_pos(), self.gamingZone)
		if self.input.lookup(BUTTON1) and not self.pause:
			pos=pygame.mouse.get_pos()
			x=(pos[0]/32)*32
			y=(pos[1]/32)*32
			
			if(x+32 > self.gamingZone.right) or (y+32 > self.gamingZone.bottom): return
			list=pygame.sprite.spritecollide(self.cursor, objects.Pipe.containers, False)
			if(len(list) > 0):
				if list[0].blocked: return
				self.score -= 50
				self.messageGroup.add(util.Message(list[0].rect.center, "-50", (0xff,0x0,0x0), 6))
				list[0].kill()
			self.drillsnd.play()
			type=self.stack.pop()
			objects.Pipe(self.cursor.rect.topleft, type)
			self.__pushStack()
		if self.input.lookup(TURBO) and not self.pause:
			self.fast=True
		if self.input.lookup(PAUSE):
			self.pause=not self.pause
		if self.input.lookup(EXIT) and not self.pause: 
			self.quit=1
			
	def __prepareGame(self, pipeGroup, uiGroup, cursorGroup):
		self.screen.blit(self.bartiles[self.pumpframe], (self.screen.get_width()-64, 0))
		self.screen.blit(self.bartiles[2], (0,self.screen.get_height()-32))
		
		if (self.rdy_delay >= 0):
			self.rdy_delay -= 1			
			cx, cy = self.leveltxt.get_size()
			cx, cy = self.readytxt.get_size()
			dx, dy = self.dialog.get_size()
			
			pipeGroup.draw(self.screen)
			uiGroup.draw(self.screen)
			self.screen.blit(self.dialog, ((448-dx)/2, (448-dy)/2))
			self.screen.blit(self.readytxt, ((448-cx)/2, ((416-cy)/2)+16))
			
			pygame.display.flip()	
			return -1
		elif(self.win==False):
			self.win_delay -= 1
			cx, cy = self.losetxt.get_size()
			dx, dy = self.dialog.get_size()
			
			cursorGroup.update()
			pipeGroup.draw(self.screen)
			cursorGroup.draw(self.screen)
			uiGroup.draw(self.screen)
			self.screen.blit(self.dialog, ((448-dx)/2, (448-dy)/2))
			self.screen.blit(self.losetxt, ((448-cx)/2, (448-cy)/2))
			
			pygame.display.flip()
			if self.win_delay!=0: return -1
			
			if (self.score >= self.highscore.topscore[9][1]):
				ask=AskNameScreen(self.screen)
				self.highscore.appendScore(ask.name, self.score)
			
			self.quit=1
			return 1
		elif(self.win==True):
			self.win_delay -= 1
			cx, cy = self.wintxt.get_size()
			dx, dy = self.dialog.get_size()
			
			cursorGroup.update()
			pipeGroup.draw(self.screen)
			cursorGroup.draw(self.screen)
			uiGroup.draw(self.screen)
			self.screen.blit(self.dialog, ((448-dx)/2, (448-dy)/2))
			self.screen.blit(self.wintxt, ((448-cx)/2, (448-cy)/2))
			
			pygame.display.flip()
			if self.win_delay!=0: return -1
			
			self.score += self.PAYMENT
			self.level += 1
			if(self.level > 20):
				#pygame.mixer.music.load(os.path.join(sys.path[0],'data','sounds', "end.ogg"))
				#pygame.mixer.music.play(-1)
				EndScreen(self.screen)
				self.quit=1
			return 1
		
		if(self.limit_flow_value==self.MIN_FLOW_VALUE) and (not self.fast):
			self.oil.flow_value=(self.MAX_FLOW_VALUE*self.limit_flow_value)/self.MIN_FLOW_VALUE
		
		if self.fast: 
			self.limit_flow_value=self.MIN_FLOW_VALUE
			num=16
		else: 
			self.limit_flow_value=self.MAX_FLOW_VALUE
			num=1
			
		if(self.oil.start_delay < self.MAX_START_DELAY): 
			if (self.pause==False): self.oil.start_delay += num #1
		elif(self.oil.start_delay >= self.MAX_START_DELAY) and (self.oil.state=='standby'): 
			if (self.pause==False): 
				#self.oil.start_delay += 1
				self.oil.moveNext()
		warn=(90*self.MAX_START_DELAY)/100
		if (self.oil.start_delay >= warn) and (self.alarm==False):
			self.warningsnd.play()
			self.alarm=True
		
		if (self.pumpcount % (self.FPS/3)==0):
			if (self.pause==False): self.pumpframe+=1
			if (self.pumpframe > 1): self.pumpframe=0
			self.pumpcount=0
		self.pumpcount+=1
		
		return 0
	
	def __spillOil(self):
		self.losesnd.play()
		self.win=False
		self.oil.spill()
		
	def __pushStack(self):
		x=random.randint(0,6)
		try:
			while True:
				a=self.stack.index(self.pipetypes[x])
				x=random.randint(0,6)
		except:
			pass
		self.stack.insert(0,self.pipetypes[x])
		
	def __calculateMinPipes(self):
		return int((self.level*1.5)+12.5)
		
	def __loadSfx(self):
		self.drillsnd = util.loadSound('drill.ogg')
		self.losesnd = util.loadSound('boo.ogg')
		self.winsnd = util.loadSound('win.ogg')
		self.moneysnd = util.loadSound('money.ogg')
		self.warningsnd = util.loadSound('warning.ogg')
		
	def __loadingScreen(self):
		self.screen.fill((0x0,0x0,0x0))
		text=util.loadText('Loading...', 26, (0xff,0xff,0xff), 'engex')
		cx, cy = text.get_size()
		self.screen.blit(text, ((512-cx)/2,220))
		pygame.display.flip()		
		
	def getTopScore(self):
		return self.highscore.topscore[0][0],self.highscore.topscore[0][1]
		#return 'Satan', 10000
		
	def getStatus(self):
		return self.level, self.score, self.quit
		
def bgmPlayer(action, file=None):
	if action=='play':
		pygame.mixer.music.stop()
		pygame.mixer.music.load(os.path.join('data','sounds', file))
		pygame.mixer.music.play(-1)
	elif action=='stop':
		pygame.mixer.music.stop()

if __name__=="__main__":
	pygame.init()
	random.seed()
	pygame.display.set_caption('Oil Worker')
	os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
	screen=pygame.display.set_mode((512, 480))	
	#main=Game(screen, 1, 0) 
	#pygame.mixer.music.set_volume(0.0)
	main=MainScreen(screen)