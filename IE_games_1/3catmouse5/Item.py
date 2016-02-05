import pygame, math, random

def getstuff(imgs, snds):
	global images, sounds
	images = imgs
	sounds = snds

def setlevel(data):
	global level
	level = data

class Trap(pygame.sprite.Sprite):
	def __init__(self, location):
		pygame.sprite.Sprite.__init__(self)
		self.image = images[0].subsurface(0,0,28,31)
		self.outline = images[0].subsurface(56,0,28,31)
		self.rect = self.image.get_rect()
		self.rect.topleft = (location[0]+2, location[1])
		self.trrect = pygame.Rect(location[0]+5, location[1]+6, 22, 21)
		self.cell = (location[0]/32, location[1]/32)
		self.state = "set"

	def trigger(self):
		sounds[0].play()
		self.state = "dead"
		self.image = images[0].subsurface(28,0,28,31)
		self.outline = images[0].subsurface(84,0,28,31)

	def draw(self, screen, ol, disp=(0,0)):
		if ol:
			screen.blit(self.outline, (self.rect.left-disp[0], self.rect.top+64-disp[1]))
		elif disp == (0,0) or self.rect.left-disp[0] <= 160 and self.rect.left-disp[0] >= -28 and self.rect.top-disp[1] <= 96 and self.rect.top-disp[1] >= -92:
			screen.blit(self.image, (self.rect.left-disp[0], self.rect.top+64-disp[1]))


class Hole(pygame.sprite.Sprite):
	def __init__(self, location, type):
		pygame.sprite.Sprite.__init__(self)
		if type is ">":
			self.image = images[1].subsurface(0,0,32,32)
			self.outline = images[1].subsurface(32,0,32,32)
		elif type is "<":
			self.image = images[2].subsurface(0,0,32,32)
			self.outline = images[2].subsurface(32,0,32,32)
		elif type is "^":
			self.image = images[3].subsurface(0,0,32,32)
			self.outline = images[3].subsurface(32,0,32,32)
		elif type is "v":
			self.image = images[4].subsurface(0,0,32,32)
			self.outline = images[4].subsurface(32,0,32,32)
		else:
			self.image = images[5]
			self.outline = images[8]
		self.owimg = images[9]
		self.rect = self.image.get_rect()
		self.rect.topleft = location
		self.cell = (location[0]/32, location[1]/32)
		self.type = type

	def draw(self, screen, ol, mrect, mhole, disp=(0,0)):
		if ol:
			screen.blit(self.outline, (self.rect.left-disp[0], self.rect.top+64-disp[1]))
		elif (disp == (0,0) or self.rect.left-disp[0] <= 160 and self.rect.left-disp[0] >= -32 and self.rect.top-disp[1] <= 96 and self.rect.top-disp[1] >= -96) and self.rect.colliderect(mrect) and not mhole:
			screen.blit(self.image, (self.rect.left-disp[0], self.rect.top+64-disp[1]))
		if not ol and (disp == (0,0) or self.rect.left-disp[0] <= 160 and self.rect.left-disp[0] >= -32 and self.rect.top-disp[1] <= 96 and self.rect.top-disp[1] >= -96):
			screen.blit(self.owimg, (self.rect.left-disp[0], self.rect.top+64-disp[1]))


class Cheese(pygame.sprite.Sprite):
	def __init__(self, location):
		pygame.sprite.Sprite.__init__(self)
		self.image = images[6].subsurface(0,0,32,32)
		self.outline = images[6].subsurface(32,0,32,32)
		self.rect = self.image.get_rect()
		self.rect.topleft = location
		self.chrect = pygame.Rect(location[0]+5, location[1]+5, 22, 22)
		self.state = "there"
		self.seen = False
		self.cell = (location[0]/32, location[1]/32)

	def remove(self):
		self.state = "taken"
		self.outline = images[8]

	def draw(self, screen, ol, disp=(0,0)):
		if ol:
			screen.blit(self.outline, (self.rect.left-disp[0], self.rect.top+64-disp[1])) 
		elif self.state is "there" and (disp == (0,0) or self.rect.left-disp[0] <= 160 and self.rect.left-disp[0] >= -32 and self.rect.top-disp[1] <= 96 and self.rect.top-disp[1] >= -96):
			screen.blit(self.image, (self.rect.left-disp[0], self.rect.top+64-disp[1]))


