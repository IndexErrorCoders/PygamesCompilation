#===================================================
# 
# objects.py - objects is a part of OilWorker package. It holds all objects used in game
#
# Copyright (C) 2008  Wil Alvarez <wil_alejandro@yahoo.com>
#
# This module is free software; you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation; either version 3 of the License, or (at your option) any later version.
#
# This module is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License 
# for more details.
#
# You should have received a copy of the GNU General Public License along with 
# this package (see COPYING); if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#===================================================

import pygame, util, os, base64

class StackBar(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = pygame.Surface((64, 448))
		self.image.set_colorkey((0x00,0xff,0x00))
		self.image.fill((0x00,0xff,0x00))
		self.rect=self.image.get_rect()
		self.rect.topleft=pos
		
		self.tpipetile = util.loadPng('pipes.png')
		self.tlateral=util.loadPng('lateral2.png')
		
	def update(self, game):
		# 1st
		x=game.pipetypes.index(game.stack[3])
		self.image.fill((0xff,0x27,0x21), (16, 147,32,32))
		self.image.blit(self.tpipetile, (16,147), (x*32, 0,32,32))
		
		# 2nd
		x=game.pipetypes.index(game.stack[2])
		self.image.fill((0x0,0xff,0x0), (16, 102,32,32))
		self.image.blit(self.tpipetile, (16,102), (x*32, 0,32,32))
		
		# 3th
		x=game.pipetypes.index(game.stack[1])
		self.image.fill((0x0,0xff,0x0), (16, 57,32,32))
		self.image.blit(self.tpipetile, (16,57), (x*32, 0,32,32))
		
		# 4th
		x=game.pipetypes.index(game.stack[0])
		self.image.fill((0x0,0xff,0x0), (16, 12,32,32))
		self.image.blit(self.tpipetile, (16,12), (x*32, 0,32,32))
		
		self.__drawOilFlow(game.oil.start_delay, game.MAX_START_DELAY)
		
	def __drawOilFlow(self, current, max):
		x=(current*110)/max
		pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (14, 413-x , 3, x),0)
		
		
