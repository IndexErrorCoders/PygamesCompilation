# -*- coding: utf-8 -*-

from main import *
from Creeps import *
from Projectiles import *
import widgets
from utils import get_Percentage, get_Distance, Timer

class Tower(Sprite):
    """A tower object, placed on the grid. Unwalkable. Fires projectiles at nearby creeps."""
    def __init__(self, screen, game, position=(0, 0), tower_image='images/towers/arrow_tower_1.png', projectile_image='images/projectiles/Arrow1.png', frameinterval=100, template=False):
        """ Create a new Tower.
        screen:
        The screen on which the tower is located (must be a pygame Surface object, such as pygame.display)
        game:
        This is the game object that holds information about the game world.
        tower_image:
        An image (as Pygame surface objects) for the tower.
        projectile_image:
        An image for the projectile the tower emits
        position:
        The (x, y) position of the tower.
        """
        Sprite.__init__(self)

        self.name = "Arrow Tower"
        self.description = None

        if not template:
            game._placed_tower_count += 1
            self.id = game._placed_tower_count
            game.last_placed_tower_id = self.id
        else:
            self.id = None

        self.type = 'Tower'
        self.screen = screen
        self.game = game
        self.image_list = None
        if tower_image.__class__ == "".__class__:
            self.image = pygame.image.load(tower_image).convert_alpha()
        elif tower_image.__class__ == [].__class__:
            self.image = pygame.image.load(tower_image[0]).convert_alpha()
            self.image_list = tower_image
            self.imageframeid = 0
            self.frametimer = Timer(frameinterval, self.next_frame, oneshot=False)

        self.icon = pygame.transform.scale(self.image, (30, 30))
        self.projectile_image = pygame.image.load(projectile_image).convert_alpha()
        self.orig_pos = position  #just for eventual need to know exactly which pixel it was placed at (and then it was snapped to the topleft of that tile)
        if not template:
            #Tile snapping code
            self.coordx_topleft, self.coordy_topleft = self.game.xy2coord(position) #these are used further down
            self.coord_topleft = (self.coordx_topleft, self.coordy_topleft)
            self.pos = game.coord2xy(self.coord_topleft)

        self.is_upgrade = False
        self.cost = 10

        #Fire-related
        self.damage = 4
        self.radius = 100 #Attacking range
        self.ratio = 1.0 #Ratio of the radius, used for upgrades. #is this really used by current collison detection?
        self.attack_speed = 700 #ms delay
        self.aoe = False #should be radius of area
        self.aoefactor = 0.50 #factor to multiply by damage on area attack
        self.projectileeffect = None
        self.last_fire_time = 0
        self.last_target_id = None


        #Experience-related
        self.level = 1
        self.experience = 0
        self.kills = 0
        self.experience_req = 5
        self.last_experience_req = 0
        self.delta_exp_req = self.experience_req - self.last_experience_req

        #Projectile-related
        self.projectile_speed = 0.23


        self.width, self.height = self.image.get_size()
        self.widthbycoord = ceil(self.width / float(game.GRID_SIZE)) #get the ceiling, to block all tiles the tower occupies a portion of.
        self.heightbycoord = ceil(self.height / float(game.GRID_SIZE))

        #Blocking all covered tiles
        #
        if not template:
            for extra_tile_y in range(int(self.heightbycoord)): #Block all occupied tiles
                for extra_tile_x in range(int(self.widthbycoord)):
                    self.game.gridpath.set_blocked((self.coordx_topleft + extra_tile_x, self.coordy_topleft + extra_tile_y))

            self.rect = Rect(self.pos[0], self.pos[1], self.width, self.height)
        #print("Image: ", tower_image, "projectile_image: ", projectile_image, "Position xy: ", self.pos, "Position Coord: ", self.coord_topleft)

    def draw(self, time_passed): ## If this turns out to be the better way, don't forget to change the drawing method from self.towers.draw(self.screen) to for tower in self.towers: tower.draw()
        if self.image_list:
            self.frametimer.update(time_passed)
        self.screen.blit(self.image, self.rect)

##        # The experience bar is 15x4 px.
##        #
##        experience_bar_length = 15
##        experience_bar_height = 4
##
##        experience_percentage = get_Percentage((self.experience_req - self.last_experience_req), (self.experience - self.last_experience_req)) #float fraction, like 0.333333 (equals 33.3333% )
##
##        experience_bar_fill_length = int(ceil(experience_percentage * experience_bar_length))
##        experience_bar_x = self.rect.centerx - (experience_bar_length / 2)
##        experience_bar_y = self.rect.centery - 10
##        self.screen.fill(   Color('grey'),
##        (experience_bar_x, experience_bar_y, experience_bar_length, experience_bar_height))
##        self.screen.fill(   Color('blue'),
##        (   experience_bar_x, experience_bar_y,
##        experience_bar_fill_length, experience_bar_height))


    def fire(self, targets):
        if self.last_fire_time + self.attack_speed < self.game.total_time_passed:
            last_target = self.game.lookup_creep(self.last_target_id)
            if self.last_target_id in targets and last_target.state == 0: #ALIVE state
                target_id = self.last_target_id
