import math
import pygame
from Source import GameData

#####################################################################
class Bullet(pygame.sprite.Sprite):
    """A bullet in the same colour as the tank which shot it"""
    images = []

    def __init__(self,colour,x,y,angle):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[colour]
        self.rect = self.image.get_rect()
        newpos = self.rect.move((x, y))
        self.rect = newpos
        self.colour = colour
        self.angle = angle

    def update(self):
        # xoffset & yoffset as in $tring$ nr.1, 1984, page 13
        xoffset = math.cos(self.angle * math.pi / 180) * GameData.bulletspeed
        yoffset = - math.sin(self.angle * math.pi / 180) * GameData.bulletspeed
        newpos = self.rect.move((xoffset, yoffset))
        self.rect = newpos
        self.x = self.rect.left
        self.y = self.rect.top
