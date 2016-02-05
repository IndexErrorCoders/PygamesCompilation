import pygame, math, random
import Particle
from Constants import *


#use **kwargs

#broken image/rect

#moving spawns
#spawns aimed at a point/object (target for particle angle)


def getstuff(imgs, snd):
	global images, sound
	images = imgs
	sound = snd

class Spawn(object):
	def __init__(self, id, loc, type, **kwargs):
		self.kwargs = kwargs
		# print self.kwargs
		self.active = False
		self.max = 0
		if kwargs.has_key("max"):
			self.max = int(kwargs["max"])
		self.rate = .1
		if kwargs.has_key("rate"):
			self.rate = float(kwargs["rate"])
		self.spawnchance = 1
		if "spawnchance" in kwargs:
			self.spawnchance = int(kwargs["spawnchance"])
		self.direction = 0
		if kwargs.has_key("direction"):
			self.direction = int(kwargs["direction"])
		self.angle = 360
		if kwargs.has_key("angle"):
			self.angle = int(kwargs["angle"])
		self.velmin = .2
		if kwargs.has_key("velmin"):
			self.velmin = float(kwargs["velmin"])
		self.velrange = .2
		if kwargs.has_key("velrange"):
			self.velrange = float(kwargs["velrange"])

		self.circle = True
		self.radius = 1
		self.width = 1
		if kwargs.has_key("width"):
			self.width = int(kwargs["width"])
			self.radius = self.width
		self.height = 0
		if kwargs.has_key("height"):
			self.height = int(kwargs["height"])
			self.circle = False
		else:
			self.height = self.width

		self.image = pygame.Surface((self.width, self.height))
		# self.rect = pygame.Rect((loc[0] - self.radius - 1, loc[1] - self.radius - 1, self.width, self.height))
		self.id = id
		self.loc = loc
		self.type = type

		self.count = 0
		self.spawntimer = 0
		self.delay = 0

	def add(self, game):
		#location
		x = 0
		y = 0
		if self.circle:
			x = random.randint(1 - self.radius, self.radius - 1)
			y = random.randint(1 - self.radius, self.radius - 1)
			while self.radius**2 < x**2 + y**2:
				x = random.randint(1 - self.radius, self.radius - 1)
				y = random.randint(1 - self.radius, self.radius - 1)
		else:
			if self.width > 1:
				x = random.randint(0, self.width - 1)
			if self.height > 1:
				y = random.randint(0, self.height - 1)
		x += self.loc[0]
		y += self.loc[1]

		#velocity
		rads = math.pi * (self.direction - self.angle / 2 + random.randint(0, self.angle)) / 180.
		v = self.velmin + random.random() * self.velrange
		xvel = v * math.cos(rads)
		yvel = -v * math.sin(rads)

		if self.type == 2:
			game.bgparticles.append(Particle.Particle(x, y, self.type, self.id, xvel, yvel, **self.kwargs))
		elif self.type == 0:
			game.bullets.append(Particle.Particle(x, y, self.type, self.id, xvel, yvel, **self.kwargs))
		elif self.type == 1 or self.type == 4:
			game.fgparticles.append(Particle.Particle(x, y, self.type, self.id, xvel, yvel, **self.kwargs))
		else:
			game.particles.append(Particle.Particle(x, y, self.type, self.id, xvel, yvel, **self.kwargs))

	def trigger(self):
		self.active = not self.active

	def update(self, game):
		if not self.active:
			return

		if game.boss_active and (self.id == 1 or self.id == 2): #wind or falling people
			return

		if self.id == 0 or self.id == 3: #light or trail
			self.loc = [game.player.rect.centerx, game.player.rect.centery]

		if self.spawntimer > 0:
			self.spawntimer -= self.rate
			return

		while self.spawntimer <= 0 and (self.count < self.max or self.max == 0):
			if self.spawnchance > 1:
				if random.randint(0, self.spawnchance - 1):
					break
			self.spawntimer += 1
			self.count += 1
			self.add(game)

	def draw(self, camsurf, camdisp):
		#if not (self.loc[0] - camdisp[0] < -self.rect.width or self.loc[1] - camdisp[1] < -self.rect.height or self.loc[0] - camdisp[0] > camsurf.get_width() or self.loc[1] - camdisp[1] > camsurf.get_height()):
		camsurf.blit(self.image, (self.loc[0] - camdisp[0], self.loc[1] - camdisp[1]))
