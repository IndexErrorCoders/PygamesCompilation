import pygame

#####################################################################
class GameOver(pygame.sprite.Sprite):
    """Game Over screen"""
    images = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        newpos = self.rect.move((100, 250))
        self.rect = newpos
