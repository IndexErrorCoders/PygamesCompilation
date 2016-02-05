import pygame, math, random
import Item

def getstuff(imgs, snds):
	global images, sounds
	images = imgs
	sounds = snds

def setlevel(data):
	global level
	level = data

class Mouse(pygame.sprite.Sprite):
	def __init__(self, location, dirs=(0,0)):
		pygame.sprite.Sprite.__init__(self)
		self.image = images[0]
		self.rect = self.image.get_rect()
		self.rect.topleft = location
		self.rect.width /= 3
		self.loc = location
		self.lastloc = self.loc
		self.xspeed = dirs[0]
		self.yspeed = dirs[1]
		self.xdir = -1
		self.ydir = 0
		if self.xspeed != 0:
			self.xdir = self.xspeed
		if self.yspeed != 0:
			self.ydir = self.yspeed
		if self.yspeed != 0 and self.xspeed == 0:
			self.xdir = 0
		if self.xspeed != 0 and self.yspeed == 0:
			self.ydir = 0
		self.spd = 3
		self.oldspd = 0
		self.moving = False
		self.in_trap = False
		self.trap_wiggle = 0
		self.trap_wiggling = 0
		self.xwiggle = 0
		self.ywiggle = 0
		self.sprint_meter = 100
		self.frameid = 0
		self.lastframe = 0
		self.framesurface = pygame.transform.rotate(self.image.subsurface(0,0,20,14), 180)
		self.framerect = self.framesurface.get_rect()
		self.frametime = 6
		self.face = 180
		self.paused = False
		self.cell = (self.loc[0]/32, self.loc[1]/32)
		self.encells = []
		self.power = False
		self.powertime = 0
		self.superspeed = 1
		self.superstamina = 1
		self.frozen = False
		self.frzimg = images[1]
		self.frzface = 0
		self.visible = []
		self.cheesecount = 0

	def move(self, x, y, lightning=1):
		self.xspeed += x
		self.yspeed += y
		if not self.in_trap and not self.paused:
			if x != 0:
				self.xdir = x
			if y != 0:
				self.ydir = y
			if self.yspeed != 0 and self.xspeed == 0:
				self.xdir = 0
			if self.xspeed != 0 and self.yspeed == 0:
				self.ydir = 0
		elif self.spd == 0 and not self.paused and not self.frozen:
			self.trap_wiggle += 1 * lightning * self.superstamina
			if self.trap_wiggling == 2:
				self.loc = (self.loc[0] - self.xwiggle, self.loc[1] - self.ywiggle)
				self.rect.topleft = self.loc
			self.trap_wiggling = 1
			if self.trap_wiggle >= 12:
				sounds[0].play()
				self.trap_wiggle = 0
				self.in_trap = False
				self.trap_wiggling = 0
				spd2 = self.oldspd
				self.oldspd = self.spd
				self.spd = spd2
				self.xdir = self.xspeed
				self.ydir = self.yspeed

	def stopmove(self, x, y):
		self.xspeed -= x
		self.yspeed -= y
		if not self.in_trap and not self.paused:
			if self.xspeed != 0 and x != 0:
				self.xdir = -x
			if self.yspeed != 0 and y != 0:
				self.ydir = -y
			if self.xspeed == 0 and self.yspeed != 0:
				self.xdir = 0
			if self.yspeed == 0 and self.xspeed != 0:
				self.ydir = 0

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

	def sprint(self, lights):
		if self.sprint_meter == 100 and not self.in_trap and not self.frozen:
			sounds[0].play()
			self.spd = 6.4
			for light in lights:
				light.setalert(self.rect.center)

	def pause(self, p):
		self.paused = p
		if p and not self.in_trap:
			spd2 = self.oldspd
			self.oldspd = self.spd
			self.spd = spd2
		elif not self.in_trap:
			spd2 = self.oldspd
			self.oldspd = self.spd
			self.spd = spd2
			if self.xspeed != 0:
				self.xdir = self.xspeed
			if self.yspeed != 0:
				self.ydir = self.yspeed
			if self.yspeed != 0 and self.xspeed == 0:
				self.xdir = 0
			if self.xspeed != 0 and self.yspeed == 0:
				self.ydir = 0

	def checkwin(self):
		if self.cheesecount != 0:
			if level[self.rect.top/32][self.rect.left/32] is 'm' or level[self.rect.top/32][self.rect.right/32] is 'm' or level[self.rect.bottom/32][self.rect.right/32] is 'm' or level[self.rect.bottom/32][self.rect.left/32] is 'm':
				return True
		return False

	def checklose(self, lights):
		if level[self.rect.top/32][self.rect.left/32] in ('s','^','v','<','>','h','m','c') and level[self.rect.top/32][self.rect.right/32] in ('s','^','v','<','>','h','m','c') and level[self.rect.bottom/32][self.rect.left/32] in ('s','^','v','<','>','h','m','c') and level[self.rect.bottom/32][self.rect.right/32] in ('s','^','v','<','>','h','m','c'):
			return False
		for light in lights:
			if light.on and math.sqrt((self.rect.centerx-light.rect.centerx)**2 + (self.rect.centery-light.rect.centery)**2) < 20+20*light.size:
				light.alert = True
				return True
		return False

	def checkhole(self):
		if level[self.rect.top/32][self.rect.left/32] in ('^','v','<','>','h') and level[self.rect.top/32][self.rect.right/32] in ('^','v','<','>','h') and level[self.rect.bottom/32][self.rect.left/32] in ('^','v','<','>','h') and level[self.rect.bottom/32][self.rect.right/32] in ('^','v','<','>','h'):
			return True
		return False

	def freeze(self):
		self.frozen = True
		if self.frzface != self.face:
			self.frzface = self.face
			self.frzimg = pygame.transform.rotate(images[1], self.face)
		sounds[2].play()

	def update(self, cheeses, traps, lightning, powerups, lights, cat=0):
		self.cell = (self.rect.center[0]/32, self.rect.center[1]/32)
		self.sight()

		if self.xspeed == 0 and self.yspeed == 0:
			self.moving = False
		else:
			self.moving = True

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
			elif self.spd != 6.4 and self.oldspd != 6.4 and self.sprint_meter < 100:
					self.powertime -= 8 * lightning
					self.sprint_meter += 10 * lightning
					if self.sprint_meter > 100:
						self.sprint_meter = 100
			if self.powertime <= 0:
				self.power = False
				self.superspeed = 1
				self.superstamina = 1
				cat.frozen = False

		if self.spd == 6.4 or self.oldspd == 6.4:
			self.sprint_meter -= 1.5 * lightning
			if self.sprint_meter <= 0:
				self.sprint_meter = 0
				if self.oldspd == 6.4:
					self.oldspd = 3
				elif self.spd == 6.4:
					self.spd = 3
		elif self.sprint_meter < 100 and self.superstamina == 1:
			self.sprint_meter += 1.25 * lightning
			if self.sprint_meter > 100:
				self.sprint_meter = 100

		if self.spd != 0 and not self.frozen:
			if self.xspeed != 0 and self.yspeed != 0:
				self.loc = (self.loc[0] + self.spd * self.xspeed * .7 * lightning * self.superspeed, self.loc[1])
			else:
				self.loc = (self.loc[0] + self.spd * self.xspeed * lightning * self.superspeed, self.loc[1])
			self.rect.topleft = self.loc
			if level[self.rect.top/32][self.rect.left/32] is 'w' or level[self.rect.top/32][self.rect.right/32] is 'w' or level[self.rect.bottom/32][self.rect.left/32] is 'w' or level[self.rect.bottom/32][self.rect.right/32] is 'w':
				if self.xspeed > 0:
					self.rect.right = self.rect.right - self.rect.right % 32 - 1
				else:
					self.rect.left = self.rect.left - self.rect.left % 32 + 32
				self.loc = (self.rect.left, self.rect.top + self.loc[1]%1)

			if self.xspeed != 0 and self.yspeed != 0:
				self.loc = (self.loc[0], self.loc[1] + self.spd * self.yspeed * .7 * lightning * self.superspeed)
			else:
				self.loc = (self.loc[0], self.loc[1] + self.spd * self.yspeed * lightning * self.superspeed)
			self.rect.topleft = self.loc
			if level[self.rect.top/32][self.rect.left/32] is 'w' or level[self.rect.top/32][self.rect.right/32] is 'w' or level[self.rect.bottom/32][self.rect.left/32] is 'w' or level[self.rect.bottom/32][self.rect.right/32] is 'w':
				if self.yspeed > 0:
					self.rect.bottom = self.rect.bottom - self.rect.bottom % 32 - 1
				else:
					self.rect.top = self.rect.top - self.rect.top % 32 + 32
				self.loc = (self.rect.left + self.loc[0]%1, self.rect.top)

		if self.trap_wiggling == 1:
			self.xwiggle = random.randint(-3,3)
			self.ywiggle = random.randint(-3,3)
			self.loc = (self.loc[0] + self.xwiggle, self.loc[1] + self.ywiggle)
			self.rect.topleft = self.loc
			self.trap_wiggling = 2
		elif self.trap_wiggling == 2:
			self.loc = (self.loc[0] - self.xwiggle, self.loc[1] - self.ywiggle)
			self.rect.topleft = self.loc
			self.trap_wiggling = 0

		for cheese in cheeses:
			if self.rect.colliderect(cheese.chrect) and cheese.state is "there":
				cheese.remove()
				self.cheesecount += 1
				sounds[1].play()
				for light in lights:
					light.setalert(self.rect.center)

		if not self.in_trap:
			for trap in traps:
				if self.rect.colliderect(trap.trrect) and trap.state is "set":
					if self.xspeed == 0:
						self.xdir = 0
					self.in_trap = True
					self.sprint_meter -= 50
					if self.sprint_meter < 0:
						self.sprint_meter = 0
					spd2 = self.oldspd
					self.oldspd = self.spd
					self.spd = spd2
					self.moving = False
					trap.trigger()
					sounds[2].play()
					for light in lights:
						light.setalert(self.rect.center)
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
						self.superstamina = 3
						self.powertime = 240
						sounds[1].play()
					elif powerup.type == 3 and not self.in_trap:
						newtrap = Item.Trap((powerup.cell[0]*32, powerup.cell[1]*32))
						traps.add(newtrap)
						if self.xspeed == 0:
							self.xdir = 0
						self.in_trap = True
						self.sprint_meter -= 50
						if self.sprint_meter < 0:
							self.sprint_meter = 0
						spd2 = self.oldspd
						self.oldspd = self.spd
						self.spd = spd2
						self.moving = False
						newtrap.trigger()
						sounds[2].play()
					elif powerup.type == 4:
						self.power = True
						cat.freeze()
						self.powertime = 90
					powerups.remove(powerup)
					break

		if self.checkhole():
			self.frameid = 2
			self.frametime = 1
		elif self.moving:
			self.frametime -= 1 * lightning
			if self.frametime <= 0:
				self.frameid = (self.frameid + 1) % 2
				self.frametime = 6
		else:
			self.frameid = 0
		self.framerect.topleft = self.rect.topleft
		if not self.in_trap and not self.frozen:
			self.rotate_sprite()

	def rotate_sprite(self):
		prevright = self.rect.right
		prevface = self.face
		if self.yspeed == 1 and not (self.xdir != 0 and self.xspeed != 0) or self.yspeed == 0 and self.ydir == 1 and self.xspeed == 0:
			self.face = 270
		elif self.yspeed == -1 and not (self.xdir != 0 and self.xspeed != 0) or self.yspeed == 0 and self.ydir == -1 and self.xspeed == 0:
			self.face = 90
		elif self.xspeed == 1 or self.xspeed == 0 and self.xdir == 1:
			self.face = 0
		elif self.xspeed == -1 or self.xspeed == 0 and self.xdir == -1:
			self.face = 180

		if prevface != self.face or self.lastframe != self.frameid or self.lastloc != self.loc:
			self.framesurface = pygame.transform.rotate(self.image.subsurface(self.frameid * 20, 0, 20, 14), self.face)
			self.framerect = self.framesurface.get_rect()
			self.framerect.topleft = self.rect.topleft
			if prevright < self.framerect.right:
				self.framerect.topleft = (self.framerect.left-3, self.framerect.top+3)
			elif prevright > self.framerect.right:
				self.framerect.topleft = (self.framerect.left+3, self.framerect.top-3)

			if level[self.framerect.top/32][self.framerect.left/32] is 'w' or level[self.framerect.bottom/32][self.framerect.left/32] is 'w':
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(self.frameid * 20, 0, 20, 14), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			elif level[self.framerect.top/32][self.framerect.right/32] is 'w' or level[self.framerect.bottom/32][self.framerect.right/32] is 'w':
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(self.frameid * 20, 0, 20, 14), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			elif level[self.framerect.bottom/32][self.framerect.left/32] is 'w' or level[self.framerect.bottom/32][self.framerect.right/32] is 'w':
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(self.frameid * 20, 0, 20, 14), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			elif level[self.framerect.top/32][self.framerect.right/32] is 'w' or level[self.framerect.top/32][self.framerect.left/32] is 'w':
				if (self.face == 0 or self.face == 180) and (prevface == 90 or prevface == 270) and self.yspeed != 0:
					self.face = self.ydir * 90 + 180
				else:
					self.face = prevface
				self.framesurface = pygame.transform.rotate(self.image.subsurface(self.frameid * 20, 0, 20, 14), self.face)
				self.framerect = self.framesurface.get_rect()
				self.framerect.topleft = self.rect.topleft
			self.rect = self.framerect
			self.loc = (self.rect.left + self.loc[0]%1, self.rect.top + self.loc[1]%1)
		else:
			self.framerect = self.rect

		if self.checkhole():
			self.frameid = 2
			self.frametime = 1
			self.framesurface = pygame.transform.rotate(self.image.subsurface(self.frameid * 20, 0, 20, 14), self.face)

		self.lastloc = self.loc
		self.lastframe = self.frameid
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
		if disp == (0,0) or self.framerect.left-disp[0] <= 160 and self.framerect.left-disp[0] >= -20 and self.framerect.top-disp[1] <= 96 and self.framerect.top-disp[1] >= -84:
			screen.blit(self.framesurface, (self.framerect.left-disp[0], self.framerect.top+64-disp[1]))
			if self.frozen:
				screen.blit(self.frzimg, (self.framerect.left-disp[0]-3, self.framerect.top+61-disp[1]))