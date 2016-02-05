# -*- coding: utf-8 -*-

__author__ = "$Author: Phelerox $"
__version__= "$Version: 0.4.3 $"
__date__   = "$Date: 2009-11-19 $"
__copyright__ = "$Copyleft (c) 2009 Marco Baxemyr $"
__license__ = "$License: GPL $"

import os, sys, pickle
from random import randint, choice
from math import sin, cos, radians, ceil, floor

import pygame
from pygame import Rect, Color
from pygame.sprite import Sprite

from gridmap import GridMap
from pathfinder import PathFinder
from simpleanimation import SimpleAnimation
import pyconsole
from pyconsole_syntax import *
from utils import Timer
from vec2d import vec2d
from widgets import Box, MessageBoard, TextWidget, TextMessage
from Creeps import *
from Towers import *


global menu, console


def create_enemy_image_lists():
    enemy_path = os.path.join(os.getcwd(), "images/enemies/")
    undead_path = os.path.join(enemy_path, "undead/")
    undeadfiles = os.listdir(undead_path)
    undead_list = []
    for undeadfile in undeadfiles:
        if "_0.png" in undeadfile and undeadfile[0:-5]+"45.png" in undeadfiles:
            undeadfiles.remove(undeadfile[0:-5]+"45.png")
            undead_list.append([os.path.join(undead_path, undeadfile[0:-5]+"0.png"),os.path.join(undead_path, undeadfile[0:-5]+"45.png")])
    print undead_list
    return [undead_list]



class Menu(object):
    BG_IMG = 'images/ZombieInvasionBg1.png'
    TITLE_IMG = 'images/widgets/menu_title/tower_defense.png'
    TITLE_IMG2 = 'images/widgets/menu_title/py.png'
    NEW_GAME_CLICK = pygame.locals.USEREVENT +1
    HELP_CLICK = pygame.locals.USEREVENT + 2
    EXIT_CLICK = pygame.locals.USEREVENT + 3
    TITLE_CLICK = pygame.locals.USEREVENT + 4
    def __init__(self, screen, pause=False, game=None):
        self.bg_img = pygame.image.load(self.BG_IMG).convert_alpha()
        self.title_img = pygame.image.load(self.TITLE_IMG).convert_alpha()
        self.title_img2 = pygame.image.load(self.TITLE_IMG2).convert_alpha()
        self.screen = screen
        self.pause = pause
        self.game = game
        # Text Widget list
        self.text_widgets = []

        self.main()

    def draw_bg(self):
            self.screen.blit(self.bg_img, (0,0))
            self.screen.blit(self.title_img, (self.screen.get_rect().center[0] - (self.title_img.get_size()[0] / 2) + (self.title_img2.get_size()[0]) / 2, (self.screen.get_rect().center[1] - self.title_img.get_size()[1] / 2 ) - 200))
            self.screen.blit(self.title_img2, ((self.screen.get_rect().center[0] - (self.title_img2.get_size()[0] / 2) - (self.title_img.get_size()[0]) / 2) + 10, (self.screen.get_rect().center[1] - self.title_img2.get_size()[1] / 2 ) - 190))
    def main(self):
        self.state = "Main"
        if not self.pause:
            self.draw_bg()
            #Create our Text Widgets

##            self.title_text = TextWidget("Py TowerDefense", colour=Color("darkred"), size=98, highlight_increase=0, event=self.TITLE_CLICK, font_filename='images/fonts/BIRTH_OF_A_HERO.ttf', bold=False, show_highlight_cursor=False)
##            self.title_text.rect.center = self.screen.get_rect().center
##            self.title_text.rect.top = 50
##            self.text_widgets.append(self.title_text)


            self.new_game_text = TextWidget("Start Game", colour=Color("gold"), size=44, highlight_increase=3, event=self.NEW_GAME_CLICK, font_filename='images/fonts/BIRTH_OF_A_HERO.ttf', bold=False)
            self.new_game_text.rect.center = self.screen.get_rect().center
            self.new_game_text.rect.left = 50
            self.text_widgets.append(self.new_game_text)

##            self.image_buttons = []
##            start_button = widgets.ImageButton(screen, 'images/widgets/menu_title/start_game.png', Rect(50, 30, 100,100), callback=self.run_game)
##            start_button.rect.center = self.screen.get_rect().center
##            start_button.rect.left = 50
##            start_button.rect.top += 30
##            self.image_buttons.append(start_button)


            self.help_text = TextWidget("Help", colour=Color("gold"), size=44, highlight_increase=3, event=self.HELP_CLICK, font_filename='images/fonts/BIRTH_OF_A_HERO.ttf', bold=False)
            self.help_text.rect.center = self.screen.get_rect().center
            self.help_text.rect.top += 100
            self.help_text.rect.left = 50
            self.text_widgets.append(self.help_text)

            self.exit_text = TextWidget("Exit Game", colour=Color("gold"), size=44, highlight_increase=3, event=self.EXIT_CLICK, font_filename='images/fonts/BIRTH_OF_A_HERO.ttf', bold=False)
            self.exit_text.rect.center = self.screen.get_rect().center
            self.exit_text.rect.top += 200
            self.exit_text.rect.left = 50
            self.text_widgets.append(self.exit_text)

        else:
            menutextstring = "Press SPACE to resume game."
            overlay_sf = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            overlay_sf.fill(Color(10, 10, 10))
            overlay_sf.set_alpha(220)
            self.screen.blit(overlay_sf, (0,0))
            menufont = pygame.font.SysFont('arial', 30)
            menurect = pygame.Rect(200,200,400,200)
            textsurface = widgets.render_textrect(menutextstring, menufont, menurect, (130,40, 0), (0,0,0), justification=0)
            self.screen.blit(textsurface, (200,200))# ((self.screen.get_width() / 2) - menutext.get_width() / 2, (self.screen.get_height() / 2) - menutext.get_height()))
        self.loop()

    def help(self):
        self.state = "Help"
        menutextstring = "Use the tower buttons to the right to place towers (or 1,2,3,4..)\n\nSPACE pauses the game.\n\nCtrl+G Displays the Grid.\n\nSelect a Tower and press S to sell\n\n\nPress SPACE to return."
