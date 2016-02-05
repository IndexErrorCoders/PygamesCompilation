"""Represents the player's ship"""

import pygame
import random

import serge.engine
import serge.actor
import serge.sound
import serge.visual
import serge.events
import serge.blocks.behaviours
import serge.blocks.actors
from serge.simplevecs import Vec2d

from theme import G
import common 
import bullet
import gun
import smoke


class PlayerShip(serge.blocks.actors.ScreenActor):
    """The player's ship"""

    def __init__(self, tag, name):
        """Initialise the PlayerShip"""
        super(PlayerShip, self).__init__(tag, name)
        self.shooting = False
        self.flashing = False
        
    def addedToWorld(self, world):
        """We were added to the world"""
        super(PlayerShip, self).addedToWorld(world)
        #
        # Place in position
        self.moveTo(G('player-ship-x'), G('player-ship-y'))
        self.setSpriteName('player-ship')
        self.setLayerName('foreground')
        self.visual.setCell(self.visual.getNumberOfCells()-1)
        #
        # Assign behaviour
        self.manager = world.findActorByName('behaviours')
        self.manager.assignBehaviour(
            self, serge.blocks.behaviours.KeyboardNSEW(G('player-ship-speed'), n=None, s=None), 'movement')
        self.flasher = self.manager.assignBehaviour(self, serge.blocks.behaviours.FlashFor(self, 5), 'flashing')
        self.flasher.pause()
        #
        # The gun display
        self.gun = gun.Gun('gun', 'gun')
        world.addActor(self.gun)
        #
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        self.broadcaster.linkEvent(common.E_RESTART_GAME, self.restartGame)
        self.broadcaster.linkEvent(common.E_LOST_GAME, self.lostGame)
        #
        self.last_position = None
        
    def updateActor(self, interval, world):
        """Update the player"""
        #
        # Player taking a shot
        if not self.shooting and self.keyboard.isDown(pygame.K_SPACE):
            if self.gun.canShoot():
                self.log.info('Firing bullet')
                self.gun.takeShot()
                b = bullet.Bullet(
                    self.x, self.y + G('bullet-offset'), G('bullet-speed'),
                    'alien', 'player-bullet', common.E_ALIEN_DESTROYED, 90)
                world.addActor(b)
                self.shooting = True
                self.visual.resetAnimation(True)
            else:
                serge.sound.Sounds.play('gun-hot')
                self.log.info('Firing a hot shot')
                b = bullet.HotBullet(
                    self.x, self.y + G('bullet-offset'), G('hot-bullet-speed'),
                    'alien', 'player-hot-bullet', common.E_ALIEN_DESTROYED, 90)
                world.addActor(b)
                self.shooting = True
                self.visual.resetAnimation(True)
        #
        # Released shot?
        if self.shooting and self.keyboard.isUp(pygame.K_SPACE):
            self.shooting = False
        #
        if self.keyboard.isClicked(pygame.K_w):
            for idx, a in enumerate(world.getActors()):
                self.log.debug('Actor %d %s' % (idx+1, a.getNiceName()))
        #
        # Make sure we are on the screen
        if self.x < self.width/2:
            self.x = self.width/2
        elif self.x > G('screen-width') - self.width/2:
            self.x = G('screen-width') - self.width/2
        #
        # Regenerate when stationary
        if self.last_position == self.x:
            self.gun.regenerateOnce(interval)
        self.last_position = self.x
        
    def restartGame(self, obj, arg):
        """Restart the game"""
        if self.flasher.isRunning():
            self.flasher.pause()
        self.visible = True
        self.flashing = False
        self.active = True
        self.gun.resetGun()
        self.gunNormal()
            
    def lostGame(self, obj, arg):
        """Lost the game"""
        self.active = False

    def resetPlayer(self):
        """Reset the player after death"""
        self.moveTo(G('player-ship-x'), G('player-ship-y'))
        if self.world.findActorByName('gamestate').isGameOver():
            self.active = False
        elif not self.flasher.isRunning():
            self.flasher.restart()
            self.active = True
            self.flashing = True

    def makeHarder(self):
        """Make it harder"""
        self.gun.makeHarder()

    def gunOverheated(self):
        """The gun got too hot"""
        self.setSpriteName('player-hot-ship')
                
    def gunNormal(self):
        """The gun cooled down"""
        self.setSpriteName('player-ship')
        self.visual.setCell(self.visual.getNumberOfCells()-1)

    def destroyTurret(self):
        """The players turret has been destroyed"""
        explosion = serge.blocks.actors.AnimateThenDieActor(
            'explosion', 'explosion', 'air-explosion', 'effects', self)
        self.world.addActor(explosion)
        #
        # Create some fragments of the ship
        total_velocity = Vec2d(0, 0)
        total_spin = 0.0
        for idx in range(3):
            #
            # Create velocity of the fragment
            if idx != 2:
                v = Vec2d(random.uniform(*G('fragment-vx-range')), random.uniform(*G('fragment-vy-range')))
                spin = random.uniform(*G('fragment-spin-range'))
                total_velocity += v
                total_spin += spin
            else:
                # Conserve x momentum and spin of all fragments
                v = Vec2d(-total_velocity[0], random.uniform(*G('fragment-vy-range')))
                spin = -total_spin
            #
            # Create the fragment
            fragment = Fragment(self, idx, spin, *v)
            self.world.addActor(fragment)
        #
        self.active = False
            

class Fragment(serge.actor.Actor):
    """A fragment of the ship"""

    def __init__(self, parent, number, spin, vx, vy):
        """Initialise the fragment"""
        super(Fragment, self).__init__('fragment', 'fragment-%d' % number)
        #
        self.setSpriteName('player-explosion')
        self.setLayerName('foreground')
        self.visual.setCell(number)
        self.moveTo(parent.x, parent.y)
        self.vx, self.vy = vx, vy
        self.spin = spin
        self.parent = parent
        
    def updateActor(self, interval, world):
        """Update the fragment"""
        #
        # Equation of motion
        self.vy += G('alien-falling-force')*interval/1000.0
        self.move(self.vx*interval/1000.0, self.vy*interval/1000.0)
        self.setAngle(self.getAngle()+self.spin*interval/1000.0)
        #
        # Look for going off the bottom of the screen
        if self.y > G('alien-offscreen-highy'):
            self.log.debug('Removing fragment %s' % self.getNiceName())
            world.scheduleActorRemoval(self)
            explosion = serge.blocks.actors.AnimateThenDieActor('explosion', 'explosion', 'ground-explosion', 'effects')
            explosion.moveTo(self.x, G('explosion-y'))
            world.addActor(explosion)
            serge.sound.Sounds.play('crash')

        #
        # Smoke trail
        world.addActor(smoke.Smoke(self))

    def removedFromWorld(self, world):
        """We were removed from the world"""
        super(Fragment, self).removedFromWorld(world)
        #
        fragments = world.findActorsByTag('fragment')
        if fragments and fragments != [self]:
            return
        else:
            self.parent.resetPlayer()
