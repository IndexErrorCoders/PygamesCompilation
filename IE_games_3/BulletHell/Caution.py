import pygame, random
from Constants import *
from Controls import *
import Enemy

class Caution(Enemy.Enemy):
    def __init__(self,pos, group):
        Enemy.Enemy.__init__(self, group)
        self.rect = pygame.Rect(pos[0],pos[1],50,50)
        self.image = images["caution"]
        self.health = 99999
        self.group = group
        self.life_time = 300
        self.age = 0
        self.melee = 0
        self.draw_time = 60
        
        self.loc = [pos[0], pos[1]]
        
    def die(self,game):
        game.enemies.remove(self)
        
    def update(self,game):
    
        self.draw_time -=1
        if self.draw_time == 0:
            self.draw_time +=60
        
        self.age += 1
        if self.age == self.life_time:
            self.die(game)
            
        self.loc[0] = 490
        self.loc[1] = 700
       
        
    def draw(self, camsurf):
        if (self.draw_time < 30):
            pass
        else:
            camsurf.blit(self.image, self.loc)