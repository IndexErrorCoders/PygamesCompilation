import pygame, random
import PlayerBullet
from Constants import *
from Controls import *


class Player(object):
    def __init__(self):
        self.frame = random.randint(0,2)
        self.image = images["player"]
        #self.image.fill((0,0,255))
        self.fullrect = self.image[0].get_rect()
        self.fullrect.center = (100,100)
        
        self.rect = pygame.Rect(100,100,25,50)
        self.rect.center = self.fullrect.center
        
        #self.hitbox = pygame.Surface((45,50))
        #self.hitbox.fill((255,255,255))

        self.state = None
        self.ability = 0
        self.flipped = False
        self.flip_time = 0
        self.flip_length = 300
        self.rushing = False
        self.rising = False
        self.rise_time = 0
        self.rise_length = 60
        self.vel = 5#deprecated
        self.velx = 6
        self.vely = 5
        self.health = 100
        self.max_health = 100
        self.weapon = 1
        self.fire_rate = 15
        self.fired = 0
        self.cooldown = 0
        self.damaged = 0
        self.light_time = 0
        self.light_length = 300
        self.rush_time = 0
        self.rush_length = 50
        self.rise_speed = 1
        self.rush_speed = 2
        self.rush_damage = 3
        self.loc = [516,105]

    def shoot(self, game):
        if self.fired == 0:
            self.fired += self.fire_rate
            if self.weapon == 1:
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 0))
            if self.weapon == 2:
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 1))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 2))
            if self.weapon == 3:
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 0))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 3))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 4))
            if self.weapon == 4:
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 0))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 3))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 4))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 5))
            if self.weapon == 5:
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 0))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 3))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 4))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 5))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 1))
                game.bullets.append(PlayerBullet.PlayerBullet(self.rect.center, 2))
                
    def rush_ability(self, game):
        if self.cooldown == 0:
            game.sound.play("player_rush")
            self.ability = 1
            self.cooldown += 60 * 6
            self.rushing = True
            self.rush_time = self.rush_length
            game.speed += 2
        else: 
            pass
        
    def time_stop(self, game):
        if self.cooldown == 0:
            game.sound.play("time_stop")
            self.ability = 2
            self.cooldown += 60 * 12
            game.time_stopped = True
            game.time_stop_time = game.time_stop_length
        else:
            pass
    
    def light_weapon(self, game):
        if self.cooldown == 0:
            game.sound.play("light_attack")
            self.ability = 3
            self.cooldown += 60 * 13
            self.light_time = self.light_length
            game.lightspawn.trigger()
        else:
            pass
            
    def weapon_upgrade(self):
        if self.weapon < 5:
            self.weapon += 1
        else:
            if self.fire_rate > 9:
                self.fire_rate -= 2
    
    def health_upgrade(self, num):
        self.health += num
        if self.health > self.max_health:
            self.health = self.max_health
    
    def speed_up(self, game, num):
        if not game.time_stopped:
            game.speed += num
        else:
            game.saved_speed += num
    
    def slow_down(self, game, num):
        game.speed -= num
        if game.speed < 0.5:
            game.speed = 0.5
    
    def slow_down_to(self, game, num):
        game.speed = num
    
    def die(self, game):
        game.sound.play("player_death")
        game.endgame = True
    
    def take_damage(self, game, dmg, speed=0.5):
        if self.damaged == 0:
            self.health -= dmg
            game.sound.play("player_damage"+str(random.randint(1,3))
            )
            if self.health <= 0:
                return
            self.damaged = 120
            if not game.time_stopped:
                self.slow_down(game, speed)

    def update(self, game):
        #flipping
        if self.flipped:
            self.flip_time -= 1
            if self.flip_time == 0:
                self.flipped = False
                game.whiteflash.set_alpha(255)
        
        if self.damaged > 0:
            self.damaged -= 1
        
        #shoot
        if controls[k_action1]:
            self.shoot(game)
        
        
        #abilities
        if controls[k_ability1]:
            self.rush_ability(game)
        if controls[k_ability2]:
            self.time_stop(game)
        if controls[k_ability3]:
            self.light_weapon(game)
        
        
        if self.fired > 0:
            self.fired -= 1
        #cooldown
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # Change the sprite
        self.frame += 1
        if self.frame > 47:
            self.frame = 0
        
        #rushing
        if self.rushing:
            self.rush_time -= 1
            self.image = images["player_rush"]
            if self.rush_time == 0:
                self.ability = 0
                self.rushing = False
                self.rising = True
                self.rise_time += self.rise_length
                self.image = images["player"][0]
                game.speed -= 2
        if self.rising:
            self.rise_time -= 1
            self.frame = 16
            if self.rise_time == 0:
                self.rising = False

        #light weapon
        if self.light_time > 0:
            self.light_time -= 1
            if self.light_time == 0:
                self.ability = 0
                game.lightspawn.trigger()
                

                
        #x move
        if controls[k_left] and not controls[k_right] and not self.flipped:
            self.loc[0] -= self.velx
        if controls[k_left] and not controls[k_right] and self.flipped:
            self.loc[0] += self.velx
        elif controls[k_right] and not controls[k_left] and not self.flipped:
            self.loc[0] += self.velx
        elif controls[k_right] and not controls[k_left] and self.flipped:
            self.loc[0] -= self.velx
        self.rect.centerx = self.loc[0]

        #x collisions
        if self.rect.left < resolution[0]/2 - playarea[0]/2:
            self.rect.left = resolution[0]/2 - playarea[0]/2
        elif self.rect.right >= resolution[0]/2 + playarea[0]/2:
            self.rect.right = resolution[0]/2 + playarea[0]/2

        
        for r in game.rocks:
            if self.rect.colliderect(r.rect):
                if game.time_stopped or game.total_distance == BOSS_DEPTH:
                    if controls[k_left]:
                        self.rect.left = r.rect.right
                    elif controls[k_right]:
                        self.rect.right = r.rect.left
                elif not self.rushing and not self.rising:
                    self.take_damage(game, r.damage, r.speed_penalty)

        self.loc = [self.rect.centerx, self.rect.centery]

        #y move
        if not self.rushing and not self.rising:
            if controls[k_up] and not controls[k_down]:
                self.loc[1] -= self.vely
                self.frame = 16
            elif controls[k_down] and not controls[k_up]:
                #self.frame = 0
                self.loc[1] += self.vely
            self.rect.centery = self.loc[1]
        elif self.rushing:
            self.loc[1] += self.vely*self.rush_speed
            self.rect.centery = self.loc[1]
        elif self.rising:
            self.loc[1] -= self.vely*self.rise_speed
            self.rect.centery = self.loc[1]

        #y collisions
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom >= resolution[1]:
            self.rect.bottom = resolution[1]

        for r in game.rocks:
            if self.rect.colliderect(r.rect):
                if game.time_stopped or game.total_distance == BOSS_DEPTH:
                    if controls[k_up]:
                        self.rect.top = r.rect.bottom
                    else:
                        self.rect.bottom = r.rect.top
                elif not self.rushing and not self.rising:
                    self.take_damage(game, r.damage, r.speed_penalty)

        self.loc = [self.rect.centerx, self.rect.centery]
        self.fullrect.center = self.rect.center
        
        for p in game.pickups:
            if self.fullrect.colliderect(p.rect):
                p.apply(game, self)
                p.die(game)
        
        if not self.rushing and not self.rising:
            for e in game.enemies:
                if self.rect.colliderect(e.rect):
                    self.take_damage(game, e.melee, e.speed_penalty)
                    if e.state == "Mirror":
                        self.flipped = True
                        game.enemies.remove(e)
                        self.flip_time += self.flip_length
                        game.whiteflash.set_alpha(255)
        else:
            for e in game.enemies:
                if self.rect.colliderect(e.rect):
                    if e.state == "Mirror":
                        e.mgroup.break_mirror()
                        game.enemies.remove(e)
                    else:
                        e.take_damage(game, self.rush_damage, True)
                

    def draw(self, camsurf):
        if self.rushing:
            camsurf.blit(images["player_rush"], self.fullrect.topleft)
        
        elif (self.damaged/8)%2==0:
            camsurf.blit(images["player"][self.frame/8], self.fullrect.topleft)
        
        #camsurf.blit(self.hitbox, self.rect)
