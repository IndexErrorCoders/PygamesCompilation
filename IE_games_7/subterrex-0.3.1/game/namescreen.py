"""The screen for selecting a cave name for the game"""

import random
import math
import pygame
import sha

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors

if serge.common.PYMUNK_OK:
    import pymunk
    import serge.physical

from theme import G, theme
import common 
import cave
import player
import climbing
import mainscreen
import history


class NameScreen(serge.blocks.actors.ScreenActor):
    """The logic for the name screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(NameScreen, self).__init__('item', 'main-screen')
        self.options = options
        self.globals = serge.blocks.singletons.Store.getItem('globals')  
        
    def addedToWorld(self, world):
        """The start screen was added to the world"""
        super(NameScreen, self).addedToWorld(world)
        #
        self.manager = world.findActorByName('behaviours')
        #
        # Logo
        the_theme = theme.getTheme('name-screen')
        L = the_theme.getProperty
        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'icon', 'ui', 
            center_position=L('logo-position'))
        #
        # Background
        bh = serge.blocks.utils.addSpriteActorToWorld(world, 'bg', 'bg', L('screen-background-sprite'), 'background', 
            center_position=L('screen-background-position'))
        #
        serge.blocks.utils.addTextItemsToWorld(world, [
                    ('Quick play - random cave', 'random', self.chooseRandomName),
                    ('Click to select a random cave', 'random-small'),
                    ('Enter a name for your cave', 'named', self.chooseName),
                    ('You will be able to return to your cave later', 'named-small'),
                    ('Previous caves', 'previous'),
                    ('Click below to return to a previously visited cave', 'previous-small'),
                    ('Back', 'back', serge.blocks.utils.backToPreviousWorld('click')),
        ], the_theme, 'ui')
        #
        # Name entry
        self.name_entry = serge.blocks.utils.addActorToWorld(world,     
            serge.blocks.actors.TextEntryWidget('entry', 'entry', L('entry-width'), L('entry-height'),
                colour=L('entry-font-colour'), font_size=L('entry-font-size'), font_name=L('entry-font-name'), 
                        justify='center', 
                        background_visual=serge.blocks.visualblocks.Rectangle((L('entry-width'), L('entry-height')),
                            L('entry-bg-colour'), L('entry-stroke-width'), L('entry-stroke-colour')),
                        background_layer='ui-back', show_cursor=True),
            center_position=L('entry-position'),
            layer_name='ui')
        self.name_entry.linkEvent(serge.events.E_ACCEPT_ENTRY, self.chooseName)
        #
        # The history table
        self.history = serge.blocks.utils.addActorToWorld(world, 
            self.globals.history,
            layer_name='ui', center_position=G('history-position', 'name-screen'))
        self.history.linkEvent(common.E_CAVE_SELECTED, self.chooseName)
        #
        # Overlay
        self.overlays = common.getOverlays(world, 'Building cave ...')
        #
        self.world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.resetCamera)
    
    def resetCamera(self, obj, arg):
        """Reset camera position"""
        self.camera.moveTo(*G('screen-background-position', 'name-screen'))
        
    def updateActor(self, interval, world):
        """Update this actor"""
        super(NameScreen, self).updateActor(interval, world)

    def chooseRandomName(self, obj, arg):
        """Choose a randomly named cave"""
        self.chooseName('RANDOM-CAVE', None)
        
    def chooseName(self, name, arg):
        """Choose a name for the cave"""
        serge.sound.Sounds.play('click')
        self.log.info('Chose name "%s"' % name)
        self.globals.last_cave_name = name
        self.globals.namescreen = self
        #
        # We defer doing the main processing until the next update because it takes some time
        # and we want to display an interstitial
        self.manager.assignBehaviour(self, serge.blocks.behaviours.TimedOneshotCallback(100, self.switchToMain), 'switch-to-main')
        self.overlays.forEach().visible = True
        
    def switchToMain(self, world, actor, interval):
        """Switch to the main world"""
        name = self.globals.last_cave_name
        self.log.info('Switching to cave %s' % name)
        #
        # Generate the random seed
        if name != 'RANDOM-CAVE':
            seed = int(sha.sha(name).hexdigest(), 16)
            #
            # Update the high score
            self.history.visitCave(name)        
        else:
            seed = random.randrange(0, 100000)
        theme.setProperty('level-seed', seed)
        #
        # Replace the old cave
        self.engine.removeWorldNamed('main-screen')
        serge.blocks.utils.createWorldsForEngine(self.engine, ['main-screen'])
        mainscreen.main(self.options)
        #
        # Mute button for sound
        mute = self.world.findActorByName('mute-button')
        serge.blocks.utils.addMuteButtonToWorlds(mute, center_position=G('mute-button-position'), world_names=['main-screen'])
        #
        # Go for it
        self.engine.setCurrentWorldByName('main-screen')
        self.overlays.forEach().visible = False
                
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = NameScreen(options)
    world = serge.engine.CurrentEngine().getWorld('name-screen')
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
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_TAB, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

