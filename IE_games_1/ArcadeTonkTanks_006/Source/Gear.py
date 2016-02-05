import pygame

############################################################
class Gear(pygame.sprite.Sprite):
    """on-screen gear indicator"""
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[2]
        self.rect = self.image.get_rect()
        newpos = self.rect.move((880, 640))
        self.rect = newpos
        self.temperature = 0
        self.update

    def update(self):
        self.image = self.images[self.gear + 2]
