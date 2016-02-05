# -*- coding: utf-8 -*-

import random

from main import *
from utils import get_Percentage
import widgets

class Creep(Sprite):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        """ Create a new Creep.

            screen:
                The screen on which the creep lives (must be a
                pygame Surface object, such as pygame.display)

            game:
                The game object that holds information about the
                game world.

            creep_images:
                A pair of images (as Pygame surface objects) for
                the creep. The first one should point at 3
                o'clock, and the second diagonally between 12
                and 3 o'clock (at 45 degrees above the horizontal
                plane)

            explosion_images:
                A list of image objects for the explosion
                animation.

            field:
                A Rect specifying the 'playing field' boundaries.
                The Creep will bounce off the 'walls' of this
                field.

            init_position:
                A vec2d or a pair specifying the initial position
                of the creep on the screen.

            init_direction:
                A vec2d or a pair specifying the initial direction
                of the creep. Must have an angle that is a
                multiple of 45 degres.

            speed:
                Creep speed, in pixels/millisecond (px/ms)
        """
        Sprite.__init__(self)
        self.id = game._spawned_creep_count
        self.type = 'Creep'
        self.name = 'Slum Zombie'
        self.screen = screen
        self.game = game

        if not init_position:
            init_position=( game.field_rect.left + game.GRID_SIZE / 2, game.field_rect.top + game.GRID_SIZE / 2)

        self.speed = random.randint(45,55)/1000. #between 45 and 55 px/second
        self.field = game.field_rect

