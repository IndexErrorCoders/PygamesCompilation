import pygame

#backrect not tested

def getstuff(imgs, fnts):
	"""Gets loaded images, sound and other."""
	global images, fonts
	images = imgs
	fonts = fnts


class Menu(object):
	"""A standard menu."""
	def __init__(self, items, nodes, f, location, align, dy, color, color2=None, backrect=False):
		"""Initializes a Menu object and preprocesses some text rendering."""
		self.items = items
		self.length = len(items)
		self.nodes = nodes
		self.font = fonts[f]
		self.loc = location
		self.dy = dy + self.font.size(items[0])[1]
		self.color = color
		self.color2 = color2
		self.backrect = None
		if backrect:
			self.backrect = images[0]
		self.highlight = 1

		self.width = 0
		self.widths = []
		for i, item in enumerate(items):
			self.widths.append(self.font.size(item)[0])
			if self.font.size(item)[0] > self.width:
				self.width = self.font.size(item)[0]
				bigwidth = i

		self.surfs = []
		self.rects = []
		self.xlocs = []

		x = location[0]
		y = location[1]
		for i, item in enumerate(self.items):
			xloc = x + align * ((self.width - self.widths[i]) / 2)
			rect = pygame.Rect(x, y, self.widths[bigwidth], self.font.size(item)[1])
			self.rects.append(rect)
			self.xlocs.append(xloc)
			y += self.dy
		
		# <EVAN>
		self.is_intro = False
		# </EVAN>
		
		self.update()

	def checkmouse(self, point):
		"""Updates the menu selection based on the mouse position."""
		for x, rect in enumerate(self.rects):
			if rect.collidepoint(point):
				self.highlight = x + 1
				if self.color2 is not None:
					self.update()
				return True
	
	# <EVAN>
	def setasintro(self):
		"""Sets the menu as an introductory menu (i.e. shows up after the title screen but before gameplay. Added by Evan."""
		self.is_intro = True
	# </EVAN>

	def movehighlight(self, x):
		"""Changes the highlighted value (after pressing up or down)."""
		self.highlight += x
		if self.highlight == 0:
			self.highlight = self.length
		elif self.highlight == -1 or self.highlight > self.length:
			self.highlight = 1
		if self.color2 is not None:
			self.update()

	def update(self):
		"""Render the text. Called when the highlighted text changes."""
		self.surfs = []
		for i, item in enumerate(self.items):
			if i == self.highlight - 1:
				surf = self.font.render(item, 0, self.color2)
			else:
				surf = self.font.render(item, 0, self.color)
			self.surfs.append(surf)

	def draw(self, camsurf):
		"""Draws the text surfaces on the given camera surface."""
		if self.highlight and self.backrect is not None:
			camsurf.blit(self.backrect, ((self.loc[0] - (self.backrect.get_width() - self.width) / 2), (self.loc[1] + (self.highlight - 1) * self.dy - (self.backrect.get_width() - self.height) / 2)))
		for y, surf in enumerate(self.surfs):
			camsurf.blit(surf, (self.xlocs[y], (self.loc[1] + y * self.dy)))
