import pygame
import math
import random
from Source import GameData
from Source import TankCopy
from Source import Score
from Source import Bullet

#####################################################################
class Tank(pygame.sprite.Sprite):
    """Yes, this is what this game is about.
    The player tank is hardcoded to be the red one."""

    images = []
    animcycle = 6

    def __init__(self,colour,respawnpoint,algorithm, visible = True):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[colour * 6]
        self.rect = self.image.get_rect()
        x = GameData.battleground[GameData.battlegroundnr].respawnpoints[respawnpoint][0] + 6
        y = GameData.battleground[GameData.battlegroundnr].respawnpoints[respawnpoint][1] + 4
        angle = GameData.battleground[GameData.battlegroundnr].respawnpoints[respawnpoint][2]
        newpos = self.rect.move((x, y))
        self.rect = newpos
        self.colour = colour
        self.algorithm = algorithm
        self.visible = visible
        self.angle = angle
        self.gear = 0
        self.bullets = 0
        self.deaths = 0
        self.kills = 0
        self.state = 0
        self.command_queue = []
        self.original = self.image
        center = self.rect.center
        rotate = pygame.transform.rotate
        self.image = rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=center)
        self.x = self.rect.left
        self.y = self.rect.top
        self.gun_cooldown = GameData.bulletloadtime
        self.gear_cooldown = GameData.gearcooldown
        # display tank on scoreboard
        self.icon_display=TankCopy(self.colour)
        if pygame.font:
            self.kills_display=Score("kills      : %d","orange",870,190 + self.colour * 75)
            self.deaths_display=Score("deaths : %d","red",870,222 + self.colour * 75)
        # Make A.I. tanks come out of their spawn point at the start of a new game
        if self.colour <> GameData.red:
            self.command_queue = []
            for i in range(0,20):
                self.command_queue.append("up")
                self.command_queue.append("shoot")
            self.command_queue.append("flush")

    def move_to_respawn_point(self,respawnpoint):
        self.x=GameData.battleground[GameData.battlegroundnr].respawnpoints[respawnpoint][0] + 6
        self.y=GameData.battleground[GameData.battlegroundnr].respawnpoints[respawnpoint][1] + 4
        self.angle=GameData.battleground[GameData.battlegroundnr].respawnpoints[respawnpoint][2]
        self.rect.left = self.x
        self.rect.top = self.y        

    def shoot(self):
        if (self.bullets < GameData.maxbullets) and (self.gun_cooldown == 0):
            #this was centerx-3, centery-0
            Bullet(self.colour,self.rect.centerx-3,self.rect.centery-3,self.angle)
            self.bullets = self.bullets + 1
            self.gun_cooldown = GameData.bulletloadtime

    def explode(self):
        self.deaths += 1
        self.gear = 0
        self.original = self.image
        flag = 0
        respawnpoint = int(random.random()*6)
        while respawnpoint in GameData.respawnlist:
            respawnpoint = int(random.random()*6)
        while len(GameData.respawnlist) > 2:
            dummy = GameData.respawnlist.pop(0)
        GameData.respawnlist.append(respawnpoint)
        self.move_to_respawn_point(respawnpoint)
        self.angle=GameData.battleground[GameData.battlegroundnr].respawnpoints[respawnpoint][2]
        self.rect.left = self.x
        self.rect.top = self.y
        self.command_queue = []
                
    def gear_up(self):
        if (self.gear < 4) and (self.gear_cooldown == 0):
            self.gear = self.gear + 1
            self.gear_cooldown = GameData.gearcooldown

    def gear_down(self):
        if (self.gear > 0) and (self.gear_cooldown == 0):
            self.gear = self.gear - 1
            self.gear_cooldown = GameData.gearcooldown
        elif self.gear_cooldown == 0:
            self.gear = -2
            self.gear_cooldown = GameData.gearcooldown

    def halt(self):
        self.gear = 0

    def right(self):
        self.angle = self.angle - GameData.angle
        if self.angle < 0:
            self.angle = 360-GameData.angle

    def left(self):
        self.angle = self.angle + GameData.angle
        if self.angle >= 360:
            self.angle = 0
    def process_commands(self, respawn_points):
        if len(self.command_queue) > 0:
            action = self.command_queue.pop(0)
            if action == "flush":
                self.command_queue = []
            if action == "up":
                self.gear_up()
            if action == "down":
                self.gear_down()
            if action == "left":
                self.left()
            if action == "right":
                self.right()
            if action == "halt":
                self.halt()
            if action == "shoot":
                if len(pygame.sprite.spritecollide(self, respawn_points, 0)) == 0:
                    self.shoot()
            # tanks can shoot while turning or changing gear
            elif (len(self.command_queue) > 0):
                if self.command_queue[0] == "shoot":
                    if len(pygame.sprite.spritecollide(self, respawn_points, 0)) == 0:
                        dummy = self.command_queue.pop(0)
                        self.shoot()

    def move(self):        
        # xoffset & yoffset as in $tring$ (magazine of the Youth Computer Club) nr.1, 1984, page 13
        xoffset = math.cos(self.angle * math.pi / 180) * self.gear * GameData.tankspeed
        yoffset = - math.sin(self.angle * math.pi / 180) * self.gear * GameData.tankspeed
        # stay out of walls
        for wall in GameData.battleground[GameData.battlegroundnr].walls:
            if wall.colliderect(self.rect):
                if wall.collidepoint(self.rect.left, self.rect.top):
                    if xoffset < 0:
                        xoffset = 0
                    if yoffset < 0:
                        yoffset = 0
                elif wall.collidepoint(self.rect.left, self.rect.bottom):
                    if xoffset < 0:
                        xoffset = 0
                    if yoffset > 0:
                        yoffset = -0
                elif wall.collidepoint(self.rect.right, self.rect.top):
                    if xoffset > 0:
                        xoffset = -0
                    if yoffset < 0:
                        yoffset = 0
                elif wall.collidepoint(self.rect.right, self.rect.bottom):
                    if xoffset > 0:
                        xoffset = -0
                    if yoffset > 0:
                        yoffset = -0
                elif wall.collidepoint(self.rect.centerx, self.rect.top):
                    if yoffset < 0:
                       yoffset = 0
                elif wall.collidepoint(self.rect.centerx, self.rect.bottom):
                    if yoffset > 0:
                        yoffset = -0
                elif wall.collidepoint(self.rect.left, self.rect.centery):
                    if xoffset < 0:
                        xoffset = 0
                elif wall.collidepoint(self.rect.right, self.rect.centery):
                    if xoffset > 0:
                        xoffset = -0
                else:
                    xoffset = 0
                    yoffset = 0
        # stay out of water
        for pool in GameData.battleground[GameData.battlegroundnr].water:
            if pool.colliderect(self.rect):
                if pool.collidepoint(self.rect.left, self.rect.top):
                    if xoffset < 0:
                        xoffset = 0
                    if yoffset < 0:
                        yoffset = 0
                elif pool.collidepoint(self.rect.left, self.rect.bottom):
                    if xoffset < 0:
                        xoffset = 0
                    if yoffset > 0:
                        yoffset = -0
                elif pool.collidepoint(self.rect.right, self.rect.top):
                    if xoffset > 0:
                        xoffset = -0
                    if yoffset < 0:
                        yoffset = 0
                elif pool.collidepoint(self.rect.right, self.rect.bottom):
                    if xoffset > 0:
                        xoffset = -0
                    if yoffset > 0:
                        yoffset = -0
                elif pool.collidepoint(self.rect.centerx, self.rect.top):
                    if yoffset < 0:
                       yoffset = 0
                elif pool.collidepoint(self.rect.centerx, self.rect.bottom):
                    if yoffset > 0:
                        yoffset = -0
                elif pool.collidepoint(self.rect.left, self.rect.centery):
                    if xoffset < 0:
                        xoffset = 0
                elif pool.collidepoint(self.rect.right, self.rect.centery):
                    if xoffset > 0:
                        xoffset = -0
                else:
                    xoffset = 0
                    yoffset = 0
        # bounce back at border
        if  self.x < 3:
            if xoffset < 0:
                xoffset = 1
        if self.x > 759:
            if xoffset > 0:
                xoffset = -1
        if self.y < 3:
            if yoffset < 0:
                yoffset = 1
        if self.y > 724:
            if yoffset > 0:
                yoffset = -1
        # move & rotate the Tank sprite
        newpos = self.rect.move((xoffset, yoffset))
        self.rect = newpos

    def update(self):
        # update scoreboard
        if pygame.font:
            self.kills_display.set_score(self.kills)
            self.deaths_display.set_score(self.deaths)
        if self.visible:
            # use next image
            self.image = self.images[(self.colour * 6) + GameData.animstep ]
            self.original = self.image
            # rotate
            center = self.rect.center
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.angle)
            self.rect = self.image.get_rect(center=center)
            self.x = self.rect.left
            self.y = self.rect.top
        else:
            center = self.rect.center
            self.image = GameData.transparant_sprite
            self.rect = self.image.get_rect(center=center)
            self.x = self.rect.left
            self.y = self.rect.top
