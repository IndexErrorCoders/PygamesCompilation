import pygame, sys, os
import Menu


#load everything more


pygame.init()
resolution = (1024,768)
playarea = (700,768)
fullscreen = True
if fullscreen:
	screen = pygame.display.set_mode(resolution, pygame.FULLSCREEN)
else:
	screen = pygame.display.set_mode(resolution)
pygame.display.set_caption("BULLET HELL")

PRINT_FPS = False
FPS = 60

CHANGEMOUSE = False
GRABEVENTS = False


#debug nonsense
PLAYER_INVINCIBLE = False



BOSS_DEPTH = 50000
BOSS_FULL_TIME = 60*60*5
BOSS_FLASHING_FREQ = 18

WALL_SPEED = 3
BG_SPEED = 2


#menu/mode constants
QUIT = -1
PAUSE_GAME = 5
RESET_GAME = 9
START_GAME = 10
LEVEL_SELECT = 11
GAME_INTRO = 15


fireball_image = pygame.image.load(os.path.join("images", "fireball.png")).convert_alpha()
playerbullet_image = pygame.image.load(os.path.join("images", "player_bullet.png")).convert_alpha()
"""
player_list = [ pygame.image.load(os.path.join("images", "temp_player.png")).convert_alpha(),
                pygame.image.load(os.path.join("images", "temp_player.png")).convert_alpha(),
                pygame.image.load(os.path.join("images", "temp_player.png")).convert_alpha(),
                pygame.image.load(os.path.join("images", "temp_player.png")).convert_alpha(),
                pygame.image.load(os.path.join("images", "temp_player.png")).convert_alpha(),
                pygame.image.load(os.path.join("images", "temp_player.png")).convert_alpha() ]"""

player_list = [pygame.image.load(os.path.join("images", "player.png")).subsurface(130 * x, 0, 130, 79).convert_alpha() for x in range(6)]
demon_list = [pygame.image.load(os.path.join("images", "enemies", "demon.png")).subsurface(110 * x, 0, 110, 62).convert_alpha() for x in range(6)]
strongerdemon_list = [pygame.image.load(os.path.join("images", "enemies", "strongerdemon.png")).subsurface(110 * x, 0, 110, 62).convert_alpha() for x in range(6)]
mirror_demon_list = [pygame.image.load(os.path.join("images", "enemies", "mirror_demon.png")).subsurface(53 * x, 0, 53, 53).convert_alpha() for x in range(6)]
demon_death_list = [pygame.image.load(os.path.join("images", "enemies", "demon_death_sheet.png")).subsurface(87 * x, 0, 87, 60).convert_alpha() for x in range(5)]

mirror_demon_flipped = pygame.transform.flip(pygame.image.load(os.path.join("images", "enemies", "mirror_demon.png")), True, False)
mirror_demon_list_flipped = [mirror_demon_flipped.subsurface(53 * x, 0, 53, 53).convert_alpha() for x in range(6)]

rock_list = [ pygame.image.load(os.path.join("images", "enemies", "rock_small.png")).convert_alpha(),
              pygame.image.load(os.path.join("images", "enemies", "rock_medium.png")).convert_alpha(),
              pygame.image.load(os.path.join("images", "enemies", "rock_large.png")).convert_alpha() ]

#images: interface, objects
images = {
	"health": pygame.image.load(os.path.join("images", "health-small.png")).convert_alpha(),
	"weapon_pickup": pygame.image.load(os.path.join("images", "pickups", "weapon.png")).convert_alpha(),
	"speed_pickup": pygame.image.load(os.path.join("images", "pickups", "speedup.png")).convert_alpha(),
	"player": player_list,
	"player_rush": pygame.image.load(os.path.join("images", "player_rush.png")).convert_alpha(),
	"demon": demon_list,
	"strongerdemon":strongerdemon_list,
	"mirror": pygame.image.load(os.path.join("images", "enemies", "mirror.png")).convert_alpha(),
	"mirror_demon": mirror_demon_list,
	"mirror_demon_flipped": mirror_demon_list_flipped,
	"demon_death": demon_death_list,
	"rock": rock_list,
	"mirror": pygame.image.load(os.path.join("images", "enemies", "mirror.png")).convert_alpha(),
	"playerbullet": playerbullet_image,
	"playerbullet_sheet": [playerbullet_image.subsurface(4 * x, 0, 4, 20).convert_alpha() for x in range(3)],
	"playerbullet_hit": pygame.image.load(os.path.join("images", "player_bullet_hit.png")).convert_alpha(),
	"playerbullet_hit_flipped": pygame.transform.flip(pygame.image.load(os.path.join("images", "player_bullet_hit.png")).convert_alpha(), False, True),
	"fireball": fireball_image,
	"fireball_sheet": [fireball_image.subsurface(11 * x, 0, 11, 26).convert_alpha() for x in range(3)],
	"light_particle": pygame.image.load(os.path.join("images", "light_particle.png")).convert_alpha(),
	"fallingrock": pygame.image.load(os.path.join("images", "boss", "falling_rock.png")).convert_alpha(),
	"caution":pygame.image.load(os.path.join("images","caution.png")).convert_alpha(),
}
black = pygame.Surface(resolution)
black.fill((0,0,0))

