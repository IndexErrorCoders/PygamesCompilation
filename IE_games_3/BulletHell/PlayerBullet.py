import pygame, random
from Constants import *
from Controls import *
import Bullet

class PlayerBullet(Bullet.Bullet):
    def __init__(self, location, type):
        Bullet.Bullet.__init__(self,location)
        self.frame = random.randint(0,2)
        self.rect = pygame.Rect(0,0,4,18)
        self.damage = 5
        self.velocity = 12
        self.xvelocity = 3
        self.rect.centerx = location[0]
        self.rect.centery = location[1]
        self.type = type
        
        self.reflected = False
        self.hitting = 0
        self.shooting = True
        
        self.loc = [self.rect.left, self.rect.top]
        
        if self.type == 1:
            self.loc[0] -= 10
        if self.type == 2:
            self.loc[0] += 10
        if self.type == 3:
            self.loc[0] -= 10
        if self.type == 4:
            self.loc[0] += 10
        
        """if self.type == 0:
            self.loc = [self.rect.left+hitbox_width/2, self.rect.top]
        if self.type == 1:
            self.loc = [self.rect.left+((hitbox_width/32)*6), self.rect.top]
        if self.type == 2:
            self.loc = [self.rect.left+((hitbox_width/32)*24), self.rect.top]
        if self.type == 3:
            self.loc = [self.rect.left+((hitbox_width/32)*6), self.rect.top]
        if self.type == 4:
            self.loc = [self.rect.left+hitbox_width/2, self.rect.top]
        if self.type == 5:
            self.image = pygame.transform.flip(self.image, False, True)
            self.loc = [self.rect.left+hitbox_width/2, self.rect.top-20]
        if self.type == 6:
            self.loc = [self.rect.left, self.rect.top]"""
    
    def reflect(self):
        self.reflected = True
        self.velocity = -self.velocity
        if self.type == -1:
            self.yvel *= -1
        self.damage = 1
    
    def hit(self):
        if self.shooting:
            self.hitting = 5
            self.shooting = False
            self.velocity = 0
            self.xvelocity = 0
        
    def update(self, game, light=False):
        if (self.rect.left < resolution[0]/2 - playarea[0]/2 or self.rect.right >= resolution[0]/2 + playarea[0]/2 or self.rect.top < 0 or self.rect.bottom >= resolution[1]) and not self.dead:
            self.die(game)
            return True
        
        if self.hitting > 0:
            self.hitting -= 1
            self.velocity = -(game.speed) if not game.boss_active else 0
        
        #print self.hitting, " ", self.shooting
        
        if self.hitting <= 0 and not self.shooting:
            self.die(game)
            return True
        
        if self.type > -1:
            # Change the sprite
            if not game.time_stopped or not self.reflected:
                self.frame += 1
                if self.frame > 38:
                    self.frame = 0
            
                if self.type == 0:
                    self.loc[1] += self.velocity+1#+game.speed/2
                if self.type == 1:
                    self.loc[1] += self.velocity#+game.speed/2
                if self.type == 2:
                    self.loc[1] += self.velocity#+game.speed/2
                if self.type == 3:
                    self.loc[1] += self.velocity#+game.speed/2
                    self.loc[0] -= self.xvelocity
                if self.type == 4:
                    self.loc[1] += self.velocity#+game.speed/2
                    self.loc[0] += self.xvelocity
                if self.type == 5:
                    self.loc[1] -= self.velocity#+game.speed/2

                self.rect.centerx = self.loc[0]
                self.rect.centery = self.loc[1]
        
        # DEAL WITH REFLECTED BULLET COLLISION ANIMATION!!!
        if self.reflected:
            if self.rect.colliderect(game.player.rect):
                if light:
                    game.player.health_upgrade(1)
                elif not game.player.rushing and not game.player.rising:
                    game.player.take_damage(game, self.damage*30)
                self.die(game)
                return True
        
        if self.shooting:
            for e in game.enemies:
                if self.rect.colliderect(e.rect) and e.alive:
                    if e.group == "boss":
                        if e.checkcollision(game, self, False, light):
                            self.hit()
                    elif e.state == "Mirror":
                        if not self.reflected:
                            self.reflect()
                        self.rect.bottom = e.rect.top
                    else:
                        self.hit()
                        e.take_damage(game, self.damage, False, light)
                        
            for r in game.rocks:
                if self.rect.colliderect(r.rect):
                    self.hit()
        
        
    def draw(self, camsurf):
        if self.hitting > 0:
            if self.type == 5 or self.reflected:
                camsurf.blit(images["playerbullet_hit_flipped"], self.loc)
            else:
                camsurf.blit(images["playerbullet_hit"], self.loc)
        elif self.hitting <= 0 and not self.shooting:
            pass
        elif self.type == 3:
            camsurf.blit(pygame.transform.rotate((images["playerbullet_sheet"][self.frame/13]), -45/2), self.loc)
        elif self.type == 4:
            camsurf.blit(pygame.transform.rotate((images["playerbullet_sheet"][self.frame/13]), 45/2), self.loc)
        elif self.type == 5:
            camsurf.blit(pygame.transform.flip((images["playerbullet_sheet"][self.frame/13]), False, True), self.loc)
        elif not self.reflected:
            camsurf.blit(images["playerbullet_sheet"][self.frame/13], self.loc)
        else:
            camsurf.blit(pygame.transform.flip((images["playerbullet_sheet"][self.frame/13]), False, True), self.rect.center)
            