##        overlay_sf = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
##        overlay_sf.fill(Color(0, 0, 0))
##        overlay_sf.set_alpha(255)
##        self.screen.blit(overlay_sf, (0,0))
        self.draw_bg()
        menufont = pygame.font.SysFont('arial', 30)
        menurect = pygame.Rect(100,100,600,400)
        textsurface = widgets.render_textrect(menutextstring, menufont, menurect, (130,40, 0), (0,0,0), justification=0)
        self.screen.blit(textsurface, (100,100))#((self.screen.get_width() / 2) - menutext.get_width() / 2, (self.screen.get_height() / 2) - menutext.get_height()))
        self.loop()

    def loop(self):
        self.resume = False
        while True:
            #pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not self.pause and self.state == "Main":
                            self.quit()
                        else:
                            if self.state == "Help":
                                self.main()
                            self.resume = True
                            self.pause = False
                            break
                    elif event.key == pygame.K_SPACE:
                        if not self.pause and self.state == "Main":
                            self.run_game()
                        elif self.state == "Help":
                            self.main()
                        else:
                            self.resume = True
                            self.pause = False
                            break
                    elif event.key== pygame.K_h and self.state == "Main":
                        self.help()
                #TextWidget stuff:
                if self.state == "Main":
                    if (event.type == pygame.ACTIVEEVENT):
                        if (event.gain == 1):
                            for text in self.text_widgets:
                                text.dirty = True
                            self.draw()
                        elif (event.state ==2):
                            #We are hidden so wait for the next event
                            pygame.event.post(pygame.event.wait())
                    elif (event.type == pygame.MOUSEMOTION):
                        for text in self.text_widgets:
                            orig = text.highlight
                            text.highlight = text.rect.collidepoint(event.pos)
                            if orig != text.highlight:
                                for t in self.text_widgets:
                                    t.dirty = True
                                self.draw_bg() #Redraw background if highlight state changes
                                #self.draw()
                    elif (event.type == pygame.MOUSEBUTTONDOWN):
                        for text in self.text_widgets:
                            text.on_mouse_button_down(event)
##                        for button in self.image_buttons:
##                            if button.rect.collidepoint(event.pos):
##                                button.clicked = True
                    elif (event.type == pygame.MOUSEBUTTONUP):
                        for text in self.text_widgets:
                            text.on_mouse_button_up(event)
                    elif (event.type == self.NEW_GAME_CLICK):
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        self.run_game()
                    elif (event.type == self.HELP_CLICK):
                        pygame.mouse.set_cursor(*pygame.cursors.arrow)
                        self.help()
                    elif (event.type == self.EXIT_CLICK):
                        self.quit()
            if self.resume == True:
                self.game.paused = False
                break
            self.draw()

    def draw(self):
        """Draw everything"""

##        for button in self.image_buttons:
##            if button.dirty == True:
##                self.draw_bg()
##                for text in self.text_widgets:
##                    text.dirty = True
##                break
##
##        for button in self.image_buttons:
##            button.update()

        rects = []
        for text in self.text_widgets:
            rect = text.draw(self.screen)
            if (rect):
                rects.append(rect)
        pygame.display.update(rects)
        pygame.display.flip()


    def run_game(self):
        self.game = Game(self.screen)
        self.game.run()
        del self

    def quit(self):
        if True:  #UserConfirm(screen, message="Exit game?"):
            pygame.quit()
            sys.exit()

class Game(object):
    # Game parameters
    BG_IMG = 'images/ZombieInvasionBg1.png'
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    GRID_SIZE = 20
    FIELD_SIZE = 620, 500
    ENEMY_FILENAME_LISTS = create_enemy_image_lists()
