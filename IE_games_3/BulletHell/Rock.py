import pygame
import random
from Constants import *
from Controls import *

class Rock(object):
    def __init__(self, location, side, size):
        if size==3:
            self.image = images["rock"][2]
        elif size==2:
            self.image = images["rock"][1]
        else:
            self.image = images["rock"][0]
            
        self.rect = self.image.get_rect()
        
        if side=="left":
            location[0] = resolution[0]/2 - playarea[0]/2
        elif side=="right":
            location[0] = (resolution[0]/2 + playarea[0]/2) - self.rect.width
            self.image = pygame.transform.flip(self.image, True, False)
        
        #self.image = pygame.Surface((70,30))
        #self.image.fill((0,0,0))
        #self.rect = pygame.Rect(location[0],location[1],70,30)
        
        self.size = 1
        
        self.damage = 10
        self.speed_penalty = 1
        
        self.vel = 1
        self.loc = [location[0],location[1]]
        self.rect.left = location[0]
        self.rect.top = location[1]
    
    def die(self, game):
        game.rocks.remove(self)
    

    def update(self, game):
        if not game.time_stopped and not game.boss_active:
            self.loc[1] -= game.speed*WALL_SPEED
            self.rect.top = self.loc[1]
    
        if self.rect.bottom < 0:
            self.die(game)

    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)
