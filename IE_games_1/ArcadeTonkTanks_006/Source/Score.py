import pygame
from Source import GameData
from pygame.locals import *

#####################################################################
class Score(pygame.sprite.Sprite):
    def __init__(self,text,color,x,y):
        """text field displaying the number of kills or deaths of a tank"""
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font("freesansbold.ttf", 20)
        self.font.set_italic(1)
        self.color = Color(color)
        self.score = 0
        self.lastscore = -1
        self.text = text
        self.update()
        self.rect = self.image.get_rect().move(x, y)

    def set_score(self,score):
        self.score = score
    

    def update(self):
        if self.score != self.lastscore:
            self.lastscore = self.score
            msg = self.text % self.score
            self.image = self.font.render(msg, 0, self.color)
