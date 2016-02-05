import pygame
from Source import GameData
from Source import StringOption
from Source import NumericalOption

#####################################################################
class Options(pygame.sprite.Sprite):
    """Options screen"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        newpos = self.rect.move((60, 100))
        self.rect = newpos
        self.maze = StringOption(GameData.battleground[GameData.battlegroundnr].name,238,116)
        #self.background = StringOption("Background.jpg",377,195)
        self.gear_delay = NumericalOption(GameData.gearcooldown,305,254)
        self.max_gun_temp = NumericalOption(GameData.maxbullets,600,317)
        self.bullet_loading_time = NumericalOption(GameData.bulletloadtime,456,369)
        self.bullet_speed = NumericalOption(GameData.bulletspeed,337,425)
        self.trigger_happiness = NumericalOption(GameData.triggerhappiness,476,480)

    def update(self):
        self.maze.set(GameData.battleground[GameData.battlegroundnr].name)
        self.gear_delay.set(GameData.gearcooldown)
        self.max_gun_temp.set(GameData.maxbullets)
        self.bullet_loading_time.set(GameData.bulletloadtime)
        self.bullet_speed.set(GameData.bulletspeed)
        self.trigger_happiness.set(GameData.triggerhappiness)
