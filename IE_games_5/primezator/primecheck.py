import pygame, sys, os, math, random

pygame.init()
screen = pygame.display.set_mode((500,100))
background = pygame.Surface((500,100))
background.fill((0,0,0))
f = pygame.font.Font(None, 32)
c = (255,255,255)

def isprime(num):
    check = 2
    while check <= int(math.sqrt(num)):
        if not num % check:
            return 0
        check += 1
    if num < 2:
        return 0
    return 1

class Textfield(object):
    def __init__(self, location):
        self.phrase = []
        self.loc = location
        self.code = 0

    def newchar(self, char):
        if len(self.phrase) < 5:
            self.phrase.append(char)
            self.newcode()

    def delchar(self):
        if len(self.phrase):
            self.phrase.pop()
            self.newcode()

    def enter(self):
        self.phrase = []
        self.code = 0

    def newcode(self):
        if self.phrase:
            self.code = int("".join(self.phrase))
        else:
            self.code = 0

    def draw(self):
        screen.blit(f.render("".join(self.phrase), 1, (255,0,0)), self.loc)

tf1 = Textfield((30,30))

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                print isprime(tf1.code)
                tf1.enter()
            elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                tf1.delchar()
            elif event.key == pygame.K_1:
                tf1.newchar("1")
            elif event.key == pygame.K_2:
                tf1.newchar("2")
            elif event.key == pygame.K_3:
                tf1.newchar("3")
            elif event.key == pygame.K_4:
                tf1.newchar("4")
            elif event.key == pygame.K_5:
                tf1.newchar("5")
            elif event.key == pygame.K_6:
                tf1.newchar("6")
            elif event.key == pygame.K_7:
                tf1.newchar("7")
            elif event.key == pygame.K_8:
                tf1.newchar("8")
            elif event.key == pygame.K_9:
                tf1.newchar("9")
            elif event.key == pygame.K_0:
                tf1.newchar("0")

    screen.blit(background,(0,0))
    tf1.draw()
    pygame.display.flip()