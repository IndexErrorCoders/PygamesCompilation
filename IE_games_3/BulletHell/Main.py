import pygame, sys, os#, tkFileDialog
# from Tkinter import Tk
from Constants import *
from Controls import *
import Sound, MenuHandler, Game


#constants only change from here because they become global in main() only; need a better way to change options

#engine structure:
#separate file for functions, could even be an object?




def loadlevel(mode, chapter, level, path = ""):
	"""Open a level file. Return success and the level data to be interpreted by game.newlevel()."""
	try:
		levpath = path
		if len(levpath) == 0:
			levpath = os.path.join("levels", "level.txt")#"level%d.txt"%(chapter))
		levfile = open(levpath)
		data = [line.strip() for line in levfile]
		leveldata = data[level]
		return True, data
	except IOError:
		#print "Error loading level at", levpath
		return False, None

def getpressed():
	"""Resets what keys or buttons are currently being pressed."""
	# global lmb_down, rmb_down
	# mousedowns = pygame.mouse.get_pressed()
	# lmb_down = mousedowns[0]
	# rmb_down = mousedowns[2]
	pass


def main(*args):
	"""Do everything."""
	#init everything
	# root = Tk()
	# root.withdraw()
	pygame.init()

	#stupid code for options menu
	global fullscreen, PRINT_FPS

	if fullscreen:
		screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode(resolution)
	camsurf = pygame.Surface(resolution)
	clock = pygame.time.Clock()

	sound = Sound.Sound()
	sound.unmute()
	sound.loadsounds()
	sound.play("intro")

	menuhandler = MenuHandler.MenuHandler()
	game = Game.Game(resolution, (0,0), sound)

	mode = 0
	chapter = 0
	level = 0

	title_id = 0

	#load configuration options
	try:
		pass
	except:
		pass

	#load saved data
	try:
		pass
	except:
		pass


	while 1:
		delta = clock.tick(FPS)
		mouse1 = pygame.mouse.get_pos()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
			#elif event.type == pygame.VIDEORESIZE:
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					lmb_down = True
				elif event.button == 3:
					rmb_down = True
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					lmb_down = False
				elif event.button == 3:
					rmb_down = False
			elif event.type == pygame.KEYDOWN:
				if event.key not in controls:
					continue
				if event.key == k_quit:
					sys.exit()
				controls[event.key] = True
				title_id += 1
			elif event.type == pygame.KEYUP:
				if event.key not in controls:
					continue
				controls[event.key] = False

#menu logic
		menuhandler.update(game)
		if menuhandler.next_selection == QUIT:
			sys.exit()

		#options menu (stupid)
		elif menuhandler.next_selection == 2:
			fullscreen = not fullscreen
			if fullscreen:
				screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
			else:
				screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
			menuhandler.next_selection = menuhandler.activemenu
		elif menuhandler.next_selection == 3:
			PRINT_FPS = not PRINT_FPS
			menuhandler.next_selection = menuhandler.activemenu

		#options menu (stupid)
		elif menuhandler.next_selection == GAME_INTRO:
			pass
		
#draw menu
		camsurf.blit(black, (0,0))

		menuhandler.draw(camsurf)

		if title_id < len(title_screens):
			camsurf.blit(title_screens[title_id], (0,0))
		else:
			camsurf.blit(black, (0,0))
			menuhandler.next_selection = START_GAME
		screen.blit(camsurf, (0,0))
		pygame.display.flip()


		path = ""
		# if menuhandler.next_selection == LEVEL_SELECT:
			# path = tkFileDialog.askopenfilename(initialdir = "levels", filetypes = [("TXT", ".txt")])
			# if len(path) > 0:
				# menuhandler.next_selection = START_GAME
			# else:
				# menuhandler.next_selection = 0
			# if fullscreen:
				# screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
			# else:
				# screen = pygame.display.set_mode(resolution)

#start game check
		if menuhandler.next_selection != START_GAME:
			continue


#start game: could make this a function
		game.newgame(mode)
		lev = loadlevel(mode, chapter, level, path)
		if not lev[0]:
			break
		game.newlevel(lev[1])

		getpressed()
		game.setmouse(mouse1)

		if GRABEVENTS:
			pygame.event.set_grab(1)

		#change background music (in game)

#game loop
		while not game.nextlevel:

