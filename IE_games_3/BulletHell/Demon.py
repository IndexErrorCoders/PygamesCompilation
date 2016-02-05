import pygame, random, math
import Enemy
import Bullet, Fireball
from Constants import *
from Controls import *

class Demon(Enemy.Enemy):
    def __init__(self, pos, group, pattern):
        Enemy.Enemy.__init__(self, group)
        self.image = images["demon"]
        #self.image.fill((255,255,255))
        self.rect = pygame.Rect(pos[0],pos[1],110,62)
        
        self.state = None
        self.group = group
        
        self.frame = 0
        
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
            self.vel=5
            self.movey=1
        if self.pattern == "circle":
            self.vel = 2
            self.movex=0
            self.movey=0
        self.circle_time = 0
        self.circle_count = 0
        self.circle_length = 360
            
        if self.pattern == "none":
            self.vel = random.randint(1,3)
            self.movex = random.randint(-1,1)
            if self.movex==0:
                self.movex=1
        #self.movey = random.randint(-1,0)
        #self.movex = 0
        #self.movey = 0

        self.health = 5
        self.melee = 20
        self.points = 1
        self.fire_rate = 90
        self.fired = 0
        
        self.loc = [pos[0], pos[1]]

    def shoot(self, game):
        if self.fired == 0 and self.pattern != "speed":
            if random.randint(0,3) == 0:
                self.fired += self.fire_rate
                game.bullets.append(Fireball.Fireball(self.rect.center))
    
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
    
    def update(self, game):
        if not game.time_stopped:

            # Change the sprite
            if self.dying > 0:
                self.frame = int((float(5-float(self.dying)/8))%5)
                if self.dying < 8 and self.frame == 0:
                    self.dying = 0
                    self.frame = 4
                else:
                    self.dying -= 1
            else:
                self.frame += 1
                if self.frame > 47:
                    self.frame = 0
            
            if self.dying <= 0 and not self.alive:
                self.die(game, True)
                return True
                
            if self.pattern == "circle":
                if self.circle_count < 2:
                    self.circle_time += 1
                    if self.circle_time == self.circle_length:
                        self.circle_time = 0
                        self.circle_count +=1
                    if self.circle_time < 90:
                        self.movex = 0.5
                        self.movey = -0.5
                    elif self.circle_time > 90 and self.circle_time <180:
                        self.movex = -0.5
                        self.movey = -0.75
                    elif self.circle_time >180 and self.circle_time <270:
                        self.movex = -0.5
                        self.movey = 0.75
                    else:
                        self.movex = 0.5
                        self.movey = 0.5
                    self.loc[0] += self.movex * self.vel
                    self.rect.left = self.loc[0]
                else:
                    self.movex = 0
                    self.movey = -2
            
            if self.pattern == "straight":
                self.vel = 3
                self.movey = 0.7
           
            if self.pattern == "zigzag":
                self.vel = 2
                self.zig_time+=1
                self.movey = 0.6
                if self.zig_time == self.zig_length:
                    self.zig_time = 0
                    self.zigging = -self.zigging
                self.loc[0] += self.zigging * self.zig_speed
                self.rect.left = self.loc[0]
            elif self.pattern  == "rzigzag":
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
    
            if self.pattern == "none" or self.pattern == "0" or self.pattern == "circle":
                #x collisions
                if self.rect.left < resolution[0]/2 - playarea[0]/2:
                    self.rect.left = resolution[0]/2 - playarea[0]/2
                    self.movex = -self.movex
                elif self.rect.right >= resolution[0]/2 + playarea[0]/2:
                    self.rect.right = resolution[0]/2 + playarea[0]/2
                    self.movex = -self.movex
    
            self.loc = [self.rect.left, self.rect.top]
            if self.pattern == "circle":
                self.loc[1] += self.movey * self.vel - (game.speed/64.)
                self.rect.top = self.loc[1] - abs(self.loc[1] % 1)
                
            else:    
            #y move
                self.loc[1] -= self.movey * self.vel + (game.speed / 4.)
                self.rect.top = self.loc[1] - abs(self.loc[1] % 1)
            
            #y collisions
            
            if self.rect.bottom < 0:
                self.die(game, False)
            
            
            self.loc = [self.rect.left, self.rect.top]
            
            
            #shoot
            if self.fired > 0:
                self.fired -= 1
            elif self.fired == 0 and self.alive:
                self.shoot(game)
            
    
    def draw(self, camsurf):
        if self.dying == 0 and self.alive:
            camsurf.blit(self.image[self.frame/8], self.rect)
        else:
            camsurf.blit(self.image[self.frame % len(self.image)], self.rect)
