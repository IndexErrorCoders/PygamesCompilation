"""The start screen for the game"""

import random
import math
import pygame


import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.singletons

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common 
import cave
import player
import climbing

class StartScreen(serge.blocks.actors.ScreenActor):
    """The logic for the start screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(StartScreen, self).__init__('item', 'main-screen')
        self.options = options
        self.globals = serge.blocks.singletons.Store.getItem('globals')  
        self.globals.cave_in_progress = common.P_NO_CAVE      

    def addedToWorld(self, world):
        """The start screen was added to the world"""
        super(StartScreen, self).addedToWorld(world)
        #
        self.camera_timer = 0
        self.manager = world.findActorByName('behaviours')
        #
        # Logo
        the_theme = theme.getTheme('start-screen')
        L = the_theme.getProperty
        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'logo', 'ui', 
            center_position=L('logo-position'))
        #
        serge.blocks.utils.addTextItemsToWorld(world, [
                    (L('title'), 'title'),
                    (L('title2'), 'title2'),
                    ('v' + common.version, 'version'),
                    ('Resume', 'resume',  self.resumePlay),
                    ('Start', 'start',  serge.blocks.utils.worldCallback('name-screen', 'click')),
                    ('Crystal collection', 'collection',  serge.blocks.utils.worldCallback('collection-screen', 'click')),
                    ('Help', 'help',  serge.blocks.utils.worldCallback('help-screen', 'click')),
                    ('Credits', 'credits',  serge.blocks.utils.worldCallback('credits-screen', 'click')),
                    ('Achievements', 'achievements', self.showAchievements),
                ],
                the_theme, 'ui')
        #
        self.start = world.findActorByName('start')
        self.resume = world.findActorByName('resume')
        self.resume.visible = False
        #
        self.music = serge.sound.Music.getItem('title-music')
        self.music.play(loops=-1)
        #
        self.world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.worldActivated)
        #
        # Overlay
        self.overlays = common.getOverlays(world, 'Starting game ...', visible=True)
        #
        # Asynchronously build the graphical elements - this takes a while
        self.manager.assignBehaviour(self, serge.blocks.behaviours.TimedOneshotCallback(100, self.buildGraphics), 'build')
        #
        # FPS counter
        if self.options.cheat:
            fps = serge.blocks.utils.addActorToWorld(world,
                serge.blocks.actors.FPSDisplay(G('fps-x'), G('fps-y'), G('fps-colour'), G('fps-size')))


    def buildGraphics(self, world, actor, interval):
        """Build the graphical elements to show"""
        self.cave = cave.Cave.generateCaveMap(self.world, False, G('start-screen-seed'))
        #
        # Add light sources
        for (x, y), selected_light in G('sources', 'start-screen'):
            colour = G('colour', selected_light)
            strength = G('strength', selected_light)
            distance = G('distance', selected_light)
            self.cave.addLight((x, y), colour, strength, distance, flare_type=selected_light, update=False)
        self.cave.updateLighting()
        #
        # Add a climber
        self.player = player.Player('player', 'player', maximum_reach=G('player-max-reach'), surface_tags=[], 
            jump_impulse=G('player-jump-impulse'), walk_impulse=G('player-walk-impulse'), can_scramble=False)
        self.player.setSpriteName('walking')
        self.player.setPhysical(serge.physical.PhysicalConditions(
            mass=20.0, force=climbing.G*20, visual_size=False, group=climbing.G_ROPES, elasticity=0.1, friction=1.0,
            width=G('player-effective-radius'), height=G('player-effective-radius')))
        self.player.setLayerName('ui')
        self.player.moveTo(*G('player-initial-position', 'start-screen'))
        world.addActor(self.player)
        #
        # And a rope
        r = climbing.Rope.addRopeFrom(world, 'rope', [], 'rope-dyn', G('rope-origin', 'start-screen'), 
            G('rope-end', 'start-screen'), 'ropes', G('rope-segment-length'), G('rope-number-segments'),
            G('rope-anchor-size'), G('rope-anchor-colour'),
            draw_rope=True, rope_width=G('rope-width'), rope_colour=G('rope-colour'))
        r.setLayerName('ui-back')
        self.player.grabNearestHangPoint(['rope-link'])
        r.damping_factor = G('rope-damping-factor')
        #
        # Put all rope links on the static layer
        r.getChildren().forEach().setLayerName('ui-back')

    def showAchievements(self, obj, arg):
        """Show the achievements"""
        serge.sound.Sounds.getItem('click').play()
        self.engine.setCurrentWorldByName('achievements-screen')
        self.camera.moveTo(G('screen-width')/2, G('screen-height')/2)
    
    def worldActivated(self, obj, arg):
        """Reset camera position"""
        self.camera.moveTo(*self.camera_pos)
        if not serge.sound.Music.isPlaying():
            self.music.play(loops=-1)
        if self.globals.cave_in_progress == common.P_IN_CAVE:
            self.start.visual.setText('Start New Cave')
            self.resume.visual.setText('Resume Cave')
        elif self.globals.cave_in_progress == common.P_DIED_IN_CAVE:
            self.start.visual.setText('Start New Cave')
            self.resume.visual.setText('Play Cave Again')
        
    def updateActor(self, interval, world):
        """Update this actor"""
        super(StartScreen, self).updateActor(interval, world)
        #
        # When we are ready ...
        if hasattr(self, 'cave') and self.cave.light.isReady():
            self.overlays.forEach().visible = False
            #
            # Move the camera
            self.camera_timer += interval/1000.0
            camera_y = G('screen-height') - G('camera-y-amp', 'start-screen')* \
                            math.cos(self.camera_timer/G('camera-period', 'start-screen')*2.0*math.pi)
            self.camera.moveTo(self.camera.x, camera_y)
            self.camera_pos = self.camera.x, self.camera.y 
            #
            # Resume button
            self.resume.visible = self.globals.cave_in_progress != common.P_NO_CAVE
            #
            # Move the player randomly
            if random.random() < G('move-player-probability', 'start-screen'):
                self.player.getPhysical().body.apply_impulse((-4000, 0))        
            #
            # Flip light
            if self.options.cheat and self.keyboard.isClicked(pygame.K_l):
                self.cave.light.visible = not self.cave.light.visible

    def resumePlay(self, obj, arg):
        """Resume play"""
        if self.globals.cave_in_progress == common.P_IN_CAVE:
            self.engine.setCurrentWorldByName('main-screen')
        elif self.globals.cave_in_progress == common.P_DIED_IN_CAVE:
            self.engine.setCurrentWorldByName('name-screen')
            self.globals.namescreen.chooseName(self.globals.last_cave_name, None)
        else:
            raise ValueError('cave_in_progress has an unexpected value "%s"' % self.globals.cave_in_progress)

def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = StartScreen(options)
    world = serge.engine.CurrentEngine().getWorld('start-screen')
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(), 'keyboard-quit')
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

