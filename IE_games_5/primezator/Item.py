import pygame, math, random

def setlevel(data, chars):
    global level, charset
    level = data
    charset = chars


class Num(pygame.sprite.Sprite):
    def __init__(self, loc, val, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.frame = pygame.Surface((32,32))
        self.loc = [loc[0]*32+48, loc[1]*32+64]
        self.x = loc[0]
        self.y = loc[1]
        self.val = val
        self.isprime = 0
        self.newframe()

    def move(self, dir, nums, ops, doors):
        self.x += dir[0]
        self.y += dir[1]
        for num in nums:
            if self != num and self.x == num.x and self.y == num.y:
                self.val += num.val
                nums.remove(num)
                self.newframe()
                self.loc = [self.x*32+48, self.y*32+64]
                return 1
        for op in ops:
            if self.x == op.x and self.y == op.y:
                if op.equate(self.val) or op.final:
                    if not op.final:
                        nums.remove(self)
                    else:
                        self.val = op.var
                        ops.remove(op)
                        self.newframe()
                        self.loc = [self.x*32+48, self.y*32+64]
                    return 1
                else:
                    self.x -= dir[0]
                    self.y -= dir[1]
                    return 0
        for door in doors:
            if self.x == door.x and self.y == door.y and door.locked:
                if self.isprime:
                    door.open(self.val)
                    nums.remove(self)
                    return 1
                else:
                    self.x -= dir[0]
                    self.y -= dir[1]
                    return 0
        self.loc = [self.x*32+48, self.y*32+64]
        return 1

    def newframe(self):
        if self.val > 99999:
            self.val = 99999

        self.isprime = 2
        while self.isprime <= int(math.sqrt(self.val)) and self.val > 1:
            if not self.val % self.isprime:
                self.isprime = 0
                break
            self.isprime += 1
        if self.isprime and self.val > 1:
            self.isprime = 1
        else:
            self.isprime = 0
        self.frame = pygame.Surface((32,32))
        self.frame.blit(self.image.subsurface(32*self.isprime,0,32,32), (0,0))
        if self.val:
            size = int(math.log10(self.val)) + 1
        else:
            size = 1
        count = 1
        while count <= size:
            self.frame.blit(charset[self.val / 10**(size-count) % 10], (16 - size * 3 + (count - 1) * 6 + 1, 11))
            count += 1

    def draw(self, screen):
        screen.blit(self.frame, self.loc)


class Op(pygame.sprite.Sprite):
    def __init__(self, loc, type, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.frame = pygame.Surface((32,32))
        self.loc = [loc[0]*32+48, loc[1]*32+64]
        self.x = loc[0]
        self.y = loc[1]
        self.type = type
        self.var = None
        self.final = 0
        if type != '2' and type != 's':
            self.newframe()
        else:
            self.frame = img

    def equate(self, var2):
        if self.var != None:
            if self.type == '-':
                if self.var < var2:
                    return 0
                self.var -= var2
                self.final = 1
            elif self.type == '*':
                self.var *= var2
                self.final = 1
            elif self.type == '/':
                if var2:
                    if self.var % var2:
                        return 0
                    self.var /= var2
                    self.final = 1
        elif self.type == '2':
            self.var = var2**2
            self.final = 1
            return 1
        elif self.type == 's':
            if math.sqrt(var2) % 1:
                return 0
            self.var = int(math.sqrt(var2))
            self.final = 1
            return 1
        else:
            self.var = var2
            self.newframe()
            return 1

    def newframe(self):
        self.frame = pygame.Surface((32,32))
        self.frame.blit(self.image.subsurface(32*bool(self.var),0,32,32), (0,0))
        if self.var == None:
            self.frame.blit(charset[10], (14,5))
        else:
            if self.var:
                size = int(math.log10(self.var)) + 1
            else:
                size = 1
            count = 1
            while count <= size:
                self.frame.blit(charset[self.var / 10**(size-count) % 10], (16 - size * 3 + (count - 1) * 6 + 1, 5))
                count += 1

    def draw(self, screen):
        screen.blit(self.frame, self.loc)


class Door(pygame.sprite.Sprite):
    def __init__(self, loc, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.frame = pygame.Surface((32,32))
        self.frame.blit(img.subsurface(32,0,32,32), (0,0))
        self.loc = [loc[0]*32+48, loc[1]*32+64]
        self.x = loc[0]
        self.y = loc[1]
        self.locked = 1

    def open(self, num):
        self.locked = 0
        self.newframe(num)

    def newframe(self, num):
        self.frame = pygame.Surface((32,32))
        self.frame.blit(self.image.subsurface(0,0,32,32), (0,0))
        size = int(math.log10(num)) + 1
        count = 1
        while count <= size:
            self.frame.blit(charset[num / 10**(size-count) % 10], (16 - size * 3 + (count - 1) * 6 + 1, 11))
            count += 1

    def draw(self, screen):
        screen.blit(self.frame, self.loc)