##    LEVEL_1_FILENAMES = [
##        ('images/creeps/zombie_0.png', 'images/creeps/zombie_45.png')
##        ]
##    LEVEL_2_FILENAMES = [
##        #('images/creeps/zombie_brown_0.png', 'images/creeps/zombie_brown_45.png')
##        ('images/creeps/skeleton_master_wizard_0.png', 'images/creeps/skeleton_master_wizard_45.png')
##        ]
##    LEVEL_3_FILENAMES = [
##        ('images/creeps/zombiesoldier_0.png', 'images/creeps/zombiesoldier_45.png')
##        ]
##    LEVEL_4_FILENAMES = [
##        ('images/creeps/Dracula_0.png', 'images/creeps/Dracula_45.png')
##        ]
##    LEVEL_5_FILENAMES = [
##        ('images/creeps/fatto_0.png' , 'images/creeps/fatto_45.png')
##        ]
##    LEVEL_6_FILENAMES = [
##        ('images/creeps/skeleton_wizard_0.png' , 'images/creeps/skeleton_wizard_45.png')
##        ]
##    LEVEL_7_FILENAMES = [
##        ('images/creeps/insectghost_0.png' , 'images/creeps/insectghost_45.png')
##        ]
##    LEVEL_8_FILENAMES = [
##        ('images/creeps/zombie_brownie_spear_0.png' , 'images/creeps/zombie_brownie_spear_45.png')
##        ]
##    LEVEL_9_FILENAMES = [
##        ('images/creeps/vampire_lieutenant_0.png' , 'images/creeps/vampire_lieutenant_45.png')
##        ]
##    LEVEL_10_FILENAMES = [
##    ('images/creeps/dead_man_0.png', 'images/creeps/dead_man_45.png')
##    ]
##    LEVEL_11_FILENAMES = [
##    ('images/creeps/Armored_Zombie_Boss_0.png', 'images/creeps/Armored_Zombie_Boss_45.png')
##    ]

    CREEPS_PER_LEVEL = 40
    n_enemies_list = []
    for level in xrange(21): #This sets how many levels there are Should be one more than amount of levels.
        n_enemies_list.append(CREEPS_PER_LEVEL)
    n_enemies_list[10] = 1 #level 11 is a boss

    def __init__(self, screen):
        global console
        self.screen = screen
        self.bg_img = pygame.image.load(self.BG_IMG).convert_alpha()
        self.bg_img_rect = self.bg_img.get_rect()
        self.field_border_width = 4
        field_outer_width = self.FIELD_SIZE[0] + 2 * self.field_border_width
        field_outer_height = self.FIELD_SIZE[1] + 2 * self.field_border_width
        self.field_rect_outer = Rect(20, 60, field_outer_width, field_outer_height)
        self.field_bgcolor = Color(80, 50, 50, 100) #Color("darkgrey")
        self.field_border_color = Color(0, 0, 0)
        self.field_box = Box(self.screen,
            rect=self.field_rect_outer,
            bgcolor=None,
            border_width=self.field_border_width,
            border_color=self.field_border_color,
            tile='images/sand.jpg')
        self.field_inner_rect = Rect(20 + self.field_border_width, 60 + self.field_border_width, self.FIELD_SIZE[0], self.FIELD_SIZE[1])


        #Statistics
        self.level = 1
        self.attacks = 0
        self.kills = 0
        self.money = 200
        self.upgradepts = 0#IDEA: For each <level> completed, the player earns <level> upgrade points. Upgrading a rank I costs 1 upgrade point. Rank II 2 points. Rank III 4 points. Rank IV 8 points. This idea would exterminate the tower experience system.
        self.lives = 30
        self.leaks = 0
        self.won = False
        self._spawned_creep_count = 0
        self._spawned_creep_count_level = 0
        self._placed_tower_count = 0
        self.last_placed_tower_id = 0
        self.level_complete = False
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.paused = False

        #pyconsole
        console = pyconsole.Console(self.screen, (0,0,800,200), functions={"addgold":self.gold_cheat, "addlives":self.add_lives,"MoreEnemies":self.spawn_more_this_level,"exit":self.quit, "exec":self.console_exec},syntax={re_add:console_add,re_function:console_func})

        self.toolbox = Box(self.screen, rect = Rect(644, 260, 155, 45), bgcolor = (50,20,0), border_width = 4, border_color = (0,0,0))

        self.tboard_text = ['Level ' + str(self.level)]
        self.tboard_rect = Rect(20, 15, field_outer_width, 40)
        self.tboard_bgcolor = Color(50, 20, 0)
        self.tboard = MessageBoard(self.screen,
            rect=self.tboard_rect,
            bgcolor=self.tboard_bgcolor,
            border_width=4,
            border_color=Color('black'),
            text=self.tboard_text,
            font=('tahoma', 20),
            font_color=Color('yellow'))

        self.mboard_text = []
        self.mboard_rect = Rect(660, 80, 130, 140)
        self.mboard_bgcolor = Color(50, 20, 0)
        self.mboard = MessageBoard(self.screen,
            rect=self.mboard_rect,
            bgcolor=self.mboard_bgcolor,
            border_width=4,
            border_color=Color('black'),
            text=self.mboard_text,
            font=('verdana', 16),
            font_color=Color('white'))

        #########Tooltips##########

	#Purchasable towers
        self.tooltip_text = []#[str(self.tower_1.name),
                    #"Damage: " + str(self.tower_1.damage),
                    #"Attack Speed: " + str(self.tower_1.attack_speed/1000.),
                    #"DPS: ~" + str(int(round(self.tower_1.damage / (self.tower_1.attack_speed / 1000.)))),
                    #"Range: " + str(self.tower_1.radius) +"px"]
        self.tooltip_rect = Rect(60,30,30,30)
        self.tooltip_bgcolor = Color(50, 20, 0)
        self.tooltip = MessageBoard(self.screen,
            rect=self.tooltip_rect,
            bgcolor=self.tooltip_bgcolor,
            border_width=4,
            border_color=Color('black'),
            text=self.tooltip_text,
            font=('verdana', 9),
            font_color=Color('white'),
            tooltip=True,
            game=self,
            alpha=170)
        #self.tower_1.kill()

        #Selected info
        self.selection = None
        self.selection_info_active = False
        self.selection_info_text = []
        self.selection_info_rect = Rect(60,30,30,30)
        self.selection_info_bgcolor = Color(50, 20, 0)
        self.selection_info = MessageBoard(self.screen,
        rect=self.selection_info_rect,
        bgcolor=self.selection_info_bgcolor,
        border_width=4,
        border_color=Color('black'),
        text=self.selection_info_text,
        font=('verdana', 9),
        font_color=Color('white'),
        tooltip=True,
        game=self)

        self.placing_tower = False
        self.placing_tower_type = [0,1]
        self.place_tower_draw_pos = None

        #self.creep_images_expression_base = "[(pygame.image.load(f1).convert_alpha(), pygame.image.load(f2).convert_alpha()) for (f1, f2) in game.LEVEL_X_FILENAMES]".split('X')

        explosion_img = pygame.image.load('images/explosion1.png').convert_alpha()
        self.explosion_images = [
            explosion_img, pygame.transform.rotate(explosion_img, 90)]

        self.field_rect = self.get_field_rect()
        self.deploy_rect = Rect(20, 60, self.FIELD_SIZE[0]-20, self.FIELD_SIZE[1]-20) #for forcing tower-placement within playing field
        self.toolbox_rect = self.get_toolbox_rect()


        self.entrance_rect = Rect(
            self.field_rect.left,
            self.field_rect.top,
            self.GRID_SIZE * 2,
            self.GRID_SIZE * 2)

        self.exit_rect = Rect(
            self.field_rect.right - self.GRID_SIZE * 2,
            self.field_rect.bottom - self.GRID_SIZE * 2,
            self.GRID_SIZE * 2,
            self.GRID_SIZE * 2)

        self.gold_image = pygame.image.load('images/money/goldenpenny.png').convert_alpha()
        ##########################

        # Create the grid-path representation of the field
        #
        self.grid_nrows = self.FIELD_SIZE[1] / self.GRID_SIZE
        self.grid_ncols = self.FIELD_SIZE[0] / self.GRID_SIZE
        self.goal_coord = (self.grid_nrows - 1, self.grid_ncols - 1)
        self.gridpath = GridPath(
            nrows=self.grid_nrows,
            ncols=self.grid_ncols,
            goal=self.goal_coord)


        self.options = dict(
            draw_grid=True)

        #Tower-instances for TOOLTIP purposes
        self.tower_templates = []
        self.tower_upgrade_templates = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for n in range(1, 9000):
            expression = ''.join(["self.tower_templates.append(Tower_", str(n), "(self.screen, self, template=True))"])
            try:
                exec expression
            except:
                self.tower_type_amount = n - 1
                print self.tower_type_amount, "Towers"
                break
            for N in range(1, 9000):
                expression2 = ''.join(["self.tower_upgrade_templates[",str(n-1),"].append(Tower_", str(n),"_",str(N), "(self.screen, self, template=True))"])
                try:
                    exec expression2
                except:
                    break
        print self.tower_upgrade_templates

        ##
        self.text_messages = []

        self.towers = pygame.sprite.Group()

        self.tower_call_expression_base = "self.towers.add(Tower_1(_screen, _game, position=pos))".split('1')

        self.add_creep_expression_base = "self.creeps.add(Creep_*(screen=self.screen, game=self))".split('*')

        #Sprite Group for storing active projectiles
        self.projectiles = pygame.sprite.Group()
        #########################################################

        # Create the creeps group and the first creep
        self.creeps = pygame.sprite.Group()
        self.creep_spawn_timer = None
        self.level_timer = Timer(5000, self.next_level, oneshot=True)

    def level_finished(self):
        self.creep_spawn_timer = None
        self._spawned_creep_count_level = 0
        self.level += 1
        self.level_timer = Timer(10000, self.next_level, oneshot=True)
        print "10 seconds until next level"

    def next_level(self):
        print "next_level"
        self.add_creep_expression = ''.join([self.add_creep_expression_base[0], str(self.level), self.add_creep_expression_base[1]])
        self.creep_spawn_timer = Timer(500, self.spawn_new_creep)

    def place_tower_draw(self, pos):
        Type = self.placing_tower_type
        try:
            image = self.tower_templates[Type[1] - 1].image
        except:
            print("Defaulting to normal tower image")
            image = pygame.image.load('images/towers/arrow_tower_1.png').convert_alpha()
        place_surface = pygame.Surface((40, 40))
        place_surface.set_alpha(150, pygame.RLEACCEL)
        coord = self.xy2coord(pos)
        snap_pos = self.coord2xy(coord)
        place_surface.blit(image, (0,0))
        self.screen.blit(place_surface, snap_pos)
        font = pygame.font.SysFont('arial', 15)
        font.set_bold(True)
        text = font.render("Press ESC to abort.", True, (0,0,0))
        self.screen.blit(text, (snap_pos[0]+50, snap_pos[1]+20))

    def place_tower(self, pos):
        Type = self.placing_tower_type
        self.placing_tower = False
        self.place_tower_draw_pos = None
        coord = self.xy2coord(pos)
        snap_pos = self.coord2xy(coord)
        if self.field_inner_rect.collidepoint(snap_pos) and self.field_inner_rect.collidepoint((snap_pos[0]+38, snap_pos[1]+30)):
            self.add_tower(Type, self.screen, self, pos)
        else:
            self.text_messages.append(widgets.TextMessage(self.screen, "Not within game field!", vec2d(self.screen.get_width() / 2, self.screen.get_height() / 2), duration=3800, size=32, initialdelay=1000, color=Color("red")))
            self.money += self.tower_templates[self.placing_tower_type[1] -1].cost

    def add_tower(self, Type, _screen, _game, pos):
        tower_call_expression = ''.join([self.tower_call_expression_base[0], str(Type[1]), self.tower_call_expression_base[1]])
        eval(tower_call_expression)



    def next_on_path(self, coord):
        """ Given a coord, returns the next coord on the path to
            the goal. None is returned if no path exists from
            the coord.
        """
        return self.gridpath.get_next(coord)

    def xy2coord(self, pos):
        """ Convert a (x, y) pair to a (nrow, ncol) coordinate
        """
        x, y = (pos[0] - self.field_rect.left, pos[1] - self.field_rect.top)
        return (int(y) / self.GRID_SIZE, int(x) / self.GRID_SIZE)

    def coord2xy(self, coord):
      nrow, ncol = coord
      return (
        self.field_rect.left + ncol * self.GRID_SIZE,
        self.field_rect.top + nrow * self.GRID_SIZE)

    def coord2xy_mid(self, coord):
        """ Convert a (nrow, ncol) coordinate to a (x, y) pair,
            where x,y is the middle of the square at the coord
        """
        nrow, ncol = coord
        return (
            self.field_rect.left + ncol * self.GRID_SIZE + self.GRID_SIZE / 2,
            self.field_rect.top + nrow * self.GRID_SIZE + self.GRID_SIZE / 2)

    def is_goal_coord(self, coord):
        return coord == self.goal_coord

    def spawn_new_creep(self):
        if self._spawned_creep_count_level >= self.n_enemies_list[self.level-1] and not len(self.creeps):
            self.level_finished()
            return
        elif self._spawned_creep_count_level >= self.n_enemies_list[self.level-1]:
            return
        try:
            eval(self.add_creep_expression)
            self._spawned_creep_count += 1
            self._spawned_creep_count_level += 1
        except NameError:
            self.won = True

    def select(self, selection):
        self.selection_info_active = True
        self.selection = selection
        if selection.type == 'Tower':
            if self.selection.description:
                selection_description = "Description: "+self.selection.description
            else:
                selection_description = ""
            self.selection_exp = self.selection.experience
            self.selection_info.text = [str(self.selection.name),
            "Level: " + str(self.selection.level),
            "Damage: " + str(self.selection.damage),
            "Attack Speed: " + str(self.selection.attack_speed/1000.),
            "DPS: ~" + str(int(round(self.selection.damage / (self.selection.attack_speed / 1000.)))),
            "Range: " + str(self.selection.radius) +"px",
            selection_description]
        elif selection.type == 'Creep':
            self.selection_health = self.selection.health
            self.selection_info.text = [str(self.selection.name),
                                        "Level: " + str(self.selection.level),
                                        "HP: " + str(self.selection.health) + "/" + str(self.selection.health_init),
                                        "Speed: " + str(int(self.selection.speed*1000.)) + "px/s"]

    def get_field_rect(self):
        """ Return the internal field rect - the rect of the game
            field exluding its border.
        """
        return self.field_box.get_internal_rect()

    def get_toolbox_rect(self):
        """ Return the internal toolbox rect - excluding its border.
        """
        return self.toolbox.get_internal_rect()

    def lookup_creep(self, creep_id):
        for creep in self.creeps:
            if creep.id == creep_id:
                return creep
        return None

    def lookup_tower(self, tower_id):
        for tower in self.towers:
            if tower.id == tower_id:
                return tower
        return None

    def get_toolbox_rect_n(self, n):
        if n < 1:
          n = 1
        rows = 1
        if n > 4 and n <= 8:
          rows = 2