class ScoreBar(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = pygame.Surface((512, 32))
		self.image.set_colorkey((0x00,0xff,0x00))
		self.rect=self.image.get_rect()
		self.rect.topleft=pos
		self.image.fill((0x00,0xff,0x00))
		
		fontcolor=(0xe0,0x79,0x00)
		self.scoretxt=util.loadText('SCORE', 12, fontcolor, 'ltypewriter')
		self.remainstxt=util.loadText('REMAINS', 12, fontcolor, 'ltypewriter')
		self.leveltxt=util.loadText('LEVEL', 12, fontcolor, 'ltypewriter')
		self.paytxt=util.loadText('PAY', 12, fontcolor, 'ltypewriter')
		self.hightxt=util.loadText('HIGHSCORE', 12, fontcolor, 'ltypewriter')
		
	def update(self, game):
		x=10
		xtab=20
		xspacing=-5
		fontsize=11
		ytitle=3
		self.image.fill((0x0,0xff,0x0), (5,5,496,24))
		
		xscore=10
		xremains=100
		xlevel=170
		xpay=230
		xhighs=300
		self.image.blit(self.scoretxt, (xscore, ytitle))
		x = xscore + self.scoretxt.get_size()[0]+xspacing
		text=util.loadText('$'+str(game.score), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		
		self.image.blit(self.remainstxt, (xremains, ytitle))
		x = xremains+ self.remainstxt.get_size()[0]+xspacing
		text=util.loadText(str(game.num_pipes), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		
		self.image.blit(self.leveltxt, (xlevel, ytitle))
		x = xlevel+self.leveltxt.get_size()[0]+xspacing
		text=util.loadText(str(game.level), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		
		self.image.blit(self.paytxt, (xpay, ytitle))
		x = xpay+self.paytxt.get_size()[0]+xspacing
		text=util.loadText('$'+str(game.PAYMENT), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		
		self.image.blit(self.hightxt, (xhighs, ytitle))
		x = xhighs+self.hightxt.get_size()[0]+(xspacing*5)
		name, score=game.getTopScore()
		text=util.loadText(name+': $'+str(score), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		
		'''
		self.image.blit(self.scoretxt, (x, ytitle))
		x += self.scoretxt.get_size()[0]+xspacing
		text=util.loadText('$'+str(game.score), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		x += text.get_size()[0]+xtab
		
		self.image.blit(self.remainstxt, (x, ytitle))
		x += self.remainstxt.get_size()[0]+xspacing
		text=util.loadText(str(game.num_pipes), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		x += text.get_size()[0]+xtab
		
		self.image.blit(self.leveltxt, (x, ytitle))
		x += self.leveltxt.get_size()[0]+xspacing
		text=util.loadText(str(game.level), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		x += text.get_size()[0]+xtab
		
		self.image.blit(self.paytxt, (x, ytitle))
		x += self.paytxt.get_size()[0]+xspacing
		text=util.loadText('$'+str(game.PAYMENT), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		x += text.get_size()[0]+xtab
		
		self.image.blit(self.hightxt, (x, ytitle))
		x += self.hightxt.get_size()[0]+(xspacing*5)
		name, score=game.getTopScore()
		text=util.loadText(name+': $'+str(score), fontsize, (255,255,255), 'vera')
		self.image.blit(text, (x, ytitle+10))
		'''
		text=util.loadText('FPS: ' + str (int (game.clock.get_fps ())), 10, (255,255,255))
		self.image.blit(text, (self.rect.width-50, 10))
		
		
		
class Cursor(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.extinguish=False
		self.pos=pos
		self.move_delay=0
		self.max_move_delay=15
		
		cursor_tile = util.loadPng("cursor.png")
		self.image = pygame.Surface((32, 32))
		self.image.set_colorkey((0x00,0xff,0x00))
		self.image.blit(cursor_tile, (0,0))
		self.rect = self.image.get_rect()
		self.rect.topleft=pos
		
	def move(self, pos, gz):
		x=(pos[0]/32)*32
		y=(pos[1]/32)*32
		
		if(x +32 <= gz.right) and (y +32 <= gz.bottom):
			self.rect.topleft=(x,y)
		
class Oil(pygame.sprite.Sprite):
	def __init__(self, pos, dir):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image = pygame.Surface((32, 32))
		self.image.set_colorkey((0x0,0xff,0x0))
		#self.image.set_alpha(96)
		self.image.fill((0x0,0xff,0x0))
		self.rect = self.image.get_rect()
		self.rect.topleft=pos
		self.dir=dir
		self.state='standby' #stand/next
		self.speed=1
		self.flow_value=0
		self.start_delay=0
	
	def moveNext(self):
		if self.dir=='left': self.rect.left -= 32
		elif self.dir=='right': self.rect.left += 32
		elif self.dir=='up': self.rect.top -= 32
		elif self.dir=='down': self.rect.top += 32
		self.state='next'
		
	def flowing(self):
		self.state='flowing'
		self.flow_value=0
		
	def spill(self):
		tile = util.loadPng("items.png")
		self.image.blit(tile, (0,0), (0,0,32,32))
		
class Pipe(pygame.sprite.Sprite):
	def __init__(self, pos, type):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.blocked=False
		self.flow=False
		self.hp=100
		self.type=type
		
		pipetile = util.loadPng('pipes.png')
		if type=='rightup':
			offset=0
			self.inarray=['right', 'up']
			self.outarray=['down', 'left']
		elif type=='leftup':
			offset=32
			self.inarray=['left', 'up']
			self.outarray=['down', 'right']
		elif type=='rightdown':
			offset=64
			self.inarray=['right','down']
			self.outarray=['up', 'left']
		elif type=='leftdown':
			offset=96
			self.inarray=['left','down']
			self.outarray=['up', 'right']
		elif type=='horizontal':
			offset=128
			self.inarray=['right','left']
			self.outarray=['right', 'left']
		elif type=='vertical':
			offset=160
			self.inarray=['up','down']
			self.outarray=['up','down']
		elif type=='cross':
			offset=192
			self.inarray=['up','down', 'left', 'right']
			self.outarray=['up','down', 'left', 'right']
			
		self.image = pygame.Surface((32, 32))
		self.image.set_colorkey((0x00,0xff,0x00))
		#self.image.fill((0x0,0x0,0xef))
		self.image.blit(pipetile, (0,0), (offset,0,32,32))
		self.rect = self.image.get_rect()
		self.rect.topleft=pos
		
	def damage(self):
		self.hp -= 1
		
	def repair(self):
		self.hp += 1
		
	def startFlow(self):
		self.flow=True
		self.blocked=True
		
	def update(self, flow_value, max_flow_value, dir):
		if not self.flow: return
		
		x=(flow_value*32)/max_flow_value
		if self.type=='horizontal' and dir=='right':
			pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (0, 13 , x, 6),0)
		elif self.type=='horizontal' and dir=='left':
			pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (32-x, 13 , x, 6),0)
		elif self.type=='vertical'and dir=='up':
			pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 32-x , 6, x),0)
		elif self.type=='vertical'and dir=='down':
			pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 0 , 6, x),0)
		elif self.type=='cross' and dir=='right':
			pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (0, 13 , x, 6),0)
		elif self.type=='cross' and dir=='left':
			pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (32-x, 13 , x, 6),0)
		elif self.type=='cross'and dir=='up':
			if (x <= 10): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 32-x , 6, x),0)
			elif (x >= 22): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 32-x, 6, x-22),0)
		elif self.type=='cross'and dir=='down':
			if (x <= 10): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 0 , 6, x),0)
			elif (x >= 22): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 22 , 6, x-22),0)
		elif self.type=='rightdown'and dir=='up':
			if (x <= 12): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (0, 13 , x, 6),0)
			else:
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (0, 13 , 12, 6),0)
			if(x >= 13): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (12,18), 1)
			if(x >= 14): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (13,18), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (14,18), 1)
			if(x >= 15): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (15,18), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (16,17), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (16,18), 1)
			if(x >= 16): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (17,17), 1)
			if(x >= 17): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (17,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,15), 1)				
			if(x >= 18): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,14), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,13), 1)
			if(x >= 19): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,12), 1)
			if (x >= 20): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 32-x , 6, x-20),0)
		elif self.type=='rightdown'and dir=='left':
			if (x <= 12): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 0 , 6, x),0)
			else:
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 0 , 6, 12),0)
			if(x >= 13): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,12), 1)
			if(x >= 14): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,14), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,13), 1)
			if(x >= 15): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (17,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (18,15), 1)
			if(x >= 16): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (17,17), 1)
			if(x >= 17): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (15,18), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (16,17), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (16,18), 1)
			if(x >= 18): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (13,18), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (14,18), 1)
			if(x >= 19): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,12), (12,18), 1)
			if (x >= 20): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (32-x, 13 , x-20, 6),0)
		elif self.type=='rightup'and dir=='down':
			if (x <= 12): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (0, 13 , x, 6),0)
			else: 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (0, 13 , 12, 6),0)
			if(x >= 13): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (12,13), 1)
			if(x >= 14): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (13,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (14,13), 1)
			if(x >= 15): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (15,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (16,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (16,14), 1)
			if(x >= 16): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (17,14), 1)
			if(x >= 17): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (17,15), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,15), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,16), 1)
			if(x >= 18): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,17), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,18), 1)
			if(x >= 19): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,19), 1)
			if (x >= 20): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 20 , 6, x-20),0)
		elif self.type=='rightup'and dir=='left':
			if (x <= 12): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 32-x , 6, x),0)
			else: 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 20 , 6, 12),0)
			if(x >= 13): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,19), 1)
			if(x >= 14): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,17), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,18), 1)
			if(x >= 15): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (17,15), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,15), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (18,16), 1)
			if(x >= 16): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (17,14), 1)
			if(x >= 17): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (15,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (16,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (16,14), 1)
			if(x >= 18): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (13,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (14,13), 1)
			if(x >= 19): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (12,19), (12,13), 1)
			if (x >= 20): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (32-x, 13 , x-18, 6),0)
		elif self.type=='leftup'and dir=='right':
			if (x <= 12): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 32-x , 6, x),0)
			else: 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 20 , 6, 12),0)
			if(x >= 13): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,19), 1)
			if(x >= 14): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,17), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,18), 1)
			if(x >= 15): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,15), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (14,15), 1)
			if(x >= 16): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (14,14), 1)
			if(x >= 17): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (15,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (16,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (15,14), 1)
			if(x >= 18): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (17,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (18,13), 1)
			if(x >= 19): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (19,13), 1)
			if (x >= 20): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (20, 13 , x-20, 6),0)
		elif self.type=='leftup'and dir=='down':
			if (x <= 12): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (32-x, 13 , x, 6),0)
			else: 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (20, 13 , 12, 6),0)
			if(x >= 13): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (19,13), 1)
			if(x >= 14): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (17,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (18,13), 1)
			if(x >= 15): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (15,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (16,13), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (15,14), 1)
			if(x >= 16): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (14,14), 1)
			if(x >= 17): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,15), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (14,15), 1)
			if(x >= 18): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,17), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,18), 1)
			if(x >= 19): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,19), (13,19), 1)
			if (x >= 20): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 20 , 6, x-20),0)
		elif self.type=='leftdown'and dir=='up':
			if (x <= 12): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (32-x, 13 , x, 6),0)
			else: 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (20, 13 , 12, 6),0)
			if(x >= 13): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (19,18), 1)
			if(x >= 14): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (18,18), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (17,18), 1)
			if(x >= 15): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (15,18), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (15,17), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (16,18), 1)
			if(x >= 16): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (14,17), 1)
			if(x >= 17): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (14,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,15), 1)
			if(x >= 18): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,14), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,13), 1)
			if(x >= 19): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,12), 1)
			if (x >= 20): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 32-x , 6, x-20),0)
		elif self.type=='leftdown'and dir=='right':
			if (x <= 12): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 0 , 6, x),0)
			else: 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (13, 0 , 6, 12),0)
			if(x >= 13): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,12), 1)
			if(x >= 14): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,14), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,13), 1)
			if(x >= 15): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (14,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,16), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (13,15), 1)
			if(x >= 16): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (14,17), 1)
			if(x >= 17): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (15,18), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (15,17), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (16,18), 1)
			if(x >= 18): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (18,18), 1)
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (17,18), 1)
			if(x >= 19): 
				pygame.draw.line(self.image,  (0x0, 0x0, 0x0), (19,12), (19,18), 1)
			if (x >= 20): 
				pygame.draw.rect(self.image, (0x0, 0x0, 0x0), (20, 13 , x-20, 6),0)
		
		
