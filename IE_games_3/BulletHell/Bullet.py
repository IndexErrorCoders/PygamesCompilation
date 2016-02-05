import pygame, random
from Constants import *
from Controls import *



class Bullet(object):
    def __init__(self, location):
        self.image = pygame.Surface((8,8))
        self.rect = pygame.Rect(100,100,8,8)
        self.image.fill((255,255,0))
        self.velocity = 8
        self.dead = False
        self.rect.center = location
        self.loc = [self.rect.left, self.rect.top]
        
    def update(self, game):
        pass

    def die(self, game):
        game.bullets.remove(self)
        self.dead = True
        
    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)

