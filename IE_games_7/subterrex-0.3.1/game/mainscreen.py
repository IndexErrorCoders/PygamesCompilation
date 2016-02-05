"""The main screen for the game"""

import random
import math
import pygame

import serge.zone
import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.tiled
import serge.blocks.singletons
import serge.blocks.sounds
from serge.simplevecs import Vec2d

from theme import G, theme
import common 
import creator
import cave
import light
import player
import bug
import climbing
import hud
import status
import flare

class MainScreen(serge.blocks.actors.ScreenActor):
    """The logic for the main screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(MainScreen, self).__init__('item', 'main-screen')
        self.options = options
        self.last_light_pos = Vec2d(0, 0)
        self.globals = serge.blocks.singletons.Store.getItem('globals')  

    def addedToWorld(self, world):
        """Added to the world"""
        super(MainScreen, self).addedToWorld(world)
        self.manager = world.findActorByName('behaviours')
        self.achievements = serge.blocks.achievements.getManager()
        serge.blocks.achievements.addAchievementsBannerToWorld(world, 'ui', 'ui-back', theme, self.manager)
        #
        world.setPhysicsStepsize(G('physics-step-size'))
        #
        self.status = serge.blocks.utils.addActorToWorld(world, status.Status('status', 'status'))
        #
        self.random_seed = G('level-seed')
        self.generateMap()
        #
        # Count the number of crystals that are in the cave
        self.status.total_crystals = len(world.findActorsByTag('crystal'))
        #
        # Player
        self.player = player.Player('player', 'player', maximum_reach=G('player-max-reach'), surface_tags=['rock'], 
            jump_impulse=G('player-jump-impulse'), walk_impulse=G('player-walk-impulse'), can_scramble=False)
        self.player.setSpriteName('walking')
        self.player.setPhysical(serge.physical.PhysicalConditions(
            mass=20.0, force=climbing.G*20, visual_size=False, group=climbing.G_ROPES, elasticity=0.1, 
            friction=G('player-friction'), width=G('player-effective-radius'), height=G('player-effective-radius')))
        self.player.setLayerName('actors')
        self.player.moveTo(*G('player-initial-position'))
        self.player.linkEvent(common.E_PLAYER_DIED, self.playerDied)
        self.player.linkEvent(common.E_CAVE_SOLVED, self.caveSolved)
        self.player.linkEvent(serge.events.E_COLLISION, self.playerCollided)
        world.addActor(self.player)
        #
        # Text
        self.main_text = serge.blocks.utils.addTextToWorld(
            world, 'You died!', 'main-text', theme.getTheme('main-screen'), 'ui')
        self.sub_text = serge.blocks.utils.addTextToWorld(
            world, 'Press ENTER to restart', 'sub-text', theme.getTheme('main-screen'), 'ui')
        self.main_text.active = False
        self.sub_text.active = False
        #
        # Bugs
        self.bugs = [serge.blocks.utils.addActorToWorld(world,
            bug.Bug('bug', 'bug', 'base-bug', self),
            center_position=self.cave.getStartPosition())
                for idx in range(G('number-bugs'))]
        #
        # The HUD
        self.hud = serge.blocks.utils.addActorToWorld(world, hud.HUD('hud', 'hud', self.status))
        self.hud.linkEvent(common.E_ADD_LIGHT, self.addLight)
        #
        # Adding ropes
        self.cave.linkEvent(common.E_ROCK_CLICKED, self.addRope)
        self.cave.linkEvent(common.E_ROCK_RIGHT_CLICKED, self.switchRope)
        #
        self.world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.worldActivated)
        self.world.linkEvent(serge.events.E_DEACTIVATE_WORLD, self.worldDeactivated)
        #
        # Sounds 
        self.addSoundTexture(world)
        #
        # Overlay
        self.overlays = common.getOverlays(world, 'Building cave ...', visible=True)
        #
        # Cheating
        if self.options.cheat:
            fps = serge.blocks.utils.addActorToWorld(world,
                serge.blocks.actors.FPSDisplay(G('fps-x'), G('fps-y'), G('fps-colour'), G('fps-size')))
                
    def worldActivated(self, obj, arg):
        """Activated the world"""
        #
        # Sounds
        self.ambience.play(-1)
        serge.sound.Music.fadeout(G('music-fade-time')*1000)
        self.player.setStopped()

    def worldDeactivated(self, obj, arg):
        """Deactivated the world"""
        #
        # Stop all sounds
        self.ambience.stop()
        
    def playerCollided(self, obj, arg):
        """Collision occured"""
        if obj.tag == 'crystal':
            self.log.info('Collision with crystal %s, %s' % (obj.getNiceName(), arg))
            self.status.collected_crystals += 1
            #
            # Achievements related to crystals
            self.achievements.makeReport('crystals', number=self.status.collected_crystals, total=self.status.total_crystals)
            #
            # Take the crystal
            obj.takenByPlayer(self.player, self.world)

    def addRope(self, rock, arg):
        """A rope was added"""
        #
        # Don't do this if the player is not active
        if not self.player.active:
            return
        #
        # Don't do this if we don't have any ropes left
        if self.status.ropes == 0:
            self.log.info('No ropes left')
            return
        #
        self.status.ropes -= 1
        self.log.info('Adding a rope to rock %s' % rock)
        try:
            r = climbing.Rope.addRopeFrom(self.world, 'rope', ['rock'], 'rope-dyn', self.mouse.getScreenPos(), 
                (self.player.x, self.player.y), 'ropes', G('rope-segment-length'), G('rope-number-segments'),
                G('rope-anchor-size'), G('rope-anchor-colour'),
                draw_rope=True, rope_width=G('rope-width'), rope_colour=G('rope-colour'))
        except climbing.TooLong, err:
            self.log.info('Rope would be too long: %s' % err)
            return False
        else:
            r.setLayerName('ropes')
            self.player.grabNearestHangPoint(['rope-link'])
            serge.sound.Sounds.getItem('fire-rope').play()
            r.damping_factor = G('rope-damping-factor')
        #
        # Mark the cave as in progress now since we have done something meaningful
        self.globals.cave_in_progress = common.P_IN_CAVE
        return True
        
    def switchRope(self, rock, arg):
        """Switch out the current rope for a new one"""
        #
        # Don't do this if the player is not active
        if not self.player.active:
            return
        #
        if self.player.isHanging():
            old_rope = self.player.getRope()
            #
            # Add the new rope
            if self.addRope(rock, arg):
                #            
                self.log.info('Switching ropes')
                #
                # Remove the old rope - wake it up first in case it went to
                # sleep
                old_rope.wakeUp()
                self.world.scheduleActorRemoval(old_rope)
                #
                # Recove the rope that we deployed
                self.status.ropes += 1

    def addSoundTexture(self, world):
        """Add sound texturing"""
        self.ambience = serge.blocks.sounds.SoundTexture('sounds', 'sounds', G('dynamic-sound-damping'))
        self.ambience.addPositionalSound(serge.blocks.sounds.RectangularRegionSound(
            serge.sound.Sounds.getItem('ambience'),
            (0, 2*G('surface-rows')*G('cell-size')[1], 10000, 10000)))        
        self.ambience.addPositionalSound(serge.blocks.sounds.RectangularRegionSound(
            serge.sound.Sounds.getItem('meadow'),
            (0, 0, 10000, 2*G('surface-rows')*G('cell-size')[1])))
        self.ambience.addPositionalSound(serge.blocks.sounds.LocationalSounds(
            serge.sound.Sounds.getItem('water'), 
            self.cave.water_falls_locations, G('water-fall-sound-dropoff')))
        self.ambience.addPositionalSound(serge.blocks.sounds.ActorsWithTagSound(
            serge.sound.Sounds.getItem('crystal'), 
            self.world, 'crystal', G('crystal-sound-dropoff')))
        self.ambience.addPositionalSound(serge.blocks.sounds.LocationalSound(
            serge.sound.Sounds.getItem('exit-sound'),
            self.cave.exit_location, G('exit-sound-dropoff')))
        self.flare_sounds = serge.blocks.sounds.LocationalSounds(
            serge.sound.Sounds.getItem('flare'),
            [], G('flare-sound-dropoff'))
        self.ambience.addPositionalSound(self.flare_sounds)
        #
        # The following sound fades in when the banner shows so we put it off screen for the moment
        self.globals.banner_sound = serge.blocks.sounds.LocationalSound(
            serge.sound.Sounds.getItem('crystal-banner'),
            (-10000, -10000), 100)
        self.ambience.addPositionalSound(self.globals.banner_sound)
        self.ambience.setListener(self.player)
        #
        creature = random.choice(G('creature-sounds'))
        self.ambience.addRandomSound(serge.sound.Sounds.getItem('%s-1' % creature), G('frog-sound-probability'))
        self.ambience.addRandomSound(serge.sound.Sounds.getItem('%s-2' % creature), G('frog-sound-probability'))
        world.addActor(self.ambience)
            
    def updateActor(self, interval, world):
        """Update this actor"""
        super(MainScreen, self).updateActor(interval, world)
        #
        # Turn off overlay when we are ready to see everything
        if self.cave.light.isReady():
            self.overlays.forEach().visible = False
        #
        # Toggle camera lock
        if self.keyboard.isClicked(pygame.K_f):
            self.status.camera_locked = not self.status.camera_locked
        #
        # Go back to name screen
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            if self.options.skip:
                self.engine.stop()
            else:
                self.engine.setCurrentWorldByName('start-screen')
        #
        # Restarting after death
        if not self.player.active and (self.keyboard.isClicked(pygame.K_RETURN) or self.keyboard.isClicked(pygame.K_KP_ENTER)):
            serge.sound.Sounds.play('click')
            if self.options.skip:
                self.engine.stop()
            else:
                self.engine.setCurrentWorldByName('start-screen')
        #
        # Update the camera
        if not self.status.camera_locked:
            if self.player.active:
                ideal_position_x = self.player.x
                ideal_position_y = self.player.y
                damping = G('camera-damping')
            else:
                ideal_position_x = self.body.x
                ideal_position_y = self.body.y - G('player-death-camera-offset')
                damping = G('camera-death-damping')
            #
            actual_position_x = min(max(G('screen-width')/2, ideal_position_x), 
                G('screen-width')*(G('cave-horizontal-screens')-0.5))
            actual_position_y = min(max(G('screen-height')/2, ideal_position_y), 
                G('screen-height')*(G('cave-vertical-screens')-0.5))
            self.camera.moveTo(
                self.camera.x*(1-damping)+actual_position_x*damping, 
                self.camera.y*(1-damping)+actual_position_y*damping)
        #
        # Some options that are only used in development mode
        if self.options.cheat:
            #
            # Drop to interactive
            if self.keyboard.isClicked(pygame.K_i):
                import pdb; pdb.set_trace()
            #
            # Create a light
            if self.keyboard.isClicked(pygame.K_n):
                colour = G('colour', 'death')
                strength = G('strength', 'death')
                distance = G('distance', 'death')
                self.cave.addLight(self.mouse.getScreenPos(), colour, strength, distance, flare_type=None)
            #
            # Turn lighting on and off
            if self.keyboard.isClicked(pygame.K_l):
                self.cave.light.visible = not self.cave.light.visible
            #
            # Scroll up and down
            if self.keyboard.isClicked(pygame.K_PAGEUP):
                self.status.camera_locked = True
                self.camera.move(0, -200)
            if self.keyboard.isClicked(pygame.K_PAGEDOWN):
                self.status.camera_locked = True
                self.camera.move(0, +200)
                
    def generateMap(self):
        """Generate a new cave map"""
        self.cave = cave.Cave.generateCaveMap(self.world, True, self.random_seed)
        self.sources = self.cave.sources
        
    def addLight(self, selected_light, arg):
        """Event triggered to add a light"""
        #
        # Don't do this if the player is not active
        if not self.player.active:
            return
        #
        # Don't do if we ran out of flares
        if self.status.getNumberOfLights(selected_light) == 0:
            self.log.info('No flares left')
            return
        #
        serge.sound.Sounds.getItem('flare-start').play()
        self.status.setNumberOfLights(selected_light, self.status.getNumberOfLights(selected_light)-1)
        colour = G('colour', selected_light)
        strength = G('strength', selected_light)
        distance = G('distance', selected_light)
        self.cave.addLight((self.player.x, self.player.y), colour, strength, distance, flare_type=selected_light)
        self.flare_sounds.locations.append((self.player.x, self.player.y))
        #
        # Mark the cave as in progress now since we have done something meaningful
        self.globals.cave_in_progress = common.P_IN_CAVE
    
    def playerDied(self, obj, arg):
        """The player died"""
        if self.options.god:
            self.log.info('Immortal player didn\'t die this time!')
            return
        #
        # Show a halo light
        colour = G('colour', 'death')
        strength = G('strength', 'death')
        distance = G('distance', 'death')
        self.cave.addLight((self.player.x, self.player.y), colour, strength, distance, flare_type=None)
        #
        # Make the player invisible
        self.player.active = False
        #
        # And replace with a dead body
        self.body = serge.blocks.utils.addSpriteActorToWorld(self.world, 'body', 'body', 'dead-body', 'actors', 
            (self.player.x, self.player.y))
        serge.sound.Sounds.getItem('player-death').play()
        #
        # Report out
        self.main_text.visual.setText('You Died!')
        self.sub_text.visual.setText('Press ENTER to restart')
        self.main_text.active = True
        self.sub_text.active = True
        #
        # Mark the cave as not in progress now
        self.globals.cave_in_progress = common.P_DIED_IN_CAVE
        #
        # Record for achievements
        self.achievements.makeReport('death', depth=self.player.y)

    def caveSolved(self, obj, arg):
        """The player reached the goal in the cave"""
        #
        # Make the player invisible
        self.player.active = False
        self.body = self.player
        #
        # Report out
        self.main_text.visual.setText('You beat the cave!')
        self.sub_text.visual.setText('Press ENTER to restart')
        self.main_text.active = True
        self.sub_text.active = True
        #
        # Mark the cave as not in progress now
        self.globals.cave_in_progress = common.P_DIED_IN_CAVE
        #
        # Achievements related to cave solving
        self.globals.history.solveCave(self.globals.last_cave_name)
        self.achievements.makeReport('solve', 
            caves=self.globals.history.getTotalSolves(), 
            this_cave=self.globals.history.getSolvesForCave(self.globals.last_cave_name),
            tme=self.status.time_spent)

        
        
def main(options):
    """Create the main logic"""
    #
    # The behaviour manager
    world = serge.engine.CurrentEngine().getWorld('main-screen')
    #
    # Prepare zone as one large one
    list(world.zones)[0].setSpatial(-20000, -20000, 40000, 40000)
    #
    # Set behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # The screen actor
    s = MainScreen(options)
    world.addActor(s)
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_m, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