title_screens = [
	pygame.image.load(os.path.join("images", "misc", "titlescreen.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "misc", "intro1.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "misc", "intro2.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "misc", "intro3.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "misc", "intro4.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "misc", "intro5.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "misc", "intro6.png")).convert_alpha(),
	pygame.image.load(os.path.join("images", "misc", "intro7.png")).convert_alpha(),
	#pygame.Surface(resolution),
]

win_screen = pygame.image.load(os.path.join("images", "misc", "winScreen.png")).convert_alpha()

scroll_image = pygame.image.load(os.path.join("images", "misc", "scroll.png")).convert_alpha()
scroll_small = pygame.image.load(os.path.join("images", "misc", "scroll_small.png")).convert_alpha()
scroll_side = pygame.image.load(os.path.join("images", "misc", "scroll_side.png")).convert_alpha()

boss_list = [ pygame.image.load(os.path.join("images", "hud", "boss1.png")).convert_alpha(),
              pygame.image.load(os.path.join("images", "hud", "boss2.png")).convert_alpha(),
              pygame.image.load(os.path.join("images", "hud", "boss3.png")).convert_alpha(),
              pygame.image.load(os.path.join("images", "hud", "boss4.png")).convert_alpha(), ]

glow_list = [ pygame.image.load(os.path.join("images", "hud", "button_glow1.png")).convert_alpha(),
              pygame.image.load(os.path.join("images", "hud", "button_glow2.png")).convert_alpha(),
              pygame.image.load(os.path.join("images", "hud", "button_glow3.png")).convert_alpha(), ]

hud_images = {
	"full_health": pygame.image.load(os.path.join("images", "hud", "health_bar_full.png")).convert_alpha(),
	"empty_health": pygame.image.load(os.path.join("images", "hud", "health_bar_empty.png")).convert_alpha(),
	"boss_full_health": pygame.image.load(os.path.join("images", "hud", "boss_health_bar_full.png")).convert_alpha(),
	"boss_empty_health": pygame.image.load(os.path.join("images", "hud", "boss_health_bar_empty.png")).convert_alpha(),
	"rush": pygame.image.load(os.path.join("images", "hud", "rush_button.png")).convert_alpha(),
	"rush_gray": pygame.image.load(os.path.join("images", "hud", "rush_button_gray.png")).convert_alpha(),
	"time_stop": pygame.image.load(os.path.join("images", "hud", "time_stop_button.png")).convert_alpha(),
	"time_stop_gray": pygame.image.load(os.path.join("images", "hud", "time_stop_button_gray.png")).convert_alpha(),
	"light": pygame.image.load(os.path.join("images", "hud", "light_button.png")).convert_alpha(),
	"light_gray": pygame.image.load(os.path.join("images", "hud", "light_button_gray.png")).convert_alpha(),
	"height_bar": pygame.image.load(os.path.join("images", "hud", "height_bar.png")).convert_alpha(),
	"player_height": pygame.image.load(os.path.join("images", "hud", "player_height.png")).convert_alpha(),
	"glow": glow_list,
	"cooldown_bar": pygame.image.load(os.path.join("images", "hud", "cooldown_bar.png")).convert_alpha(),
	"cooldown_sphere_top": pygame.image.load(os.path.join("images", "hud", "cooldown_sphere_half.png")).convert_alpha(),
	"cooldown_sphere_bottom": pygame.transform.flip(pygame.image.load(os.path.join("images", "hud", "cooldown_sphere_half.png")).convert_alpha(), True, True),
	"boss_bg": pygame.image.load(os.path.join("images", "hud", "boss_fire_bg.png")).convert_alpha(),
	"boss": boss_list,
}