##        creep_images_expression = ''.join(game.creep_images_expression_base[0] + str(game.level) + game.creep_images_expression_base[1])
##        try:
##            creep_images = choice(eval(creep_images_expression))
##        except:
##            creep_images = choice([(pygame.image.load(f1).convert_alpha(), pygame.image.load(f2).convert_alpha()) for (f1, f2) in game.LEVEL_1_FILENAMES])
        #print range(0,len(game.ENEMY_FILENAME_LISTS)),len(game.ENEMY_FILENAME_LISTS)
        creep_images = choice([(pygame.image.load(f1).convert_alpha(), pygame.image.load(f2).convert_alpha()) for (f1, f2) in game.ENEMY_FILENAME_LISTS[choice(range(0,len(game.ENEMY_FILENAME_LISTS)))]])

        # base_image_0/45 hold the original images, un-rotated
        #
        self.base_image_0 = creep_images[0]
        self.base_image_45 = creep_images[1]
        # self.image is the current image representing the creep
        # in the game. It's rotated to the creep's direction.
        #
        self.image = self.base_image_0
        self.explosion_images = game.explosion_images
        self.width, self.height = self.image.get_size()
        # A vector specifying the creep's position on the screen
        #
        self.pos = vec2d(init_position)
        self.prev_pos = vec2d(self.pos)
        self.rect = Rect(self.pos[0], self.pos[1], self.width, self.height)
        # The direction is a normalized vector
        #
        self.direction = vec2d(init_direction).normalized()
        self.state = Creep.ALIVE
        self.effects = [] #ProjectileEffects are stored and updated from here
        self.health_init = 15 * (game.level * 2 + game.level) + int((game.level*1.5)**2)
        self.health = self.health_init

        self.level = game.level
        self.gold = int(round(self.level / 1.99))
        self.damage = 1 #determines how many lives are lost when the creep reaches its destination
    def is_alive(self):
        return self.state in (Creep.ALIVE, Creep.EXPLODING)

    def update(self, time_passed):
        """ Update the creep.

            time_passed:
                The time passed (in ms) since the previous update.
        """
        if self.state == Creep.ALIVE:
            # Maybe it's time to change the direction ?
            #
            self._compute_direction(time_passed)

            # Make the creep image point in the correct direction.
            # Note that two images are used, one for diagonals
            # and one for horizontals/verticals.
            #
            # round() on the angle is necessary, to make it
            # exact, despite small deviations that may result from
            # floating-point calculations
            #
            if int(round(self.direction.angle)) % 90 == 45:
                self.image = pygame.transform.rotate(
                    self.base_image_45, -(self.direction.angle + 45))
            elif int(round(self.direction.angle)) % 90 == 0:
                self.image = pygame.transform.rotate(
                    self.base_image_0, -self.direction.angle)
            else:
                assert False

            # Compute and apply the displacement to the position
            # vector. The displacement is a vector, having the angle
            # of self.direction (which is normalized to not affect
            # the magnitude of the displacement)
            #
            displacement = vec2d(
                self.direction.x * self.speed * time_passed,
                self.direction.y * self.speed * time_passed)

            self.prev_pos = vec2d(self.pos)
            self.pos += displacement

            self.rect = Rect(self.pos[0], self.pos[1], self.width, self.height)
            # When the image is rotated, its size is changed.
            self.image_w, self.image_h = self.image.get_size()
            self.image_rect = Rect(self.pos[0], self.pos[1], self.image_w, self.image_h) #is a separate rect needed? this one is used for selection graphics

            for effect in self.effects:
                effect.update(time_passed)
                if effect.dead:
                    self.effects.remove(effect)


        elif self.state == Creep.EXPLODING:
            if self.explode_animation.active:
                self.explode_animation.update(time_passed)
            else:
                self._die()

        elif self.state == Creep.DEAD:
            pass

    def draw(self):
        """ Blit the creep onto the screen that was provided in
            the constructor.
        """
        if self.state == Creep.ALIVE:
            # The creep image is placed at self.pos. To allow for
            # smooth movement even when the creep rotates and the
            # image size changes, its placement is always
            # centered.
            #
            self.draw_rect = self.image.get_rect().move(
                self.pos.x - self.image_w / 2,
                self.pos.y - self.image_h / 2)
            self.screen.blit(self.image, self.draw_rect)

            # The health bar is 15x4 px.
            #
            health_bar_length = 15
            health_bar_height = 4

            health_percentage = get_Percentage(self.health_init, self.health) #float fraction, like 0.333333 (equals 33.3333% )

            health_bar_fill_length = int(ceil(health_percentage * health_bar_length))
            health_bar_x = self.pos.x - floor(health_bar_length / 2) + 1
            health_bar_y = (self.pos.y - self.image_h / 2) - floor(health_bar_length / 2) - 1
            self.screen.fill(   Color('red'),
                (health_bar_x, health_bar_y, health_bar_length, health_bar_height))
            self.screen.fill(   Color('green'),
                                (   health_bar_x, health_bar_y,
                                    health_bar_fill_length, health_bar_height))

            for effect in self.effects:
                effect.draw()

        elif self.state == Creep.EXPLODING:
            self.explode_animation.draw()

        elif self.state == Creep.DEAD:
            pass

    #------------------ PRIVATE PARTS ------------------#

    # States the creep can be in.
    #
    # ALIVE: The creep is roaming around the screen
    # EXPLODING:
    #   The creep is now exploding, just a moment before dying.
    # DEAD: The creep is dead and inactive
    #
    (ALIVE, EXPLODING, DEAD) = range(3)

    def _die(self):
        self.state = Creep.DEAD
        self.game.kills += 1
        self.game.money += self.gold
        self.game.text_messages.append(widgets.TextMessage(self.game.screen, '+'+str(self.gold), vec2d(self.pos[0], self.pos[1]-22), duration=1100, size=15))
        self.kill()

    def _slaycitizen(self):
        self.game.text_messages.append(widgets.TextMessage(self.screen, "Leak!", self.pos, duration=2000, size=14, initialdelay=400, color=(245,15,15)))
        self.game.leaks += self.damage
        self.game.lives -= self.damage
        self.kill()

    def _compute_direction(self, time_passed):
        """ Finds out where to go
        """
        coord = self.game.xy2coord(self.pos)

        if self.game.is_goal_coord(coord):
            self._slaycitizen() #Removes a life and dies
        else:
            x_mid, y_mid = self.game.coord2xy_mid(coord)

            if ((x_mid - self.pos.x) * (x_mid - self.prev_pos.x) < 0 or
                (y_mid - self.pos.y) * (y_mid - self.prev_pos.y) < 0):

                success = False
                for n in range(0, 900):
                    try:
                        next_coord = self.game.next_on_path(coord)
                        self.direction = vec2d(
                            next_coord[1] - coord[1],
                            next_coord[0] - coord[0]).normalized()
                        break #PATH okay!
                    except:
                        self.game.lookup_tower(self.game.last_placed_tower_id - n).sell()
                        self.game.text_messages.append(widgets.TextMessage(self.game.screen, "Don't entirely block the path!", vec2d(self.game.screen.get_width() / 2, self.game.screen.get_height() / 2), duration=3800, size=32, initialdelay=1000, color=Color("red")))

    def _point_is_inside(self, point):
        """ Is the point (given as a vec2d) inside our creep's
            body?
        """
        img_point = point - vec2d(
            int(self.pos.x - self.image_w / 2),
            int(self.pos.y - self.image_h / 2))

        try:
            pix = self.image.get_at(img_point)
            return pix[3] > 0
        except IndexError:
            return False

    def _decrease_health(self, n, attacker=None):
        """ Decrease my health by n (or to 0, if it's currently
            less than n)
        """
        self.health = max(0, self.health - n)
        if self.health == 0:
            if attacker and self.state == Creep.ALIVE:
                attacker.tower.add_experience(self.level)
            self._die()

##    def _explode(self):
##        """ Starts the explosion animation that ends the Creep's
##            life.
##        """
##        self.state = Creep.EXPLODING
##        pos = ( self.pos.x - self.explosion_images[0].get_width() / 2,
##                self.pos.y - self.explosion_images[0].get_height() / 2)
##        self.explode_animation = SimpleAnimation(
##            self.screen, pos, self.explosion_images,
##            100, 300)


