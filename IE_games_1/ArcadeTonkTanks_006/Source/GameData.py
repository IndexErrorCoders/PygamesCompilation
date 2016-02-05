# GameData : this module contains all global constants & variables
#
# Arcade Tonk Tanks 0.0.6
#
# Module created on 2009-11-02 by Koen Lefever. License: GPL v.3
###################################################################

from pygame.locals import *
from Source import BattleGround

screenrect     = Rect(0, 0, 1024, 768)      # constant: complete window
arenarect      = Rect(0, 0, 800, 768)       # constant: part of window to play in
scorerect      = Rect(800, 0, 224, 768)     # constant: part of the window with score board
tankspeed      = 1                          # constant: actual speed = tankspeed * tank.gear
angle          = 7.5                        # constant: if 90/angle is integer, the up, down, left & right movements will be straight
animstep = 0                                # variable: animation cycle

# Game Options
gearcooldown = 5                            # variable: time between switching gears & delay when changing values in options screen
maxbullets = 5                              # variable: increase to allow more bullets on screen at the same time
bulletloadtime = 15                         # variable: increase to shoot slower
bulletspeed = 8                             # variable: increase to have faster bullets
triggerhappiness = 3                        # variable: increase to make the A.I. tanks shoot more


#Define BattleGrounds
battleground = [BattleGround("Ground Zero", "Arcade_tanks_background.jpg",
                             [Rect(0, 0, 1024, 1), Rect(0, 0, 1, 768), Rect(795, 0, 8, 768), Rect(0, 763, 1024, 1), Rect(1023, 0, 1, 768),
                              Rect(1, 50, 60, 10), Rect(1, 705, 60, 10), Rect(740, 50, 60, 10), Rect(740,705,60,10),
                              Rect(372, 0, 10, 60), Rect(430, 0, 10, 60), Rect(372, 700, 10, 68), Rect(430, 700, 10, 68),
                              Rect(310, 250, 180, 30), Rect(310, 503, 180, 30), Rect(50,369,180,30), Rect(570,369,180,30)],
                             [], [[380,712,90], [5,7,0], [745,717,180],[5,717,0],[745,7,180],[380,10,270]], True, False),                              
                BattleGround("Around the blocks", "The-Rock-0.1-sans_bunker.png",
                             [Rect(0, 0, 1024, 1), Rect(0, 0, 1, 768), Rect(795, 0, 8, 768), Rect(0, 763, 1024, 1), Rect(1023, 0, 1, 768),
                              Rect(1, 60, 100, 150), Rect(1, 545, 100, 150), Rect(700, 60, 100, 150), Rect(700,545,100,150),
                              Rect(212, 0, 160, 80), Rect(440, 0, 160, 80), Rect(212, 688, 160, 80), Rect(440, 688, 160, 80),
                              Rect(310, 145, 180, 140), Rect(310, 483, 180, 140), Rect(70,279,180,210), Rect(550,279,180,210)],
                             [], [[380,712,90], [5,7,0], [745,717,180], [5,717,0], [745,7,180], [380,10,270]], True, False),
                BattleGround("The Monolith", "Arcade_tanks_background.jpg", [Rect(310, 200, 180, 350)], [],
                             [[380,717,90], [5,7,0], [745,717,180], [5,717,0], [745,7,180], [380,10,270]], True, False),
                BattleGround("The Void", "Arcade_tanks_background.jpg", [], [],
                             [[380,717,90], [5,7,0], [745,717,180], [5,717,0], [745,7,180], [380,10,270]], True, False),
                BattleGround("The Canal", "The-Rock-0.1-sans_bunker.png",
                             [Rect(143, 0, 145, 70), Rect(515, 0, 145, 70),
                              Rect(296, 232, 240, 166), Rect(662, 411, 141, 162), Rect(0, 411, 137, 166),
                              Rect(143, 699, 145, 70), Rect(515, 699, 145, 70)],
                             [Rect(0, 301, 803, 208)],
                             [[380,717,90], [5,7,0], [745,717,180], [5,717,0], [745,7,180], [380,10,270]], True, True),
                BattleGround("Atlantikwall","Atlantikwall.png",                                      
                             [Rect(694, 0, 108, 8), Rect(722, 64, 80, 44), Rect(798, 7, 5, 56), Rect(330, 216, 55, 36),
                              Rect(387, 233, 20, 21), Rect(329, 310, 67, 50), Rect(395, 309, 13, 27), Rect(329, 251, 5, 57),
                              Rect(157, 269, 21, 79), Rect(87, 268, 14, 82), Rect(101, 247, 68, 25), Rect(0, 661, 42, 22),
                              Rect(0, 682, 81, 19), Rect(0, 759, 94, 8), Rect(0, 702, 5, 57), Rect(331, 726, 64, 40),
                              Rect(372, 685, 26, 81), Rect(454, 686, 24, 81), Rect(477, 698, 35, 67), Rect(397, 761, 57, 6),
                              Rect(720, 682, 81, 20), Rect(759, 631, 42, 48), Rect(718, 759, 84, 8), Rect(796, 703, 6, 62)],
                             [Rect(0, 0, 558, 23), Rect(1, 15, 508, 21), Rect(0, 29, 429, 52), Rect(0, 83, 246, 131),
                              Rect(192, 218, 120, 283), Rect(172, 385, 236, 115), Rect(247, 482, 136, 32), Rect(1, 211, 54, 359),
                              Rect(1, 566, 46, 17), Rect(0, 581, 28, 15), Rect(185, 204, 94, 24), Rect(34, 194, 41, 47),
                              Rect(19, 222, 51, 190), Rect(393, 13, 56, 44), Rect(219, 163, 36, 85), Rect(221, 374, 157, 134),
                              Rect(288, 228, 29, 168)],
                             [[400,706,90], [740,15,180], [105,285,270], [340,264,0], [14,714,0], [740,713,180]], False, False),
                BattleGround("The River","The-River-0.2.png",
                             [Rect( 1 , 0 , 94 , 23 ),Rect( 0 , 24 , 21 , 53 ),Rect( 1 , 78 , 95 , 24 ),Rect( 327 , 0 , 61 , 52 ),
                              Rect( 373 , 13 , 18 , 78 ),Rect( 368 , 1 , 25 , 90 ),Rect( 377 , 1 , 71 , 15 ),Rect( 446 , 1 , 25 , 89 ),
                              Rect( 0 , 374 , 21 , 95 ),Rect( 76 , 373 , 23 , 95 ),Rect( 13 , 448 , 64 , 31 ),Rect( 430 , 338 , 95 , 29 ),
                              Rect( 439 , 421 , 85 , 31 ),Rect( 415 , 363 , 35 , 54 ),Rect( 429 , 417 , 20 , 29 ),Rect( 342 , 701 , 52 , 66 ),
                              Rect( 373 , 673 , 25 , 93 ),Rect( 452 , 673 , 24 , 28 ),Rect( 453 , 703 , 53 , 64 ),Rect( 398 , 746 , 52 , 21 ),
                              Rect( 759 , 637 , 43 , 54 ),Rect( 706 , 677 , 95 , 21 ),Rect( 780 , 701 , 22 , 65 ),Rect( 705 , 754 , 73 , 13 )],
                             [Rect( 0 , 708 , 87 , 59 ),Rect( 11 , 650 , 127 , 54 ),Rect( 38 , 569 , 106 , 134 ),Rect( 46 , 497 , 102 , 67 ),
                              Rect( 154 , 443 , 17 , 84 ),Rect( 253 , 434 , 84 , 65 ),Rect( 290 , 257 , 83 , 208 ),Rect( 268 , 383 , 25 , 47 ),
                              Rect( 330 , 222 , 55 , 211 ),Rect( 388 , 221 , 146 , 70 ),Rect( 537 , 198 , 103 , 58 ),Rect( 537 , 258 , 62 , 17 ),
                              Rect( 106 , 466 , 45 , 29 ),Rect( 759 , 0 , 41 , 73 ),Rect( 626 , 43 , 129 , 54 ),Rect( 562 , 101 , 95 , 26 ),
                              Rect( 598 , 64 , 95 , 47 ),Rect( 597 , 63 , 110 , 45 )],
                             [[400, 692, 90],[30, 33, 0],[395, 32, 270],[25, 392, 90],[459, 376, 0],[724, 709, 180]], False, False)]