##        elif n > 10 and n <= 15:
##          rows = 3
##        elif n > 15 and n <= 20:
##          rows = 4
##        elif n > 20 and n <= 25:
##          rows = 5
##        elif n > 25 and n <= 30:
##          rows = 6
##        elif n > 30 and n <= 35:
##          rows = 7
##        elif n > 35 and n <= 40:
##          rows = 8

        n_rect = Rect(
        self.toolbox_rect.left + (30 * (n-1)) - ((rows-1) * 6 * 30) + 4 *n,
        self.toolbox_rect.top + (30 * ((rows-1))) + 4 * rows,
        (30),
        (30))
        return n_rect

    def draw_background(self):
##        img_rect = self.bg_img.get_rect()
##        nrows = int(self.screen.get_height() / img_rect.height) + 1
##        ncols = int(self.screen.get_width() / img_rect.width) + 1
##
##        for y in range(nrows):
##            for x in range(ncols):
##                img_rect.topleft = (x * img_rect.width,
##                                    y * img_rect.height)
        self.screen.blit(self.bg_img, (0,0))
        ##Triforce image in corner
        self.bg_overlay_tower = pygame.image.load('images/Triforce.png').convert_alpha()
        self.screen.blit(self.bg_overlay_tower, (653, 440))

    def draw_portals(self):
        entrance_sf = pygame.Surface((self.entrance_rect.w, self.entrance_rect.h))
        entrance_sf.fill(Color(80, 200, 80))
        entrance_sf.set_alpha(150)
        self.screen.blit(entrance_sf, self.entrance_rect)

        self.bg_portal_image = pygame.image.load('images/magic_stones.png').convert_alpha()
        self.screen.blit(self.bg_portal_image, (603, 528))

        exit_sf = pygame.Surface((self.exit_rect.w, self.exit_rect.h))
        exit_sf.fill(Color(200, 80, 80))
        exit_sf.set_alpha(150)
        self.screen.blit(exit_sf, self.exit_rect)

    def draw_grid(self):
        for y in range(self.grid_nrows + 1):
            pygame.draw.line(
                self.screen,
                Color(50, 50, 50),
                (self.field_rect.left, self.field_rect.top + y * self.GRID_SIZE - 1),
                (self.field_rect.right - 1, self.field_rect.top + y * self.GRID_SIZE - 1))

        for x in range(self.grid_ncols + 1):
            pygame.draw.line(
                self.screen,
                Color(50, 50, 50),
                (self.field_rect.left + x * self.GRID_SIZE - 1, self.field_rect.top),
                (self.field_rect.left + x * self.GRID_SIZE - 1, self.field_rect.bottom - 1))

    def draw(self):
        self.draw_background()
        self.field_box.draw()

        if self.options['draw_grid']:
            self.draw_grid()

        self.tboard.draw()
        self.mboard.text = self.mboard_text
        self.mboard.draw()

        self.toolbox.draw()

        self.screen.blit(self.gold_image, (750, 107))
        self.screen.blit(self.fps, (650, 20))
        if not self.selection_info_active or self.selection.type == 'Creep':
            self.screen.blit(self.build_upgrade_text, (724-(self.fpsfont.size("BUILD")[0]/2),245-(self.fpsfont.size("BUILD")[1]/2)))
        elif self.selection.type == "Tower":
            self.screen.blit(self.build_upgrade_text, (724-(self.fpsfont.size("UPGRADE")[0]/2),245-(self.fpsfont.size("UPGRADE")[1]/2)))
        #for n in range(25):

        #n += 1

        #pygame.draw.rect(self.screen, (200, 20, 20), self.get_toolbox_rect_n(n))
        if not self.selection_info_active or self.selection.type == 'Creep':
            for n in range(1, self.tower_type_amount + 1):
                self.screen.blit(self.tower_templates[n - 1].icon, self.get_toolbox_rect_n(n))
        elif self.selection.type == "Tower":
            if not str(self.selection.__class__)[22] == "_": #this means tier-two towers can't be upgraded
                for n in range(1, len(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1])+1):
                    self.screen.blit(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].icon, self.get_toolbox_rect_n(n))

        #for tower in self.towers:  #Uncomment the draw-function in Tower() Class, if that turns out to be the better way.
        #tower.draw()

        if self.selection_info_active:
            if self.selection.type == 'Tower':
                if self.selection_exp == self.selection.experience:
                    self.selection_info.draw()
                else:
                    self.select(self.selection)
                    self.selection_info.draw()
            elif self.selection.type == 'Creep':
                if self.selection_health == self.selection.health:
                    self.selection_info.draw()
                elif self.selection.health == 0:
                    self.selection_info_active = False
                else:
                    self.select(self.selection)
                    self.selection_info.draw()

        for tower in self.towers:
            tower.draw(self.time_passed)
            if tower == self.selection and self.selection_info_active:
                pygame.draw.circle(self.screen, Color("grey"), tower.rect.center, tower.radius, 2)

        for creep in self.creeps:
            creep.draw()

        if self.selection_info_active:
            if self.selection.type == "Tower":
                select_sf = pygame.Surface((self.selection.rect.w, self.selection.rect.h))
                select_sf.fill(Color(80, 200, 80))
                select_sf.set_alpha(150)
                self.screen.blit(select_sf, self.selection.rect)
                font = pygame.font.SysFont('arial', 15)
                font.set_bold(True)
                text = font.render("Press S to Sell for 75%.", True, (0,0,0))
                self.screen.blit(text, (self.selection.rect[0]+50, self.selection.rect[1]+20))
            else:
                select_sf = pygame.Surface((self.selection.image_rect.w, self.selection.image_rect.h))
                select_sf.fill(Color(80, 200, 80))
                select_sf.set_alpha(150)
                self.screen.blit(select_sf, self.selection.rect)

        for projectile in self.projectiles:
            projectile.draw()

        if self.placing_tower and self.place_tower_draw_pos:
            self.place_tower_draw(self.place_tower_draw_pos)
        self.draw_portals()

        for text_message in self.text_messages:
            text_message.update(self.time_passed)
            if not text_message.timealive > text_message.duration or text_message.duration == 0:
                text_message.draw()
            else:
                self.text_messages.remove(text_message)
