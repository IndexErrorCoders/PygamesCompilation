import pygame
from Constants import *
from Controls import *
import Enemy, Demon, Mirror

class MirrorGroup(Enemy.Enemy):
    def __init__(self, pos, group):
        #self.image = pygame.Surface((64,64))
        #self.image.fill((255,255,255))
        self.rect = pygame.Rect(pos[0],pos[1],64,64)
        
        self.state = None
        
        self.health = 1
        self.melee = 20
        self.points = 1
        self.pickups_prob = [('none',0.999)]
        self.group = group
        self.vel = 0 #deprecated
        self.velx = 1
        self.vely = 1.5
        self.melee = 0
        self.movex = 0
        self.movey = 0
        self.breaking = 0
        self.accel = 1
        self.mirror = None
        self.left_demon = None
        self.right_demon = None
        self.mirror_falling = False
        self.mirror_breaking = False
        
        self.loc = [pos[0], pos[1]]
    
    def reposition_children(self):
        # Set positions relative to MirrorGroup object
        if self.mirror != None:
            self.mirror.loc = self.loc
            self.mirror.rect.top = self.rect.top
            self.mirror.rect.left = self.rect.left
            self.mirror.vel = self.vel
        
            if self.left_demon != None:
                self.left_demon.reposition([self.mirror.rect.left-25, self.mirror.rect.top-50])
                self.mirror.vel = self.vel
        
            if self.right_demon != None:
                self.right_demon.reposition([self.mirror.rect.right-25, self.mirror.rect.top-50])
                self.mirror.vel = self.vel
        else:
            if self.left_demon != None:
                self.left_demon.reposition([self.rect.left-56, self.rect.top-50])
            if self.right_demon != None:
                self.right_demon.reposition([self.rect.right+56, self.rect.top-50])
    
    def attach(self, mirror, left, right):
        self.mirror = mirror
        self.left_demon = left
        self.right_demon = right
        mirror.mgroup = self
        left.mgroup = self
        right.mgroup = self
    
    def take_damage(self, game, num):
        pass
    
    def die(self, game):
        self.movey = 1
        self.vel = 3
    
    def break_mirror(self):
        self.breaking = 1
        self.mirror_breaking = True
    
    def mirror_fall(self, game):
        self.movey = 1
        self.mirror_falling = True
        self.vely *= 4 + (game.speed/5)
    
    def update(self, game):
        if self.mirror != None:
            self.no_mirror = True
            for e in game.enemies:
                if e is self.mirror:
                    self.no_mirror = False
                    break
            if self.no_mirror:
                self.mirror = None
                  
        if self.left_demon != None and self.left_demon.dying:
            self.left_demon = None
        if self.right_demon != None and self.right_demon.dying:
            self.right_demon = None
        
        if (self.left_demon == None and self.right_demon == None) and self.mirror != None and not self.mirror_falling:
            self.mirror_fall(game)
        
        
        if not game.time_stopped:
            if self.mirror_falling:
                self.movex = 0
                self.movey = 1
                
            elif self.mirror != None and not self.mirror_falling:

                if game.player.rect.centerx > self.rect.centerx:
                    self.movex = 1
                elif game.player.rect.centerx < self.rect.centerx:
                    self.movex = -1
                else:
                    self.movex = 0
                
                """
                if game.player.rect.centery > self.rect.centery:
                    self.movey = 1
                """
                if self.mirror.rect.top <= 2:
                    self.movey = -1
                if game.player.rect.centery < self.rect.centery:
                    self.movey = -1
                    
                #else:
                    #self.movey = 0
            elif self.mirror_breaking:
                if self.left_demon != None:
                    self.left_demon.movex = -0.5
                    self.left_demon.movey = -3
                    self.left_demon.vel = 2.5
                if self.right_demon != None:
                    self.right_demon.movex = 0.5
                    self.right_demon.movey = -3
                    self.right_demon.vel = 2.5
            else:
                self.movey = 1 
                self.vely = -3
            
            self.loc[0] += self.movex*self.velx
            self.loc[1] += self.movey*self.vely - (game.speed/2)
            self.rect.left = self.loc[0]
            self.rect.top = self.loc[1]
            
            #x collisions
            if self.rect.left < resolution[0]/2 - playarea[0]/2:
                self.rect.left = resolution[0]/2 - playarea[0]/2
                self.movex = -self.movex
            elif self.rect.right >= resolution[0]/2 + playarea[0]/2:
                self.rect.right = resolution[0]/2 + playarea[0]/2
                self.movex = -self.movex
                
            self.loc = [self.rect.left, self.rect.top]
           
            if not self.mirror_breaking:
                self.reposition_children()
    
    def draw(self, camsurf):
        pass#camsurf.blit(self.image, self.loc)
