import pygame
from Source import GameData

#####################################################################
class Logo(pygame.sprite.Sprite):
    """animated Arcade Tonk tanks logo"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        newpos = self.rect.move((805, 10))
        self.rect = newpos

    def update(self):
        self.image = self.images[int(GameData.animstep/2)]
