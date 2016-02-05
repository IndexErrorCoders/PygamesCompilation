import pygame
import Bullet, Fireball
from Constants import *
from Controls import *


class FastFire(Fireball.Fireball):
    def __init__(self, location, direction, xvel = 0, yvel = 0):
        Fireball.Fireball.__init__(self,location)
        self.dir = direction
        self.velocity = 6
        self.xvel = xvel
        self.yvel = yvel
        if xvel == 0 and yvel == 0:
            self.xvel = self.velocity
            self.yvel = -self.velocity
            if self.dir == 0:
                self.xvel = 0
            elif self.dir == 1 or self.dir == 3:
                self.xvel = -self.velocity
        self.damage = 20
        self.rect.center = location
        self.loc = [self.rect.left, self.rect.top]
        
    def update(self, game):
        if (self.rect.left < resolution[0]/2 - playarea[0]/2 or self.rect.right >= resolution[0]/2 + playarea[0]/2 or self.rect.top < 0 or self.rect.bottom >= resolution[1]) and not self.dead:
            self.die(game)
            return
        
        if not game.time_stopped:
            self.loc[0] += self.xvel
            self.rect.left = self.loc[0]

            self.loc[1] += self.yvel
            self.rect.top = self.loc[1]

        if self.rect.colliderect(game.player.rect):
            self.die(game)
            if not game.player.rushing:
                game.player.take_damage(game, self.damage)
            return
        for r in game.rocks:
            if self.rect.colliderect(r.rect):
                self.die(game)
                return
        
    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)