class Powerup(pygame.sprite.Sprite):
	def __init__(self, location, type):
		pygame.sprite.Sprite.__init__(self)
		self.image = images[7].subsurface(0,0,28,28)
		self.outline = images[7].subsurface(28,0,28,28)
		self.cell = location
		self.rect = self.image.get_rect()
		self.rect.topleft = (location[0]*32+2, location[1]*32+2)
		if type < 4:
			type = 1#superspeed
		elif type < 7:
			type = 2#superstamina
		elif type < 9:
			type = 3#trap
		else:
			type = 4#freeze
		self.type = type
		self.timer = 750
		sounds[3].play()

	def move(self, location):
		self.cell = location
		self.rect.topleft = (location[0]*32+2, location[1]*32+2)

	def update(self, lightning):
		self.timer -= lightning
		if self.timer <= 0:
			self.timer = 750
			sounds[3].play()
			return True
		return False

	def draw(self, screen, ol, disp=(0,0)):
		if ol:
			screen.blit(self.outline, (self.rect.left-disp[0], self.rect.top+64-disp[1])) 
		elif disp == (0,0) or self.rect.left-disp[0] <= 160 and self.rect.left-disp[0] >= -28 and self.rect.top-disp[1] <= 96 and self.rect.top-disp[1] >= -94:
			screen.blit(self.image, (self.rect.left-disp[0], self.rect.top+64-disp[1]))


