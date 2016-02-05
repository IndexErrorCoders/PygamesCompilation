#! /usr/bin/env python

#-------------------------------
#util.py - part of the BrainLibs pygame package
#Started Jan 20, 2008
#Copyright (C) 2008, BrainLabs
#-------------------------------
#Contributors:
#PyMike93 (pymike93@gmail.com)
#Andy Sommerville (aksommerville@gmail.com)
#Wil Alvarez (wil_alejandro@yahoo.com)
#-------------------------------

import os, sys
import zlib, base64

import pygame
from pygame.locals import *
#import brainlibs #might be needed pylzma.pyd can be included with brainlibs. a pylzma.so file will also have to be compiled for linux distros
import __main__


#####################################################################
#$$$$$$$$$$$$$$$$$$$$$$$$ Image compression $$$$$$$$$$$$$$$$$$$$$$$$#
#####################################################################


def compressImage(surface, format , compressionmethod = "zlib" ):
        """Compresses a pygame surface. To decompress use the
        decompressImage function."""
        string = pygame.image.tostring(surface, format)
        if compressionmethod == "zlib":
                compressed = base64.encodestring(zlib.compress(string))
        else:
                compressed = base64.encodestring(brainlibs.pylzma.compress(string))
        return compressed


def decompressImage(image_string, size, format , compressionmethod = "zlib"):
        """Decompresses an image string that was compressed
        with the compressImage function."""
        if compressionmethod == "zlib":
                decompressed = zlib.decompress(base64.decodestring(image_string))
        else:
                decompressed = brainlibs.pylzma.decompress(base64.decodestring(image_string))
        surface = pygame.image.fromstring(decompressed, size, format)
        return surface


#####################################################################
#$$$$$$$$$$$$$$$$$$$$$$$$$$ Code Executor $$$$$$$$$$$$$$$$$$$$$$$$$$#
#####################################################################


def openCode(file):
      """Opens a file and returns its string and total dir."""
      f = open(file, "rU")
      filepath = os.path.abspath(file)
      code = f.read()
      f.close()
      return code, filepath


def compileCode(string, filepath):
      """Compiles a string of code without making a .pyc file."""
      return compile(string, filepath, "exec")


def runCompiledCode(compiled_code):
      """Runs compiled code."""
      locals = __main__.__dict__
      exec compiled_code in locals


def runCode(file):
      """Opens a file, compiles it, and runs it, without making .pyc files."""
      code, filepath = openCode(file)
      compiled_code = compileCode(code, filepath)
      runCompiledCode(compiled_code)
      
#####################################################################
#$$$$$$$$$$$$$$$$$$$$$$$$$$ Miscelaneous $$$$$$$$$$$$$$$$$$$$$$$$$$#
#####################################################################

def loadPng(name):
	""" Load image and return image object"""
	fullname = os.path.join(sys.path[0], 'data', 'images', name)
	#fullname = name
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

def loadText(text, size, color, font=None, bold=False):
	'''
	This can be used to define ours own text fonts
	'''
	#font_path=os.path.join(sys.path[0],'brainlibs','brainlibs')
	font_path=sys.path[0]
	
	if font=='engex': font=os.path.join(font_path,'data','fonts','engeexpa.ttf')
	elif font=='forgotte': font=os.path.join(font_path,'data','fonts','forgotte.ttf')
	elif font=='sans': font=os.path.join(font_path,'data','fonts','FreeSans.ttf')
	elif font=='vera': font=os.path.join(font_path, 'data','fonts','Vera.ttf')
	elif font=='zero': font=os.path.join(font_path,'data', 'fonts','zerothre.ttf')
	elif font=='modernab': font=os.path.join(font_path,'data','fonts','MgOpenModernaBold.ttf')
	elif font=='featured': font=os.path.join(font_path,'data','fonts','featuredItem.ttf')
	elif font=='ltypewriter': font=os.path.join(font_path,'data','fonts','LucidaTypewriterBold.ttf')
	elif font == None: font=os.path.join(font_path, 'data','fonts','Vera.ttf')
	
	ffont=pygame.font.Font(font, size)
	if(bold==True): ffont.set_bold(1)
		
	return ffont.render(text, 0, color)
	
def loadSound(name):
	class NoneSound:
		def play(self): pass
	
	if not pygame.mixer:
		return NoneSound()
		
	fullname = os.path.join(sys.path[0], 'data', 'sounds', name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'Cannot load sound:', fullname
		raise SystemExit, message
	
	return sound
	
def colorDiff(color, add):
	r=color[0]+add[0]
	g=color[1]+add[1]
	b=color[2]+add[2]

	if (r > 255): r=255
	elif (r < 0): r=0
	
	if (g > 255): g=255
	elif (g < 0): g=0
	
	if (b > 255): b=255
	elif (b < 0): b=0
	
	return (r,g,b)
	
class Message(pygame.sprite.Sprite):
	def __init__(self, pos, text, color, rate):
		pygame.sprite.Sprite.__init__(self)
		
		msg=loadText(text, 10, color, 'vera', True)
		self.image = pygame.Surface(msg.get_size())
		self.image.set_colorkey((0, 0, 0), pygame.locals.RLEACCEL)
		self.image.blit(msg, (0, 0))
		self.rect = self.image.get_rect(center = pos)
		self.trans = 255
		self.rate=rate

	def update(self):
		self.trans -= self.rate
		if self.trans <= 0:
			self.kill()
		self.rect.move_ip(0, -1)
		self.image.set_alpha(self.trans, RLEACCEL)

if __name__ == "__main__":
      print "This is running", os.path.abspath("gui.py")
      runCode("gui.py")
