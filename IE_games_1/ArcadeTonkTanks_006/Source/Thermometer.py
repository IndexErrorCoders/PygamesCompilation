import pygame
from Source import GameData


#####################################################################
class Thermometer(pygame.sprite.Sprite):
    """The maximum gun temperature is actually the number of bullets a tank has on-screen"""
    images = []
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        newpos = self.rect.move((825, 630))
        self.rect = newpos
        self.temperature = 0
        self.update

    def update(self):
        self.image = self.images[int(self.temperature * 5 / GameData.maxbullets)]