class Light(pygame.sprite.Sprite):
	def __init__(self, location, size):
		pygame.sprite.Sprite.__init__(self)
		self.image = images[10+size].subsurface(0, 0, 80+40*size, 80+40*size)
		self.aimg = images[10+size].subsurface(80+40*size, 0, 80+40*size, 80+40*size)
		self.cell = location
		self.rect = self.image.get_rect()
		self.rect.topleft = (location[0]*32, location[1]*32)
		self.loc = self.rect.topleft
		self.size = size
		self.on = True
		self.alert = False
		self.atime = 0
		x = float(random.randint(-20,20))
		y = float(random.randint(-20,20))
		while x == 0 and y == 0:
			x = float(random.randint(-20,20))
			y = float(random.randint(-20,20))
		self.xvel = float(x/2*(6-self.size)) / math.sqrt(x**2+y**2)
		self.yvel = float(y/2*(6-self.size)) / math.sqrt(x**2+y**2)

	def setalert(self, mloc):
		if self.alert and self.atime < 142:
			self.atime = 141
			self.xvel = float(6 - self.size) * (mloc[0] - self.rect.centerx) / 1.75 / math.sqrt((mloc[0] - self.rect.centerx)**2 + (mloc[1] - self.rect.centery)**2)
			self.yvel = float(6 - self.size) * (mloc[1] - self.rect.centery) / 1.75 / math.sqrt((mloc[0] - self.rect.centerx)**2 + (mloc[1] - self.rect.centery)**2)
		elif not self.alert:
			self.alert = True
			self.on = True
			self.atime = 150
			self.xvel = float(6 - self.size) * (mloc[0] - self.rect.centerx) / 1.75 / math.sqrt((mloc[0] - self.rect.centerx)**2 + (mloc[1] - self.rect.centery)**2)
			self.yvel = float(6 - self.size) * (mloc[1] - self.rect.centery) / 1.75 / math.sqrt((mloc[0] - self.rect.centerx)**2 + (mloc[1] - self.rect.centery)**2)

	def update(self, lightning, mrect, lights):
		if self.alert:
			self.atime -= lightning
			if self.atime <= 0:
				self.atime = 0
				self.alert = False

		while self.on:
			if level[mrect.top/32][mrect.left/32] in ('s','^','v','<','>','h','m','c') and level[mrect.top/32][mrect.right/32] in ('s','^','v','<','>','h','m','c') and level[mrect.bottom/32][mrect.left/32] in ('s','^','v','<','>','h','m','c') and level[mrect.bottom/32][mrect.right/32] in ('s','^','v','<','>','h','m','c'):
				break
			if self.on and math.sqrt((self.rect.centerx-mrect.centerx)**2 + (self.rect.centery-mrect.centery)**2) < 40+20*self.size:
				for l in lights:
					l.setalert(mrect.center)
			break

		if not self.alert:
			if self.on:
				if random.randint(1, 360/lightning) == 1:
					self.on = False
					sounds[1].play()
			else:
				if random.randint(1, 90/lightning) == 1:
					if self.rect.colliderect(mrect):
						if random.randint(0,2) == 2:
							self.on = True
							sounds[2].play()
					else:
						self.on = True
						sounds[2].play()

		if self.atime < 80 and self.alert:
			if math.sqrt((self.rect.centerx - mrect.centerx)**2 + (self.rect.centery - mrect.centery)**2) > 60+30*self.size:
				if random.randint(1,30) == 1:
					if random.randint(0,1) == 1:
						x = float(random.randint(-20,20))
						y = float(random.randint(-20,20))
						while x == 0 and y == 0:
							x = float(random.randint(-20,20))
							y = float(random.randint(-20,20))
					else:
						x = float((mrect.centerx - self.rect.centerx + random.randint(-100,100))) / 25
						y = float((mrect.centery - self.rect.centery + random.randint(-100,100))) / 25
						while x == 0 and y == 0:
							x = float((mrect.centerx - self.rect.centerx + random.randint(-100,100))) / 25
							y = float((mrect.centery - self.rect.centery + random.randint(-100,100))) / 25
					self.xvel = float(x/2*(6-self.size)) / math.sqrt(x**2+y**2)
					self.yvel = float(y/2*(6-self.size)) / math.sqrt(x**2+y**2)
		elif self.atime < 142 and self.alert and not (level[mrect.top/32][mrect.left/32] in ('s','^','v','<','>','h','m','c') and level[mrect.top/32][mrect.right/32] in ('s','^','v','<','>','h','m','c') and level[mrect.bottom/32][mrect.left/32] in ('s','^','v','<','>','h','m','c') and level[mrect.bottom/32][mrect.right/32] in ('s','^','v','<','>','h','m','c')):
			self.xvel = float(6 - self.size) * (mrect.centerx - self.rect.centerx) / 1.75 / math.sqrt((mrect.centerx - self.rect.centerx)**2 + (mrect.centery - self.rect.centery)**2)
			self.yvel = float(6 - self.size) * (mrect.centery - self.rect.centery) / 1.75 / math.sqrt((mrect.centerx - self.rect.centerx)**2 + (mrect.centery - self.rect.centery)**2)
		elif not self.alert:
			if random.randint(1,75) == 1:
				if random.randint(0,4) != 4:
					x = float(random.randint(-20,20))
					y = float(random.randint(-20,20))
					while x == 0 and y == 0:
						x = float(random.randint(-20,20))
						y = float(random.randint(-20,20))
				else:
					x = float((mrect.centerx - self.rect.centerx + random.randint(-200,200))) / 30
					y = float((mrect.centery - self.rect.centery + random.randint(-200,200))) / 30
					while x == 0 and y == 0:
						x = float((mrect.centerx - self.rect.centerx + random.randint(-200,200))) / 30
						y = float((mrect.centery - self.rect.centery + random.randint(-200,200))) / 30
				self.xvel = float(x/2*(6-self.size)) / math.sqrt(x**2+y**2)
				self.yvel = float(y/2*(6-self.size)) / math.sqrt(x**2+y**2)


		if self.atime < 142:
			if self.alert:
				self.loc = (self.loc[0] + self.xvel*2*lightning, self.loc[1])
				if self.loc[0] < 16:
					self.xvel *= -1
					self.loc = (16, self.loc[1])
				elif self.loc[0]+self.size*40 > 704:
					self.xvel *= -1
					self.loc = (704-self.size*40, self.loc[1])

				self.loc = (self.loc[0], self.loc[1] + self.yvel*2*lightning)
				if self.loc[1] < 16:
					self.yvel *= -1
					self.loc = (self.loc[0], 16)
				elif self.loc[1]+self.size*40 > 480:
					self.yvel *= -1
					self.loc = (self.loc[0], 480-self.size*40)

			elif self.on:
				self.loc = (self.loc[0] + self.xvel*lightning, self.loc[1])
				if self.loc[0] < 16:
					self.xvel *= -1
					self.loc = (16, self.loc[1])
				elif self.loc[0]+self.size*40 > 704:
					self.xvel *= -1
					self.loc = (704-self.size*40, self.loc[1])

				self.loc = (self.loc[0], self.loc[1] + self.yvel*lightning)
				if self.loc[1] < 16:
					self.yvel *= -1
					self.loc = (self.loc[0], 16)
				elif self.loc[1]+self.size*40 > 480:
					self.yvel *= -1
					self.loc = (self.loc[0], 480-self.size*40)

			else:
				self.loc = (self.loc[0] + self.xvel*.75*lightning, self.loc[1])
				if self.loc[0] < 16:
					self.xvel *= -1
					self.loc = (16, self.loc[1])
				elif self.loc[0]+self.size*40 > 704:
					self.xvel *= -1
					self.loc = (704-self.size*40, self.loc[1])

				self.loc = (self.loc[0], self.loc[1] + self.yvel*.75*lightning)
				if self.loc[1] < 16:
					self.yvel *= -1
					self.loc = (self.loc[0], 16)
				elif self.loc[1]+self.size*40 > 480:
					self.yvel *= -1
					self.loc = (self.loc[0], 480-self.size*40)

			self.rect.topleft = self.loc

	def draw(self, screen):
		if self.alert:
			screen.blit(self.aimg, (0,0))
		else:
			screen.blit(self.image, (0,0))
