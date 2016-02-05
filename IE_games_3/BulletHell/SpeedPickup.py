import pygame
import Pickup
from Constants import *
from Controls import *


class SpeedPickup(Pickup.Pickup):
    def __init__(self, pos):
        self.image = images["speed_pickup"]
        self.rect = pygame.Rect(pos[0],pos[1],30,30)
        
        self.vel = -1
        self.speed = 1
        self.loc = [pos[0],pos[1]]
    
    def die(self, game):
        game.pickups.remove(self)
    
    def apply(self, game, player):
        player.speed_up(game, self.speed)

    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)
