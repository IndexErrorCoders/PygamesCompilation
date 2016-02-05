import pygame
from Controls import *
from Constants import *


#possible issues with needing to reset next_selection? do so in Main?
#can probably fix in update() by setting activemenu to next_selection

#think about multiple menus available at once (size, res, loc for each menu)
#think about how level editor works


def getstuff():
	"""Gets loaded images, sound and other."""
	global fullscreen, PRINT_FPS


class MenuHandler(object):
	"""Handles all menu object interactions."""
	def __init__(self):
		"""Initializes the object."""
		self.activemenu = 0
		self.next_selection = 0
		self.mode = 0
		self.chapter = 0
		self.level = 0

	def handleevent(self, event):
		"""Interprets the given event."""
		if event.type == pygame.MOUSEMOTION:
			menus[self.activemenu].checkmouse(event.pos)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			menus[self.activemenu].checkmouse(event.pos)
		elif event.type == pygame.MOUSEBUTTONUP:
			if menus[self.activemenu].checkmouse(event.pos):
				if menus[self.activemenu].highlight != 0:
					self.next_selection = menus[self.activemenu].nodes[menus[self.activemenu].highlight-1]
		elif event.type == pygame.KEYDOWN:
			if event.key not in controls:
				return
			controls[event.key] = True
			if event.key == k_quit:
				self.next_selection = menus[self.activemenu].nodes[-1]
			elif event.key == k_pause:
				if self.activemenu == PAUSE_GAME:
					self.next_selection = START_GAME
					menus[self.activemenu].highlight = 1
			elif event.key == k_up:
				menus[self.activemenu].movehighlight(-1)
			elif event.key == k_down:
				menus[self.activemenu].movehighlight(1)
			elif event.key == k_up2:
				menus[self.activemenu].movehighlight(-1)
			elif event.key == k_down2:
				menus[self.activemenu].movehighlight(1)
			elif event.key == k_action1 or event.key == k_action2:
				if menus[self.activemenu].highlight != 0:
					self.next_selection = menus[self.activemenu].nodes[menus[self.activemenu].highlight-1]
		elif event.type == pygame.KEYUP:
			if event.key not in controls:
				return
			controls[event.key] = False

	def update(self, game):
		"""Special menu logic that takes place (such as changing game options)."""
		if self.next_selection != self.activemenu:
			if self.next_selection == QUIT or self.next_selection == RESET_GAME:
				menus[self.activemenu].highlight = 1

			menus[self.activemenu].update()

			if self.next_selection == 0:
				if game.pause:
					self.next_selection = PAUSE_GAME

			if menus[self.activemenu].highlight == len(menus[self.activemenu].nodes):
				menus[self.activemenu].highlight = 1

			if self.next_selection in menus:
				menus[self.activemenu].update()
				self.activemenu = self.next_selection

	def draw(self, surf):
		"""Draw the active menu and any extra objects."""

		if not menus[self.activemenu].is_intro:
			back = scroll_small #pygame.Surface((400,400))#scroll image
		else:
			back = scroll_side
		
		surf.blit(back, (resolution[0] / 2 - back.get_width() / 2, resolution[1] / 2 - back.get_height() / 2))

		menus[self.activemenu].draw(surf)
