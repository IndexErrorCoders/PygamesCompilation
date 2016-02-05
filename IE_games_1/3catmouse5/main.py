import pygame, sys, os, math, random
import Cat, Mouse, Item, Menu
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((800,640))
pygame.display.set_caption("A Game of Cat and Mouse")
menuimg = pygame.image.load(os.path.join("images", "menuback.png")).convert_alpha()
menupaper = pygame.image.load(os.path.join("images", "paper1.png")).convert_alpha()
instrpaper = pygame.image.load(os.path.join("images", "paper2.png")).convert_alpha()
background = menuimg
black = pygame.image.load(os.path.join("images", "black.png")).convert_alpha()
clock = pygame.time.Clock()
f = pygame.font.Font("nyala.ttf", 22)
f2 = pygame.font.Font("nyala.ttf", 18)
start = 0
cdir = (0,0)
mdir = (0,0)

pupson = True
lightning = 1
nightvision = False
vision = 2
difficulty = 1
fson = False

catwin = pygame.mixer.Sound(os.path.join("sounds", "catwin.wav"))
mousewin = pygame.mixer.Sound(os.path.join("sounds", "mousewin.wav"))
pounce = pygame.mixer.Sound(os.path.join("sounds", "pounce.wav"))
sprint = pygame.mixer.Sound(os.path.join("sounds", "sprint.wav"))
trap = pygame.mixer.Sound(os.path.join("sounds", "trap.wav"))
meow = pygame.mixer.Sound(os.path.join("sounds", "catmeow.wav"))
lighton = pygame.mixer.Sound(os.path.join("sounds", "lighton.wav"))
lightoff = pygame.mixer.Sound(os.path.join("sounds", "lightoff.wav"))
alarm = pygame.mixer.Sound(os.path.join("sounds", "alarm.wav"))
pupup = pygame.mixer.Sound(os.path.join("sounds", "powerup.wav"))
#titlemusic = os.path.join("sounds", "title.mid") 
#multimusic = os.path.join("sounds", "multi.mid")
#nightmusic = os.path.join("sounds", "night.mid")
#pygame.mixer.music.load(titlemusic)
#pygame.mixer.music.play(-1)
alarmtimer = 0
oldtimer = 0

textwindow = pygame.image.load(os.path.join("images", "twindow.png")).convert_alpha()
textwindow2 = pygame.image.load(os.path.join("images", "twindow2.png")).convert_alpha()
textwindowrect = textwindow.get_rect()
textwindowrect.topleft = (302,265)
hud = pygame.image.load(os.path.join("images", "hud.png")).convert_alpha()
cwindow = pygame.image.load(os.path.join("images", "windowc.png")).convert_alpha()
cpowdow = pygame.image.load(os.path.join("images", "windowcb.png")).convert_alpha()
mwindow = pygame.image.load(os.path.join("images", "windowm.png")).convert_alpha()
mpowdow = pygame.image.load(os.path.join("images", "windowmb.png")).convert_alpha()
gaugecover = pygame.image.load(os.path.join("images", "gaugecover.png")).convert_alpha()
pouncebar = pygame.Surface((100,12))
pouncerect = pygame.Rect(124,17,100,12)
pouncebar.fill((0,255,0))
sprintbar = pygame.Surface((100,12))
sprintrect = pygame.Rect(576,17,100,12)
sprintbar.fill((0,255,0))
glowframe = 0
fdir = 1
cpowerbar = pygame.Surface((100,12))
cpowerbar.fill((0,255,255))
cpowerrect = cpowerbar.get_rect()
cpowerrect.topleft = (124,35)
mpowerbar = pygame.Surface((100,12))
mpowerbar.fill((0,255,255))
mpowerrect = mpowerbar.get_rect()
mpowerrect.topleft = (576,35)


