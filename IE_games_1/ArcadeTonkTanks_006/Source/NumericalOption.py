import pygame

#####################################################################
class NumericalOption(pygame.sprite.Sprite):
    """Numerical value which can be changed in the Options screen"""
    def __init__(self,value,x,y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font("freesansbold.ttf", 30)
        self.color = pygame.Color("red")
        self.value = value
        self.lastvalue = -999  # An impossible value for any option
        self.update()
        self.rect = self.image.get_rect().move(x, y)

    def set(self,value):
        self.value = value
    

    def update(self):
        if self.value != self.lastvalue:
            self.lastvalue = self.value
            msg =  str(self.value)
            self.image = self.font.render(msg, 0, self.color)