battlegroundnr = len(battleground)-1      # start game with the last battleground

"""# Maze definitions (list with lists of rectangles representing walls)
mazes = [[Rect(0, 0, 1024, 1), Rect(0, 0, 1, 768), Rect(795, 0, 8, 768), Rect(0, 763, 1024, 1), Rect(1023, 0, 1, 768),
        Rect(1, 50, 60, 10), Rect(1, 705, 60, 10), Rect(740, 50, 60, 10), Rect(740,705,60,10),
        Rect(372, 0, 10, 60), Rect(430, 0, 10, 60), Rect(372, 708, 10, 60), Rect(430, 708, 10, 60),
        Rect(310, 250, 180, 30), Rect(310, 503, 180, 30),Rect(50,369,180,30),Rect(570,369,180,30)], # Ground Zero
        [Rect(0, 0, 1024, 1), Rect(0, 0, 1, 768), Rect(795, 0, 8, 768), Rect(0, 763, 1024, 1), Rect(1023, 0, 1, 768),
        Rect(1, 60, 100, 150), Rect(1, 545, 100, 150), Rect(700, 60, 100, 150), Rect(700,545,100,150),
        Rect(212, 0, 160, 80), Rect(440, 0, 160, 80), Rect(212, 688, 160, 80), Rect(440, 688, 160, 80),
        Rect(310, 150, 180, 150), Rect(310, 483, 180, 150),Rect(70,279,180,210),Rect(550,279,180,210)], # Blocks
        [Rect(310, 200, 180, 350)], # The Monolith
        []] # The Void                                                                      # variable
mazenames = ["Ground Zero","Around The Blocks","The Monolith","The Void"]                   # constant
mazenumber = 0                                                                              # variable
maze = mazes[mazenumber]                                                                    # variable
mazename = mazenames[mazenumber]                                                            # variable"""

# Respawn point: [x,y,angle]
respawnpoints = [[5,7,0], [745,717,180],[5,717,0],[745,7,180],[380,10,270],[380,717,90]]    # constant
respawnlist = []    # variable: list to keep where recently a tank has respawned - to prevent the next tank respawning there

# Player colours and numbers
red    = 0                                                                                  # constant
blue   = 1                                                                                  # constant
green  = 2                                                                                  # constant
yellow = 3                                                                                  # constant
grey   = 4                                                                                  # constant
purple = 5                                                                                  # constant
colour = ['red','blue','green','yellow','grey','purple']                                    # constant

gamestate = "splash screen"                                                                 #variable

