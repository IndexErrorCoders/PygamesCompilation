# -*- coding: utf-8 -*-
from main import *
from vec2d import *
import widgets
import simpleanimation

class Projectile(Sprite):
    """A projectile object, fired by a tower upon a target."""
    def __init__(self, screen, game, tower, target, aoe=False, aoefactor=0.50, effect=None):
        """Launch another projectile.
            screen:
                The screen on which the projectile is drawn and located.
            game:
                This is the game object that holds information about the game world.
            tower:
                This is the tower object firing the projectile_image
            target:
                This is the target of the projectile.
            aoe (optional):
                defaults to False
            aoefactor (optional):
                defaults to 0.50, and defines how much of the damage should be dealt in the area of effect.
            effect (optional):
                defaults to None

            projectile_image:
                is found within the tower object (tower.projectile_image).

        """

        Sprite.__init__(self)

        self.screen = screen
        self.game = game
        self.tower = tower
        self.target = target
        self.speed = self.tower.projectile_speed
        self.pos = vec2d((self.tower.pos[0] + (self.tower.width / 2), self.tower.pos[1] + (self.tower.height / 2)))
        self.aoe = aoe
        self.aoefactor = aoefactor
        if type(effect) != type([]) and type(effect) != type(None):
            self.effects = [effect]
        elif type(effect) == type([]):
            self.effects = effect
        else:
            self.effects = []
        self.base_image = self.tower.projectile_image
        self._compute_direction()
        self.image = pygame.transform.rotate(
            self.base_image, -self.direction.angle)

        self.width = self.base_image.get_width()
        self.height = self.base_image.get_height()
        self.rect = Rect(self.pos[0], self.pos[1], self.width, self.height)
        #self.radius = used further down for aoe collision detection


        self.age = 0
        self.duration = 1 * 2000
        self.game.projectiles.add(self)



    def update(self, time_passed):
        if self.target.is_alive():
            ##for creep in self.game.creeps:
            ##Collision = pygame.sprite.collide_circle(creep, self) #Collision detection with the tower's range
            ##if Collision:
            ##creep._decrease_health(self.tower.damage)
            ##self.kill()

            Collision = pygame.sprite.collide_circle(self.target, self) #Collision detection
            if Collision:
                if self.aoe:
                    self.radius = self.aoe #self.radius is used by collide_circle below. Above, the collide_circle assumed a radius encompassing the projectile
                    for enemy in self.game.creeps:
                        if pygame.sprite.collide_circle(enemy, self) and enemy.id != self.target.id:
                            enemy._decrease_health(self.tower.damage*self.aoefactor,attacker=self)
                            if self.effects:
                                if enemy.health > 0:
                                    for effect in self.effects:
                                        EffectDict[effect](enemy, self)
                                        enemy.effects[-1].CausedByAoE = True

                self.target._decrease_health(self.tower.damage, attacker=self)
                if self.effects:
                    if self.target.health > 0:
                        for effect in self.effects:
                            EffectDict[effect](self.target, self)
                self.kill()
            else:
                self._compute_direction()

                self.target_mid = vec2d(
                    (self.target.rect[0] - (self.target.width / 2)),
                    (self.target.rect[1] - (self.target.width / 2)))

                self.mid_point = vec2d(
                    (self.target.rect[0] - (self.target.width / 2)),
                    (self.target.rect[1] - (self.target.width / 2)))

                remaining_distance = abs(self.target_mid - self.mid_point)

                if remaining_distance > self.speed * time_passed:
                    displacement = vec2d(
                        self.direction.x * self.speed * time_passed,
                        self.direction.y * self.speed * time_passed)
                else:
                    displacement = vec2d(
                        self.direction.x * remaining_distance[0],
                        self.direction.y * remaining_distance[1])

                self.pos += displacement
                self.rect = Rect(self.pos[0], self.pos[1], self.width, self.height)

                self.image = pygame.transform.rotate(
                self.base_image, -self.direction.angle)


                self.age += time_passed
                if self.age > self.duration:
                    self.kill()
        else:
            self.kill()

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def _compute_direction(self):
        aim = self.target.rect
        self.direction = vec2d(
            aim[0] - self.pos[0],
            aim[1] - self.pos[1]).normalized()

