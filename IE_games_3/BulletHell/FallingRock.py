import pygame
import Bullet, Enemy
from Constants import *
from Controls import *


class FallingRock(Enemy.Enemy):
    def __init__(self, x):
        Enemy.Enemy.__init__(self, "none")
        self.image = images["fallingrock"]
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = 1 - self.rect.height

        self.velocity = 4
        self.xvel = 0
        self.yvel = 8

        self.damage = 10
        self.loc = [self.rect.left, self.rect.top]
        
    def update(self, game):
        if self.rect.bottom >= resolution[1]:
            self.die(game, False)
            return
        
        if not game.time_stopped:
            self.loc[0] += self.xvel
            self.rect.left = self.loc[0]

            self.loc[1] += self.yvel
            self.rect.top = self.loc[1]

        if self.rect.colliderect(game.player.rect):
            self.die(game, False)
            if not game.player.rushing:
                game.player.take_damage(game, self.damage)
            return
        for r in game.rocks:
            if self.rect.colliderect(r.rect):
                self.die(game, False)
                return
        
    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)