##            elif self.damage > self.game.lookup_creep(choice(targets)).health_init: #attack enemy closest to goal if one attack is sure to kill
##                shortest_distance = -1
##                for possible_targetid in targets:
##                    possible_target = self.game.lookup_creep(possible_targetid)
##                    distance_to_goal = get_Distance((possible_target.rect[0], possible_target.rect[1]), self.game.coord2xy(self.game.goal_coord))
##                    if distance_to_goal < shortest_distance or shortest_distance == -1 :
##                        shortest_distance = distance_to_goal
##                        target_id = possible_targetid
##            else: #Last target not alive, attack the enemy with least health.
##                lowest_hp = -1
##                for possible_targetid in targets:
##                    possible_target = self.game.lookup_creep(possible_targetid)
##                    if possible_target.health < lowest_hp or lowest_hp == -1:
##                        lowest_hp = possible_target.health
##                        target_id = possible_targetid
            else:
                target_id = choice(targets)

            self.projectile = Projectile(self.screen, self.game, self, self.game.lookup_creep(target_id), self.aoe, self.aoefactor, self.projectileeffect)


            self.game.attacks += 1
            self.last_fire_time = self.game.total_time_passed
            self.last_target_id = target_id
            self.play_sound()

    def next_frame(self):
        if self.imageframeid < len(self.image_list) - 1:
            self.imageframeid += 1
        else:
            self.imageframeid = 0
        self.image = pygame.image.load(self.image_list[self.imageframeid]).convert_alpha()

    def sell(self):
        sellamount = int(round(0.75 * self.cost))
        self.game.money += sellamount
        self.game.text_messages.append(widgets.TextMessage(self.game.screen, 'Sold! '+'+'+str(sellamount), vec2d(self.pos[0], self.pos[1]-22), duration=3100, size=23, initialdelay=800))
        self.game.selection_info_active = False
        for extra_tile_y in range(int(self.heightbycoord)): #Block all occupied tiles
            for extra_tile_x in range(int(self.widthbycoord)):
                self.game.gridpath.set_blocked((self.coordx_topleft + extra_tile_x, self.coordy_topleft + extra_tile_y), blocked=False)
        self.kill()

    def add_experience(self, amount):
        pass
##        self.kills +=1
##        self.experience += amount
##        if self.experience >= self.experience_req:
##            self.level_up()

    def level_up(self):
        self.level += 1
        self.last_experience_req = self.experience_req
        self.experience_req += 5 * (self.level * self.level)
        self.delta_exp_req = self.experience_req - self.last_experience_req
        self.damage += 2
        if self.experience >= self.experience_req:
            print "I leveled up another time!"
            self.level_up()

    def play_sound(self):
        pass

class Tower_1(Tower):
    def __init__(self, screen, game, position=(0, 0), tower_image='images/towers/arrow_tower_1.png', projectile_image='images/projectiles/Arrow1.png', template=False): #tower_image='images/towers/arrow_tower_1.png', projectile_image='images/projectiles/Arrow1.png', template=False):
        Tower.__init__(self, screen, game, position, tower_image, projectile_image, template)
        self.name = "Basic " + self.name
        self.description = "Standard Arrow Tower."
        self.damage = 15
        self.attack_speed = 800
        self.cost = 10
    def level_up(self):
        Tower.level_up(self)
        self.damage += 3
    def play_sound(self):
        tower_sound = pygame.mixer.Sound("audio/sfx/bow01.wav")
        channel = tower_sound.play()

class Tower_1_1(Tower):
    def __init__(self, screen, game, position=(0, 0), tower_image='images/towers/arrow_tower_2.png', projectile_image='images/projectiles/Arrow2.png', template=False):
        Tower.__init__(self, screen, game, position, tower_image, projectile_image, template)
        self.name = "Rapid Arrow Tower"
        self.description = "Good range, excellent speed and low damage."
        self.damage = 10
        self.attack_speed = 300
        self.radius = 150
        self.cost = 25
        self.is_upgrade = True

class Tower_2(Tower):
    def __init__(self, screen, game, position=(0, 0), tower_image='images/towers/frost_tower.png', projectile_image='images/projectiles/Frost_arrow.png', template=False):
        Tower.__init__(self, screen, game, position, tower_image, projectile_image, template)
        self.name = "Frost Tower"
        self.damage = 28
        self.attack_speed = 500
        self.radius = 110
        self.cost = 70
        self.projectileeffect = 1
        self.aoe = 40
class Tower_3(Tower):
    def __init__(self, screen, game, position=(0, 0), tower_image='images/towers/Firetower.png', projectile_image='images/projectiles/Fire_arrow.png', template=False):
        Tower.__init__(self, screen, game, position, tower_image, projectile_image, template)
        self.name = "Ember Tower"
        self.damage = 58
        self.attack_speed = 525
        self.radius = 100
        self.cost = 120
        self.aoe = 40
        self.aoefactor = 0.0
        self.projectileeffect = [2]
class Tower_4(Tower):
    def __init__(self, screen, game, position=(0, 0), tower_image=[
    'images/towers/wizard_tower/Wizards_Tower_Anim(1).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(2).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(3).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(4).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(5).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(6).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(7).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(8).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(9).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(10).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(11).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(12).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(13).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(14).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(15).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(16).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(18).png',
    'images/towers/wizard_tower/Wizards_Tower_Anim(19).png'], projectile_image='images/projectiles/Fire_arrow.png', template=False):
        Tower.__init__(self, screen, game, position, tower_image, projectile_image, template)
        self.name = "Wizard Tower"
        self.damage = 102
        self.attack_speed = 450
        self.radius = 150
        self.cost = 240
        self.aoe = 10
        self.aoefactor = 0.2
