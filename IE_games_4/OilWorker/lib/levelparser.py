#===================================================
# 
# levelparser.py - a simple library to read game levels stored in .xpm images 
#
# Copyright (C) 2008  Wil Alvarez <wil_alejandro@yahoo.com>
#
# This library is free software; you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation; either version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License 
# for more details.
#
# You should have received a copy of the GNU General Public License along with 
# this library (see COPYING); if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#===================================================

import pygame, os, sys

class LevelParser:
	def __init__(self, filename='maxlvl'):
		self.filename=filename
		if (os.path.isfile(self.filename)==False):
			self.saveMaxLevel(1)
		
	def parseLevel(self, level):
		levelarray=[]
		img = self.__loadLevel(str(level)+'.xpm')
		x, y = img.get_size()
		
		for i in range(y):
			line=[]
			for j in range(x):
				p=img.get_at((j,i))
				line.append(p)
			levelarray.append(line)
		
		return levelarray
		
	def readMaxLevel(self):
		fd=open(self.filename,'r')
		maxlevel = fd.read()
		fd.close()
		
		return int(maxlevel[:-1])
		
	def saveMaxLevel(self, maxlevel):
		if (os.path.isfile(self.filename)==False):
			fd=open(self.filename,'w+')
			fd.close()
		else:
			current=self.readMaxLevel()
			if current > maxlevel: return
		
		fd=open(self.filename,'w+')
		fd.write(str(maxlevel)+'\0')
		fd.close()
		
	def __loadLevel(self, level):
		""" Load image levels .xpm"""
		fullname = os.path.join(sys.path[0], 'data', 'levels', level)
		try:
			image = pygame.image.load(fullname)
			if image.get_alpha() is None:
				image = image.convert()
			else:
				image = image.convert_alpha()
		except pygame.error, message:
			print 'Cannot load image:', fullname
			raise SystemExit, message
		return image