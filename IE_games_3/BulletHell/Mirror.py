import pygame
from Constants import *
from Controls import *
import Enemy

class Mirror(Enemy.Enemy):
    def __init__(self, pos, group):
        Enemy.Enemy.__init__(self, group)
        self.image = images["mirror"]#pygame.Surface((120,55))
        #self.image.fill((255,255,255))
        self.rect = pygame.Rect(pos[0],pos[1],120,55)
        
        self.state = "Mirror"
        self.group = group
        self.mgroup = None
        self.vel = 4
        self.health = 1
        self.melee = 20
        self.points = 1
        self.dying = False
        self.damaged = 0
        self.breaking = 0
        
        self.loc = [pos[0], pos[1]]
        
    def die(self, game):
        game.enemies.remove(self)
    
    def break_mirror(self):
        self.breaking = 1
    
    def update(self, game):
        
        if not game.time_stopped:
            self.loc[0] += self.movex*self.vel
            self.loc[1] += self.movey*self.vel
            self.rect.left = self.loc[0]
            self.rect.top = self.loc[1]
            
            #x collisions
            if self.rect.left < resolution[0]/2 - playarea[0]/2:
                self.rect.left = resolution[0]/2 - playarea[0]/2
                self.movex = -self.movex
            elif self.rect.right >= resolution[0]/2 + playarea[0]/2:
                self.rect.right = resolution[0]/2 + playarea[0]/2
                self.movex = -self.movex
            if self.rect.top > playarea[1] or self.rect.bottom < 0:
                self.die(game)
            
            self.loc = [self.rect.left, self.rect.top]
    
    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)
