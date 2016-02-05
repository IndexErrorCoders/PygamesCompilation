import pygame, sys, os, math, random
import Menu, Player, Item

pygame.init()
screen = pygame.display.set_mode((480, 480))
pygame.display.set_caption("The Primezator 42953")
background = pygame.Surface((480, 480))
backimg = pygame.image.load(os.path.join("images", "back.png"))
background.blit(backimg, (0,0))
pauseimg = pygame.image.load(os.path.join("images", "pause.png")).convert_alpha()
title = pygame.image.load(os.path.join("images", "title.png")).convert_alpha()

f = pygame.font.Font("freesansbold.ttf", 16)
clock = pygame.time.Clock()
start = 0
level = 0
timer = .0
highscore = 0
highscores = [float(line.strip()) for line in open(os.path.join("levels", "bests.txt"))]

char = pygame.image.load(os.path.join("images", "chars.png"))
charset = [char.subsurface(0, 0, 4, 9).convert_alpha(), char.subsurface(4, 0, 4, 9).convert_alpha(), char.subsurface(8, 0, 4, 9).convert_alpha(), char.subsurface(12, 0, 4, 9).convert_alpha(), char.subsurface(16, 0, 4, 9).convert_alpha(), char.subsurface(20, 0, 4, 9).convert_alpha(), char.subsurface(24, 0, 4, 9).convert_alpha(), char.subsurface(28, 0, 4, 9).convert_alpha(), char.subsurface(32, 0, 4, 9).convert_alpha(), char.subsurface(36, 0, 4, 9).convert_alpha(), char.subsurface(40, 0, 4, 9).convert_alpha()]

nums = pygame.sprite.Group()
ops = pygame.sprite.Group()
doors = pygame.sprite.Group()

images = {
    '.': pygame.image.load(os.path.join("images", "blank.png")).convert_alpha(),
    'w': pygame.image.load(os.path.join("images", "wall.png")).convert_alpha(),
    'p': pygame.image.load(os.path.join("images", "player.png")).convert_alpha(),
    'd': pygame.image.load(os.path.join("images", "door.png")).convert_alpha(),
    '#': pygame.image.load(os.path.join("images", "num.png")).convert_alpha(),
    '-': pygame.image.load(os.path.join("images", "sub.png")).convert_alpha(),
    '*': pygame.image.load(os.path.join("images", "mult.png")).convert_alpha(),
    '/': pygame.image.load(os.path.join("images", "div.png")).convert_alpha(),
    '2': pygame.image.load(os.path.join("images", "sqr.png")).convert_alpha(),
    's': pygame.image.load(os.path.join("images", "root.png")).convert_alpha()
}

codes = [
42953,47395,34525,20243,68232,
99091,76253,58864,53540,34482,
87381,36911,68362,12938,76083,
66054,89919,93530,37246,28998,
98372,72919,27105,57472,87650,

64112,80209,62481,96234,43371,
50706,51171,41696,49561,59159,
41432,63330,23001,53838,19745,
80736,26645,23067,62070,10737,
52279,48440,44339,84206,10525,

83305,73721,22879,86822,59874,
18995,59654,68422,37655,80455,
50575,99909,72753,22943,51199,
37654,67658,22739,32426,17419,
65156,73462,86919,81242,49863,

16684,31969,20360,27710,17185,
67791,62944,34086,16629,80175,
32355,11682,55812,26904,44332,
91983,96932,77034,83889,27236,
35102,59213,69574,97652,32172]


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
        screen.blit(f.render(''.join(self.phrase), 1, (255,255,0)), self.loc)

def changehighscore():
    scores = []
    for score in highscores:
        scores.append(str(score))
        scores.append("\n")
    highscorefile = open(os.path.join("levels", "bests.txt"), "w")
    highscorefile.writelines(scores)