class Well(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		tile = util.loadPng("items.png")
		self.image = pygame.Surface((32, 32))
		self.image.set_colorkey((0x00,0xff,0x00))
		self.image.blit(tile, (0,0), (32,0,32,32))
		self.rect = self.image.get_rect()
		self.rect.topleft=pos
		self.blocked=True
		self.inarray=[]
		
class Refinery(pygame.sprite.Sprite):
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self, self.containers)
		tile = util.loadPng("items.png")
		self.image = pygame.Surface((32, 32))
		self.image.set_colorkey((0x00,0xff,0x00))
		self.image.blit(tile, (0,0), (64,0,32,32))
		self.rect = self.image.get_rect()
		self.rect.topleft=pos
		self.blocked=True
		
class Obstacle(pygame.sprite.Sprite):
	def __init__(self, pos, type):
		pygame.sprite.Sprite.__init__(self, self.containers)
		tile = util.loadPng("items.png")
		self.image = pygame.Surface((32, 32))
		self.image.set_colorkey((0x00,0xff,0x00))
		self.rect = self.image.get_rect()
		self.rect.topleft=pos
		self.blocked=True
		self.inarray=[]
		
		if type=='rock1':
			xoffset=96
			yoffset=0
		elif type=='rock2':
			xoffset=128
			yoffset=0
		elif type=='cactus1':
			xoffset=160
			yoffset=0
		elif type=='cactus2':
			xoffset=192
			yoffset=0
		elif type=='bones':
			xoffset=0
			yoffset=32
		elif type=='palmtree':
			xoffset=32
			yoffset=32
		elif type=='shrub1':
			xoffset=64
			yoffset=32
		elif type=='shrub2':
			xoffset=96
			yoffset=32
			
		self.image.blit(tile, (0,0), (xoffset,yoffset,32,32))

