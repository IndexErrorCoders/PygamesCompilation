import pygame
import random
import Pickup, HealthPickup, WeaponPickup, SpeedPickup, Group
from Constants import *
from Controls import *

class Enemy(object):
    def __init__(self, group):
        self.image = pygame.Surface((64,64))
        self.image.fill((255,255,255))
        self.rect = pygame.Rect(100,100,64,64)
        
        self.state = None
        self.group = group
        
        self.vel = 3
        self.health = 20
        self.melee = 20
        self.speed_penalty = .5
        self.points = 1
        self.alive = True
        self.dying = 0
        self.damaged = 0
        self.movex = 0
        self.movey = 0
        self.pickups_prob = [('health',0.15), ('speed',0.15), ('none',0.85)]
        
        self.loc = [100,100]
    
    def take_damage(self, game, num, rushed=False, light=False):
        self.health -= num
        if self.health <= 0:
            self.die(game, True)
        else:
            self.damaged = True
    
    def die(self, game, killed):
        game.enemies.remove(self)
        if killed:
            game.score += self.points
    
    def begin_dying(self, game):
        if self.dying == 0:
            if not self.group == "none":
                game.groups[self.group].num_enemies -=1
                if game.groups[self.group].num_enemies ==0:
                    self.spawnpickup(game)
                    del game.groups[self.group]
            
    def spawnpickup(self, game):
        if game.groups[self.group].drop == "weapon":
            game.pickups.append(WeaponPickup.WeaponPickup(self.rect.center))
        elif game.groups[self.group].drop == "health":
            game.pickups.append(HealthPickup.HealthPickup(self.rect.center))
        elif game.groups[self.group].drop == "speed":
            game.pickups.append(SpeedPickup.SpeedPickup(self.rect.center))
        else:
            pass
           
            
    def offscreen_kill(self,game):
        game.enemies.remove(self)

    def update(self, game):
        pass

    def draw(self, camsurf):
        camsurf.blit(self.image, self.loc)