def newlevel(level):
    background.blit(backimg, (0,0))
    nums.empty()
    ops.empty()
    doors.empty()
    global player
    count = 0
    try:
        levfile = open(os.path.join("levels", "level%d.txt"%(level)))
        data = [line.strip() for line in levfile]
        Item.setlevel(data, charset)
        for y, row in enumerate(data[:12]):
            for x, cell in enumerate(row):
                if cell != 'w':
                    cell = '.'
                background.blit(images[cell], (32*x+48, 32*y+64))
        for y, row in enumerate(data[:12]):
            for x, cell in enumerate(row):
                if cell == '-' or cell == '*' or cell == '/' or cell == '2' or cell == 's':
                    ops.add(Item.Op((x, y), cell, images[cell]))
                elif cell == 'p':
                    player = Player.Player((x, y), data, images['p'])
                elif cell == 'd':
                    doors.add(Item.Door((x, y), images['d']))
                elif cell == '#':
                    nums.add(Item.Num((x, y), int(data[12+count]), images['#']))
                    count += 1
        return 1
    except IOError:
        return 0


menu1 = Menu.Menu(["Start", "Level Select"], f, (189,325), 30, (255,255,255))
tf1 = Textfield((250,215))

while 1:
    mouse = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            menu1.checkmouse(mouse)
        if event.type == pygame.MOUSEBUTTONDOWN:
            menu1.checkmouse(mouse)
            start = menu1.highlight
            if start == 1:
                level = 1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                menu1.movehighlight(-1)
            elif event.key == pygame.K_DOWN:
                menu1.movehighlight(1)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                start = menu1.highlight
                if start == 1:
                    level = 1
    screen.blit(background, (0,0))
    screen.blit(title, (100,100))
    menu1.draw(screen)
    pygame.display.flip()

    while start == 2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if tf1.code in codes:
                        level = codes.index(tf1.code) + 1
                    else:
                        level = 0
                    start = 1
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
        screen.blit(background, (0,0))
        screen.blit(pauseimg, (140,156))
        screen.blit(f.render("Code:", 1, (255,255,255)), (192,215))
        screen.blit(f.render("space  -  begin", 1, (255,255,255)), (180,260))
        screen.blit(f.render("q  -  quit", 1, (255,255,255)), (218,285))
        tf1.draw()
        pygame.display.flip()

    while start == 1:
        delta = clock.tick()
        if newlevel(level):
            pause = 0
            prelevel = 1
            postlevel = 0
            endgame = 0
            timer = .0
            highscore = highscores[level-1]
        else:
            start = 0
            endgame = 1

        while not endgame:
            while pause:
                delta = clock.tick(60)
                timer += delta
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            pause = 0
                        if event.key == pygame.K_q:
                            pause = 0
                            endgame = 1
                            start = 0
                        if event.key == pygame.K_r:
                            pause = 0
                            endgame = 1
                            level -= 1

                screen.blit(background, (0,0))
                for door in doors:
                    door.draw(screen)
                for op in ops:
                    op.draw(screen)
                for num in nums:
                    num.draw(screen)
                player.draw(screen)
                screen.blit(f.render("Level:", 1, (255,255,255)), (50,24))
                screen.blit(f.render(str(level), 1, (255,255,255)), (115,24))
                screen.blit(f.render("Best:", 1, (255,255,255)), (190,24))
                screen.blit(f.render(str(highscore), 1, (255,255,255)), (249,24))
                screen.blit(f.render("Time:", 1, (255,255,255)), (325,24))
                screen.blit(f.render(str(round((timer/1000),1)), 1, (255,255,255)), (385,24))
                screen.blit(pauseimg, (140,156))
                screen.blit(f.render("PAUSED", 1, (255,255,255)), (208,195))
                screen.blit(f.render("space  -  unpause", 1, (255,255,255)), (180,250))
                screen.blit(f.render("q  -  quit", 1, (255,255,255)), (218,275))
                screen.blit(f.render("r  -  restart", 1, (255,255,255)), (221,300))
                pygame.display.flip()

            while prelevel:
                delta = clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            prelevel = 0
                        if event.key == pygame.K_q:
                            prelevel = 0
                            endgame = 1
                            start = 0

                screen.blit(background, (0,0))
                for door in doors:
                    door.draw(screen)
                for op in ops:
                    op.draw(screen)
                for num in nums:
                    num.draw(screen)
                player.draw(screen)
                screen.blit(pauseimg, (140,156))
                screen.blit(f.render("Level:", 1, (255,255,255)), (190,190))
                screen.blit(f.render(str(level), 1, (255,255,0)), (250,190))
                screen.blit(f.render("Best:", 1, (255,255,255)), (197,215))
                screen.blit(f.render(str(highscore), 1, (255,255,0)), (250,215))
                screen.blit(f.render("Code:", 1, (255,255,255)), (192,240))
                screen.blit(f.render(str(codes[level-1]), 1, (255,255,0)), (250,240))
                screen.blit(f.render("space  -  begin", 1, (255,255,255)), (180,280))
                screen.blit(f.render("q  -  quit", 1, (255,255,255)), (218,305))
                pygame.display.flip()

            if not endgame:
                delta = clock.tick(60)
                timer += delta
                #print float(1000)/delta
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            player.move([0,-1], nums, ops, doors)
                        if event.key == pygame.K_DOWN:
                            player.move([0,1], nums, ops, doors)
                        if event.key == pygame.K_LEFT:
                            player.move([-1,0], nums, ops, doors)
                        if event.key == pygame.K_RIGHT:
                            player.move([1,0], nums, ops, doors)
                        if event.key == pygame.K_SPACE:
                            pause = 1

                endcheck = 1
                for door in doors:
                    if door.locked:
                        endcheck = 0
                        break
                for op in ops:
                    if op.var:
                        endcheck = 0
                        break
                if endcheck and not len(nums):
                    postlevel = 1
                    endgame = 1
                    if round((timer/1000),1) < highscore:
                        highscore = round((timer/1000),1)
                        highscores.pop(level-1)
                        highscores.insert(level-1, round((timer/1000),1))
                        changehighscore()

                screen.blit(background, (0,0))
                for door in doors:
                    door.draw(screen)
                for op in ops:
                    op.draw(screen)
                for num in nums:
                    num.draw(screen)
                player.draw(screen)
                screen.blit(f.render("Level:", 1, (255,255,255)), (50,24))
                screen.blit(f.render(str(level), 1, (255,255,255)), (115,24))
                screen.blit(f.render("Best:", 1, (255,255,255)), (190,24))
                screen.blit(f.render(str(highscore), 1, (255,255,255)), (249,24))
                screen.blit(f.render("Time:", 1, (255,255,255)), (325,24))
                screen.blit(f.render(str(round((timer/1000),1)), 1, (255,255,255)), (385,24))
                pygame.display.flip()

            while postlevel:
                delta = clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            postlevel = 0
                        if event.key == pygame.K_q:
                            postlevel = 0
                            endgame = 1
                            start = 0
                        if event.key == pygame.K_r:
                            postlevel = 0
                            endgame = 1
                            level -= 1

                screen.blit(background, (0,0))
                for door in doors:
                    door.draw(screen)
                for op in ops:
                    op.draw(screen)
                for num in nums:
                    num.draw(screen)
                player.draw(screen)
                screen.blit(pauseimg, (140,156))
                screen.blit(f.render("Best:", 1, (255,255,255)), (197,190))
                screen.blit(f.render(str(highscore), 1, (255,255,0)), (250,190))
                screen.blit(f.render("Time:", 1, (255,255,255)), (192,215))
                screen.blit(f.render(str((round((timer/1000),1))), 1, (255,255,0)), (250,215))
                screen.blit(f.render("space  -  next", 1, (255,255,255)), (180,255))
                screen.blit(f.render("q  -  quit", 1, (255,255,255)), (218,280))
                screen.blit(f.render("r  -  restart", 1, (255,255,255)), (221,305))
                pygame.display.flip()

            if endgame:
                background.blit(backimg, (0,0))

            if start and endgame:
                level += 1
                if newlevel(level):
                    endgame = 0
                    prelevel = 1
                    timer = .0
                    highscore = highscores[level-1]
                else:
                    start = 0