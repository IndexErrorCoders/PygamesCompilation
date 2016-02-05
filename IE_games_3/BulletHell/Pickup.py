import pygame
from Constants import *
from Controls import *


class Pickup(object):
    def __init__(self, pos):
        self.image = pygame.Surface((30,30))
        self.image.fill((255,0,255))
        self.rect = pygame.Rect(pos[0],pos[1],30,30)
        
        self.vel = 1
        self.loc = [pos[0],pos[1]]
    
    def die(self, game):
        game.pickups.remove(self)

    def update(self, game):
        if not game.time_stopped:
            self.loc[1] -= game.speed
            self.rect.top = self.loc[1]
    
            self.loc = [self.rect.left, self.rect.top]
        
        if self.rect.bottom < resolution[1]/2 - playarea[1]/2 or self.rect.top >= resolution[1]/2 + playarea[1]/2:
            self.die(game)

    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)
