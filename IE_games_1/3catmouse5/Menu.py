import pygame, math, sys, os, random

class Menu(object):
	def __init__(self, id, items, nodes, f, location, dy, color, backrect=0, color2=0):
		self.id = id
		self.items = items
		self.length = len(items)
		self.nodes = nodes
		self.font = f
		self.loc = location
		self.dy = dy + f.size(items[0])[1]
		self.color = color
		self.color2 = color2
		if backrect:
			self.backrect = pygame.image.load(os.path.join("images", "backrect.png")).convert_alpha()
		else:
			self.backrect = 0
		self.highlight = 0

		self.width = 0
		self.widths = []
		for i, item in enumerate(items):
			self.widths.append(f.size(item)[0])
			if f.size(item)[0] > self.width:
				self.width = f.size(item)[0]
				bigwidth = i

		self.surfs = []
		self.rects = []

		x = location[0]
		y = location[1]
		for item in items:
			surf = f.render(item, 1, color)
			rect = pygame.Rect(x, y, self.widths[bigwidth], f.size(item)[1])
			self.surfs.append(surf)
			self.rects.append(rect)
			y += self.dy

	def checkmouse(self, point):
		for x, rect in enumerate(self.rects):
			if rect.collidepoint(point):
				self.highlight = x + 1
				if self.color2:
					self.update()
				return True
			elif self.color2:
				self.update()

	def movehighlight(self, x):
		self.highlight += x
		if self.highlight == 0:
			self.highlight = self.length
		elif self.highlight == -1 or self.highlight > self.length:
			self.highlight = 1
		if self.color2:
			self.update()

	def update(self):
		self.surfs = []
		for i, item in enumerate(self.items):
			if i == self.highlight - 1:
				surf = self.font.render(item, 1, self.color2)
			else:
				surf = self.font.render(item, 1, self.color)
			self.surfs.append(surf)

	def draw(self, screen):
		if self.highlight and self.backrect:
			screen.blit(self.backrect, ((self.loc[0] - 5), (self.loc[1] + (self.highlight - 1) * self.dy - 5)))
		for y, surf in enumerate(self.surfs):
			screen.blit(surf, ((self.loc[0] + (self.width - self.widths[y]) / 2), (self.loc[1] + y * self.dy)))