background_tiles = {
	"bg1": pygame.image.load(os.path.join("images", "background.png")).convert_alpha(),
	"wall_left": pygame.image.load(os.path.join("images", "wall_left.png")).convert_alpha(),
	"wall_right": pygame.image.load(os.path.join("images", "wall_right.png")).convert_alpha(), #pygame.transform.flip(pygame.image.load(os.path.join("images", "wall_right.png")).convert_alpha(), False, True),
	"burn1": pygame.image.load(os.path.join("images", "alt_tiles", "burningguy.png")).convert_alpha(),
	"burn2": pygame.image.load(os.path.join("images", "alt_tiles", "burningguy2.png")).convert_alpha(),
	"person": pygame.image.load(os.path.join("images", "alt_tiles", "fallingperson.png")).convert_alpha(),
}

bg_lava_sheet = pygame.image.load(os.path.join("images", "boss", "bglava_639x55.png")).convert_alpha()
bg_lava = [
	bg_lava_sheet.subsurface(0,0,639,55),
	bg_lava_sheet.subsurface(639,0,639,55),
	bg_lava_sheet.subsurface(639*2,0,639,55),
	bg_lava_sheet.subsurface(639*3,0,639,55)
]
fg_lava_sheet = pygame.image.load(os.path.join("images", "boss", "lava_645x71.png")).convert_alpha()
fg_lava = [
	fg_lava_sheet.subsurface(0,0,645,71),
	fg_lava_sheet.subsurface(645,0,645,71),
	fg_lava_sheet.subsurface(645*2,0,645,71)
]

boss_background = {
	"fg_rocks": pygame.image.load(os.path.join("images", "boss", "foreground_rocks.png")).convert_alpha(),
	"bg_rocks": pygame.image.load(os.path.join("images", "boss", "bgrocks.png")).convert_alpha(),
	"lavadrops_left": pygame.image.load(os.path.join("images", "boss", "lavadropsleft_94x57.png")).convert_alpha(),
	"lavadrops_right": pygame.image.load(os.path.join("images", "boss", "lavadropsright.png")).convert_alpha(),
	"fg_lava": fg_lava,
	"bg_lava": bg_lava,
}

boss_sheet_image = pygame.image.load(os.path.join("images", "boss", "boss.png")).convert_alpha()
boss_sheet = [
	boss_sheet_image.subsurface(0,0,369,318),
	boss_sheet_image.subsurface(369,0,369,318),
	boss_sheet_image.subsurface(369*2,0,369,318),
	boss_sheet_image.subsurface(369*3,0,369,318),
	boss_sheet_image.subsurface(369*4,0,369,318)
]

#fonts
fonts = {
	0: pygame.font.Font(os.path.join("fonts", "Demon  Night.ttf"), 32),
	
}


#sound: effects, music
sfx = {
	"player_death": os.path.join("sounds", "sfx", "Player_death.wav"),
	"player_damage1": os.path.join("sounds", "sfx", "Player_damage1.wav"),
	"player_damage2": os.path.join("sounds", "sfx", "Player_damage2.wav"),
	"player_damage3": os.path.join("sounds", "sfx", "Player_damage3.wav"),
	"player_rush":os.path.join("sounds","sfx","Player_rush.wav"),
	"time_stop":os.path.join("sounds","sfx","time_stop.wav"),
	"light_attack":os.path.join("sounds","sfx","light_attack.wav"),
	"oww":os.path.join("sounds","sfx","OW!.wav"),
	"intro": os.path.join("sounds", "sfx", "intro.wav"),
}
musics = {
	# "start": os.path.join("sounds", "music", "Level Intro.wav"),
	"level": os.path.join("sounds", "music", "Level Loop3.wav"),
	"boss": os.path.join("sounds", "music", "Boss Music.wav"),
	
}
# music_wait = 60 * 24 + 85

#menus
Menu.getstuff(None, fonts)
menus = {
	0: Menu.Menu(("GO", "OPTIONS", "QUIT"), (10, 1, -1), 0, (resolution[0] / 2, resolution[1] / 2), 1, 16, (255,255,255), (255,0,0)),
	5: Menu.Menu(("RESUME", "RESET", "QUIT"), (10, 9, -1), 0, (resolution[0] / 2 - 50, resolution[1] / 2 - 70), 1, 16, (0,0,0), (255,0,0)),
	15: Menu.Menu(("NEXT", "SKIP"), (15, 10), 0, (resolution[0] / 2 - 50, resolution[1] / 2 - 70), 1, 10, (0,0,0), (255,0,0)),
#	1: Menu.Menu(("FULLSCREEN", "SHOW FPS", "BACK"), (2, 3, 0), 0, (0,0), 2, 16, (255,255,255), (255,0,0)),

}

menus[15].setasintro()




