import pygame

#####################################################################
class StringOption(pygame.sprite.Sprite):
    """Text value which can be changed from the Options screen"""
    def __init__(self,value,x,y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font("freesansbold.ttf", 30)
        self.color = pygame.Color("red")
        self.value = value
        self.lastvalue = ""
        self.update()
        self.rect = self.image.get_rect().move(x, y)

    def set(self,value):
        self.value = value
    

    def update(self):
        if self.value != self.lastvalue:
            self.lastvalue = self.value
            msg =  self.value
            self.image = self.font.render(msg, 0, self.color)
