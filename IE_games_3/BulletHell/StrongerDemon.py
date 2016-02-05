import pygame, random
import Enemy
import Bullet, FastFire
from Constants import *
from Controls import *

class StrongerDemon(Enemy.Enemy):
    def __init__(self, pos, group, pattern):
        Enemy.Enemy.__init__(self, group)
        self.image = images["strongerdemon"]
        #self.image.fill((255,255,255))
        self.rect = pygame.Rect(pos[0],pos[1],110,62)
        
        self.state = None
        
        self.frame = 0
        self.vel = 3
        self.movex = 1
        self.movey = 1
        self.health = 11
        self.melee = 20
        self.points = 3
        self.fire_rate = 60
        self.fired = 0
        
        
        self.pattern = pattern 
        self.zig_time = 0
        self.zig_length = 120
        if pattern == "zigzag":
            self.zigging = 1
        else:
            self.zigging = -1
        self.zig_speed = 2
        if self.pattern == "speed":
            self.movex=0
            self.vel=7
            self.movey=1
        if self.pattern == "circle":
            self.vel = 2
            self.movex=0
            self.movey=0
        self.circle_time = 0
        self.circle_count = 0
        self.circle_length = 360
            
 
        
        
        
        
        self.loc = [pos[0], pos[1]]
    
    def begin_dying(self, game):
    	Enemy.Enemy.begin_dying(self, game)
        if self.dying == 0:
            self.dying = 40
            self.alive = False
            self.image = images["demon_death"]
            self.vel = 0
            self.movex = 0
            self.movey = 0
    
    def die(self, game, killed):
        if self.alive:
            self.begin_dying(game)
        else:
            Enemy.Enemy.die(self, game, killed)
            

    def shoot(self, game):
        if self.fired == 0:
            if random.randint(0,5) == 0:
                self.fired += self.fire_rate
                if self.pattern == "single":
                    game.bullets.append(FastFire.FastFire(self.rect.center,0))
                else:    
                    game.bullets.append(FastFire.FastFire(self.rect.center,0))
                    game.bullets.append(FastFire.FastFire(self.rect.center,1))
                    game.bullets.append(FastFire.FastFire(self.rect.center,2))
            
    def update(self, game):
        if not game.time_stopped:
        
            # Change the sprite
            if self.dying > 0:
                self.frame = int((float(5-float(self.dying)/8))%5)
                self.dying -= 1
            else:
	            self.frame += 1
	            if self.frame > 47:
	                self.frame = 0
            
            if self.dying <= 0 and not self.alive:
                self.die(game, True)
                return True
            
            #self.loc[0] += self.movex*self.vel
            self.rect.left = self.loc[0]
            self.loc[1] -= self.movey*self.vel
            self.rect.top = self.loc[1]
    
            #shoot
            if self.fired == 0 and self.pattern != "speed":
                self.shoot(game)
            
            if self.fired > 0:
                self.fired -= 1
                
                
            if self.pattern == "circle":
                if self.circle_count < 2:
                    self.circle_time += 1
                    if self.circle_time == self.circle_length:
                        self.circle_time = 0
                        self.circle_count +=1
                    if self.circle_time < 90:
                        self.movex = -0.5
                        self.movey = 0.5
                    elif self.circle_time > 90 and self.circle_time <180:
                        self.movex = 0.5
                        self.movey = 0.75
                    elif self.circle_time >180 and self.circle_time <270:
                        self.movex = 0.5
                        self.movey = -0.75
                    else:
                        self.movex = -0.5
                        self.movey = -0.5
                    self.loc[0] += self.movex * self.vel
                    self.rect.left = self.loc[0]
                else:
                    self.movex = 0
                    self.movey = 2
            
            elif self.pattern == "straight" or self.pattern == "single":
                self.vel = 3
                self.movey = 0.7
           
            elif self.pattern == "zigzag" or self.pattern == "rzigzag":
                self.vel = 2
                self.zig_time+=1
                self.movey = 0.6
                if self.zig_time == self.zig_length:
                    self.zig_time = 0
                    self.zigging = -self.zigging
                self.loc[0] += self.zigging * self.zig_speed
                self.rect.left = self.loc[0]
            #update velocities based  on patterns
            #x
            #y
            else:
                self.loc[0] += self.movex * self.vel
                self.rect.left = self.loc[0]
            
            #x collisions
            if (self.pattern == "none" or self.pattern == "0" or self.pattern =="straight" or self.pattern == "circle"):
                if self.rect.left < resolution[0]/2 - playarea[0]/2:
                    self.rect.left = resolution[0]/2 - playarea[0]/2
                    self.movex = -self.movex
                elif self.rect.right >= resolution[0]/2 + playarea[0]/2:
                    self.rect.right = resolution[0]/2 + playarea[0]/2
                    self.movex = -self.movex
                
            #y collisions
            if self.rect.bottom < 0:
               self.die(game, False)
               

            self.loc = [self.rect.left, self.rect.top]
    
    def draw(self, camsurf):
        if self.dying == 0 and self.alive:
            camsurf.blit(self.image[self.frame/8], self.rect)
        else:
            camsurf.blit(self.image[self.frame % len(self.image)], self.rect)
        #camsurf.blit(self.image[self.frame/8], self.rect)
        