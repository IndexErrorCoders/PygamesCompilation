from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform

import os

def open_file(name):
    fullname = os.path.join('data', name)
    file = open(fullname, 'r')
    return file

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

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

def load_font(name, size=12):
    fullname = os.path.join('data', name)
    try:
        font = pygame.font.Font(fullname, size)
    except pygame.error, message:
        print 'Cannot load font:', fullname
        raise SystemExit, message
    return font
    
class Highscore(PygameHelper):
    def __init__(self):
        self.w, self.h = 800, 600
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        
        # Load sounds
        pygame.mixer.stop()
        self.music = load_sound('music_endgame.ogg')
        self.music_credits = load_sound('music_credits.ogg')
        self.music.play()
        self.playSound = True
        
        self.background = load_image('score_background.png')
        
        self.font = load_font('adelle.ttf', 24)
        file = open_file('archive.txt')
        list_of_scores = file.readlines()
        list_of_scores.sort(lambda a,b: cmp(float(a.split(' ')[0]), float(b.split(' ')[0])))
        print list_of_scores
        
        self.score1 = self.font.render(list_of_scores[-1], True, (255, 255, 255))
        self.score2 = self.font.render(list_of_scores[-2], True, (255, 255, 255))
        self.score3 = self.font.render(list_of_scores[-3], True, (255, 255, 255))
        self.score4 = self.font.render(list_of_scores[-4], True, (255, 255, 255))
        self.score5 = self.font.render(list_of_scores[-5], True, (255, 255, 255))
        self.score6 = self.font.render(list_of_scores[-6], True, (255, 255, 255))
        self.score7 = self.font.render(list_of_scores[-7], True, (255, 255, 255))
        self.score8 = self.font.render(list_of_scores[-8], True, (255, 255, 255))
        self.score9 = self.font.render(list_of_scores[-9], True, (255, 255, 255))
        self.score10 = self.font.render(list_of_scores[-10], True, (255, 255, 255))
        
        
        print list_of_scores
        
    def update(self):
        if pygame.mixer.get_busy() == False:
            self.music_credits.play(-1)
     
    def keyDown(self, key):
        if key == K_s:
            if self.playSound == True: 
                pygame.mixer.pause()
                self.playSound = False
            elif self.playSound == False:
                pygame.mixer.unpause()
                self.playSound = True
    
    def keyUp(self, key):
        pass
        
    def mouseUp(self, button, pos):
        pass
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.score1, (300, 180))
        self.screen.blit(self.score2, (300, 210))
        self.screen.blit(self.score3, (300, 240))
        self.screen.blit(self.score4, (300, 270))
        self.screen.blit(self.score5, (300, 300))
        self.screen.blit(self.score6, (300, 330))
        self.screen.blit(self.score7, (300, 360))
        self.screen.blit(self.score8, (300, 390))
        self.screen.blit(self.score9, (300, 420))
        self.screen.blit(self.score10, (300, 450))
        