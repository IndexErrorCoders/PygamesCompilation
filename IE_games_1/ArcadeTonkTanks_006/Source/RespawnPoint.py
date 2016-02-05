import pygame
from Source import GameData

#####################################################################
class RespawnPoint(pygame.sprite.Sprite):
    """Place where a tank enters the game at the start or after being killed"""
    
    images = []

    def __init__(self, x, y, angle, visible = True):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        newpos = self.rect.move((x, y))
        self.rect = newpos
        self.angle = angle
        self.visible = visible
        center = self.rect.center
        rotate = pygame.transform.rotate
        self.original = self.image
        self.image = rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=center)
        self.x = self.rect.left
        self.y = self.rect.top

    def update(self):
        if self.visible:
            self.image = self.images[ GameData.animstep ]        
            self.original = self.image
            center = self.rect.center
            rotate = pygame.transform.rotate
            self.original = self.image
            self.image = rotate(self.original, self.angle)
            self.rect = self.image.get_rect(center=center)
            self.x = self.rect.left
            self.y = self.rect.top
        else:
            self.image = GameData.transparant_sprite
            center = self.rect.center
            self.rect = self.image.get_rect(center=center)
            self.x = self.rect.left
            self.y = self.rect.top
