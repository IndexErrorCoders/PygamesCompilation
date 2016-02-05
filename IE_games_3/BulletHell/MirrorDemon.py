import pygame
import Enemy, Demon
import Bullet, Fireball
from Constants import *
from Controls import *

class MirrorDemon(Demon.Demon):
    def __init__(self, pos, group, side):
        Demon.Demon.__init__(self, pos, group, str(0))
        self.frame = 0
        if side=="left":
            self.image = images["mirror_demon_flipped"]
        else:
            self.image = images["mirror_demon"]
        #self.image.fill((255,255,255))
        self.rect = pygame.Rect(pos[0],pos[1],64,64)
        
        self.state = None
        
        self.vel = 0
        self.movex = 0
        self.movey = 0
        self.health = 10
        self.melee = 20
        self.points = 1
        self.fire_rate = 30
        self.fired = 0
        
        self.loc = [pos[0], pos[1]]
    
    def reposition(self, location):
        self.loc = [location[0], location[1]]
        self.rect.left = location[0]
        self.rect.top = location[1]
    
    def update(self, game):
        if not game.time_stopped:

            # Change the sprite
            if self.dying > 0:
                self.frame = int((float(5-float(self.dying)/8))%5)
                if self.dying < 8 and self.frame == 0:
                    self.dying = 0
                    self.frame = 4
                else:
                    self.dying -= 1
            else:
                self.frame += 1
                if self.frame > 47:
                    self.frame = 0
            
            if self.dying <= 0 and not self.alive:
                self.die(game, True)
                return True
            
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
    
            self.loc = [self.rect.left, self.rect.top]
    
    """
    def draw(self, camsurf):
        camsurf.blit(self.image[(self.frame/8) % len(self.image)], self.rect)
    """
