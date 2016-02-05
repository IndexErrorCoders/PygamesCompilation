import pygame
from Constants import *



class Hud(object):
	def __init__(self):
		self.scoretext = fonts[0].render("SCORE", 0, (255,255,255)).convert_alpha()
		self.full_health = hud_images["full_health"]
		self.empty_health = hud_images["empty_health"]
		self.healthbar = pygame.Surface((10,100))
		self.cooldownbar = hud_images["cooldown_bar"] #pygame.Surface((10,1))
		self.cooldowntop = hud_images["cooldown_sphere_top"]
		self.cooldownbottom = hud_images["cooldown_sphere_bottom"]
		#self.cooldownbar.fill((255,255,255))

		self.boss_sheet = hud_images["boss"]
		self.boss_active = False
		self.boss_power = 0
		self.boss_frame = 0
		self.boss_health = 0
		self.boss_max_health = 100
		self.boss_full_health = hud_images["boss_full_health"]
		self.boss_empty_health = hud_images["boss_empty_health"]
		self.boss_bg = hud_images["boss_bg"]
		self.boss_transition = 0
		
		self.height_bar = hud_images["height_bar"]
		self.player_height = hud_images["player_height"]
		self.player_completion = 0
		self.total_time = 0
		
		self.ability = 0
		self.button_glow_frame = 0

		self.abilityicon1 = hud_images["rush"]
		self.abilityicon1_gray = hud_images["rush_gray"]
		self.abilityicon2 = hud_images["time_stop"]
		self.abilityicon2_gray = hud_images["time_stop_gray"]
		self.abilityicon3 = hud_images["light"]
		self.abilityicon3_gray = hud_images["light_gray"]

		self.score = 0
		self.health = 100
		self.boss_health = 100
		self.cooldown = 0
		self.total_distance = 0
		self.boss_health = 100

	def update(self, game):
		self.score = game.score
		self.health = game.player.health
		self.boss_health = game.boss.health
		self.cooldown = game.player.cooldown
		self.total_distance = game.total_distance
		self.boss_health = game.boss.health
		self.boss_max_health = game.boss.max_health
		self.boss_active = game.boss_active
		self.player_completion = float(game.total_distance)/BOSS_DEPTH if game.total_distance <= BOSS_DEPTH else 1
		self.total_time = game.total_time
		
		if self.player_completion >= 0.995:
			self.boss_transition += 1
		else:
			self.boss_transition = 0

		if game.total_time < 1*BOSS_FULL_TIME/4:
		  self.boss_frame = 0

		if game.total_time >= 1*BOSS_FULL_TIME/4 and game.total_time < (1*BOSS_FULL_TIME/4)+7*BOSS_FLASHING_FREQ:
			if game.total_time%BOSS_FLASHING_FREQ<(BOSS_FLASHING_FREQ/2):
				self.boss_frame = 0
			else:
				self.boss_frame = 1
		
		elif game.total_time > (1*BOSS_FULL_TIME/4)+2*60:
			self.boss_frame = 1
		
		if game.total_time >= 2*BOSS_FULL_TIME/4 and game.total_time < (2*BOSS_FULL_TIME/4)+7*BOSS_FLASHING_FREQ:
			if game.total_time%BOSS_FLASHING_FREQ<(BOSS_FLASHING_FREQ/2):
				self.boss_frame = 1
			else:
				self.boss_frame = 2
		
		elif game.total_time > (2*BOSS_FULL_TIME/4)+2*60:
			self.boss_frame = 2
		
		if game.total_time >= 3*BOSS_FULL_TIME/4 and game.total_time < (3*BOSS_FULL_TIME/4)+7*BOSS_FLASHING_FREQ:
			if game.total_time%BOSS_FLASHING_FREQ<(BOSS_FLASHING_FREQ/2):
				self.boss_frame = 2
			else:
				self.boss_frame = 3
		
		elif game.total_time > (3*BOSS_FULL_TIME/4)+2*60:
			self.boss_frame = 3

		self.ability = game.player.ability
		self.button_glow_frame = (game.total_time/6)%3
		
		if self.cooldown > 0:
			self.cooldownbar = hud_images["cooldown_bar"].subsurface(0, 0, 20, 13+(self.cooldown/4 + 1))


	def draw(self, camsurf):
		#score
		#camsurf.blit(self.scoretext, (resolution[0] - 125, 600))
		#camsurf.blit(fonts[0].render("%04d"%self.score, 1, (255,255,255)), (resolution[0] - 125, 650))

		#health bar
		camsurf.blit(self.empty_health, (resolution[0] - 100, 50))
		if self.health > 0:
			camsurf.blit(self.full_health.subsurface(0,0,81,self.health*3), (resolution[0] - 100, 50))

		#boss health bar
		if self.boss_transition > 0:
			height = 450
			modifier = (height/self.boss_transition)
			if modifier < 30 and modifier > 0:
				modifier = 30
			
			camsurf.blit(self.boss_empty_health, (20, resolution[1] - height + modifier))
			if self.boss_health > 0:
				camsurf.blit(self.boss_full_health.subsurface(0,0,81,(float(self.boss_health)/self.boss_max_health)*300), (20, resolution[1] - height + modifier))

		#cooldown bar
		cooldown_bar_height = 13

		if self.cooldown == 0:
			camsurf.blit(hud_images["glow"][self.button_glow_frame], (87,33))
		
		if self.cooldown > 0:
			camsurf.blit(self.cooldownbar, (100,50))
			cooldown_bar_height = self.cooldownbar.get_rect().height

		camsurf.blit(self.cooldowntop, (95,40))
		camsurf.blit(self.cooldownbottom, (95,40+cooldown_bar_height))
		
		#boss image, boss background, and height bar
		if not self.boss_active:
			height = 400
			modifier = (self.boss_transition)*4
			
			bg_completion = float(self.total_time)/BOSS_FULL_TIME
			if bg_completion > 1:
				bg_completion = 1
			
			camsurf.blit(self.height_bar, (20, resolution[1] - height + modifier))
			camsurf.blit(self.player_height, (14, resolution[1] - (height-(240*self.player_completion)) + modifier))
			camsurf.blit(self.boss_bg, (-48, resolution[1] - 190*(bg_completion) + modifier))
			camsurf.blit(self.boss_sheet[self.boss_frame], (0, resolution[1] - 249 + modifier))
		
		if self.ability == 1:
			camsurf.blit(hud_images["glow"][self.button_glow_frame], (43,43))
		elif self.ability == 2:
			camsurf.blit(hud_images["glow"][self.button_glow_frame], (43,93))
		elif self.ability == 3:
			camsurf.blit(hud_images["glow"][self.button_glow_frame], (43,143))
		
		if self.cooldown == 0 or self.ability == 1:
			camsurf.blit(self.abilityicon1, (50,50))
		else:
			camsurf.blit(self.abilityicon1_gray, (50,50))
		
		if self.cooldown == 0 or self.ability == 2:
			camsurf.blit(self.abilityicon2, (50,100))
		else:
			camsurf.blit(self.abilityicon2_gray, (50,100))
		
		if self.cooldown == 0 or self.ability == 3:
			camsurf.blit(self.abilityicon3, (50,150))
		else:
			camsurf.blit(self.abilityicon3_gray, (50,150))
