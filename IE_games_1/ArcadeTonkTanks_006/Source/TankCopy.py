import pygame
import random
from Source import GameData

#####################################################################
# TankCopy for display on scoreboard
class TankCopy(pygame.sprite.Sprite):
    """The tank as displayed on the score board"""

    images = []

    def __init__(self,colour):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[colour * 6]
        self.rect = self.image.get_rect()
        newpos = self.rect.move((815,200 + colour * 75))
        self.rect = newpos
        self.colour = colour
        self.angle = int(random.random()*360)
        self.direction = int(random.random()*2)
        if self.direction == 0:
            self.direction = -1
        
    def update(self):
        self.angle = self.angle + (int(GameData.angle / 2) * self.direction)
        if self.angle > 360:
            self.angle = 0
        self.image = self.images[(self.colour * 6) + GameData.animstep ]
        self.original = self.image
        center = self.rect.center
        rotate = pygame.transform.rotate
        self.image = rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=center)
        self.x = self.rect.left
        self.y = self.rect.top