#pause menu
			while game.pause:
				delta = clock.tick(FPS)
				mouse1 = pygame.mouse.get_pos()

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						if game.forcequit():
							sys.exit()
					else:
						menuhandler.handleevent(event)

				menuhandler.update(game)
				if menuhandler.next_selection == START_GAME:
					#resume
					game.setpause(False)
					if GRABEVENTS:
						pygame.event.set_grab(1)
					delta = clock.tick()
				elif menuhandler.next_selection == RESET_GAME:
					#reset
					game.resetlevel()
					if GRABEVENTS:
						pygame.event.set_grab(1)
				elif menuhandler.next_selection == QUIT:
					game.quitgame()

				#options menu (stupid)
				elif menuhandler.next_selection == 2:
					fullscreen = not fullscreen
					if fullscreen:
						screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
					else:
						screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
					menuhandler.next_selection = menuhandler.activemenu
				elif menuhandler.next_selection == 3:
					PRINT_FPS = not PRINT_FPS
					menuhandler.next_selection = menuhandler.activemenu


#pause draw (copies from menu draw temporarily)
				camsurf.blit(black, (0,0))
				camsurf.blit(game.camsurf, game.loc)

				menuhandler.draw(camsurf)
				#extras

				screen.blit(camsurf, (0,0))
				pygame.display.flip()

#continue game
			if not game.endgame:
				delta = clock.tick(FPS)
				if PRINT_FPS:
					print 1000./delta
				mouse1 = pygame.mouse.get_pos()
				game.mouse1 = game.convertmouse(mouse1)

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						if game.forcequit():
							sys.exit()
					#elif event.type == pygame.VIDEORESIZE:
					else:
						game.handleevent(event)

#update main and game
				if game.changemouse(mouse1):
					pygame.mouse.set_pos(game.unconvertmouse())

				game.update(delta)

#draw
				camsurf.blit(black, (0,0))
				game.draw(camsurf)

				screen.blit(camsurf, (0,0))
				if PRINT_FPS:
					screen.blit(fonts[0].render(str(1000./delta), 1, (255,255,255)), (0,0))
				pygame.display.flip()

#pre-pause
				if game.pause:
					menuhandler.activemenu = PAUSE_GAME
					menuhandler.next_selection = PAUSE_GAME
					if GRABEVENTS:
						pygame.event.set_grab(0)

				if game.endgame:
					#sound
					
					#wait
					levtimer = 0
					a = 0
					game.cover.set_alpha(0)
					while levtimer < 2000:
						levtimer += clock.tick(FPS)
						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								sys.exit()
							elif event.type == pygame.MOUSEBUTTONDOWN:
								if event.button == 1:
									lmb_down = True
								elif event.button == 3:
									rmb_down = True
							elif event.type == pygame.MOUSEBUTTONUP:
								if event.button == 1:
									lmb_down = False
								elif event.button == 3:
									rmb_down = False
							elif event.type == pygame.KEYDOWN:
								if event.key not in controls:
									continue
								controls[event.key] = True
							elif event.type == pygame.KEYUP:
								if event.key not in controls:
									continue
								controls[event.key] = False

						a += 2
						game.cover.set_alpha(a)
						screen.blit(camsurf, (0,0))
						screen.blit(game.cover, (0,0))
						pygame.display.flip()

				if game.wingame:
					levtimer = 0
					a = 0
					game.whiteflash.set_alpha(0)
					while levtimer < 4000:
						levtimer += clock.tick(FPS)
						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								sys.exit()
							else:
								game.handleevent(event)

						game.update(0)

						camsurf.blit(black, (0,0))
						game.draw(camsurf)

						a += 1
						game.whiteflash.set_alpha(a)
						screen.blit(camsurf, (0,0))
						screen.blit(game.whiteflash, (0,0))
						pygame.display.flip()

					#screen.blit(fonts[0].render("WINNER!", 1, (0,0,0)), (400,300))
					
					#BLIT WIN SCREEN
					screen.blit(win_screen, (0, 0))
					pygame.display.flip()
					game.endgame = False

					while not game.endgame:
						delta = clock.tick(FPS)
						for event in pygame.event.get():
							if event.type == pygame.QUIT:
								sys.exit()
							elif event.type == pygame.MOUSEBUTTONDOWN:
								if event.button == 1:
									lmb_down = True
								elif event.button == 3:
									rmb_down = True
							elif event.type == pygame.MOUSEBUTTONUP:
								if event.button == 1:
									lmb_down = False
								elif event.button == 3:
									rmb_down = False
							elif event.type == pygame.KEYDOWN:
								if event.key not in controls:
									continue
								controls[event.key] = True
								game.endgame = True
							elif event.type == pygame.KEYUP:
								if event.key not in controls:
									continue
								controls[event.key] = False

#quit game
			else:
				sound.stopmusic()
				sound.play("intro")
				title_id = 0

				game.nextlevel = True
				menuhandler.activemenu = 0
				menuhandler.next_selection = 0

if __name__ == "__main__":
	main(*sys.argv)
