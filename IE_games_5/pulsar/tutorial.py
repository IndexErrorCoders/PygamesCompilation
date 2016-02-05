from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform
import os

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image #, image.get_rect()

class Tutorial(PygameHelper):
    def __init__(self):
        self.w, self.h = 800, 600
        self.selected = 0
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        self.backgrounds = ['tut_background.png', 'tut_background2.png', 'tut_background3.png']
        self.background = load_image(self.backgrounds[self.selected])
    def update(self):
        pass
    
    def keyDown(self, key):
        if key == K_SPACE:
            if self.selected < 2:
                self.selected += 1
            else:
                self.running = False
    
    def keyUp(self, key):
        pass
        
    def mouseUp(self, button, pos):
        pass
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
    def draw(self):
        self.background = load_image(self.backgrounds[self.selected])
        self.screen.blit(self.background, (0, 0))