class ProjectileEffect(object):
    id = 0
    """Effects affecting creeps upon impact, for a duration. This class is only for subclassing."""
    def __init__(self, target, parent, duration=2000, efficiency=1.0):
        """Takes the following arguments:
        target (instance of an enemy)
        duration (optional, default value 20000 the amount of time the effect should be in place, in milliseconds)
        efficiency (optional, default value is 1.0 the exact effect of this setting varies between effects,
        but genereally it will be multiplied with the specific effects' strength)"""
        self.target = target
        self.duration = duration
        self.efficiency = efficiency
        self.parent = parent
        self.age = 0
        self.dead = False
        self.firstupdate = True
        self.CausedByAoE = False
        self.apply() #apply the effect on the target and store it in a list within the creep
        self.update(0)
    def apply(self):
        if not self.CausedByAoE: #If the effect was caused by an Area of Effect attack, don't restore and replace
            for effect in self.target.effects:
                if effect.id == self.id:
                    effect.restore()
                    self.target.effects.remove(effect)
                    break

            self.target.effects.append(self)
    def update(self):
        """to be overridden by subclass effects"""
        pass#raise NotImplementedError("Subclass must implement abstract method")
    def restore(self):
        """to be overridden by subclasses.
        Use this function for restoring a creep to its original state,
        or if anything special should happen when another effect
        of the same type replaces the currently active effect"""
        pass#raise NotImplementedError("Subclass must implement abstract method")
    def draw(self):
        """to be overridden by subclass effects"""
        pass#raise NotImplementedError("Subclass must implement abstract method")

class FreezeEffect(ProjectileEffect):
    id = 1
    def update(self, time_passed):
        if self.firstupdate:
            self.targetorigspeed = self.target.speed
            self.target.speed = self.target.speed * (0.50 / self.efficiency)
            self.firstupdate = False
        elif self.age >= self.duration and not self.dead:
            self.restore()
        self.age += time_passed
    def restore(self):
        self.target.speed = self.targetorigspeed
        self.dead = True

class BurnEffect(ProjectileEffect):
    id = 2
    burninterval = random.randint(950,1050)
    duration = burninterval * 6
    burndmg = 15
    burnimgs = [pygame.image.load('images/effects/fire.png'),
                pygame.image.load('images/effects/fire2.png')]
    image = burnimgs[0]
    def update(self, time_passed):
        if self.firstupdate:
            self.DoTTimer = Timer(self.burninterval, self.burn)
            self.animation = simpleanimation.OverlayAnimation(self.target.screen, self.target, self.target.pos, self.burnimgs, 300, duration=-1)
            self.firstupdate = False
        elif self.age >= self.duration and not self.dead:
            self.dead = True
        else:
            self.DoTTimer.update(time_passed)
        self.age += time_passed
        self.animation.update(time_passed)
    def burn(self, restoring=False):
        if not restoring:
            self.target._decrease_health(self.burndmg * self.efficiency, attacker=self.parent)
            #self.target.game.text_messages.append(widgets.TextMessage(self.target.game.screen, '-'+str(self.burndmg * self.efficiency)+'hp', vec2d(self.target.pos[0], self.target.pos[1]-22), duration=2100, size=11, color=Color("red")))
        else:
            millisec_since_last_burn = self.age
            while millisec_since_last_burn > self.burninterval:
                millisec_since_last_burn -= self.burninterval

            proportionate_damage = round((float(millisec_since_last_burn) / self.burninterval) * self.burndmg * self.efficiency)
            if proportionate_damage >= 1:
                self.target._decrease_health(proportionate_damage, attacker=self.parent)
                #self.target.game.text_messages.append(widgets.TextMessage(self.target.game.screen, '-'+str(proportionate_damage)+'hp', vec2d(self.target.pos[0], self.target.pos[1]-22), duration=2100, size=11, color=Color("red")))
    def restore(self):
        self.burn(restoring=True)
    def draw(self):
        self.animation.draw()


EffectDict = {1:FreezeEffect,2:BurnEffect}