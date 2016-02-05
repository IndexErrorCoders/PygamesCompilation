import pygame
from Constants import *

"""
sfx:
none

musics:
none
"""

class Sound(object):
	def __init__(self):
		self.noaudio = True
		self.mute = True
		self.sounds = None
		self.currentmusic = None

	def loadsounds(self):
		if not self.noaudio and self.sounds is None:
			self.sounds = dict([(x, pygame.mixer.Sound(sfx[x])) for x in sfx])

	def unmute(self):
		if self.mute:
			if self.noaudio:
				try:
					pygame.mixer.init()
					if self.sounds:
						self.sounds = dict([(x, pygame.mixer.Sound(sfx[x])) for x in sfx])
					self.mute = False
					# if musics:
						# self.startmusic(self.currentmusic)
					self.noaudio = False
				except:
					self.mute = True
			else:
				self.mute = False
				self.startmusic(self.currentmusic)
		else:
			self.stopmusic()
			self.mute = True

	def play(self, id):
		if not self.mute:
			self.sounds[id].play()

	def startmusic(self, id):
		self.currentmusic = id
		if not self.mute:
			pygame.mixer.music.load(musics[id])
			pygame.mixer.music.play(-1)

	def stopmusic(self):
		if not self.mute:
			pygame.mixer.music.stop()

	def pausemusic(self):
		if not self.mute:
			pygame.mixer.music.pause()

	def unpausemusic(self):
		if not self.mute:
			pygame.mixer.music.unpause()
