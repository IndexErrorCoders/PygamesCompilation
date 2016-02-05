import pygame, math, random
from Controls import *
from Constants import *
import Player
import Boss
import Enemy, Demon, Mirror, StrongerDemon, Rock, MirrorDemon, Caution
import Group, MirrorGroup
import Spawn
import Pickup, HealthPickup, WeaponPickup, SpeedPickup
import Hud



"""

currently includes extra text on top for fps, distance, time





"""





class Game(object):
	"""The game object."""
	def __init__(self, size, loc, sound):
		"""Initializes the game."""
		#necessary data
		self.size = size
		self.loc = loc
		self.camsurf = pygame.Surface(size)
		self.camdisp = (0,0)
		self.sound = sound

		self.background1 = pygame.Surface(size)
		self.background1.fill((0,0,0))

		self.cover = pygame.Surface(size)
		self.cover.fill((127,0,0))
		self.cover.set_alpha(0)

		self.whiteflash = pygame.Surface(size)
		self.whiteflash.fill((255,255,255))
		self.whiteflash.set_alpha(0)

		self.triangle = pygame.Surface((500, resolution[1]))
		pygame.draw.polygon(self.triangle, (255,255,0), [(250,0), (0,resolution[1]), (500,resolution[1])])
		self.triangle.set_colorkey((0,0,0))
		self.triangle.set_alpha(63)

		self.bgtiles = [['bg1'] * 4] * 5
		self.bg_top = 0

		#game states
		self.mode = 0
		self.chapter = 0
		self.level = 0
		self.nextlevel = False
		self.endgame = False
		self.pause = False
		self.wingame = False
		self.leveldata = []

		#gameplay variables
		self.total_distance = 0
		self.total_time = 0
		self.speed = 2
		self.score = 0
		self.time_stopped = False
		self.time_stop_time = 0
		self.time_stop_length = 180
		self.saved_speed = 1
		self.boss_active = False
		self.boss_power = 0

		#control variables
		self.mouse1 = (0,0)
		self.prevmouse = (0,0)

		#objects
		self.spawndata = []
		self.player = None
		self.boss = None
		self.bullets = []
		self.enemies = []
		self.mirrors = []
		self.rocks = []
		self.pickups = []
		self.particles = []
		self.bgparticles = []
		self.fgparticles = []

		self.hud = Hud.Hud()
		self.lightspawn = None
		self.trailspawn = None
		self.windspawn1 = None
		self.fallspawn = None
		self.lavaspawn = None

	def newgame(self, mode):
		"""Prepares a new game."""
		self.mode = mode
		self.nextlevel = False
		self.endgame = False
		self.pause = False
		self.wingame = False

	def newlevel(self, leveldata):
		"""Interprets a loaded level file's data into a new level. Prepares other objects for a new level."""
		#reset a lot
		self.leveldata = leveldata
		self.nextlevel = False
		self.endgame = False
		self.pause = False
		self.wingame = False

		self.sound.startmusic("level")
		self.musicpause = 0

		self.total_distance = 0
		self.total_time = 0
		self.speed = 2
		self.score = 0
		self.bgtiles = [['bg1'] * 4] * 6
		self.bg_top = 0
		self.boss_active = False
		self.boss_power = 0

		self.time_stopped = False
		self.time_stop_time = 0

		self.player = Player.Player()
		self.boss = Boss.Boss()
		self.bullets = []
		self.enemies = []
		self.rocks = []
		self.pickups = []
		self.particles = []
		self.bgparticles = []
		self.fgparticles = []
		self.groups = {}

		#parse and interpret data
		self.spawndata = [line.split(',') for line in leveldata]
		self.spawndata.append(["49800","0","rock","left","2"])
		self.spawndata.append(["49800","0","rock","right","2"])

		#test stuff directly
		self.lightspawn = Spawn.Spawn(0, (0,0), 0, width = 5, rate = 5, velmin = 10., velrange = 5., direction = 270, angle = 60)
		self.trailspawn = Spawn.Spawn(3, (0,0), 3, width = 10, rate = .25, velmin = .1, velrange = .1, decay = 2)
		self.trailspawn.trigger()
		self.windspawn1 = Spawn.Spawn(1, (0, resolution[1] - 1), 1, width = resolution[0], height = 1, rate = .1, velmin = 16., velrange = 8., direction = 90, angle = 0)
		self.windspawn1.trigger()
		self.fallspawn = Spawn.Spawn(2, (200, -background_tiles["person"].get_height() + 1), 2, width = 650, height = 1, rate = .05, spawnchance = 100, velmin = 3., velrange = 1., direction = 270, angle = 0)
		self.fallspawn.trigger()
		self.lavaspawn = Spawn.Spawn(4, (0, resolution[1] - 1), 4, width = resolution[0], height = 1, rate = 1, spawnchance = 10, velmin = .125, velrange = .5, direction = 90, angle = 0)
		

	def resetlevel(self):
		"""Resets the current level without reloading it."""
		#save check before?
		self.setpause(False)
		self.newlevel(self.leveldata)

	def quitgame(self):
		"""Quit out of the current game."""
		#may include saving data (check/auto before/during?)
		self.setpause(False)
		self.nextlevel = True
		self.endgame = True

	def forcequit(self):
		"""Is called upon the program exiting. Can save any data here or halt the program from quitting by returning False."""
		return True

	def setpause(self, p):
		"""Pauses or unpauses the game."""
		self.pause = p
		# if p:
			
		# else:
			

	def convertmouse(self, m1):
		"""Returns the relative location of a position within the game."""
		return (m1[0] - self.loc[0], m1[1] - self.loc[1])

	def unconvertmouse(self):
		"""Returns the absolute location of game's mouse on the window containing the game."""
		return (self.mouse1[0] + self.loc[0], self.mouse1[1] + self.loc[1])

	def setmouse(self, m1):
		"""Sets the game's location and states for the mouse."""
		self.mouse1 = self.convertmouse(m1)

	def changemouse(self, m1):
		"""Changes the mouse's location on screen. Returns whether the mouse has moved."""
		if CHANGEMOUSE:
			return self.mouse1 != self.convertmouse(m1)
		return False

	def handleevent(self, event):
		"""Interprets the given event."""
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				lmb_down = True
			elif event.button == 3:
				rmb_down = True
		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				lmb_down = False
			elif event.button == 3:
				rmb_down = False
		if event.type == pygame.KEYDOWN:
			if event.key not in controls:
				return
			controls[event.key] = True
			if event.key == k_quit or event.key == k_pause:
				self.setpause(True)
		elif event.type == pygame.KEYUP:
			if event.key not in controls:
				return
			controls[event.key] = False

	def update(self, delta):
		"""Updates all game objects."""

		if self.nextlevel:
			self.endgame = True
			return

		# Deal with time stop
		if self.time_stopped:
			self.time_stop_time -= 1
			if self.time_stop_time == 0:
				self.player.ability = 0
				self.speed = self.saved_speed
				self.time_stopped = False
				self.saved_speed = 0
				self.whiteflash.set_alpha(255)
				self.sound.unpausemusic()
			elif self.time_stop_time == self.time_stop_length-1:
				self.saved_speed = self.speed
				self.speed = 0
				self.whiteflash.set_alpha(255)
				self.sound.pausemusic()

		#speed up gradually until reaching the standard speed
		if self.speed < 1 and not self.time_stopped:
			self.speed += 0.002
			if self.speed > 1:
				self.speed = 1

		if controls[k_boss] and not self.boss_active:
			self.spawndata = self.spawndata[-2:]
			self.total_distance = BOSS_DEPTH - 1000

		if self.boss_active and not self.time_stopped:
			self.speed = 1

		self.total_time += 1
		#check boss depth
		if self.total_distance < BOSS_DEPTH:
			self.total_distance += self.speed
			if self.total_distance >= BOSS_DEPTH:
				self.total_distance = BOSS_DEPTH
				self.speed = 2
				self.boss_active = True
				self.boss.activate(self)
				self.enemies.append(self.boss)
				self.sound.stopmusic()
				self.sound.startmusic("boss")
			else:
				self.boss_power = 0
				if self.total_distance > 49500 and not self.lavaspawn.active:
					self.lavaspawn.trigger()

		while not self.boss_active and len(self.spawndata) > 0 and int(self.spawndata[0][0]) < self.total_distance:
			try:
				x = self.spawndata[0][1]
				try:
					x = int(x)
				except:
					pass
				type = self.spawndata[0][2]
				group = self.spawndata[0][3]
				pattern = ""
				try:
					pattern = self.spawndata[0][4]
				except:
					pass
				if type == "demon":
					self.enemies.append(Demon.Demon((x, resolution[1]), group, pattern))
				elif type == "strongerdemon":
					self.enemies.append(StrongerDemon.StrongerDemon((x, resolution[1]), group, pattern))
				elif type == "mirror":
					mirror = Mirror.Mirror((x, resolution[1]),group)
					left_demon = MirrorDemon.MirrorDemon((x, resolution[1]), group, "left")
					right_demon = MirrorDemon.MirrorDemon((x, resolution[1]), group, "right")
					group = MirrorGroup.MirrorGroup((x, resolution[1]), group)
					group.attach(mirror, left_demon, right_demon)
					self.enemies.append(mirror)
					self.enemies.append(left_demon)
					self.enemies.append(right_demon)
					self.mirrors.append(group)
				elif type == "caution":
					caution = Caution.Caution((x, resolution[1]),group)
					self.enemies.append(caution)
				elif type == "rock":
					side = self.spawndata[0][3]
					size = int(self.spawndata[0][4])
					self.rocks.append(Rock.Rock([x, resolution[1]], side, size))
				elif type == "pickup":
					if group == "weapon":
						self.pickups.append(WeaponPickup.WeaponPickup((x, resolution[1])))
					elif group == "health":
						self.pickups.append(HealthPickup.HealthPickup((x, resolution[1])))
					elif group == "speed":
						self.pickups.append(SpeedPickup.SpeedPickup((x, resolution[1])))
					else:
						pass
				else:
					self.groups.setdefault(x, Group.Group(x, int(type), group))
				self.spawndata.pop(0)
			except:
				print self.spawndata[0]
				oops

		for r in self.rocks:
			r.update(self)
		for p in self.pickups:
			p.update(self)

		self.lightspawn.update(self)
		self.trailspawn.update(self)
		self.windspawn1.update(self)
		self.fallspawn.update(self)
		self.lavaspawn.update(self)
		for p in self.particles:
			p.update(self)
		for p in self.bgparticles:
			p.update(self)
		for p in self.fgparticles:
			p.update(self)
		for b in self.bullets:
			b.update(self)

		for m in self.mirrors:
			m.update(self)

		for e in self.enemies:
			e.update(self)

		self.player.update(self)
		if PLAYER_INVINCIBLE:
			self.player.health = 100

		self.hud.update(self)

		if self.player.health <= 0:
			self.sound.play("player_death")
			self.endgame = True

		#check game status
		if self.nextlevel:
			self.endgame = True
		else:
			pass
			#check if goal is met

		#debug print everything
		#print len(self.stuffs)

	def draw(self, surf):
		"""Draws all game objects."""
		self.camsurf.blit(black, self.camdisp)

		#background
		if self.total_distance < BOSS_DEPTH:
			self.bg_top -= BG_SPEED * self.speed
		if self.bg_top <= -background_tiles["bg1"].get_height():
			self.bg_top += background_tiles["bg1"].get_height()
			self.bgtiles.pop(0)
			self.bgtiles.append(["bg1" if random.randint(0,11) else ("burn1" if random.randint(0,1) else "burn2") for x in xrange(4)])
		top = self.bg_top
		for y in xrange(6):
			for x in xrange(4):
				self.camsurf.blit(background_tiles[self.bgtiles[y][x]], (150 + x * background_tiles["bg1"].get_width(), self.bg_top + y * background_tiles["bg1"].get_height()))

		self.cover.set_alpha(self.total_distance / 250)
		self.camsurf.blit(self.cover, (0,0))

		for p in self.bgparticles:
			p.draw(self.camsurf)

		#walls and other background
		if self.total_distance > 49000:
			self.camsurf.blit(boss_background["bg_rocks"], (180, 50500 - self.total_distance))
			self.camsurf.blit(boss_background["bg_lava"][(self.total_time / 5) % 4], (190, 50700 - self.total_distance))

		for r in self.rocks:
			r.draw(self.camsurf)
		top = -WALL_SPEED * self.total_distance
		while top < -background_tiles["wall_left"].get_height():
			top += background_tiles["wall_left"].get_height()
		while top < resolution[1]:
			self.camsurf.blit(background_tiles["wall_left"], (0, top))
			self.camsurf.blit(background_tiles["wall_right"], (resolution[0] - background_tiles["wall_right"].get_width(), top))
			top += background_tiles["wall_left"].get_height()

		#objects
		for e in self.enemies:
			e.draw(self.camsurf)
		for p in self.pickups:
			p.draw(self.camsurf)
		for b in self.bullets:
			b.draw(self.camsurf)
		for p in self.particles:
			p.draw(self.camsurf)

		if self.player.light_time > 0:
			self.camsurf.blit(self.triangle, (self.player.rect.centerx - 250, self.player.rect.centery))
		self.player.draw(self.camsurf)

		#foreground
		if self.total_distance > 49000:
			self.camsurf.blit(boss_background["fg_lava"][(self.total_time / 5) % 3], (190, 50720 - self.total_distance))
			self.camsurf.blit(boss_background["fg_rocks"], (140, 50450 - self.total_distance))

		for p in self.fgparticles:
			p.draw(self.camsurf)

		#hud
		self.hud.draw(self.camsurf)

		# self.camsurf.blit(fonts[0].render(str(self.total_distance), 1, (255,255,255)), (resolution[0]-190,0))
		# self.camsurf.blit(fonts[0].render(str(self.speed), 1, (255,255,255)), (resolution[0]-45,0))
		# self.camsurf.blit(fonts[0].render(str(self.total_time / 60), 1, (255,255,255)), (resolution[0]-90,0))

		if self.player.flipped:
			self.camsurf = pygame.transform.flip(self.camsurf, True, False)

		a = self.whiteflash.get_alpha()
		if a > 0:
			a -= 17
			self.whiteflash.set_alpha(a)
		self.camsurf.blit(self.whiteflash, (0,0))

		# shake = (0,0)
		shake = (int(abs(self.speed - 3) / 2 * ((random.randint(-1,1) * (random.randint(0,4) / 4)))), int(abs(self.speed - 3) / 2 * (random.randint(-1,1) * (random.randint(0,4) / 4))))
		if self.boss_active:
			if self.boss.shake_screen:
				shake = (random.randint(-10,10), random.randint(-10,10))
		if self.speed < 5 and not self.boss_active:
			shake = (0,0)

		surf.blit(self.camsurf, (self.loc[0] + shake[0], self.loc[1] + shake[1]))
