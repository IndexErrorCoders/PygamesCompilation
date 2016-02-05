import pygame, math, random
from Constants import *
from Controls import *
import PlayerBullet


class Particle(PlayerBullet.PlayerBullet):
	def __init__(self, x, y, type, id, xvel, yvel, **kwargs):
		PlayerBullet.PlayerBullet.__init__(self, (x,y), -1)
		self.image = None
		if type == 0: # light ability
			self.image = images["light_particle"] #pygame.Surface((2,2))
			#self.image.fill((255,255,255))
			self.damage = .1
		elif type == 1: # wind lines
			self.image = pygame.Surface((1, random.randint(48,96)))
			self.image.fill((200,200,200))
			self.image.set_alpha(127)
		elif type == 2: # falling guy
			self.image = background_tiles["person"]#pygame.Surface((1,64))
		elif type == 3: # trail
			self.image = pygame.Surface((random.randint(1,2), random.randint(1,2)))
			self.image.fill((255,255,0))
		elif type == 4:
			self.image = pygame.Surface((random.randint(1,2), random.randint(1,2)))
			self.image.fill((random.randint(200,255),random.randint(0,127),0))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

		self.loc = [x, y]
		self.type = type
		self.spawnid = id
		self.xvel = xvel
		self.yvel = yvel

		self.ploc = [x, y]

		self.drawable = True

		self.xfriction = 1
		self.yfriction = 1
		if kwargs.has_key("xfriction"):
			self.xfriction = kwargs["xfriction"]
		if kwargs.has_key("yfriction"):
			self.yfriction = kwargs["yfriction"]
		else:
			self.yfriction = self.xfriction

		self.life = 100
		self.decay = 0
		if kwargs.has_key("decay"):
			self.decay = kwargs["decay"]

	def destroy(self, game):
		if self.type == 2:
			game.bgparticles.remove(self)
		elif self.type == 0:
			game.bullets.remove(self)
		elif self.type == 3:
			game.particles.remove(self)
		elif self.type == 1 or self.type == 4:
			game.fgparticles.remove(self)

	def update(self, game):
		self.life -= self.decay
		if self.life <= 0:
			self.destroy(game)
			return

		if game.time_stopped and self.type != 4:
			return

		if self.type == 1:
			self.drawable = game.speed > 2

		xacc = 0
		yacc = 0
		if self.type == 4:
			xacc = random.random() * .1 * random.randint(-1,1)
			yacc = -.0001 * random.random()
		self.xvel += xacc
		self.yvel += yacc

		#x move
		pmovex = 0
		if self.type == 0 and not self.reflected:
			pmovex = game.player.loc[0] - self.ploc[0]
			self.ploc[0] = game.player.loc[0]
		self.loc[0] += self.xvel + pmovex

		#x collisions
		if self.loc[0] <= -self.rect.width or self.loc[0] > resolution[0]:
			self.destroy(game)
			return

		self.rect.left = self.loc[0]

		#y move
		pmovey = 0
		if self.type == 0 and not self.reflected:
			pmovey = game.player.loc[1] - self.ploc[1]
			self.ploc[1] = game.player.loc[1]
		elif self.type == 0:
			pmovey -= 8
		elif self.type == 1:
			pmovey -= game.speed
		elif self.type == 2:
			pmovey -= game.speed - 1
		elif self.type == 3:
			pmovey -= game.speed
		self.loc[1] += self.yvel + pmovey

		#y collisions
		if self.loc[1] <= -self.rect.height or self.loc[1] > resolution[1]:
			self.destroy(game)
			return

		self.rect.top = self.loc[1]

		#other
		if self.reflected:
			if self.rect.colliderect(game.player.rect):
				game.player.health_upgrade(1)
				self.destroy(game)
				return

		if self.type == 0:
			if PlayerBullet.PlayerBullet.update(self, game, True):
				return

		#debug
		#print xacc, yacc

	def draw(self, camsurf, camdisp=(0,0)):
		#if not (self.loc[0] - camdisp[0] < -self.rect.width or self.loc[1] - camdisp[1] < -self.rect.height or self.loc[0] - camdisp[0] > camsurf.get_width() or self.loc[1] - camdisp[1] > camsurf.get_height()):
		if self.drawable:
			camsurf.blit(self.image, (self.loc[0] - camdisp[0], self.loc[1] - camdisp[1]))

		