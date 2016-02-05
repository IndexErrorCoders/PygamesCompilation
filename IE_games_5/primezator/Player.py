import pygame, math, random

class Player(pygame.sprite.Sprite):
    def __init__(self, loc, level, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.loc = [loc[0]*32+48, loc[1]*32+64]
        self.x = loc[0]
        self.y = loc[1]
        self.level = level

    def move(self, dir, nums, ops, doors):
        self.x += dir[0]
        self.y += dir[1]
        if self.x < 0:
            self.x = 0
        if self.x > 11:
            self.x = 11
        if self.y < 0:
            self.y = 0
        if self.y > 11:
            self.y = 11
        if self.level[self.y][self.x] == 'w':
            self.x -= dir[0]
            self.y -= dir[1]
        for num in nums:
            if self.x == num.x and self.y == num.y:
                if (self.x + dir[0]) < 0 or (self.x + dir[0]) > 11 or (self.y + dir[1]) < 0 or (self.y + dir[1]) > 11:
                    self.x -= dir[0]
                    self.y -= dir[1]
                    break
                if self.level[self.y + dir[1]][self.x + dir[0]] == 'w':
                    self.x -= dir[0]
                    self.y -= dir[1]
                    break
                if not num.move(dir, nums, ops, doors):
                    self.x -= dir[0]
                    self.y -= dir[1]
                break
        for op in ops:
            if self.x == op.x and self.y == op.y:
                self.x -= dir[0]
                self.y -= dir[1]
        for door in doors:
            if self.x == door.x and self.y == door.y and door.locked:
                self.x -= dir[0]
                self.y -= dir[1]
                break
        self.loc = [self.x*32+48, self.y*32+64]

    def draw(self, screen):
        screen.blit(self.image, self.loc)