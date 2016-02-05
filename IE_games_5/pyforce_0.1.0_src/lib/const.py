#==========================================================================
#    PyForce 0.1.0
#    Copyright (C) 2010 Xueqiao Xu <xueqiaoxu@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==========================================================================


DEBUG = False

FPS_ENABLED = True

# screen config
RESOLUTION = (360, 480)
CAPTION    = 'Py Force'
FPS_LIMIT  = 60

# path
IMG_PATH = 'res/img/'
SFX_PATH = 'res/sfx/'
LEVEL_PATH = 'res/level/'

# terrain layer config
TERRAIN_IMG = 'map_01.png'
TERRAIN_SPEED = 0.5

# shadow config
SHADOW_OFFSET = (40, 20)

# my ship config
MY_SHIP_LIVE = 3
MY_SHIP_COOLDOWN = 10
MY_SHIP_COLLIDE_RADIUS = 10

INIT_BOMB_NUM = 3

MY_SHIP_1_SPEED = 3
MY_SHIP_1_HP = 200

# enemy ship config
SHIP_A_SPEED = 2
SHIP_A_COOLDOWN = 500
SHIP_A_COOLDOWN_COUNT = 80
SHIP_A_HP = 50
SHIP_A_COLLIDE_RADIUS = 7

SHIP_B_SPEED = 2
SHIP_B_COOLDOWN = 200
SHIP_B_COOLDOWN_COUNT = 120
SHIP_B_HP = 400
SHIP_B_COLLIDE_RADIUS = 7

SHIP_C_SPEED = 0.7
SHIP_C_COOLDOWN = 200
SHIP_C_COOLDOWN_COUNT = 180
SHIP_C_HP = 650
SHIP_C_COLLIDE_RADIUS = 7

BLADE_SPIN_SPEED = 15
BLADE_OFFSET = (-20, -20)


SHIP_A_1_IMG = 'ship_a_1.png'
SHIP_A_2_IMG = 'ship_a_2.png'
SHIP_A_3_IMG = 'ship_a_3.png'
SHIP_A_4_IMG = 'ship_a_4.png'
SHIP_A_5_IMG = 'ship_a_5.png'
SHIP_A_6_IMG = 'ship_a_6.png'
SHIP_A_SHADOW = 'ship_a_shadow.png'

SHIP_B_1_IMG = 'ship_b_1.png'
SHIP_B_2_IMG = 'ship_b_2.png'
SHIP_B_3_IMG = 'ship_b_3.png'
SHIP_B_4_IMG = 'ship_b_4.png'
SHIP_B_5_IMG = 'ship_b_5.png'
SHIP_B_6_IMG = 'ship_b_6.png'
SHIP_B_SHADOW = 'ship_b_shadow.png'


SHIP_C_1_IMG = 'ship_c_1.png'
SHIP_C_2_IMG = 'ship_c_2.png'
SHIP_C_3_IMG = 'ship_c_3.png'
SHIP_C_4_IMG = 'ship_c_4.png'
SHIP_C_5_IMG = 'ship_c_5.png'
SHIP_C_6_IMG = 'ship_c_6.png'
SHIP_C_SHADOW = 'ship_c_shadow.png'


# turret config
TURRET_A_HP = 300
TURRET_A_COOLDOWN = 180
TURRET_A_COOLDOWN_COUNT = 120
TURRET_A_BASE_IMG = 'turret_a_base.png'
TURRET_A_BARREL_IMG = 'turret_a_barrel.png'
TURRET_A_COOLDOWN = 120
TURRET_A_COOLDOWN_COUNT = 60
TURRET_A_COLLIDE_RADIUS = 15


# collision 
COLLISION_DAMAGE = 10

# my bullet config
MY_BULLET_SPEED_Y = 10
MY_BULLET_SPEED_X = 0.5

MY_BULLET_0_DAMAGE = 50
MY_BULLET_0_COLLIDE_RADIUS = 3
MY_BULLET_0_CENTER_OFFSET = (2, 2)

MY_BULLET_1_DAMAGE = 75
MY_BULLET_1_COLLIDE_RADIUS = 4
MY_BULLET_1_CENTER_OFFSET = (3, 3)

MY_BULLET_2_DAMAGE = 100
MY_BULLET_2_COLLIDE_RADIUS = 5
MY_BULLET_2_CENTER_OFFSET = (4, 4)

# enemy bullet config
AIM_BULLET_COOLDOWN = 6


BULLET_A_SPEED = 1.5
BULLET_A_DAMAGE = 20
BULLET_A_1_IMG = 'bullet_a_1.png'
BULLET_A_2_IMG = 'bullet_a_2.png'
BULLET_A_COLLIDE_RADIUS = 3
BULLET_A_CENTER_OFFSET = (3, 3)

BULLET_B_SPEED = 2
BULLET_B_DAMAGE = 40
BULLET_B_1_IMG = 'bullet_b_1.png'
BULLET_B_2_IMG = 'bullet_b_2.png'
BULLET_B_COLLIDE_RADIUS = 3
BULLET_B_CENTER_OFFSET = (3, 3)



BULLET_C_SPEED = 1.5
BULLET_C_DAMAGE = 15
BULLET_C_1_IMG = 'bullet_c_1.png'
BULLET_C_2_IMG = 'bullet_c_2.png'
BULLET_C_COLLIDE_RADIUS = 2
BULLET_C_CENTER_OFFSET = (2, 2)

BULLET_C_COOLDOWN = 6
BULLET_C_NUMBER = 10

BULLET_D_SPEED = 0.7
BULLET_D_DAMAGE = 50
BULLET_D_1_IMG = 'bullet_d_1.png'
BULLET_D_2_IMG = 'bullet_d_2.png'
BULLET_D_COLLIDE_RADIUS = 4
BULLET_D_CENTER_OFFSET = (4, 4)


BULLET_E_SPEED = 0.5
BULLET_E_DAMAGE = 50
BULLET_E_1_IMG = 'bullet_d_1.png'
BULLET_E_2_IMG = 'bullet_d_2.png'
BULLET_E_COLLIDE_RADIUS = 4
BULLET_E_CENTER_OFFSET = (4, 4)


# powerup config
POWERUP_SPEED = 0.7
POWERUP_SCATTER_RANGE_Y = 30
POWERUP_SCATTER_RANGE_X = 40
POWERUP_SCATTER_SPEED_Y = 1
POWERUP_OFFSET_SPEED = 0.5
POWERUP_OFFSET_RANGE = 20
POWERUP_COLLIDE_RADIUS = 12

ORB_SPIN_SPEED = 5 # degrees per frame

FIRE_UP = 'fire_up.png'
FIRE_UP_OFFSET = (5, 5)

SHIELD = 'shield.png'
SHIELD_OFFSET = (5, 5)
SHIELD_HP = 50

# explosion config
EXPLOSION_COOLDOWN = 3


# fps layer config
FPS_FONT_SIZE = 32
FPS_ALPHA = 180 # 0 --> 255 : transparent --> opaque
FPS_COOLDOWN = 10

# SFX config
BGM = 'arena1.ogg'
EXPLOSION = 'explosion.ogg'