class HighScore:
	def __init__(self, rows=10, top=1000, nonames=True, filename='highscore'):
		self.filename=filename
		self.topscore=[]
		self.rows=rows
		self.top=top
		self.nonames=nonames
		if (self.rows > 10): self.rows=10
		self.step=self.top/self.rows
		
		if nonames:
			self.defaultnames=[' ', ' ', ' ', ' ',' ', ' ',' ', ' ',' ', ' ']
		else:
			#self.defaultnames=['Wil', 'Karla', 'Alex', 'David', 'Bob', 'Foo', 'Saul','Jayson', 'Kris', '']
			self.defaultnames=['AAA', 'AAA', 'AAA', 'AAA', 'AAA', 'AAA', 'AAA','AAA', 'AAA', 'AAA']
		
		if (os.path.isfile(self.filename)==False):
			for r in range(self.rows):
				self.topscore.append([self.defaultnames[r], top-(self.step*r)])
			self.saveScoreTable()
		else:
			self.readScoreTable()
			
	def readScoreTable(self):
		fd=open(self.filename,'r')
		buffer=fd.read()
		fd.close()
		
		self.topscore=[]
		encoded=buffer.split('\0')
		for i in range(len(encoded)-1):
			line = base64.b64decode(encoded[i])
			row=line.split(',')
			self.topscore.append([row[0], int(row[1])])
		
		self.rows=len(encoded)-1
		
		return self.topscore
		
	def saveScoreTable(self):
		fd=open(self.filename,'w+')
		for r in range(self.rows):
			line=self.topscore[r][0]+','+str(self.topscore[r][1])
			encoded=base64.b64encode(line)
			fd.write(encoded+'\0')
		fd.close()
		
	def appendScore(self, name, score):
		if self.nonames: name=' '
		
		for i in range(self.rows):
			if (score > self.topscore[i][1]): 
				self.topscore.pop(9)
				self.topscore.insert(i, [name, score])
				self.saveScoreTable()
				break
		
		