class GridPath(object):
    """ Represents the game grid and answers questions about
        paths on this grid.

        After initialization, call set_blocked for changed
        information about the state of blocks on the grid, and
        get_next to get the next coordinate on the path to the
        goal from a given coordinate.
    """
    def __init__(self, nrows, ncols, goal):
        self.map = GridMap(nrows, ncols)
        self.goal = goal

        # Path cache. For a coord, keeps the next coord to move
        # to in order to reach the goal. Invalidated when the
        # grid changes (with set_blocked)
        #
        self._path_cache = {}

    def get_next(self, coord):
        """ Get the next coordinate to move to from 'coord'
            towards the goal.
        """
        # If the next path for this coord is not cached, compute
        # it
        #
        if not (coord in self._path_cache):
            self._compute_path(coord)

        # _compute_path adds the path for the coord to the cache.
        # If it's still not cached after the computation, it means
        # that no path exists to the goal from this coord.
        #
        if coord in self._path_cache:
            return self._path_cache[coord]
        else:
            return None

    def set_blocked(self, coord, blocked=True):
        """ Set the 'blocked' state of a coord
        """
        self.map.set_blocked(coord, blocked)

        # Invalidate cache, because the map has changed
        #
        self._path_cache = {}

    def _compute_path(self, coord):
        pf = PathFinder(self.map.successors, self.map.move_cost,
                self.map.move_cost)

        # Get the whole path from coord to the goal into a list,
        # and for each coord in the path write the next coord in
        # the path into the path cache
        #
        path_list = list(pf.compute_path(coord, self.goal))

        for i, path_coord in enumerate(path_list):
            next_i = i if i == len(path_list) - 1 else i + 1
            self._path_cache[path_coord] = path_list[next_i]

class Creep_1(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Slum Zombie"
        self.speed = random.randint(45,55)/1000. #between 45 and 55 px/second

class Creep_2(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Alt. Slum Zombie"
        self.health_init += 30
        self.health += 30
        self.speed = random.randint(47,57)/1000.
class Creep_3(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Zombie Soldier"
        self.health_init += 50
        self.health += 50
        self.speed = random.randint(50,60)/1000.
class Creep_4(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Dracula"
        self.health_init += 70
        self.health += 70
        self.speed = random.randint(65,75)/1000.
class Creep_5(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Fat Zombie"
        self.health_init += 80
        self.health += 80
        self.speed = random.randint(65,75)/1000.
class Creep_6(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Dark Wizard"
        self.health_init += 100
        self.health += 100
        self.speed = random.randint(69,79)/1000.
class Creep_7(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Insect Ghost"
        self.health_init += 120
        self.health += 120
        self.speed = random.randint(72,82)/1000.
class Creep_8(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Brown Zombie [Spear]"
        self.health_init += 130
        self.health += 130
        self.speed = random.randint(75,85)/1000.
class Creep_9(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Vampire Lieutenant"
        self.health_init += 170
        self.health += 170
        self.speed = random.randint(75,85)/1000.

class Creep_10(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 350
        self.health += 350
        self.speed = random.randint(79,89)/1000.

class Creep_11(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Armored Zombie Boss"
        self.health_init *= 40
        self.health *= 40
        self.speed = random.randint(63, 64)/1000.
        self.gold = 6*40
        self.damage = 5
        self.game.text_messages.append(widgets.TextMessage(self.game.screen, "A boss has spawned!", vec2d(self.game.screen.get_width() / 2, self.screen.get_height() / 2), duration=3800, size=32, initialdelay=800, color=Color("darkgreen")))

class Creep_12(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 950
        self.health += 950
        self.speed = random.randint(79,89)/1000.
class Creep_13(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 950
        self.health += 950
        self.speed = random.randint(79,89)/1000.
class Creep_14(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 950
        self.health += 950
        self.speed = random.randint(79,89)/1000.
class Creep_15(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 1450
        self.health += 1450
        self.speed = random.randint(79,89)/1000.
class Creep_16(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 1450
        self.health += 1450
        self.speed = random.randint(79,89)/1000.
class Creep_17(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 1450
        self.health += 1450
        self.speed = random.randint(79,89)/1000.
class Creep_18(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 1450
        self.health += 1450
        self.speed = random.randint(79,89)/1000.
class Creep_19(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 1450
        self.health += 1450
        self.speed = random.randint(79,89)/1000.
class Creep_20(Creep):
    """ A creep sprite that spawns at one coord and walks to another
    """
    def __init__(self, screen, game, init_position=None, init_direction=(1, 1)):
        Creep.__init__(self, screen, game, init_position, init_direction)
        self.name = "Quite Dead Man"
        self.health_init += 4450
        self.health += 4450
        self.speed = random.randint(79,89)/1000.