images = {
	'a': pygame.image.load(os.path.join("images", "cat.png")).convert_alpha(),
	'm': pygame.image.load(os.path.join("images", "mouse.png")).convert_alpha(),
	'c': pygame.image.load(os.path.join("images", "cheese.png")).convert_alpha(),
	'w': pygame.image.load(os.path.join("images", "wall.png")).convert_alpha(),
	'.': pygame.image.load(os.path.join("images", "grass.png")).convert_alpha(),
	's': pygame.image.load(os.path.join("images", "safe.png")).convert_alpha(),
	'h': pygame.image.load(os.path.join("images", "home.png")).convert_alpha(),
	't': pygame.image.load(os.path.join("images", "trap.png")).convert_alpha(),
	'>': pygame.image.load(os.path.join("images", "holel.png")).convert_alpha(),
	'<': pygame.image.load(os.path.join("images", "holer.png")).convert_alpha(),
	'^': pygame.image.load(os.path.join("images", "holed.png")).convert_alpha(),
	'v': pygame.image.load(os.path.join("images", "holeu.png")).convert_alpha(),
	'p': pygame.image.load(os.path.join("images", "powerup.png")).convert_alpha()
}
overhole = textwindow.subsurface(0,0,32,32)
homeol = images['h'].subsurface(32,0,32,32)
safeol = pygame.image.load(os.path.join("images", "safe2.png")).convert_alpha()
nightvision1 = pygame.Surface((160,160))
nightvision2 = pygame.Surface((160,160))
nightvision3 = pygame.Surface((0,0))
nightsurf = pygame.Surface((160,160))
nightsurf.set_colorkey((0,0,0))
nightsurf2 = pygame.Surface((0,0))
nightsurf2.set_colorkey((0,0,0))
light1 = pygame.image.load(os.path.join("images", "light1.png")).convert_alpha()
light2 = pygame.image.load(os.path.join("images", "light2.png")).convert_alpha()
light3 = pygame.image.load(os.path.join("images", "light3.png")).convert_alpha()
nightsight1 = pygame.image.load(os.path.join("images", "sight.png")).convert_alpha()
icec = pygame.image.load(os.path.join("images", "icec.png")).convert_alpha()
icem = pygame.image.load(os.path.join("images", "icem.png")).convert_alpha()
slash = pygame.image.load(os.path.join("images", "slash.png")).convert_alpha()
border = pygame.image.load(os.path.join("images", "border.png")).convert_alpha()
bordsurfs = (
	border.subsurface(0,0,32,2), border.subsurface(0,1,32,2), border.subsurface(0,2,32,2), border.subsurface(0,3,32,2),
	border.subsurface(0,4,32,2), border.subsurface(0,5,32,2), border.subsurface(0,6,32,2), border.subsurface(0,7,32,2),
	border.subsurface(0,8,32,2), border.subsurface(0,9,32,2), border.subsurface(0,10,32,2), border.subsurface(0,11,32,2),
	border.subsurface(0,12,32,2), border.subsurface(0,13,32,2), border.subsurface(0,14,32,2), border.subsurface(0,15,32,2),
	border.subsurface(0,16,32,2), border.subsurface(0,17,32,2), border.subsurface(0,18,32,2), border.subsurface(0,19,32,2),
	border.subsurface(0,20,32,2), border.subsurface(0,21,32,2), border.subsurface(0,22,32,2), border.subsurface(0,23,32,2),
	border.subsurface(0,24,32,2), border.subsurface(0,25,32,2), border.subsurface(0,26,32,2), border.subsurface(0,27,32,2),
	border.subsurface(0,28,32,2), border.subsurface(0,29,32,2), border.subsurface(0,30,32,2),
	
	border.subsurface(0,0,2,32), border.subsurface(1,0,2,32), border.subsurface(2,0,2,32), border.subsurface(3,0,2,32),
	border.subsurface(4,0,2,32), border.subsurface(5,0,2,32), border.subsurface(6,0,2,32), border.subsurface(7,0,2,32),
	border.subsurface(8,0,2,32), border.subsurface(9,0,2,32), border.subsurface(10,0,2,32), border.subsurface(11,0,2,32),
	border.subsurface(12,0,2,32), border.subsurface(13,0,2,32), border.subsurface(14,0,2,32), border.subsurface(15,0,2,32),
	border.subsurface(16,0,2,32), border.subsurface(17,0,2,32), border.subsurface(18,0,2,32), border.subsurface(19,0,2,32),
	border.subsurface(20,0,2,32), border.subsurface(21,0,2,32), border.subsurface(22,0,2,32), border.subsurface(23,0,2,32),
	border.subsurface(24,0,2,32), border.subsurface(25,0,2,32), border.subsurface(26,0,2,32), border.subsurface(27,0,2,32),
	border.subsurface(28,0,2,32), border.subsurface(29,0,2,32), border.subsurface(30,0,2,32)
)
instrimgs = (
	pygame.image.load(os.path.join("images", "instr1.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "instr2.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "instr3.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "instr4.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "instr5.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "instr6.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "instr7.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "instr8.png")).convert_alpha()
)


winners = ((f.render("Cat wins!", 1, (5,235,255)).convert_alpha(), (361,270)), (f.render("Mouse wins!", 1, (5,235,255)).convert_alpha(), (348,270)), (f.render("Success!", 1, (5,235,255)).convert_alpha(), (365,270)), (f.render("Caught!", 1, (5,235,255)).convert_alpha(), (368,270)))
powtext = (f2.render("Super Speed", 1, (255,20,20)).convert_alpha(), f2.render("Super Stamina", 1, (0,127,0)).convert_alpha(), f2.render("Freeze", 1, (20,20,255)).convert_alpha())

Cat.getstuff((images['a'], icec), (pounce, meow))
Mouse.getstuff((images['m'], icem), (sprint, mousewin, catwin))
Item.getstuff((images['t'], images['>'], images['<'], images['^'], images['v'], images['w'], images['c'], images['p'], safeol, overhole, light1, light2, light3), (trap, lightoff, lighton, pupup)) 
cheeses = pygame.sprite.Group()
traps = pygame.sprite.Group()
holes = pygame.sprite.Group()
powerups = pygame.sprite.Group()
lights = pygame.sprite.Group()
lspawns = []


def newlevel(level, cdirs, mdirs):
	global cat, mouse, bounds, homecell, safes, walls, lspawns
	cheeses.empty()
	traps.empty()
	holes.empty()
	powerups.empty()
	lights.empty()
	lspawns = []
	safes = []
	walls = []
	if start == 10:
		data = [line.strip() for line in open(os.path.join("levels", "map%d.txt"%level))]
	elif start == 12:
		data = [line.strip() for line in open(os.path.join("levels", "mmap%d.txt"%level))]
	else:
		data = [line.strip() for line in open(os.path.join("levels", "tmap%d.txt"%level))]
	bounds = data[1:19]
	Mouse.setlevel(bounds)
	if start == 10 or start == 11 and level < 6:
		Cat.setlevel(bounds)
	else:
		Item.setlevel(bounds)
	for y, row in enumerate(bounds):
		for x, cell in enumerate(row):
			if cell is 'w':
				sides = []
				if y > 0:
					if bounds[y-1][x] != 'w':
						sides.append(1)
				if y < 17:
					if bounds[y+1][x] != 'w':
						sides.append(2)
				if x > 0:
					if bounds[y][x-1] != 'w':
						sides.append(3)
				if x < 24:
					if bounds[y][x+1] != 'w':
						sides.append(4)
				walls.append(((x,y), tuple(sides), random.randint(0,30)))
			elif cell is 'h' or cell is '<' or cell is '>' or cell is '^' or cell is 'v':
				holes.add(Item.Hole((32*x,32*y), cell))
				if cell is 'h':
					cell = 'w'
			elif cell is 'a':
				cat = Cat.Cat((32*x,32*y), cdirs)
				cell = '.'
			elif cell is 'l':
				lspawns.append((x,y))
				cell = '.'
			elif cell is 'm':
				mouse = Mouse.Mouse((32*x,32*y), mdirs)
			elif cell is 'c':
				cheeses.add(Item.Cheese((32*x,32*y)))
			elif cell is 't':
				traps.add(Item.Trap((32*x,32*y)))
			if cell is '.' or cell is 's' or cell is 't' or cell is 'm' or cell is 'c':
				background.blit(images['.'].subsurface(random.randint(0,32), random.randint(0,32), 32, 32), (32*x,32*y))
			else:
				background.blit(images[cell], (32*x,32*y))
			if cell is 's' or cell is 'm' or cell is 'c':
				background.blit(images['s'], (32*x,32*y))
				if cell is 's':
					safes.append((x,y))
			if cell is 'm':
				background.blit(images['h'].subsurface(0,0,32,32), (32*x,32*y))
				homecell = (x,y)
			if x == 24:
				break

	if start == 12:
		if difficulty > 0:
			lights.add(Item.Light(lspawns[0], 1))
		if difficulty > 1:
			lights.add(Item.Light(lspawns[1], 0))
			lights.add(Item.Light(lspawns[2], 2))
			lights.add(Item.Light(lspawns[3], 0))
	if start == 11:
		if level > 6:
			lights.add(Item.Light(lspawns[0], 1))
		if level == 8:
			lights.add(Item.Light(lspawns[1], 0))
			lights.add(Item.Light(lspawns[2], 2))
			lights.add(Item.Light(lspawns[3], 0))


menus = (
	Menu.Menu(0, ("Multiplayer", "Single - Mouse", "Instructions", "Options"), (10, 12, 11, 4), f, (339,140), 25, (10,10,10), False, (255,20,20)),
	Menu.Menu(4, ("Multi Powerups:", "Lightning Mode:", "Multi Night Mode:", "Nightvision Sight:", "Single Difficulty:", "Fullscreen Mode:", "Back"), (6, 6, 6, 6, 6, 6, 0), f, (298,114), 12, (10,10,10), False, (255,20,20)),
	Menu.Menu(5, ("Continue", "Options", "Main Menu"), (10, 4, 0), f, (357,134), 25, (10,10,10), False, (255,20,20)),
)
activemenu = menus[0]

while 1:
	mouse1 = pygame.mouse.get_pos()
	delta = clock.tick(30)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.MOUSEMOTION:
			activemenu.checkmouse(mouse1)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			activemenu.checkmouse(mouse1)
		elif event.type == pygame.MOUSEBUTTONUP:
			if activemenu.checkmouse(mouse1):
				if activemenu.highlight != 0:
					start = activemenu.nodes[activemenu.highlight-1]
			if activemenu.id == 4:
				if mouse1[0] >= 455 and mouse1[0] <= 494 and mouse1[1] >= 114 and mouse1[1] <= 135:
					start = 6
					activemenu.highlight = 1
				elif mouse1[0] >= 455 and mouse1[0] <= 486 and mouse1[1] >= 147 and mouse1[1] <= 168:
					start = 6
					activemenu.highlight = 2
				elif mouse1[0] >= 455 and mouse1[0] <= 494 and mouse1[1] >= 180 and mouse1[1] <= 201:
					start = 6
					activemenu.highlight = 3
				elif mouse1[0] >= 455 and mouse1[0] <= 521 and mouse1[1] >= 213 and mouse1[1] <= 234:
					start = 6
					activemenu.highlight = 4
				elif mouse1[0] >= 455 and mouse1[0] <= 521 and mouse1[1] >= 246 and mouse1[1] <= 267:
					start = 6
					activemenu.highlight = 5
				elif mouse1[0] >= 455 and mouse1[0] <= 486 and mouse1[1] >= 279 and mouse1[1] <= 300:
					start = 6
					activemenu.highlight = 6
			if start == 6:
				activemenu.update()
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				activemenu.movehighlight(-1)
				mdir = (mdir[0], mdir[1]-1)
			elif event.key == pygame.K_DOWN:
				activemenu.movehighlight(1)
				mdir = (mdir[0], mdir[1]+1)
			elif event.key == pygame.K_LEFT:
				mdir = (mdir[0]-1, mdir[1])
			elif event.key == pygame.K_RIGHT:
				mdir = (mdir[0]+1, mdir[1])
			elif event.key == pygame.K_z:
				cdir = (cdir[0], cdir[1]-1)
			elif event.key == pygame.K_s:
				cdir = (cdir[0], cdir[1]+1)
			elif event.key == pygame.K_q:
				cdir = (cdir[0]-1, cdir[1])
			elif event.key == pygame.K_d:
				cdir = (cdir[0]+1, cdir[1])
			elif event.key == pygame.K_RETURN:
				if activemenu.highlight != 0:
					start = activemenu.nodes[activemenu.highlight-1]
			elif event.key == pygame.K_ESCAPE:
				if activemenu.id == 0:
					sys.exit()
				else:
					start = activemenu.nodes[len(activemenu.nodes)-1]
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_UP:
				mdir = (mdir[0], mdir[1]+1)
			elif event.key == pygame.K_DOWN:
				mdir = (mdir[0], mdir[1]-1)
			elif event.key == pygame.K_LEFT:
				mdir = (mdir[0]+1, mdir[1])
			elif event.key == pygame.K_RIGHT:
				mdir = (mdir[0]-1, mdir[1])
			elif event.key == pygame.K_z:
				cdir = (cdir[0], cdir[1]+1)
			elif event.key == pygame.K_s:
				cdir = (cdir[0], cdir[1]-1)
			elif event.key == pygame.K_q:
				cdir = (cdir[0]+1, cdir[1])
			elif event.key == pygame.K_d:
				cdir = (cdir[0]-1, cdir[1])

	if mdir[0] < -1:
		mdir = (-1, mdir[1])
	elif mdir[0] > 1:
		mdir = (1, mdir[1])
	if mdir[1] < -1:
		mdir = (mdir[0], -1)
	elif mdir[1] > 1:
		mdir = (mdir[0], 1)
	if cdir[0] < -1:
		cdir = (-1, cdir[1])
	elif cdir[0] > 1:
		cdir = (1, cdir[1])
	if cdir[1] < -1:
		cdir = (cdir[0], -1)
	elif cdir[1] > 1:
		cdir = (cdir[0], 1)

	if start != activemenu.id:
		if start == 6:
			start = 4
			if activemenu.highlight == 1:
				pupson = (pupson + 1) % 3
			elif activemenu.highlight == 2:
				if lightning == 2:
					lightning = 1
				else:
					lightning = 2
			elif activemenu.highlight == 3:
				if nightvision:
					nightvision = False
				else:
					nightvision = True
			elif activemenu.highlight == 4:
				vision = (vision + 1) % 3
			elif activemenu.highlight == 5:
				difficulty = (difficulty + 1) % 3
			elif activemenu.highlight == 6:
				if fson:
					screen = pygame.display.set_mode((800,640))
					fson = False
				else:
					screen = pygame.display.set_mode((800,640), pygame.FULLSCREEN)
					fson = True
		for menu in menus:
			if menu.id == start:
				activemenu = menu
				break

	screen.blit(background, (0,0))
	if activemenu.id == 0 or activemenu.id == 4:
		screen.blit(menupaper, (250,99))
	if activemenu.id == 4:
		if pupson == 0:
			screen.blit(f.render("Off", 1, (220,0,0)), (455,114))
		elif pupson == 1:
			screen.blit(f.render("Low", 1, (0,0,220)), (455,114))
		else:
			screen.blit(f.render("High", 1, (0,220,0)), (455,114))
		if lightning == 2:
			screen.blit(f.render("On", 1, (0,220,0)), (455,147))
		else:
			screen.blit(f.render("Off", 1, (220,0,0)), (455,147))
		if nightvision:
			screen.blit(f.render("On", 1, (0,220,0)), (455,180))
		else:
			screen.blit(f.render("Off", 1, (220,0,0)), (455,180))
		if vision == 0:
			screen.blit(f.render("Low", 1, (220,0,0)), (455,213))
		elif vision == 1:
			screen.blit(f.render("Medium", 1, (0,0,220)), (455,213))
		else:
			screen.blit(f.render("High", 1, (0,220,0)), (455,213))
		if difficulty == 0:
			screen.blit(f.render("Easy", 1, (220,0,0)), (455,246))
		elif difficulty == 1:
			screen.blit(f.render("Medium", 1, (0,0,220)), (455,246))
		else:
			screen.blit(f.render("Hard", 1, (0,220,0)), (455,246))
		if fson:
			screen.blit(f.render("On", 1, (0,220,0)), (455,279))
		else:
			screen.blit(f.render("Off", 1, (220,0,0)), (455,279))
	activemenu.draw(screen)
	pygame.display.flip()

	while start >= 10:
		if start == 10:
			#pygame.mixer.music.stop()
			#pygame.mixer.music.load(multimusic)
			#pygame.mixer.music.play(-1)
			pass
		elif start == 12:
			#pygame.mixer.music.stop()
			#pygame.mixer.music.load(nightmusic)
			#pygame.mixer.music.play(-1)
			pass
		background = pygame.Surface((800,576))
		background.fill((0,0,0))
		timeleft = 120999
		if pupson == 1:
			powertimer = 15000
		elif pupson == 2:
			powertimer = 5000
		usedpows = []
		usedlevs = []
		mousescore = 0
		catscore = 0
		level = 1
		newlevel(level, cdir, mdir)
		nextlevel = False
		pause = False
		endgame = False
		pausestart = 5
		tutnext = False
		winner = 0

		while not nextlevel:
			while pause:
				mouse1 = pygame.mouse.get_pos()
				delta = clock.tick(30)
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						sys.exit()
					elif event.type == pygame.MOUSEMOTION:
						activemenu.checkmouse(mouse1)
					elif event.type == pygame.MOUSEBUTTONDOWN:
						activemenu.checkmouse(mouse1)
					elif event.type == pygame.MOUSEBUTTONUP:
						if activemenu.checkmouse(mouse1):
							if activemenu.highlight != 0:
								pausestart = activemenu.nodes[activemenu.highlight-1]
						if activemenu.id == 4:
							if mouse1[0] >= 455 and mouse1[0] <= 494 and mouse1[1] >= 114 and mouse1[1] <= 135:
								pausestart = 6
								activemenu.highlight = 1
							elif mouse1[0] >= 455 and mouse1[0] <= 486 and mouse1[1] >= 147 and mouse1[1] <= 168:
								pausestart = 6
								activemenu.highlight = 2
							elif mouse1[0] >= 455 and mouse1[0] <= 494 and mouse1[1] >= 180 and mouse1[1] <= 201:
								pausestart = 6
								activemenu.highlight = 3
							elif mouse1[0] >= 455 and mouse1[0] <= 521 and mouse1[1] >= 213 and mouse1[1] <= 234:
								pausestart = 6
								activemenu.highlight = 4
							elif mouse1[0] >= 455 and mouse1[0] <= 521 and mouse1[1] >= 246 and mouse1[1] <= 267:
								pausestart = 6
								activemenu.highlight = 5
							elif mouse1[0] >= 455 and mouse1[0] <= 486 and mouse1[1] >= 279 and mouse1[1] <= 300:
								pausestart = 6
								activemenu.highlight = 6
						if start == 6:
							activemenu.update()
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_SPACE and pausestart == 5:
							pause = False
							mouse.pause(False)
							if start == 10:
								cat.pause(False)
							delta = clock.tick()
							if pupson == 0:
								powerups.empty()
							elif pupson == 1:
								for powerup in powerups:
									if len(powerups) > 2:
										powerups.remove(powerup)
									else:
										break
								powertimer = (timeleft - 15999) % 20000
							elif start == 10:
								powertimer = (timeleft + 4000) % 10000
							if start == 12:
								if difficulty == 0:
									for light in lights:
										lights.remove(light)
								elif difficulty == 1:
									if len(lights) == 4:
										for light in lights:
											if light.size != 1:
												lights.remove(light)
									elif len(lights) == 0:
										lights.add(Item.Light(lspawns[0], 1))
								else:
									if len(lights) == 0:
										lights.add(Item.Light(lspawns[0], 1))
									if len(lights) == 1:
										lights.add(Item.Light(lspawns[1], 0))
										lights.add(Item.Light(lspawns[2], 2))
										lights.add(Item.Light(lspawns[3], 0))
						elif event.key == pygame.K_RETURN:
							if activemenu.highlight != 0:
								pausestart = activemenu.nodes[activemenu.highlight-1]
						elif event.key == pygame.K_UP:
							activemenu.movehighlight(-1)
							mouse.move(0,-1)
						elif event.key == pygame.K_DOWN:
							activemenu.movehighlight(1)
							mouse.move(0,1)
						elif event.key == pygame.K_LEFT:
							mouse.move(-1, 0)
						elif event.key == pygame.K_RIGHT:
							mouse.move(1,0)
						elif event.key == pygame.K_z:
							if start == 10:
								cat.move(0,-1)
							else:
								cdir = (cdir[0], cdir[1]-1)
						elif event.key == pygame.K_q:
							if start == 10:
								cat.move(-1,0)
							else:
								cdir = (cdir[0]-1, cdir[1])
						elif event.key == pygame.K_s:
							if start == 10:
								cat.move(0,1)
							else:
								cdir = (cdir[0], cdir[1]+1)
						elif event.key == pygame.K_d:
							if start == 10:
								cat.move(1,0)
							else:
								cdir = (cdir[0]+1, cdir[1])
						elif event.key == pygame.K_ESCAPE:
							if pausestart == 5:
								pause = False
								endgame = True
								nextlevel = True
								if start == 10:
									cdir = (cat.xspeed, cat.yspeed)
								mdir = (mouse.xspeed, mouse.yspeed)
								start = 0
								#pygame.mixer.music.stop()
								#pygame.mixer.music.load(titlemusic)
								#pygame.mixer.music.play(-1)
							else:
								pausestart = 5
					elif event.type == pygame.KEYUP:
						if event.key == pygame.K_UP:
							mouse.stopmove(0,-1)
						elif event.key == pygame.K_DOWN:
							mouse.stopmove(0,1)
						elif event.key == pygame.K_LEFT:
							mouse.stopmove(-1, 0)
						elif event.key == pygame.K_RIGHT:
							mouse.stopmove(1,0)
						elif event.key == pygame.K_z:
							if start == 10:
								cat.stopmove(0,-1)
							else:
								cdir = (cdir[0], cdir[1]+1)
						elif event.key == pygame.K_q:
							if start == 10:
								cat.stopmove(-1,0)
							else:
								cdir = (cdir[0]+1, cdir[1])
						elif event.key == pygame.K_s:
							if start == 10:
								cat.stopmove(0,1)
							else:
								cdir = (cdir[0], cdir[1]-1)
						elif event.key == pygame.K_d:
							if start == 10:
								cat.stopmove(1,0)
							else:
								cdir = (cdir[0]-1, cdir[1])
				if mdir[0] < -1:
					mdir = (-1, mdir[1])
				elif mdir[0] > 1:
					mdir = (1, mdir[1])
				if mdir[1] < -1:
					mdir = (mdir[0], -1)
				elif mdir[1] > 1:
					mdir = (mdir[0], 1)
				if cdir[0] < -1:
					cdir = (-1, cdir[1])
				elif cdir[0] > 1:
					cdir = (1, cdir[1])
				if cdir[1] < -1:
					cdir = (cdir[0], -1)
				elif cdir[1] > 1:
					cdir = (cdir[0], 1)

				if pausestart != activemenu.id:
					if pausestart == 6:
						pausestart = 4
						if activemenu.highlight == 1:
							pupson = (pupson + 1) % 3
						elif activemenu.highlight == 2:
							if lightning == 2:
								lightning = 1
							else:
								lightning = 2
						elif activemenu.highlight == 3:
							if nightvision:
								nightvision = False
							else:
								nightvision = True
						elif activemenu.highlight == 4:
							vision = (vision + 1) % 3
						elif activemenu.highlight == 5:
							difficulty = (difficulty + 1) % 3
						elif activemenu.highlight == 6:
							if fson:
								screen = pygame.display.set_mode((800,640))
								fson = False
							else:
								screen = pygame.display.set_mode((800,640), pygame.FULLSCREEN)
								fson = True
					if pausestart == 0 and activemenu.id == 4:
						pausestart = 5
					elif pausestart == 0:
						#pygame.mixer.music.stop()
						#pygame.mixer.music.load(titlemusic)
						#pygame.mixer.music.play(-1)
						pause = False
						endgame = True
						nextlevel = True
						if start == 10:
							cdir = (cat.xspeed, cat.yspeed)
						mdir = (mouse.xspeed, mouse.yspeed)
						start = 0
					if pausestart == 10:
						pause = False
						mouse.pause(False)
						if start == 10:
							cat.pause(False)
						if pupson == 0:
							powerups.empty()
						elif pupson == 1:
							for powerup in powerups:
								if len(powerups) > 2:
									powerups.remove(powerup)
								else:
									break
							powertimer = (timeleft - 15999) % 20000
						elif start == 10:
							powertimer = (timeleft + 4000) % 10000
						if start == 12:
							if difficulty == 0:
								for light in lights:
									lights.remove(light)
							elif difficulty == 1:
								if len(lights) == 4:
									for light in lights:
										if light.size != 1:
											lights.remove(light)
								elif len(lights) == 0:
									lights.add(Item.Light(lspawns[0], 1))
							else:
								if len(lights) == 0:
									lights.add(Item.Light(lspawns[0], 1))
								if len(lights) == 1:
									lights.add(Item.Light(lspawns[1], 0))
									lights.add(Item.Light(lspawns[2], 2))
									lights.add(Item.Light(lspawns[3], 0))
						delta = clock.tick()
					for menu in menus:
						if menu.id == pausestart:
							activemenu = menu
							break

				screen.blit(menupaper, (250,99))
				if activemenu.id == 4:
					if pupson == 0:
						screen.blit(f.render("Off", 1, (220,0,0)), (455,114))
					elif pupson == 1:
						screen.blit(f.render("Low", 1, (0,0,220)), (455,114))
					else:
						screen.blit(f.render("High", 1, (0,220,0)), (455,114))
					if lightning == 2:
						screen.blit(f.render("On", 1, (0,220,0)), (455,147))
					else:
						screen.blit(f.render("Off", 1, (220,0,0)), (455,147))
					if nightvision:
						screen.blit(f.render("On", 1, (0,220,0)), (455,180))
					else:
						screen.blit(f.render("Off", 1, (220,0,0)), (455,180))
					if vision == 0:
						screen.blit(f.render("Low", 1, (220,0,0)), (455,213))
					elif vision == 1:
						screen.blit(f.render("Medium", 1, (0,0,220)), (455,213))
					else:
						screen.blit(f.render("High", 1, (0,220,0)), (455,213))
					if difficulty == 0:
						screen.blit(f.render("Easy", 1, (0,220,0)), (455,246))
					elif difficulty == 1:
						screen.blit(f.render("Medium", 1, (0,0,220)), (455,246))
					else:
						screen.blit(f.render("Hard", 1, (220,0,0)), (455,246))
					if fson:
						screen.blit(f.render("On", 1, (0,220,0)), (455,279))
					else:
						screen.blit(f.render("Off", 1, (220,0,0)), (455,279))
				activemenu.draw(screen)
				pygame.display.flip()

			if not endgame:
				delta = clock.tick(30)
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						sys.exit()
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_UP:
							mouse.move(0,-1,lightning)
						elif event.key == pygame.K_DOWN:
							mouse.move(0,1,lightning)
						elif event.key == pygame.K_LEFT:
							mouse.move(-1,0,lightning)
						elif event.key == pygame.K_RIGHT:
							mouse.move(1,0,lightning)
						elif event.key == pygame.K_RSHIFT:
							mouse.sprint(lights)
						elif event.key == pygame.K_z:
							if start == 10 or start == 11 and level < 6:
								cat.move(0,-1)
							else:
								cdir = (cdir[0], cdir[1]-1)
						elif event.key == pygame.K_q:
							if start == 10 or start == 11 and level < 6:
								cat.move(-1,0)
							else:
								cdir = (cdir[0]-1, cdir[1])
						elif event.key == pygame.K_s:
							if start == 10 or start == 11 and level < 6:
								cat.move(0,1)
							else:
								cdir = (cdir[0], cdir[1]+1)
						elif event.key == pygame.K_d:
							if start == 10 or start == 11 and level < 6:
								cat.move(1,0)
							else:
								cdir = (cdir[0]+1, cdir[1])
						elif event.key == pygame.K_LCTRL:
							if start == 10 or start == 11 and level < 6:
								cat.pounce()
						elif event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
							if start == 11:
								if event.key == pygame.K_ESCAPE:
									endgame = True
									nextlevel = True
									if level < 6:
										cdir = (cat.xspeed, cat.yspeed)
									mdir = (mouse.xspeed, mouse.yspeed)
									start = 0
									background = menuimg
							else:
								pause = True
								mouse.pause(True)
								if start == 10:
									cat.pause(True)
						elif event.key == pygame.K_n:
							if start == 11 and level != 8:
								nextlevel = True
								tutnext = True
						elif event.key == pygame.K_b:
							if start == 11:
								nextlevel = True
								endgame = True
								tutnext = True
					elif event.type == pygame.KEYUP:
						if event.key == pygame.K_UP:
							mouse.stopmove(0,-1)
						elif event.key == pygame.K_DOWN:
							mouse.stopmove(0,1)
						elif event.key == pygame.K_LEFT:
							mouse.stopmove(-1,0)
						elif event.key == pygame.K_RIGHT:
							mouse.stopmove(1,0)
						elif event.key == pygame.K_z:
							if start == 10 or start == 11 and level < 6:
								cat.stopmove(0,-1)
							else:
								cdir = (cdir[0], cdir[1]+1)
						elif event.key == pygame.K_q:
							if start == 10 or start == 11 and level < 6:
								cat.stopmove(-1,0)
							else:
								cdir = (cdir[0]+1, cdir[1])
						elif event.key == pygame.K_s:
							if start == 10 or start == 11 and level < 6:
								cat.stopmove(0,1)
							else:
								cdir = (cdir[0], cdir[1]-1)
						elif event.key == pygame.K_d:
							if start == 10 or start == 11 and level < 6:
								cat.stopmove(1,0)
							else:
								cdir = (cdir[0]-1, cdir[1])
				if mdir[0] < -1:
					mdir = (-1, mdir[1])
				elif mdir[0] > 1:
					mdir = (1, mdir[1])
				if mdir[1] < -1:
					mdir = (mdir[0], -1)
				elif mdir[1] > 1:
					mdir = (mdir[0], 1)
				if cdir[0] < -1:
					cdir = (-1, cdir[1])
				elif cdir[0] > 1:
					cdir = (1, cdir[1])
				if cdir[1] < -1:
					cdir = (cdir[0], -1)
				elif cdir[1] > 1:
					cdir = (cdir[0], 1)

				if pupson != 0 and start == 10:
					for powerup in powerups:
						if powerup.update(lightning):
							okay = False
							while not okay:
								okay = True
								cell = (random.randint(1,23), random.randint(1,13))
								if bounds[cell[1]][cell[0]] not in ('.', 'a') or cell in usedpows:
									okay = False
								if abs(cell[0] - mouse.cell[0]) < 4 and abs(cell[1] - mouse.cell[1]) < 4 or abs(cell[0] - cat.cell[0]) < 4 and abs(cell[1] - cat.cell[1]) < 4:
									okay = False
								for pup in powerups:
									if pup.cell == cell:
										okay = False
							powerup.move(cell)
							usedpows.append(cell)

					powertimer -= delta * lightning
					if powertimer <= 0:
						if pupson == 1:
							if len(powerups) < 2:
								okay = False
								while not okay:
									okay = True
									cell = (random.randint(1,23), random.randint(1,13))
									if bounds[cell[1]][cell[0]] not in ('.', 'a') or cell in usedpows:
										okay = False
									if abs(cell[0] - mouse.cell[0]) < 4 and abs(cell[1] - mouse.cell[1]) < 4 or abs(cell[0] - cat.cell[0]) < 4 and abs(cell[1] - cat.cell[1]) < 4:
										okay = False
									for powerup in powerups:
										if powerup.cell == cell:
											okay = False
								powerups.add(Item.Powerup(cell, random.randint(1,9)))
								usedpows.append(cell)
							powertimer = 20000
						else:
							if len(powerups) < 4:
								okay = False
								while not okay:
									okay = True
									cell = (random.randint(1,23), random.randint(1,13))
									if bounds[cell[1]][cell[0]] not in ('.', 'a') or cell in usedpows:
										okay = False
									if abs(cell[0] - mouse.cell[0]) < 4 and abs(cell[1] - mouse.cell[1]) < 4 or abs(cell[0] - cat.cell[0]) < 4 and abs(cell[1] - cat.cell[1]) < 4:
										okay = False
									for powerup in powerups:
										if powerup.cell == cell:
											okay = False
								powerups.add(Item.Powerup(cell, random.randint(1,9)))
								usedpows.append(cell)
							powertimer = 10000

				if start == 10 or start == 11 and level < 6:
					mouse.update(cheeses, traps, lightning, powerups, lights, cat)
					cat.update(traps, lightning, powerups, mouse)
				else:
					mouse.update(cheeses, traps, lightning, powerups, lights)
					lights.update(lightning, mouse.rect, lights)
					if start == 11 and level > 6:
						for light in lights:
							if light.rect.bottom < 320:
								light.yvel *= -1

				if start == 12 or start == 11 and level > 6:
					if alarmtimer > 0:
						oldtimer = alarmtimer
						for light in lights:
							if light.alert:
								alarmtimer -= 1
								if alarmtimer <= 0:
									alarm.play()
									alarmtimer = 25
								break
						if alarmtimer == oldtimer:
							alarmtimer = 0
					else:
						for light in lights:
							if light.alert:
								alarm.play()
								alarmtimer = 25
								break

				if start != 11:
					timeleft -= delta * lightning
				if mouse.checkwin():
					nextlevel = True
					if start == 12 or start == 11 and level > 5:
						winner = 2
					else:
						winner = 1
					mousescore += mouse.cheesecount
					mousewin.play()
				elif start == 12 or start == 11 and level > 5:
					if timeleft < 1000 or mouse.checklose(lights):
						nextlevel = True
						winner = 3
						catscore += 1
						catwin.play()
				elif start == 10 or start == 11 and level < 6:
					if cat.checkwin(mouse.rect) or timeleft < 1000:
						nextlevel = True
						winner = 0
						catscore += 1
						catwin.play()

				if start == 10 and not nightvision or start == 11 and level < 6:
					screen.blit(background, (0,64))
					for cheese in cheeses:
						cheese.draw(screen, False)
					for powerup in powerups:
						powerup.draw(screen, False)
					for trap in traps:
						trap.draw(screen, False)
					mouse.draw(screen)
					cat.draw(screen)
					for hole in holes:
						hole.draw(screen, False, mouse.rect, mouse.checkhole())
					if mouse.checkhole():
						mouse.draw(screen)
				elif start == 10:
					screen.blit(black, (0,64))
					if vision != 0:
						for cheese in cheeses:
							if vision == 2 or vision == 1 and (cheese.cell in cat.encells or cheese.cell in mouse.encells):
								cheese.draw(screen, True)
						for wall in walls:
							if vision == 2 or vision == 1 and (wall[0] in cat.encells or wall[0] in mouse.encells):
								for b in wall[1]:
									if b == 1:
										screen.blit(bordsurfs[wall[2]], (wall[0][0]*32, wall[0][1]*32+63))
									elif b == 2:
										screen.blit(bordsurfs[wall[2]], (wall[0][0]*32, wall[0][1]*32+95))
									elif b == 3:
										screen.blit(bordsurfs[wall[2]+31], (wall[0][0]*32-1, wall[0][1]*32+64))
									else:
										screen.blit(bordsurfs[wall[2]+31], (wall[0][0]*32+31, wall[0][1]*32+64))
						for hole in holes:
							if vision == 2 or vision == 1 and (hole.cell in cat.encells or hole.cell in mouse.encells):
								hole.draw(screen, True, mouse.rect, mouse.checkhole())
						if vision == 2 or vision == 1 and (homecell in cat.encells or homecell in mouse.encells):
							screen.blit(homeol, (homecell[0]*32, homecell[1]*32+64))
						for safe in safes:
							if vision == 2 or vision == 1 and (safe in cat.encells or safe in mouse.encells):
								screen.blit(safeol, (safe[0]*32, safe[1]*32+64))
						for trap in traps:
							if vision == 2 or vision == 1 and (trap.cell in cat.encells or trap.cell in mouse.encells):
								trap.draw(screen, True)
						for powerup in powerups:
							if vision == 2:
								powerup.draw(screen, True)

					if cat.face == 0:
						nightvision1.blit(background, (-24-cat.rect.left, 69-cat.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision1, False, (cat.rect.left+24, cat.rect.top-5))
						for powerup in powerups:
							powerup.draw(nightvision1, False, (cat.rect.left+24, cat.rect.top-5))
						for trap in traps:
							trap.draw(nightvision1, False, (cat.rect.left+24, cat.rect.top-5))
						mouse.draw(nightvision1, (cat.rect.left+24, cat.rect.top-5))
						cat.draw(nightvision1, (cat.rect.left+24, cat.rect.top-5))
						for hole in holes:
							hole.draw(nightvision1, False, mouse.rect, mouse.checkhole(), (cat.rect.left+24, cat.rect.top-5))
						nightsurf.blit(nightvision1, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (cat.rect.left+24, cat.rect.top-5))
					elif cat.face == 90:
						nightvision1.blit(background, (69-cat.rect.left, 184-cat.rect.bottom))
						for cheese in cheeses:
							cheese.draw(nightvision1, False, (cat.rect.left-69, cat.rect.bottom-120))
						for powerup in powerups:
							powerup.draw(nightvision1, False, (cat.rect.left-69, cat.rect.bottom-120))
						for trap in traps:
							trap.draw(nightvision1, False, (cat.rect.left-69, cat.rect.bottom-120))
						mouse.draw(nightvision1, (cat.rect.left-69, cat.rect.bottom-120))
						cat.draw(nightvision1, (cat.rect.left-69, cat.rect.bottom-120))
						for hole in holes:
							hole.draw(nightvision1, False, mouse.rect, mouse.checkhole(), (cat.rect.left-69, cat.rect.bottom-120))
						nightsurf.blit(nightvision1, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (cat.rect.left-69, cat.rect.bottom-120))
					elif cat.face == 180:
						nightvision1.blit(background, (184-cat.rect.right, 69-cat.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision1, False, (cat.rect.right-184, cat.rect.top-5))
						for powerup in powerups:
							powerup.draw(nightvision1, False, (cat.rect.right-184, cat.rect.top-5))
						for trap in traps:
							trap.draw(nightvision1, False, (cat.rect.right-184, cat.rect.top-5))
						mouse.draw(nightvision1, (cat.rect.right-184, cat.rect.top-5))
						cat.draw(nightvision1, (cat.rect.right-184, cat.rect.top-5))
						for hole in holes:
							hole.draw(nightvision1, False, mouse.rect, mouse.checkhole(), (cat.rect.right-184, cat.rect.top-5))
						nightsurf.blit(nightvision1, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (cat.rect.right-184, cat.rect.top-5))
					else:
						nightvision1.blit(background, (69-cat.rect.left, -24-cat.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision1, False, (cat.rect.left-69, cat.rect.top+88))
						for powerup in powerups:
							powerup.draw(nightvision1, False, (cat.rect.left-69, cat.rect.top+88))
						for trap in traps:
							trap.draw(nightvision1, False, (cat.rect.left-69, cat.rect.top+88))
						mouse.draw(nightvision1, (cat.rect.left-69, cat.rect.top+88))
						cat.draw(nightvision1, (cat.rect.left-69, cat.rect.top+88))
						for hole in holes:
							hole.draw(nightvision1, False, mouse.rect, mouse.checkhole(), (cat.rect.left-69, cat.rect.top+88))
						nightsurf.blit(nightvision1, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (cat.rect.left-69, cat.rect.top+88))

					if mouse.face == 0:
						nightvision2.blit(background, (-mouse.rect.left, 73-mouse.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision2, False, (mouse.rect.left, mouse.rect.top-9))
						for powerup in powerups:
							powerup.draw(nightvision2, False, (mouse.rect.left, mouse.rect.top-9))
						for trap in traps:
							trap.draw(nightvision2, False, (mouse.rect.left, mouse.rect.top-9))
						mouse.draw(nightvision2, (mouse.rect.left, mouse.rect.top-9))
						cat.draw(nightvision2, (mouse.rect.left, mouse.rect.top-9))
						for hole in holes:
							hole.draw(nightvision2, False, mouse.rect, mouse.checkhole(), (mouse.rect.left, mouse.rect.top-9))
						if mouse.checkhole():
							mouse.draw(nightvision2, (mouse.rect.left, mouse.rect.top-9))
						nightsurf.blit(nightvision2, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (mouse.rect.left, mouse.rect.top-9))
					elif mouse.face == 90:
						nightvision2.blit(background, (73-mouse.rect.left, 140-mouse.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top-76))
						for powerup in powerups:
							powerup.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top-76))
						for trap in traps:
							trap.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top-76))
						mouse.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top-76))
						cat.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top-76))
						for hole in holes:
							hole.draw(nightvision2, False, mouse.rect, mouse.checkhole(), (mouse.rect.left-73, mouse.rect.top-76))
						if mouse.checkhole():
							mouse.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top-76))
						nightsurf.blit(nightvision2, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (mouse.rect.left-73, mouse.rect.top-76))
					elif mouse.face == 180:
						nightvision2.blit(background, (140-mouse.rect.left, 73-mouse.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision2, False, (mouse.rect.left-140, mouse.rect.top-9))
						for powerup in powerups:
							powerup.draw(nightvision2, False, (mouse.rect.left-140, mouse.rect.top-9))
						for trap in traps:
							trap.draw(nightvision2, False, (mouse.rect.left-140, mouse.rect.top-9))
						mouse.draw(nightvision2, (mouse.rect.left-140, mouse.rect.top-9))
						cat.draw(nightvision2, (mouse.rect.left-140, mouse.rect.top-9))
						for hole in holes:
							hole.draw(nightvision2, False, mouse.rect, mouse.checkhole(), (mouse.rect.left-140, mouse.rect.top-9))
						if mouse.checkhole():
							mouse.draw(nightvision2, (mouse.rect.left-140, mouse.rect.top-9))
						nightsurf.blit(nightvision2, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (mouse.rect.left-140, mouse.rect.top-9))
					else:
						nightvision2.blit(background, (73-mouse.rect.left, -mouse.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top+64))
						for powerup in powerups:
							powerup.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top+64))
						for trap in traps:
							trap.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top+64))
						mouse.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top+64))
						cat.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top+64))
						for hole in holes:
							hole.draw(nightvision2, False, mouse.rect, mouse.checkhole(), (mouse.rect.left-73, mouse.rect.top+64))
						if mouse.checkhole():
							mouse.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top+64))
						nightsurf.blit(nightvision2, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (mouse.rect.left-73, mouse.rect.top+64))

				elif start == 12 or start == 11 and level > 5:
					screen.blit(black, (0,64))
					screen.blit(homeol, (homecell[0]*32, homecell[1]*32+64))
					if vision > 0 or start == 11:
						if vision == 2 and not (start == 11 and level == 8):
							for wall in walls:
								if wall[0] in mouse.encells:
									for b in wall[1]:
										if b == 1:
											screen.blit(bordsurfs[wall[2]], (wall[0][0]*32, wall[0][1]*32+63))
										elif b == 2:
											screen.blit(bordsurfs[wall[2]], (wall[0][0]*32, wall[0][1]*32+95))
										elif b == 3:
											screen.blit(bordsurfs[wall[2]+31], (wall[0][0]*32-1, wall[0][1]*32+64))
										else:
											screen.blit(bordsurfs[wall[2]+31], (wall[0][0]*32+31, wall[0][1]*32+64))
						for safe in safes:
							if safe in mouse.encells:
								screen.blit(safeol, (safe[0]*32, safe[1]*32+64))
						for cheese in cheeses:
							if cheese.cell in mouse.encells:
								cheese.draw(screen, True)
						for trap in traps:
							if trap.cell in mouse.encells:
								trap.draw(screen, True)
						for hole in holes:
							if hole.cell in mouse.encells:
								hole.draw(screen, True, mouse.rect, mouse.checkhole())

					if mouse.face == 0:
						nightvision2.blit(background, (-mouse.rect.left, 73-mouse.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision2, False, (mouse.rect.left, mouse.rect.top-9))
						for powerup in powerups:
							powerup.draw(nightvision2, False, (mouse.rect.left, mouse.rect.top-9))
						for trap in traps:
							trap.draw(nightvision2, False, (mouse.rect.left, mouse.rect.top-9))
						mouse.draw(nightvision2, (mouse.rect.left, mouse.rect.top-9))
						for hole in holes:
							hole.draw(nightvision2, False, mouse.rect, mouse.checkhole(), (mouse.rect.left, mouse.rect.top-9))
						if mouse.checkhole():
							mouse.draw(nightvision2, (mouse.rect.left, mouse.rect.top-9))
						nightsurf.blit(nightvision2, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (mouse.rect.left, mouse.rect.top-9))
					elif mouse.face == 90:
						nightvision2.blit(background, (73-mouse.rect.left, 140-mouse.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top-76))
						for powerup in powerups:
							powerup.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top-76))
						for trap in traps:
							trap.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top-76))
						mouse.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top-76))
						for hole in holes:
							hole.draw(nightvision2, False, mouse.rect, mouse.checkhole(), (mouse.rect.left-73, mouse.rect.top-76))
						if mouse.checkhole():
							mouse.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top-76))
						nightsurf.blit(nightvision2, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (mouse.rect.left-73, mouse.rect.top-76))
					elif mouse.face == 180:
						nightvision2.blit(background, (140-mouse.rect.left, 73-mouse.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision2, False, (mouse.rect.left-140, mouse.rect.top-9))
						for powerup in powerups:
							powerup.draw(nightvision2, False, (mouse.rect.left-140, mouse.rect.top-9))
						for trap in traps:
							trap.draw(nightvision2, False, (mouse.rect.left-140, mouse.rect.top-9))
						mouse.draw(nightvision2, (mouse.rect.left-140, mouse.rect.top-9))
						for hole in holes:
							hole.draw(nightvision2, False, mouse.rect, mouse.checkhole(), (mouse.rect.left-140, mouse.rect.top-9))
						if mouse.checkhole():
							mouse.draw(nightvision2, (mouse.rect.left-140, mouse.rect.top-9))
						nightsurf.blit(nightvision2, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (mouse.rect.left-140, mouse.rect.top-9))
					else:
						nightvision2.blit(background, (73-mouse.rect.left, -mouse.rect.top))
						for cheese in cheeses:
							cheese.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top+64))
						for powerup in powerups:
							powerup.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top+64))
						for trap in traps:
							trap.draw(nightvision2, False, (mouse.rect.left-73, mouse.rect.top+64))
						mouse.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top+64))
						for hole in holes:
							hole.draw(nightvision2, False, mouse.rect, mouse.checkhole(), (mouse.rect.left-73, mouse.rect.top+64))
						if mouse.checkhole():
							mouse.draw(nightvision2, (mouse.rect.left-73, mouse.rect.top+64))
						nightsurf.blit(nightvision2, (0,0))
						nightsurf.blit(nightsight1, (0,0))
						screen.blit(nightsurf, (mouse.rect.left-73, mouse.rect.top+64))

					for light in lights:
						if light.on:
							nightvision3 = pygame.Surface((80+40*light.size, 80+40*light.size))
							nightvision3.blit(background, (-light.rect.left, -light.rect.top))
							for cheese in cheeses:
								cheese.draw(nightvision3, False, (light.rect.left, light.rect.top+64))
							for powerup in powerups:
								powerup.draw(nightvision3, False, (light.rect.left, light.rect.top+64))
							for trap in traps:
								trap.draw(nightvision3, False, (light.rect.left, light.rect.top+64))
							mouse.draw(nightvision3, (light.rect.left, light.rect.top+64))
							for hole in holes:
								hole.draw(nightvision3, False, mouse.rect, mouse.checkhole(), (light.rect.left, light.rect.top+64))
							if mouse.checkhole():
								mouse.draw(nightvision3, (light.rect.left, light.rect.top+64))
							nightsurf2 = pygame.Surface((80+40*light.size, 80+40*light.size))
							nightsurf2.set_colorkey((0,0,0))
							nightsurf2.blit(nightvision3, (0,0))
							light.draw(nightsurf2)
							screen.blit(nightsurf2, (light.rect.left, light.rect.top+64))

				if start == 11:
					screen.blit(instrpaper, (32,80))
					screen.blit(textwindow2, (57,139))
					if level != 8:
						screen.blit(f.render("N:  Next", 1, (0,230,255)), (64,168))
					screen.blit(f.render("B:  Back", 1, (0,230,255)), (64,238))
					screen.blit(instrimgs[level-1], (160,104))

				screen.blit(gaugecover, (124,17))
				screen.blit(gaugecover, (124,35))
				screen.blit(gaugecover, (576,17))
				screen.blit(gaugecover, (576,35))
				glowframe += fdir * lightning
				if glowframe > 31:
					glowframe = 32
					fdir = -1
				elif glowframe < 1:
					glowframe = 0
					fdir = 1
				if start == 10 or start == 11 and level < 6:
					pouncerect.left = 24 + cat.pounce_meter
					if cat.pounce_meter == 100 and cat.superstamina == 4:
						pouncebar.fill((64+glowframe,64+glowframe,192-glowframe))
					elif cat.pounce_meter == 100:
						pouncebar.fill((glowframe,255-glowframe,glowframe))
					else:
						pouncebar.fill((255-glowframe,glowframe,0))
					screen.blit(pouncebar, pouncerect)
					if cat.superstamina == 4:
						cpowerrect.topleft = (24+float(100)*cat.powertime/240, 35)
					elif cat.superspeed == 2:
						cpowerrect.topleft = (24+float(100)*cat.powertime/180, 35)
					elif mouse.frozen:
						cpowerrect.topleft = (24+float(100)*cat.powertime/90, 35)
					else:
						cpowerrect.topleft = (24,35)
					cpowerbar.fill((0,255-glowframe,255-glowframe))
					screen.blit(cpowerbar, cpowerrect)
				sprintrect.left = 476 + mouse.sprint_meter
				if mouse.sprint_meter == 100 and mouse.superstamina == 3:
					sprintbar.fill((0,glowframe,255-glowframe))
				elif mouse.sprint_meter == 100:
					sprintbar.fill((glowframe,255-glowframe,glowframe))
				else:
					sprintbar.fill((255-glowframe,glowframe,0))
				screen.blit(sprintbar, sprintrect)
				if start == 10 or start == 11 and level == 5:
					if mouse.superstamina == 3:
						mpowerrect.topleft = (476+float(100)*mouse.powertime/240, 35)
					elif mouse.superspeed == 2:
						mpowerrect.topleft = (476+float(100)*mouse.powertime/180, 35)
					elif cat.frozen:
						mpowerrect.topleft = (476+float(100)*mouse.powertime/90, 35)
					else:
						mpowerrect.topleft = (476,35)
				else:
					mpowerrect.topleft = (476,35)
				mpowerbar.fill((0,255-glowframe,255-glowframe))
				screen.blit(mpowerbar, mpowerrect)
				screen.blit(hud, (0,0))
				if start == 10 or start == 11 and level < 6:
					screen.blit(cwindow, (93,3))
					screen.blit(f2.render(str(catscore), 1, (255,0,0)), (99,32))
				elif start != 0:
					for x, cheese in enumerate(cheeses):
						screen.blit(cheese.image, (150+50*x,16))
						if cheese.state is "taken":
							screen.blit(slash, (150+50*x,16))
				screen.blit(mwindow, (505,3))
				screen.blit(f2.render(str(mousescore), 1, (255,0,0)), (681,32))
				if start == 10 or start == 11 and level == 5:
					if cat.powertime != 0:
						screen.blit(cpowdow, (93,57))
						if cat.superspeed == 2:
							screen.blit(powtext[0], (152,65))
						elif cat.superstamina == 4:
							screen.blit(powtext[1], (146,65))
						elif mouse.frozen:
							screen.blit(powtext[2], (171,65))
					if mouse.powertime != 0:
						screen.blit(mpowdow, (505,57))
						if mouse.superspeed == 2:
							screen.blit(powtext[0], (564,65))
						elif mouse.superstamina == 3:
							screen.blit(powtext[1], (558,65))
						elif cat.frozen:
							screen.blit(powtext[2], (583,65))
				screen.blit(f.render(str(timeleft/60000) + ":", 1, (255,0,0)), (385,31))
				if timeleft%60000/1000 < 10:
					screen.blit(f.render("0" + str(timeleft%60000/1000), 1, (255,0,0)), (399,31))
				else:
					screen.blit(f.render(str(timeleft%60000/1000), 1, (255,0,0)), (399,31))
				pygame.display.flip()

				if pause:
					pausestart = 5
					activemenu = menus[2]
					for menu in menus:
						menu.highlight = 0
						menu.update()

				if nextlevel:
					if start != 11 and start != 0:
						#pygame.mixer.music.stop()
						pass
					if start == 10 or start == 11 and level < 6:
						cdir = (cat.xspeed, cat.yspeed)
					mdir = (mouse.xspeed, mouse.yspeed)
					windowtimer = 0
					while windowtimer < 1000 and start != 0 and not tutnext:
						windowtimer += clock.tick(30)
						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								sys.exit()
							elif event.type == pygame.KEYDOWN:
								if event.key == pygame.K_UP:
									mdir = (mdir[0], mdir[1]-1)
								elif event.key == pygame.K_DOWN:
									mdir = (mdir[0], mdir[1]+1)
								elif event.key == pygame.K_LEFT:
									mdir = (mdir[0]-1, mdir[1])
								elif event.key == pygame.K_RIGHT:
									mdir = (mdir[0]+1, mdir[1])
								elif event.key == pygame.K_z:
									cdir = (cdir[0], cdir[1]-1)
								elif event.key == pygame.K_q:
									cdir = (cdir[0]-1, cdir[1])
								elif event.key == pygame.K_s:
									cdir = (cdir[0], cdir[1]+1)
								elif event.key == pygame.K_d:
									cdir = (cdir[0]+1, cdir[1])
							elif event.type == pygame.KEYUP:
								if event.key == pygame.K_UP:
									mdir = (mdir[0], mdir[1]+1)
								elif event.key == pygame.K_DOWN:
									mdir = (mdir[0], mdir[1]-1)
								elif event.key == pygame.K_LEFT:
									mdir = (mdir[0]+1, mdir[1])
								elif event.key == pygame.K_RIGHT:
									mdir = (mdir[0]-1, mdir[1])
								elif event.key == pygame.K_z:
									cdir = (cdir[0], cdir[1]+1)
								elif event.key == pygame.K_q:
									cdir = (cdir[0]+1, cdir[1])
								elif event.key == pygame.K_s:
									cdir = (cdir[0], cdir[1]-1)
								elif event.key == pygame.K_d:
									cdir = (cdir[0]-1, cdir[1])
						if mdir[0] < -1:
							mdir = (-1, mdir[1])
						elif mdir[0] > 1:
							mdir = (1, mdir[1])
						if mdir[1] < -1:
							mdir = (mdir[0], -1)
						elif mdir[1] > 1:
							mdir = (mdir[0], 1)
						if cdir[0] < -1:
							cdir = (-1, cdir[1])
						elif cdir[0] > 1:
							cdir = (1, cdir[1])
						if cdir[1] < -1:
							cdir = (cdir[0], -1)
						elif cdir[1] > 1:
							cdir = (cdir[0], 1)

					if start != 11 and start != 0:
						pause = True
						pausestart = 5
						activemenu = menus[2]
						activemenu.highlight = 1
						activemenu.update()
					elif start != 0:
						nextlevel = False
						if tutnext:
							tutnext = False
							if endgame:
								level -= 1
								endgame = False
							else:
								level += 1
						if level == 9 or level == 0:
							nextlevel = True
							endgame = True
							start = 0
							background = menuimg
							activemenu = menus[0]
							for menu in menus:
								menu.highlight = 0
								menu.update()
						else:
							newlevel(level, cdir, mdir)
							if level == 5:
								powerups.add(Item.Powerup((11, 11), 4))
								powerups.add(Item.Powerup((15, 11), 1))
								powerups.add(Item.Powerup((11, 15), 8))
								powerups.add(Item.Powerup((15, 15), 9))
							timeleft = 120999

					while pause:
						mouse1 = pygame.mouse.get_pos()
						clock.tick(30)
						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								sys.exit()
							elif event.type == pygame.MOUSEMOTION:
								activemenu.checkmouse(mouse1)
							elif event.type == pygame.MOUSEBUTTONDOWN:
								activemenu.checkmouse(mouse1)
							elif event.type == pygame.MOUSEBUTTONUP:
								if activemenu.checkmouse(mouse1):
									if activemenu.highlight != 0:
										pausestart = activemenu.nodes[activemenu.highlight-1]
								if activemenu.id == 4:
									if mouse1[0] >= 455 and mouse1[0] <= 494 and mouse1[1] >= 114 and mouse1[1] <= 135:
										pausestart = 6
										activemenu.highlight = 1
									elif mouse1[0] >= 455 and mouse1[0] <= 486 and mouse1[1] >= 147 and mouse1[1] <= 168:
										pausestart = 6
										activemenu.highlight = 2
									elif mouse1[0] >= 455 and mouse1[0] <= 494 and mouse1[1] >= 180 and mouse1[1] <= 201:
										pausestart = 6
										activemenu.highlight = 3
									elif mouse1[0] >= 455 and mouse1[0] <= 521 and mouse1[1] >= 213 and mouse1[1] <= 234:
										pausestart = 6
										activemenu.highlight = 4
									elif mouse1[0] >= 455 and mouse1[0] <= 521 and mouse1[1] >= 246 and mouse1[1] <= 267:
										pausestart = 6
										activemenu.highlight = 5
									elif mouse1[0] >= 455 and mouse1[0] <= 486 and mouse1[1] >= 279 and mouse1[1] <= 300:
										pausestart = 6
										activemenu.highlight = 6
								if start == 6:
									activemenu.update()
							elif event.type == pygame.KEYDOWN:
								if event.key == pygame.K_SPACE and pausestart == 5:
									pause = False
									delta = clock.tick()
								elif event.key == pygame.K_RETURN:
									if activemenu.highlight != 0:
										pausestart = activemenu.nodes[activemenu.highlight-1]
								elif event.key == pygame.K_UP:
									activemenu.movehighlight(-1)
									mdir = (mdir[0], mdir[1]-1)
								elif event.key == pygame.K_DOWN:
									activemenu.movehighlight(1)
									mdir = (mdir[0], mdir[1]+1)
								elif event.key == pygame.K_LEFT:
									mdir = (mdir[0]-1, mdir[1])
								elif event.key == pygame.K_RIGHT:
									mdir = (mdir[0]+1, mdir[1])
								elif event.key == pygame.K_z:
									cdir = (cdir[0], cdir[1]-1)
								elif event.key == pygame.K_q:
									cdir = (cdir[0]-1, cdir[1])
								elif event.key == pygame.K_s:
									cdir = (cdir[0], cdir[1]+1)
								elif event.key == pygame.K_d:
									cdir = (cdir[0]+1, cdir[1])
								elif event.key == pygame.K_ESCAPE:
									if pausestart == 5:
										pause = False
										nextlevel = True
										endgame = True
										start = 0
										#pygame.mixer.music.stop()
										#pygame.mixer.music.load(titlemusic)
										#pygame.mixer.music.play(-1)
										background = menuimg
									else:
										pausestart = 5
							elif event.type == pygame.KEYUP:
								if event.key == pygame.K_UP:
									mdir = (mdir[0], mdir[1]+1)
								elif event.key == pygame.K_DOWN:
									mdir = (mdir[0], mdir[1]-1)
								elif event.key == pygame.K_LEFT:
									mdir = (mdir[0]+1, mdir[1])
								elif event.key == pygame.K_RIGHT:
									mdir = (mdir[0]-1, mdir[1])
								elif event.key == pygame.K_z:
									cdir = (cdir[0], cdir[1]+1)
								elif event.key == pygame.K_q:
									cdir = (cdir[0]+1, cdir[1])
								elif event.key == pygame.K_s:
									cdir = (cdir[0], cdir[1]-1)
								elif event.key == pygame.K_d:
									cdir = (cdir[0]-1, cdir[1])
						if mdir[0] < -1:
							mdir = (-1, mdir[1])
						elif mdir[0] > 1:
							mdir = (1, mdir[1])
						if mdir[1] < -1:
							mdir = (mdir[0], -1)
						elif mdir[1] > 1:
							mdir = (mdir[0], 1)
						if cdir[0] < -1:
							cdir = (-1, cdir[1])
						elif cdir[0] > 1:
							cdir = (1, cdir[1])
						if cdir[1] < -1:
							cdir = (cdir[0], -1)
						elif cdir[1] > 1:
							cdir = (cdir[0], 1)

						if pausestart != activemenu.id:
							if pausestart == 6:
								pausestart = 4
								if activemenu.highlight == 1:
									pupson = (pupson + 1) % 3
								elif activemenu.highlight == 2:
									if lightning == 2:
										lightning = 1
									else:
										lightning = 2
								elif activemenu.highlight == 3:
									if nightvision:
										nightvision = False
									else:
										nightvision = True
								elif activemenu.highlight == 4:
									vision = (vision + 1) % 3
								elif activemenu.highlight == 5:
									difficulty = (difficulty + 1) % 3
								elif activemenu.highlight == 6:
									if fson:
										screen = pygame.display.set_mode((800,640))
										fson = False
									else:
										screen = pygame.display.set_mode((800,640), pygame.FULLSCREEN)
										fson = True
							if pausestart == 0 and activemenu.id == 4:
								pausestart = 5
							elif pausestart == 0:
								pause = False
								nextlevel = True
								endgame = True
								start = 0
								background = menuimg
							if pausestart == 10:
								pause = False
								delta = clock.tick()
							for menu in menus:
								if menu.id == pausestart:
									activemenu = menu
									break

						screen.blit(menupaper, (250,99))
						if activemenu.id == 5:
							screen.blit(textwindow, textwindowrect)
							screen.blit(winners[winner][0], winners[winner][1])
							if start == 12:
								screen.blit(f.render("Wins:", 1, (0,230,255)),(338,295))
							elif start == 10:
								screen.blit(f.render("Mouse:", 1, (0,230,255)), (328,295))
							if start == 12:
								screen.blit(f.render("Losses:", 1, (0,230,255)),(326,315))
							elif start == 10:
								screen.blit(f.render("Cat:", 1, (0,230,255)), (356,315))
							screen.blit(f.render(str(mousescore), 1, (10,240,255)), (441,295))
							screen.blit(f.render(str(catscore), 1, (10,240,255)), (441,315))
						elif activemenu.id == 4:
							if pupson == 0:
								screen.blit(f.render("Off", 1, (220,0,0)), (455,114))
							elif pupson == 1:
								screen.blit(f.render("Low", 1, (0,0,220)), (455,114))
							else:
								screen.blit(f.render("High", 1, (0,220,0)), (455,114))
							if lightning == 2:
								screen.blit(f.render("On", 1, (0,220,0)), (455,147))
							else:
								screen.blit(f.render("Off", 1, (220,0,0)), (455,147))
							if nightvision:
								screen.blit(f.render("On", 1, (0,220,0)), (455,180))
							else:
								screen.blit(f.render("Off", 1, (220,0,0)), (455,180))
							if vision == 0:
								screen.blit(f.render("Low", 1, (220,0,0)), (455,213))
							elif vision == 1:
								screen.blit(f.render("Medium", 1, (0,0,220)), (455,213))
							else:
								screen.blit(f.render("High", 1, (0,220,0)), (455,213))
							if difficulty == 0:
								screen.blit(f.render("Easy", 1, (0,220,0)), (455,246))
							elif difficulty == 1:
								screen.blit(f.render("Medium", 1, (0,0,220)), (455,246))
							else:
								screen.blit(f.render("Hard", 1, (220,0,0)), (455,246))
							if fson:
								screen.blit(f.render("On", 1, (0,220,0)), (455,279))
							else:
								screen.blit(f.render("Off", 1, (220,0,0)), (455,279))
						activemenu.draw(screen)
						pygame.display.flip()

					if nextlevel and (start == 10 or start == 12):
						#pygame.mixer.music.play(-1)
						usedlevs.append(level)
						if len(usedlevs) > 15:
							usedlevs.pop(0)
						while level in usedlevs:
							level = random.randint(1,30)
						nextlevel = False
						newlevel(level, cdir, mdir)
						timeleft = 120999
						if pupson == 1:
							powertimer = 15000
						elif pupson == 2:
							powertimer = 5000
						usedpows = []
						pause = False
					elif start != 11 and start != 0:
						#pygame.mixer.music.load(titlemusic)
						#pygame.mixer.music.play(-1)
						nextlevel = True
						endgame = True
						background = menuimg
						activemenu = menus[0]
						for menu in menus:
							menu.highlight = 0
							menu.update()

			else:
				#pygame.mixer.music.load(titlemusic)
				#pygame.mixer.music.play(-1)
				background = menuimg
				activemenu = menus[0]
				for menu in menus:
					menu.highlight = 0
					menu.update()