##        if self.tooltip.active:
##            self.selection_info_active = False  ##TEMPORARY UGLY FIX FIXME. Probably not required anymore, let us hope so ;)
##        elif self.selection_info_active:
##            self.tooltip.active = False
        if self.tooltip.active:
            self.tooltip.draw() #self.screen.blit(self.tooltip, (self.get_toolbox_rect_n(self.tooltip_id)))

    def enough_money(self, cost):
        return (cost <= self.money)

    def upgrade_tower(self, tower, upgradeid):
        pos = tower.pos
        towerclass = str(tower.__class__)
        expression = "upg_tower = Tower_1(self.screen, self, position=pos)".split('1')
        exec expression[0]+towerclass[21]+"_"+str(upgradeid)+expression[1]
        if self.enough_money(upg_tower.cost):
            self.money -= upg_tower.cost
            tower.kill()
            self.towers.add(upg_tower)
            self.select_info_active = False
        else:
            upg_tower.kill()

    def run(self):
        # The main game loop
        #
        self.total_time_passed = 0
        while True:
            # Limit frame speed to 30 FPS
            #
            self.time_passed = self.clock.tick(40) #FPS
            #~ time_passed = self.clock.tick()
            #~ print time_passed
            self.total_time_passed += self.time_passed
            try:
                self.FPS = 1 / (self.time_passed / 1000.0)
            except:
                self.FPS = 999
            # If too long has passed between two frames, don't
            # update (the game must have been suspended for some
            # reason, and we don't want it to "jump forward"
            # suddenly)
            #
            if self.time_passed > 100:
                continue


            console.process_input()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        console.set_active()
                    elif event.key == pygame.K_SPACE:
                        if not self.game_over:
                            self.paused = not self.paused
                            if self.paused:
                                pausemenu = Menu(self.screen, pause=True, game=self)
                        else:
                            del self
                            menu = Menu(screen)
                    elif event.key == pygame.K_ESCAPE:
                        if self.placing_tower:
                            self.placing_tower = False
                            self.money += self.tower_templates[self.placing_tower_type[1] - 1].cost
                        else:
                            if UserConfirm(screen, message="Return to Main Menu and lose progress?", backgroundclass=self):
                                del self
                                menu = Menu(screen)
                    elif event.key == pygame.K_g:
                        if pygame.key.get_mods() & pygame.KMOD_CTRL:
                            self.options['draw_grid'] = not self.options['draw_grid']
                    elif event.key == pygame.K_s and self.selection_info_active and self.selection.type == 'Tower':
                        self.selection.sell()
                    elif event.key >= pygame.K_1 and event.key <= pygame.K_4:
                        if not self.selection_info_active or self.selection.type == 'Creep':
                            n = event.key - 48
                            if n in range(1, self.tower_type_amount + 1):
                                self.last_placing_tower_type = self.placing_tower_type
                                self.placing_tower_type = [0, n]
                                if self.placing_tower == False and self.enough_money(self.tower_templates[n - 1].cost):
                                    self.placing_tower = True
                                else:
                                    if self.placing_tower:
                                        self.money += self.tower_templates[self.last_placing_tower_type[1] - 1].cost
                                        self.place_tower_draw_pos = None
                                    self.placing_tower = False
                                if self.placing_tower and self.enough_money(self.tower_templates[n - 1].cost):
                                    self.place_tower_draw_pos = pygame.mouse.get_pos()
                                    self.placing_tower_type = [0,n]
                                    self.money -= self.tower_templates[self.placing_tower_type[1] - 1].cost
                                else: ##No compensation if pressing 1 two times
                                    if self.placing_tower_type == [0,n] and self.placing_tower:
                                        self.money += self.tower_templates[self.placing_tower_type[1] - 1].cost
                                        self.place_tower_draw_pos = None
                        elif self.selection.type == "Tower":
                            n = event.key - 48
                            if n in range(1, len(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1])+1):
                                self.upgrade_tower(self.selection,n)

                elif event.type == pygame.MOUSEMOTION:
