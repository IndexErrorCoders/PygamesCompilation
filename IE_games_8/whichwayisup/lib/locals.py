#This file contains constant values used throughout the game code.

GAME_NAME_SHORT = "wwisup"

SCREEN_WIDTH = 520
SCREEN_HEIGHT = 520

PLAY_AREA_WIDTH = 520
PLAY_AREA_HEIGHT = 520

FULL_TILES_HOR = 20
FULL_TILES_VER = 20

TILES_HOR = 13
TILES_VER = 13

TILE_DIM = 40

PLAY_AREA_CENTER_X = (-FULL_TILES_HOR / 2 + TILES_HOR) * TILE_DIM
PLAY_AREA_CENTER_Y = (-FULL_TILES_VER / 2 + TILES_VER) * TILE_DIM

GRAVITY = 1.0
GRAVITY_PARTICLE = 0.5

PLAYER_JUMP_ACC = GRAVITY * 10.0

PLAYER_AIR_JUMP = GRAVITY * 0.55

FPS = 24

#The time used flipping the level, in frames, and time from lever activation to the flipping, also in frames.
FLIP_FRAMES = 30
FLIP_DELAY = 15

#In pixels per second or pixels per second^2
PLAYER_MAX_SPEED = 6.0
PLAYER_MAX_ACC = 4.0

PLAYER_ACC_AIR_MULTIPLIER = 0.18

PLAYER_COLLISION_ADJUST = 11 #In pixels
PLAYER_LIFE = 36 #Hit points

#Spikes offset for rect placement - the spikes are smaller than the rest of tiles:
SPIKES_VER_OFFSET = 4

#In frames
SPIDER_FIRE_DELAY = 30

SPIDER_TOO_WIDE = 7
SPIDER_PROJECTILE_SPEED = 5
SPIDER_DAMAGE = 5

BLOB_JUMP_ACC = PLAYER_JUMP_ACC * 1.05
BLOB_AIR_JUMP = GRAVITY * 0.5

BLOB_DAMAGE = 5

# Indexing for collision, including the "damage", which means the index of collision damage...
# Also used for indexing player input.
# This could be done better with a dictionary or just bare strings, I suppose.
RIGHT = 0
LEFT = 2
DOWN = 1
UP = 3
JUMP = DAMAGE = 4
SPECIAL = STAY = 5
PAUSE = 6
ANALOG = 7

CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

#Colors
COLOR_DUST = {}
COLOR_DUST["brown"] = (220, 200, 170)
COLOR_DUST["green"] = (190, 185, 175)
COLOR_DUST["grey"] = (190, 190, 185)
COLOR_BLOOD = (200, 40, 10)
COLOR_GUI_DARK = (120, 120, 120)
COLOR_GUI = (230, 230, 230)
COLOR_GUI_HILIGHT = (255, 255, 255)
COLOR_GUI_BG = (0, 0, 0)

GUI_MENU_TOP = 160

#Editor colors:
COLOR_GUI_EDIT_HILIGHT = (200, 0, 0)

#Trigger indexes
TRIGGER_FLIP = "TRIGGER_FLIP"
TRIGGER_PICKUP = "TRIGGER_PICKUP"
TRIGGER_TEXT = "TRIGGER_TEXT"
TRIGGER_FLIPPED = "flipped"
TRIGGER_LEVEL_BEGIN = "level_begin"

#For the GUI
FONT_SIZE = 12

#Game ending types
END_NONE = 0
END_LOSE = 1
END_WIN = 2
END_NEXT_LEVEL = 3
END_QUIT = 4
END_HARD_QUIT = 5
END_MENU = 6

TOTAL_LEVELS = 7

MENU_QUIT = -5
MENU_SOUND = -4
MENU_DIALOGUE = -3
MENU_FULLSCREEN = -2
MENU_WORLD = -1

MENU_OFFSET = 5

MENU_MAX_VISIBLE = 7

FADE_IN = -0.7
FADE_NONE = 0
FADE_OUT = 0.7
FADE_STATE_BLACK = 255
FADE_STATE_HALF = 128
FADE_STATE_NONE = 0

#World names must also correspond to the text file names in the levels directory (.txt is added)
WORLDS = ["Quest For The Keys", "The Other Side", "A Piece of Cake"]

#How many old log lines are kept in the log file when the log is updated
MAX_OLD_LOG_LINES = 50