import pygame, random
import Bullet
from Constants import *
from Controls import *


class Fireball(Bullet.Bullet):
    def __init__(self, location):
        Bullet.Bullet.__init__(self,location)
        self.frame = random.randint(0,2)
        self.image = images["fireball_sheet"][0]
        self.rect = pygame.Rect(100,100,11,26)
        #self.image = pygame.Surface((10,10))
        #self.rect = pygame.Rect(100,100,8,8)
        #self.image.fill((255,0,0))
        self.velocity = 3.5
        self.damage = 20
        self.rect.center = location
        self.loc = [self.rect.left, self.rect.top]
        
    def update(self, game):
        if (self.rect.left < resolution[0]/2 - playarea[0]/2 or self.rect.right >= resolution[0]/2 + playarea[0]/2 or self.rect.top < 0 or self.rect.bottom >= resolution[1]) and not self.dead:
            self.die(game)
            return
        
        if not game.time_stopped:
            # Change the sprite
            self.frame += 1
            if self.frame > 38:
                self.frame = 0
            
            self.loc[1] -= self.velocity+game.speed/2
            self.rect.left = self.loc[0]
            self.rect.top = self.loc[1]
        
        if self.rect.colliderect(game.player.rect):
            self.die(game)
            if not game.player.rushing:
                game.player.take_damage(game, self.damage)
        
        for r in game.rocks:
            if self.rect.colliderect(r.rect):
                self.die(game)
                break
        
    def draw(self, camsurf):
        camsurf.blit(images["fireball_sheet"][self.frame/13], self.loc)

