import pygame
import Pickup
from Constants import *
from Controls import *


class HealthPickup(Pickup.Pickup):
    def __init__(self, pos):
        self.image = images["health"]
        self.rect = pygame.Rect(pos[0],pos[1],30,30)
        
        self.vel = -1
        self.health = 30
        self.loc = [pos[0],pos[1]]
    
    def die(self, game):
        game.pickups.remove(self)
    
    def apply(self, game, player):
        player.health_upgrade(self.health)

    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)