##                    if self.placing_tower:
##                        if not self.deploy_rect.collidepoint(pygame.mouse.get_pos()):
##                            x, y = pygame.mouse.get_pos()
##                            field_x_start, field_y_start, field_x_length, field_y_length = self.deploy_rect
##                            field_x_max = field_x_start + field_x_length
##                            field_x_min = field_x_length - field_x_start
##                            field_y_max = field_y_start + field_y_length
##                            field_y_min = field_y_length - field_y_start
##                            print x, y, "( ", field_x_start, field_y_start, field_x_length, field_y_length, " )"
##                            if x > field_x_max:
##                                pygame.mouse.set_pos(field_x_max, y)
##                            elif x < field_x_min:
##                                pygame.mouse.set_pos(field_x_min, y)
##                            elif y > field_y_max:
##                                pygame.mouse.set_pos(x, field_y_max)
##                            elif y < field_y_min:
##                                pygame.mouse.set_pos(x, field_y_min)
##                                draw_pos = pygame.mouse.get_pos()
##                        else:
##                            draw_pos = event.pos
##                            self.place_tower_draw_pos = draw_pos
                    if self.placing_tower:
                        draw_pos = event.pos
                        self.place_tower_draw_pos = draw_pos
                    else:
                        dirty = False #used for determining wheter the mouse is hovering over any icon at all
                        for n in range(1, self.tower_type_amount + 1):
                            if not self.selection_info_active or self.selection.type == 'Creep':
                                if self.get_toolbox_rect_n(n).collidepoint(event.pos):
                                    if self.tower_templates[n - 1].description:
                                        selection_description = "Description: "+self.tower_templates[n - 1].description
                                    else:
                                        selection_description = ""
                                    tooltipfont = pygame.font.SysFont('arial', 12)
                                    self.tooltip.active = True
                                    self.tooltip_id = 1
                                    self.tooltip.text = [str(self.tower_templates[n - 1].name),
                                    "Cost: " + str(self.tower_templates[n - 1].cost),
                                    "Damage: " + str(self.tower_templates[n - 1].damage),
                                    "Attack Speed: " + str(self.tower_templates[n - 1].attack_speed/1000.),
                                    "DPS: ~" + str(int(round(self.tower_templates[n - 1].damage / (self.tower_templates[n - 1].attack_speed / 1000.)))),
                                    "Range: " + str(self.tower_templates[n - 1].radius) + "px",
                                    selection_description]

                                    self.tooltip.update(Rect(event.pos[0] - 65, event.pos[1] - 143, 130, 140))

                                    dirty = True
                                if not dirty:
                                    self.tooltip.active = False
                            elif self.selection.type == "Tower":
                                if not str(self.selection.__class__)[22] == "_": #this means tier-two towers can't be upgraded
                                    if n in range(1, len(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1])+1):
                                        if self.get_toolbox_rect_n(n).collidepoint(event.pos):
                                            if self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].description:
                                                selection_description = "Description: "+self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].description
                                            else:
                                                selection_description = ""
                                            tooltipfont = pygame.font.SysFont('arial', 12)
                                            self.tooltip.active = True
                                            self.tooltip_id = 1
                                            self.tooltip.text = [str(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].name),
                                            "Cost: " + str(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].cost),
                                            "Damage: " + str(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].damage),
                                            "Attack Speed: " + str(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].attack_speed/1000.),
                                            "DPS: ~" + str(int(round(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].damage / (self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].attack_speed / 1000.)))),
                                            "Range: " + str(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n-1].radius) + "px",
                                            selection_description]

                                            self.tooltip.update(Rect(event.pos[0] - 65, event.pos[1] - 143, 130, 140))
                                            dirty = True
                                        if not dirty:
                                            self.tooltip.active = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.placing_tower:
                    Collision = False
                    for tower in self.towers:
                        for tile_x in range(2):
                            for tile_y in range(2):
                                Collision = tower.rect.collidepoint(((event.pos[0] + (20 * tile_x)), (event.pos[1] + (20 * tile_y))))
                                if Collision:
                                    break
                            if Collision:
                                break
                        if Collision:
                            break
                    if not Collision:
                        self.place_tower(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.selection_info_active or self.selection.type == 'Creep':
                        for n in range(1, self.tower_type_amount + 1):
                            if self.get_toolbox_rect_n(n).collidepoint(event.pos) and self.money  >= self.tower_templates[n - 1].cost:
                                self.placing_tower = not self.placing_tower
                                if self.placing_tower:
                                    self.place_tower_draw_pos = pygame.mouse.get_pos()
                                    self.placing_tower_type = [0,n]
                                    self.money -= self.tower_templates[self.placing_tower_type[1] - 1].cost
                                else:
                                    self.place_tower_draw_pos = None
                        else:
                            Collision = None
                            if self.towers:
                                towers_or_do_once = self.towers
                            else:
                                towers_or_do_once = range(1)
                            for tower in towers_or_do_once:
                                if self.towers:
                                    Collision = tower.rect.collidepoint(event.pos)
                                if Collision:
                                    self.select(tower)
                                    break
                                for creep in self.creeps:
                                    Collision = creep.rect.collidepoint(event.pos)
                                    if Collision:
                                        self.select(creep)
                                        break
                                if Collision:
                                    break

                            if not Collision:
                                self.selection_info_active = False
                    elif self.selection.type == 'Tower':
                        for n in range(1, len(self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1]) + 1):
                            if not str(self.selection.__class__)[22] == "_": #this means tier-two towers can't be upgraded
                                if self.get_toolbox_rect_n(n).collidepoint(event.pos) and self.money >= self.tower_upgrade_templates[int(str(self.selection.__class__)[21])-1][n - 1].cost:
                                    self.upgrade_tower(self.selection,n)
                        else:
                            Collision = None
                            if self.towers:
                                towers_or_do_once = self.towers
                            else:
                                towers_or_do_once = range(1)
                            for tower in towers_or_do_once:
                                if self.towers:
                                    Collision = tower.rect.collidepoint(event.pos)
                                if Collision:
                                    self.select(tower)
                                    break
                                for creep in self.creeps:
                                    Collision = creep.rect.collidepoint(event.pos)
                                    if Collision:
                                        self.select(creep)
                                        break
                                if Collision:
                                    break

                            if not Collision:
                                self.selection_info_active = False

            if not self.paused and not self.game_over:
                msg1 = 'Creeps: %d' % len(self.creeps)
                msg2 = 'Gold: %d' % self.money
                msg3 = 'Lives: %d' % self.lives
                msg4 = 'Leaks: %d' % self.leaks
                msg5 = 'Kills: %d' % self.kills
                msg6 = ''
                if self.lives <= 0:
                    msg6 = 'Lost!'
                    if not self.game_over:
                        self.GameOver()
                elif self.won and self.lives:
                    msg6 = 'Won!'
                    if not self.game_over:
                        self.Victory()

                self.fpsfont = pygame.font.Font('images/fonts/BIRTH_OF_A_HERO.ttf', 32)#SysFont('arial', 24)
                self.fpsfont.set_bold(True)
                self.fps = self.fpsfont.render("FPS: "+ str(int(self.FPS)), True, (0, 0, 0))
                if not self.selection_info_active or self.selection.type == 'Creep':
                    self.build_upgrade_text = self.fpsfont.render("BUILD", True, (0,0,0))
                elif self.selection.type == "Tower":
                    self.build_upgrade_text = self.fpsfont.render("UPGRADE", True, (0,0,0))

                self.mboard_text = [msg1, msg2, msg3, msg4, msg5, msg6]

                if not len(self.creeps):  #write a self.waiting_level
                    if self.level_complete == False and self._spawned_creep_count_level >= self.n_enemies_list[self.level-1]:
                        self.text_messages.append(widgets.TextMessage(self.screen, "Level Complete!", vec2d(self.screen.get_width() / 2, self.screen.get_height() / 2), duration=3800, size=32, initialdelay=800))
                        self.level_complete = True
                    if self.level_timer:
                        self.tboard.text = ['Level ' + str(self.level) + ' Starts in..' + str(int((self.level_timer.interval - self.level_timer.time) / 1000))]
                else:
                    if self.level_complete == True:
                        self.level_complete = False
                    self.tboard.text = ['Level ' + str(self.level)]
                if self.creep_spawn_timer:
                    self.creep_spawn_timer.update(self.time_passed)
                if self.level_timer:
                    self.level_timer.update(self.time_passed)

                # Update and all creeps
                for creep in self.creeps:   #Unoptimized, bad to for-loop through the creeps twice each frame!
                    creep.update(self.time_passed)
                for projectile in self.projectiles:
                    projectile.update(self.time_passed)

                for tower in self.towers:
                    possible_targets = []

                    for creep in self.creeps:
                        Collision = pygame.sprite.collide_circle(creep, tower) #Collision detection with the tower's range
                        if Collision and creep.health > 0:
                            possible_targets.append(creep.id)
                    if possible_targets:
                        tower.fire(possible_targets)
                if not self.game_over:
                    self.draw()
                    console.draw()
                    pygame.display.flip()

    def Victory(self):
        if console.active:
            console.set_active(b=False)
        self.game_over = True
        self.paused = True
        overlay_sf = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay_sf.fill(Color(10, 100, 10))
        overlay_sf.set_alpha(220)
        self.screen.blit(overlay_sf, (0,0))
        widgets.TextMessage(self.screen, "You have Survived!", vec2d(self.screen.get_width() / 2, self.screen.get_height() / 2), duration=0, size=32, flashy=False).draw()
        widgets.TextMessage(self.screen, "Press SPACE to return to Menu.", vec2d(self.screen.get_width() / 2, (self.screen.get_height() / 2)+50), duration=0, size=16, flashy=False).draw()
        pygame.display.flip()

    def GameOver(self):
        if console.active:
            console.set_active(b=False)
        self.game_over = True
        self.paused = True
        overlay_sf = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay_sf.fill(Color(100, 10, 10))
        overlay_sf.set_alpha(220)
        self.screen.blit(overlay_sf, (0,0))
        widgets.TextMessage(self.screen, "Game Over!", vec2d(self.screen.get_width() / 2, self.screen.get_height() / 2), duration=0, size=32, flashy=False).draw()
        widgets.TextMessage(self.screen, "Press SPACE to return to Menu.", vec2d(self.screen.get_width() / 2, (self.screen.get_height() / 2)+50), duration=0, size=16, flashy=False).draw()
        pygame.display.flip()

    def save(self): #NOT WORKING
        savefile = open("savegame", "w")
        #pickle.dump(self, savefile)
        savefile.write(jelly.jelly(self, persistentStore=None, invoker=None))
        savefile.close()
    def load(self): #NOT WORKING
        savefile = open("savegame", "r")
        #self = pickle.load(savefile)
        self = jelly.unjelly(savefile.read())
        savefile.close()
    def gold_cheat(self, n):
        """Adds argument to game money."""
        self.money += n
        return str(n)+" Gold added!"

    def spawn_more_this_level(self, n=0, all=0, fixed=False):
        """Spawns n more creeps during active level. Optionally, all=True can be set, to affect all levels. Additionally, fixed=True sets enemy count to n, instead of adding n."""
        if not all:
            if not fixed:
                self.n_enemies_list[self.level-1] += n
            else:
                self.n_enemies_list[self.level-1] = n
            return str(self.n_enemies_list[self.level-1])+" enemies will spawn during level "+str(self.level)
        else:
            if not fixed:
                for level in enumerate(len(self.n_enemies_list)):
                    self.n_enemies_list[level] += n
            else:
                for level in enumerate(len(self.n_enemies_list)):
                    self.n_enemies_list[level] = n
            return str(self.n_enemies_list[self.level-1])+" enemies will spawn during current and all remaining levels."
        return

    def add_lives(self, n=0):
        self.lives += n
        return "Added "+str(n)+" Lives."

    def console_exec(self, expression):
        try:
            expression = str(expression)
        except:
            pass
        if expression.__class__ == "".__class__:
            try:
                exec expression
            except:
                return "Couldn't execute expression ( "+str(expression)+" )."
            else:
                return "Successfully executed!"
        return "Not a string!"

    def quit(self):
        if UserConfirm(screen, message="Really quit?", backgroundclass=self):
            pygame.quit()
            sys.exit()


