import pygame
import random
from Source import GameData

#####################################################################
# You may regcognise the explosion from the Pygame tutorials
class Explosion(pygame.sprite.Sprite):
    """Boom!"""
    # defaultlife = 21
    animcycle = 44
    images = []
    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.imageset = int(random.random()*3)
        if self.imageset == 0:
            self.image = self.images0[0]
        elif self.imageset == 1:
            self.image = self.images1[0]
        else:
            self.image = self.images2[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = 0

    def update(self):
        self.life = self.life + 1
        if self.imageset == 0:
            self.image = self.images0[self.life]
        elif self.imageset == 1:
            self.image = self.images1[self.life]
        else:
            self.image = self.images2[self.life]
        if self.life == self.animcycle:
            if (GameData.gamestate == "fighting") or (GameData.gamestate == "splash"):
                self.kill()
            else:
                self.life = 0
                self.imageset = int(random.random()*3)
