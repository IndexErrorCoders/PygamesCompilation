import pygame, math, random
import Item

def getstuff(imgs, snds):
	global images, sounds
	images = imgs
	sounds = snds

def setlevel(data):
	global level
	level = data

class Cat(pygame.sprite.Sprite):
	def __init__(self, location, dirs):
		pygame.sprite.Sprite.__init__(self)
		self.image = images[0]
		self.rect = self.image.get_rect()
		self.rect.topleft = location
		self.rect.width /= 5
		self.loc = self.rect.topleft
		self.lastloc = self.loc
		self.cell = self.rect.left/32, self.rect.top/32
		self.cells = []
		self.xspeed = dirs[0]
		self.yspeed = dirs[1]
		self.xdir = 1
		self.ydir = 0
		if self.xspeed != 0:
			self.xdir = self.xspeed
		if self.yspeed != 0:
			self.ydir = self.yspeed
		if self.yspeed != 0 and self.xspeed == 0:
			self.xdir = 0
		if self.xspeed != 0 and self.yspeed == 0:
			self.ydir = 0
		self.spd = 3.9
		self.oldspd = 0
		self.moving = False
		self.paused = False
		self.xpounce = 0
		self.ypounce = 0
		self.pounce_meter = 100
		self.stamina_lag = 0
		self.disable = False
		self.frameid = 0
		self.lastframe = 0
		self.framesurface = self.image.subsurface(0,0,48,22)
		self.framerect = self.framesurface.get_rect()
		self.frametime = 4
		self.eatrect = pygame.Rect(location[0]+32, location[1]+3, 10, 16)
		self.face = 0
		self.in_trap = False
		self.power = False
		self.powertime = 0
		self.superspeed = 1
		self.superstamina = 1
		self.frozen = False
		self.frzimg = images[1]
		self.frzface = 0
		self.encells = []
		self.visible = []

	def move(self, x, y):
		self.xspeed += x
		self.yspeed += y
		if not self.disable and not self.in_trap and not self.paused:
			if x != 0:
				self.xdir = x
			if y != 0:
				self.ydir = y
			if self.yspeed != 0 and self.xspeed == 0:
				self.xdir = 0
			if self.xspeed != 0 and self.yspeed == 0:
				self.ydir = 0
		elif self.in_trap and not self.disable and not self.paused and not self.frozen:
			self.in_trap = False
			self.spd = 3.9
			if self.xspeed != 0:
				self.xdir = self.xspeed
			if self.yspeed != 0:
				self.ydir = self.yspeed
			if self.yspeed != 0 and self.xspeed == 0:
				self.xdir = 0
			if self.xspeed != 0 and self.yspeed == 0:
				self.ydir = 0

	def stopmove(self, x, y):
		self.xspeed -= x
		self.yspeed -= y
		if not self.disable and not self.paused:
			if self.xspeed != 0 and x != 0:
				self.xdir = -x
			if self.yspeed != 0 and y != 0:
				self.ydir = -y
			if self.xspeed == 0 and self.yspeed != 0:
				self.xdir = 0
			if self.yspeed == 0 and self.xspeed != 0:
				self.ydir = 0

	def checkwin(self, mouserect):
		if self.eatrect.colliderect(mouserect) and self.rect.colliderect(mouserect):
			return True
		return False

	def pounce(self):
		if self.pounce_meter == 100 and not self.frozen:
			sounds[0].play()
			self.spd = 10
			self.stamina_lag = 20
			self.disable = True
			self.xpounce = self.xspeed
			self.ypounce = self.yspeed
			if self.xpounce == 0 and self.ypounce == 0:
				self.xpounce = self.xdir
				self.ypounce = self.ydir

	def sight(self):
		self.visible = []
		if self.face == 0:
			self.visible = [(self.cell[0], self.cell[1]+1), self.cell, (self.cell[0], self.cell[1]-1),
				(self.cell[0]+1, self.cell[1]+2), (self.cell[0]+1, self.cell[1]+1), (self.cell[0]+1, self.cell[1]), (self.cell[0]+1, self.cell[1]-1), (self.cell[0]+1, self.cell[1]-2),
				(self.cell[0]+2, self.cell[1]+2), (self.cell[0]+2, self.cell[1]+1), (self.cell[0]+2, self.cell[1]), (self.cell[0]+2, self.cell[1]-1), (self.cell[0]+2, self.cell[1]-2),
				(self.cell[0]+3, self.cell[1]+2), (self.cell[0]+3, self.cell[1]+1), (self.cell[0]+3, self.cell[1]), (self.cell[0]+3, self.cell[1]-1), (self.cell[0]+3, self.cell[1]-2),
				(self.cell[0]+4, self.cell[1]+1), (self.cell[0]+4, self.cell[1]), (self.cell[0]+4, self.cell[1]-1)
			]
		elif self.face == 90:
			self.visible = [(self.cell[0]+1, self.cell[1]), self.cell, (self.cell[0]-1, self.cell[1]),
				(self.cell[0]+2, self.cell[1]-1), (self.cell[0]+1, self.cell[1]-1), (self.cell[0], self.cell[1]-1), (self.cell[0]-1, self.cell[1]-1), (self.cell[0]-2, self.cell[1]-1),
				(self.cell[0]+2, self.cell[1]-2), (self.cell[0]+1, self.cell[1]-2), (self.cell[0], self.cell[1]-2), (self.cell[0]-1, self.cell[1]-2), (self.cell[0]-2, self.cell[1]-2),
				(self.cell[0]+2, self.cell[1]-3), (self.cell[0]+1, self.cell[1]-3), (self.cell[0], self.cell[1]-3), (self.cell[0]-1, self.cell[1]-3), (self.cell[0]-2, self.cell[1]-3),
				(self.cell[0]+1, self.cell[1]-4), (self.cell[0], self.cell[1]-4), (self.cell[0]-1, self.cell[1]-4)
			]
		elif self.face == 180:
			self.visible = [(self.cell[0], self.cell[1]+1), self.cell, (self.cell[0], self.cell[1]-1),
				(self.cell[0]-1, self.cell[1]+2), (self.cell[0]-1, self.cell[1]+1), (self.cell[0]-1, self.cell[1]), (self.cell[0]-1, self.cell[1]-1), (self.cell[0]-1, self.cell[1]-2),
				(self.cell[0]-2, self.cell[1]+2), (self.cell[0]-2, self.cell[1]+1), (self.cell[0]-2, self.cell[1]), (self.cell[0]-2, self.cell[1]-1), (self.cell[0]-2, self.cell[1]-2),
				(self.cell[0]-3, self.cell[1]+2), (self.cell[0]-3, self.cell[1]+1), (self.cell[0]-3, self.cell[1]), (self.cell[0]-3, self.cell[1]-1), (self.cell[0]-3, self.cell[1]-2),
				(self.cell[0]-4, self.cell[1]+1), (self.cell[0]-4, self.cell[1]), (self.cell[0]-4, self.cell[1]-1)
			]
		elif self.face == 270:
			self.visible = [(self.cell[0]+1, self.cell[1]), self.cell, (self.cell[0]-1, self.cell[1]),
				(self.cell[0]+2, self.cell[1]+1), (self.cell[0]+1, self.cell[1]+1), (self.cell[0], self.cell[1]+1), (self.cell[0]-1, self.cell[1]+1), (self.cell[0]-2, self.cell[1]+1),
				(self.cell[0]+2, self.cell[1]+2), (self.cell[0]+1, self.cell[1]+2), (self.cell[0], self.cell[1]+2), (self.cell[0]-1, self.cell[1]+2), (self.cell[0]-2, self.cell[1]+2),
				(self.cell[0]+2, self.cell[1]+3), (self.cell[0]+1, self.cell[1]+3), (self.cell[0], self.cell[1]+3), (self.cell[0]-1, self.cell[1]+3), (self.cell[0]-2, self.cell[1]+3),
				(self.cell[0]+1, self.cell[1]+4), (self.cell[0], self.cell[1]+4), (self.cell[0]-1, self.cell[1]+4)
			]

		for cell in self.visible:
			if cell not in self.encells:
				self.encells.append(cell)

	def pause(self, p):
		self.paused = p
		if p:
			self.oldspd = self.spd
			self.spd = 0
		else:
			self.spd = self.oldspd
			self.oldspd = 0
			if self.xspeed != 0:
				self.xdir = self.xspeed
			if self.yspeed != 0:
				self.ydir = self.yspeed
			if self.yspeed != 0 and self.xspeed == 0:
				self.xdir = 0
			if self.xspeed != 0 and self.yspeed == 0:
				self.ydir = 0

	def freeze(self):
		self.frozen = True
		if self.frzface != self.face:
			self.frzface = self.face
			self.frzimg = pygame.transform.rotate(images[1], self.face)
		sounds[1].play()

	def update(self, traps, lightning, powerups, mouse):
		if self.xspeed == 0 and self.yspeed == 0:
			self.moving = False
		elif not self.in_trap:
			self.moving = True

		self.sight()

		if self.xspeed > 1:
			self.xspeed = 1
		if self.xspeed < -1:
			self.xspeed = -1
		if self.yspeed > 1:
			self.yspeed = 1
		if self.yspeed < -1:
			self.yspeed = -1

		if self.power:
			if self.superstamina == 1:
				self.powertime -= 1 * lightning
			elif self.spd != 10 and self.oldspd != 10 and self.pounce_meter < 100:
					self.powertime -= 8 * lightning
					self.pounce_meter += 10 * lightning
					if self.pounce_meter > 100:
						self.pounce_meter = 100
			if self.powertime <= 0:
				self.power = False
				self.superspeed = 1
				self.superstamina = 1
				mouse.frozen = False

		if self.spd == 10:
			self.pounce_meter -= 8 * lightning
			if self.pounce_meter <= 0:
				self.pounce_meter = 0
				self.spd = 0
		elif self.spd == 0:
			self.stamina_lag -= 1 * lightning * self.superstamina
			if self.stamina_lag <= 0:
				self.stamina_lag = 0
				self.spd = 3.9
				self.disable = False
				self.xdir = self.xspeed
				self.ydir = self.yspeed
		elif self.pounce_meter < 100 and not (self.spd == 0 and self.frozen) and self.superstamina == 1:
			self.pounce_meter += 1.5 * lightning
			if self.pounce_meter >= 100:
				self.pounce_meter = 100

		if self.spd != 0 and not self.frozen and not self.in_trap:
			for x in xrange(2):
				if self.spd == 10:
					if self.xpounce != 0 and self.ypounce != 0:
						self.loc = (self.loc[0] + self.spd * self.xpounce * .35 * lightning * self.superspeed, self.loc[1])
					else:
						self.loc = (self.loc[0] + self.spd * self.xpounce * .5 * lightning * self.superspeed, self.loc[1])
				else:
					if self.xspeed != 0 and self.yspeed != 0:
						self.loc = (self.loc[0] + self.spd * self.xspeed * .35 * lightning * self.superspeed, self.loc[1])
					else:
						self.loc = (self.loc[0] + self.spd * self.xspeed * .5 * lightning * self.superspeed, self.loc[1])
				self.rect.topleft = self.loc
				while level[self.rect.top/32][self.rect.left/32] in ('w','>','<','^','v','s') or level[self.rect.top/32][self.rect.right/32] in ('w','>','<','^','v','s') or level[self.rect.bottom/32][self.rect.left/32] in ('w','>','<','^','v','s') or level[self.rect.bottom/32][self.rect.right/32] in ('w','>','<','^','v','s') or level[self.rect.top/32][self.rect.midtop[0]/32] in ('w','>','<','^','v','s') or level[self.rect.bottom/32][self.rect.midbottom[0]/32] in ('w','>','<','^','v','s') or level[self.rect.midleft[1]/32][self.rect.left/32] in ('w','>','<','^','v','s') or level[self.rect.midright[1]/32][self.rect.right/32] in ('w','>','<','^','v','s'):
					if self.xdir > 0:
						self.rect.right = self.rect.right - self.rect.right % 32 - 1
					else:
						self.rect.left = self.rect.left - self.rect.left % 32 + 32
					self.loc = (self.rect.left, self.rect.top + self.loc[1]%1)
				if self.face == 0:
					self.eatrect.topleft = (self.rect.left+36, self.rect.top+3)
					self.eatrect.size = (10,16)
				elif self.face == 90:
					self.eatrect.topleft = (self.rect.left+3, self.rect.top+2)
					self.eatrect.size = (16,10)
				elif self.face == 180:
					self.eatrect.topleft = (self.rect.left+2, self.rect.top+3)
					self.eatrect.size = (10,16)
				else:
					self.eatrect.topleft = (self.rect.left+3, self.rect.top+36)
					self.eatrect.size = (16,10)
				if self.eatrect.colliderect(mouse.rect):
					break

			for x in xrange(2):
				if self.spd == 10:
					if self.xpounce != 0 and self.ypounce != 0:
						self.loc = (self.loc[0], self.loc[1] + self.spd * self.ypounce * .35 * lightning * self.superspeed)
					else:
						self.loc = (self.loc[0], self.loc[1] + self.spd * self.ypounce * .5 * lightning * self.superspeed)
				else:
					if self.xspeed != 0 and self.yspeed != 0:
						self.loc = (self.loc[0], self.loc[1] + self.spd * self.yspeed * .35 * lightning * self.superspeed)
					else:
						self.loc = (self.loc[0], self.loc[1] + self.spd * self.yspeed * .5 * lightning * self.superspeed)
				self.rect.topleft = self.loc
				while level[self.rect.top/32][self.rect.left/32] in ('w','>','<','^','v','s') or level[self.rect.top/32][self.rect.right/32] in ('w','>','<','^','v','s') or level[self.rect.bottom/32][self.rect.left/32] in ('w','>','<','^','v','s') or level[self.rect.bottom/32][self.rect.right/32] in ('w','>','<','^','v','s') or level[self.rect.top/32][self.rect.midtop[0]/32] in ('w','>','<','^','v','s') or level[self.rect.bottom/32][self.rect.midbottom[0]/32] in ('w','>','<','^','v','s') or level[self.rect.midleft[1]/32][self.rect.left/32] in ('w','>','<','^','v','s') or level[self.rect.midright[1]/32][self.rect.right/32] in ('w','>','<','^','v','s'):
					if self.ydir > 0:
						self.rect.bottom = self.rect.bottom - self.rect.bottom % 32 - 1
					else:
						self.rect.top = self.rect.top - self.rect.top % 32 + 32
					self.loc = (self.rect.left + self.loc[0]%1, self.rect.top)
				if self.face == 0:
					self.eatrect.topleft = (self.rect.left+36, self.rect.top+3)
					self.eatrect.size = (10,16)
				elif self.face == 90:
					self.eatrect.topleft = (self.rect.left+3, self.rect.top+2)
					self.eatrect.size = (16,10)
				elif self.face == 180:
					self.eatrect.topleft = (self.rect.left+2, self.rect.top+3)
					self.eatrect.size = (10,16)
				else:
					self.eatrect.topleft = (self.rect.left+3, self.rect.top+36)
					self.eatrect.size = (16,10)
				if self.eatrect.colliderect(mouse.rect):
					break

		self.cell = (self.eatrect.center[0]/32, self.eatrect.center[1]/32)
		self.cells = (self.cell, (self.rect.left/32, self.rect.top/32), (self.rect.left/32, self.rect.bottom/32), (self.rect.right/32, self.rect.top/32), (self.rect.right/32, self.rect.bottom/32))
		if not self.in_trap:
			for trap in traps:
				if self.rect.colliderect(trap.trrect) and trap.state is "set":
					self.in_trap = True
					self.spd = 0
					self.moving = False
					self.pounce_meter -= 50
					if self.pounce_meter < 0:
						self.pounce_meter = 0
					trap.trigger()
					sounds[1].play()
					break

		if not self.power:
			for powerup in powerups:
				if self.rect.colliderect(powerup.rect):
					if powerup.type == 1:
						self.power = True
						self.superspeed = 2
						self.powertime = 180
						sounds[1].play()
					elif powerup.type == 2:
						self.power = True
						self.superstamina = 4
						self.powertime = 240
						sounds[1].play()
					elif powerup.type == 3 and not self.in_trap:
						newtrap = Item.Trap((powerup.cell[0]*32, powerup.cell[1]*32))
						traps.add(newtrap)
						self.in_trap = True
						self.spd = 0
						self.moving = False
						self.pounce_meter -= 50
						if self.pounce_meter < 0:
							self.pounce_meter = 0
						newtrap.trigger()
						sounds[1].play()
					elif powerup.type == 4:
						self.power = True
						mouse.freeze()
						self.powertime = 90
					powerups.remove(powerup)
					break

		if self.spd == 10 or self.oldspd == 10:
			self.frameid = 4
		elif self.moving and not self.disable:
			self.frametime -= 1 * lightning
			if self.frametime <= 0:
				self.frameid = (self.frameid + 1) % 4
				self.frametime = 4
		else:
			self.frameid = 0
		self.framerect.topleft = self.rect.topleft
		if self.spd != 0 and not self.frozen and not self.in_trap:
			self.rotate_sprite()

	def rotate_sprite(self):
		prevright = self.rect.right
		prevface = self.face
		if not self.disable:
			if self.yspeed == 1 and not (self.xdir != 0 and self.xspeed != 0) or self.yspeed == 0 and self.ydir == 1 and self.xspeed == 0:
				self.face = 270
			elif self.yspeed == -1 and not (self.xdir != 0 and self.xspeed != 0) or self.yspeed == 0 and self.ydir == -1 and self.xspeed == 0:
				self.face = 90
			elif self.xspeed == 1 or self.xspeed == 0 and self.xdir == 1:
				self.face = 0
			elif self.xspeed == -1 or self.xspeed == 0 and self.xdir == -1:
				self.face = 180
		else:
			if self.xpounce == 1:
				self.face = 0
			elif self.xpounce == -1:
				self.face = 180
			elif self.ypounce == 1:
				self.face = 270
			elif self.ypounce == -1:
				self.face = 90

		if prevface != self.face or self.lastframe != self.frameid or self.lastloc != self.loc:
			self.framesurface = pygame.transform.rotate(self.image.subsurface(pygame.Rect((self.frameid * 48, 0, 48, 22))), self.face)
			self.framerect = self.framesurface.get_rect()
			self.framerect.topleft = self.rect.topleft
			if prevright < self.framerect.right:
				self.framerect.topleft = (self.framerect.left-13, self.framerect.top+13)
			elif prevright > self.framerect.right:
				self.framerect.topleft = (self.framerect.left+13, self.framerect.top-13)
			if self.face == 0:
				self.eatrect.topleft = (self.rect.left+36, self.rect.top+3)
				self.eatrect.size = (10,16)
			elif self.face == 90:
				self.eatrect.topleft = (self.rect.left+3, self.rect.top+2)
				self.eatrect.size = (16,10)
			elif self.face == 180:
				self.eatrect.topleft = (self.rect.left+2, self.rect.top+3)
				self.eatrect.size = (10,16)
			else:
				self.eatrect.topleft = (self.rect.left+3, self.rect.top+36)
				self.eatrect.size = (16,10)

			if (level[self.framerect.top/32][self.framerect.left/32] in ('w','>','<','^','v','s') or level[self.framerect.bottom/32][self.framerect.left/32] in ('w','>','<','^','v','s') or level[self.framerect.midleft[1]/32][self.framerect.left/32] in ('w','>','<','^','v','s')):
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(pygame.Rect((self.frameid * 48, 0, 48, 22))), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			elif (level[self.framerect.top/32][self.framerect.right/32] in ('w','>','<','^','v','s') or level[self.framerect.bottom/32][self.framerect.right/32] in ('w','>','<','^','v','s') or level[self.framerect.midright[1]/32][self.framerect.right/32] in ('w','>','<','^','v','s')):
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(pygame.Rect((self.frameid * 48, 0, 48, 22))), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			elif (level[self.framerect.bottom/32][self.framerect.left/32] in ('w','>','<','^','v','s') or level[self.framerect.bottom/32][self.framerect.right/32] in ('w','>','<','^','v','s') or level[self.framerect.bottom/32][self.framerect.midbottom[0]/32] in ('w','>','<','^','v','s')):
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(pygame.Rect((self.frameid * 48, 0, 48, 22))), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			elif (level[self.framerect.top/32][self.framerect.right/32] in ('w','>','<','^','v','s') or level[self.framerect.top/32][self.framerect.left/32] in ('w','>','<','^','v','s') or level[self.framerect.bottom/32][self.framerect.midtop[0]/32] in ('w','>','<','^','v','s')):
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(pygame.Rect((self.frameid * 48, 0, 48, 22))), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			elif (level[self.framerect.midleft[1]/32][self.framerect.left/32] in ('w','>','<','^','v','s') or level[self.framerect.midright[1]/32][self.framerect.right/32] in ('w','>','<','^','v','s')):
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(pygame.Rect((self.frameid * 48, 0, 48, 22))), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			elif (level[self.framerect.bottom/32][self.framerect.midbottom[0]/32] in ('w','>','<','^','v','s') or level[self.framerect.top/32][self.framerect.midtop[0]/32] in ('w','>','<','^','v','s')):
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(pygame.Rect((self.frameid * 48, 0, 48, 22))), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			self.rect = self.framerect
			self.loc = (self.rect.left + self.loc[0]%1, self.rect.top + self.loc[1]%1)
			if self.face == 0:
				self.eatrect.topleft = (self.rect.left+36, self.rect.top+3)
				self.eatrect.size = (10,16)
			elif self.face == 90:
				self.eatrect.topleft = (self.rect.left+3, self.rect.top+2)
				self.eatrect.size = (16,10)
			elif self.face == 180:
				self.eatrect.topleft = (self.rect.left+2, self.rect.top+3)
				self.eatrect.size = (10,16)
			else:
				self.eatrect.topleft = (self.rect.left+3, self.rect.top+36)
				self.eatrect.size = (16,10)
		else:
			self.framerect = self.rect

		self.lastloc = self.loc
		self.lastframe = self.frameid
		if self.spd != 10:
			if self.face == 0:
				self.xdir = 1
				self.ydir = self.yspeed
			elif self.face == 90:
				self.xdir = self.xspeed
				self.ydir = -1
			elif self.face == 180:
				self.xdir = -1
				self.ydir = self.yspeed
			else:
				self.xdir = self.xspeed
				self.ydir = 1

	def draw(self, screen, disp=(0,0)):
		if disp == (0,0) or self.framerect.left-disp[0] <= 160 and self.framerect.left-disp[0] >= -48 and self.framerect.top-disp[1] <= 96 and self.framerect.top-disp[1] >= -112:
			screen.blit(self.framesurface, (self.framerect.left-disp[0], self.framerect.top+64-disp[1]))
			if self.frozen:
				screen.blit(self.frzimg, (self.framerect.left-disp[0]-3, self.framerect.top+61-disp[1]))