def UserConfirm(screen, message="Are You Sure?", backgroundclass=None):
    global console
    if console.active:
            console.set_active(b=False)

    global confirmed, rejected
    confirmed, rejected = False, False
    def confirm():
        global confirmed
        confirmed = True
        if console.active:
            console.set_active(b=False)
        return
    def reject():
        global rejected
        rejected = True
        if console.active:
            console.set_active(b=False)
        return
    text_widgets = []
    if backgroundclass:
        overlay_sf = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay_sf.fill(Color(10, 10, 10))
        overlay_sf.set_alpha(220)
        screen.blit(overlay_sf, (0,0))
    else: screen.fill((0,0,0))
    message_text = widgets.TextWidget(message, Color("gold"), size=32, highlight_increase=0, font_filename='images/fonts/FFFTusj.ttf', show_highlight_cursor=False, event=None)
    message_text.rect.center = screen.get_rect().center
    message_text.rect.top -= 50
    text_widgets.append(message_text)

    image_buttons = []

    confirmrect = Rect(screen.get_rect().center[0]-96-60, screen.get_rect().center[1]+50, 100, 100)
    confirm_button = widgets.ImageButton(screen, ['images/widgets/confirm.png', 'images/widgets/confirm_full.png'], confirmrect, callback=confirm)
    image_buttons.append(confirm_button)

    rejectrect = Rect(screen.get_rect().center[0]+60, screen.get_rect().center[1]+50, 100, 100)
    reject_button = widgets.ImageButton(screen, ['images/widgets/reject.png', 'images/widgets/reject_full.png'], rejectrect, callback=reject)
    image_buttons.append(reject_button)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in image_buttons:
                    if button.rect.collidepoint(event.pos):
                        button.clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    confirm()
                elif event.key == pygame.K_ESCAPE:
                    reject()

        if confirmed:
            return True
        elif rejected:
            return False

        for button in image_buttons:
            if button.dirty == True:
                if backgroundclass:
                    backgroundclass.draw()
                    screen.blit(overlay_sf, (0,0))
                    for text in text_widgets:
                        text.dirty = True
                    break
                else:
                    pygame.draw.rect(screen, (0,0,0), button.maxrect)

        for button in image_buttons:
            button.update()

        """Draw everything"""
        rects = []
        for text in text_widgets:
            rect = text.draw(screen)
            if (rect):
                rects.append(rect)
        pygame.display.update(rects)
        pygame.display.flip()


def we_are_frozen():
    """Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located."""

    return hasattr(sys, "frozen")


def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))

    return os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))

if __name__ == "__main__":
    if module_path() != '':
        os.chdir(module_path()) #Make sure the current working directory is correct
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    pygame.init()
    global screen
    while 1:
        screen = pygame.display.set_mode(
                        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)
        pygame.display.set_caption("Zombie Invasion: Tower Defense")
        pygame.display.set_icon(pygame.image.load("images/projectiles/Frost_arrow.png"))
        menu = Menu(screen)
