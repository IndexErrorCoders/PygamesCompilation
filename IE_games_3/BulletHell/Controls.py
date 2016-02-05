import pygame, sys, os


#reassignment/reset functions?


pygame.init()

#controls

k_quit = pygame.K_ESCAPE
k_pause = pygame.K_p

k_up2 = pygame.K_UP
k_down2 = pygame.K_DOWN
k_left2 = pygame.K_LEFT
k_right2 = pygame.K_RIGHT
k_up = pygame.K_z
k_down = pygame.K_s
k_left = pygame.K_q
k_right = pygame.K_d

k_action1 = pygame.K_SPACE
k_action2 = pygame.K_RETURN
k_ability1 = pygame.K_j
k_ability2 = pygame.K_k
k_ability3 = pygame.K_l
k_debug_weaponup = pygame.K_x
k_boss = pygame.K_8

controls = {
	k_quit: False,
	k_pause: False,
	k_up: False,
	k_down: False,
	k_left: False,
	k_right: False,
	k_up2: False,
	k_down2: False,
	k_left2: False,
	k_right2: False,
	k_action1: False,
	k_action2: False,
	k_ability1: False,
	k_ability2: False,
	k_ability3: False,
	k_debug_weaponup: False,
	k_boss: False,
}

#mouse
lmb_down = False
rmb_down = False


