"""The level screen for the game"""

import os
import time
import pygame

import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.sound
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.layout
import terrain.generator
import smacktalker

from theme import G, theme
import common


class RandomLevelScreen(serge.blocks.actors.ScreenActor):
    """The logic for the level screen"""
    
    def __init__(self, options):
        """Initialise the screen"""
        super(RandomLevelScreen, self).__init__('item', 'main-screen')
        self.options = options
        self._take_screenshots = G('auto-screenshots')
        self._screenshot_interval = G('screenshot-interval')
        self._last_screenshot = time.time() - self._screenshot_interval + 1.0
        self._screenshot_path = G('screenshot-path')
        self.music = common.MAIN_MUSIC
        self.initialised = False

    def addedToWorld(self, world):
        """The level screen was added to the world"""
        super(RandomLevelScreen, self).addedToWorld(world)
        #
        # Logo
        the_theme = theme.getTheme('random-level-screen')
        L = the_theme.getProperty
        logo = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'logo', 'logo', 'foreground',
            center_position=L('logo-position'))
        title = serge.blocks.utils.addSpriteActorToWorld(world, 'logo', 'title', 'title', 'foreground',
            center_position=L('title-position'))
        bg = serge.blocks.utils.addSpriteActorToWorld(
            world, 'bg', 'bg', 'dark-background',
            layer_name='background',
            center_position=(G('screen-width') / 2, G('screen-height') / 2),
        )
        # Preview of level
        self.level_preview = serge.blocks.utils.addVisualActorToWorld(
            world, 'level-preview', 'level-preview',
            serge.visual.SurfaceDrawing(
                L('level-preview-width'), L('level-preview-height'),
            ),
            layer_name='ui',
            center_position=L('level-preview-position'),
        )
        #
        # Size menu
        self.size_options = L('size-options')
        self.size_menu = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.ToggledMenu(
                'size-menu', 'size-menu',
                ['Small', 'Medium', 'Large'],
                serge.blocks.layout.VerticalBar(
                    'bar', 'bar', L('size-width'), L('size-height'),
                ),
                default='Medium',
                on_colour=L('menu-on-colour'),
                off_colour=L('menu-off-colour'),
                callback=self.sizeSelected,
                font_colour=L('menu-font-colour'),
                mouse_over_colour=L('menu-mouse-over-colour'),
                font_size=L('size-font-size'),
                font_name=L('menu-font'),
                width=L('size-item-width'),
                height=L('size-item-height'),
            ),
            center_position=L('size-position'),
            layer_name='ui'
        )
        #
        # Amount of open space menu
        self.space_options = L('space-options')
        self.space_menu = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.ToggledMenu(
                'space-menu', 'space-menu',
                ['Open', 'Blocked'],
                serge.blocks.layout.VerticalBar(
                    'bar', 'bar', L('space-width'), L('space-height'),
                ),
                default='Open',
                on_colour=L('menu-on-colour'),
                off_colour=L('menu-off-colour'),
                callback=self.spaceSelected,
                font_colour=L('menu-font-colour'),
                mouse_over_colour=L('menu-mouse-over-colour'),
                font_size=L('space-font-size'),
                height=L('space-item-height'),
                font_name=L('menu-font'),
                width=L('space-item-width'),
            ),
            center_position=L('space-position'),
            layer_name='ui'
        )
        # Generate button
        generate = serge.blocks.utils.addSpriteActorToWorld(
            world, 'generate', 'generate', 'generate',
            layer_name='ui',
            center_position=L('generate-position'),
        )
        generate.linkEvent(serge.events.E_LEFT_CLICK, self.generateLevel)
        # Select button
        select = serge.blocks.utils.addSpriteActorToWorld(
            world, 'select', 'select', 'select',
            layer_name='ui',
            center_position=L('select-position'),
        )
        select.linkEvent(serge.events.E_LEFT_CLICK, self.selectLevel)
        #
        # Resume button
        self.resume = serge.blocks.utils.addSpriteActorToWorld(
            world, 'resume', 'resume', 'resume',
            layer_name='ui',
            center_position=L('resume-position'),
        )
        self.resume.linkEvent(serge.events.E_LEFT_CLICK, common.tweenWorlds('main-screen'))
        # Back button
        back = serge.blocks.utils.addSpriteActorToWorld(
            world, 'back', 'back', 'back',
            layer_name='ui',
            center_position=L('back-position'),
        )
        back.linkEvent(serge.events.E_LEFT_CLICK, common.tweenBackWorlds('level-screen'))
        #
        # Smack talking
        self.smack = smacktalker.RandomlyAppearingSmacker('smack', 'smack', 'random-level-screen',
                                                          'waiting-for-random-level')
        world.addActor(self.smack)
        self.smack.visible = False
        #
        self.initialised = True
        self.generateLevel()
        #
        # Events
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.activatedWorld)

    def activatedWorld(self, obj, arg):
        """The world was activated"""
        if self.engine.getCurrentWorld().name != 'start-screen':
            self.music.play(-1)
        self.resume.active = common.LEVEL_IN_PROGRESS

    def sizeSelected(self, obj, arg):
        """The size was selected"""
        self.log.debug('Selected size %s' % arg)
        if self.initialised:
            self.generateLevel()

    def spaceSelected(self, obj, arg):
        """The space was selected"""
        self.log.debug('Selected space %s' % arg)
        if self.initialised:
            self.generateLevel()

    def generateLevel(self, obj=None, arg=None):
        """Regenerate the level"""
        #
        # Create and initialise out generator
        generator = terrain.generator.Generator()
        generator.setOptions(
            os.path.join('levels', 'bomber.xml'),
            os.path.join('levels', 'bomber-out.xml'),
            'main',
        )
        #
        # Settings
        width, height = self.size_options[self.size_menu.getSelection()]
        destructible, between = self.space_options[self.space_menu.getSelection()]
        #
        # Override the settings
        root = generator.root.find('builders/builder[@name="Bomber procedural"]')
        root.find('width').text = width
        root.find('height').text = height
        root.find('destructibleBlocks').text = destructible
        root.find('blocksBetweenEnemies').text = between
        #
        # Generate the level
        generator.createBuilders()
        generator.createRenderers()
        generator.runBuilderNamed('Bomber procedural')
        generator.renderOutput('main')
        generator.renderOutput('tiled')
        #
        # Update the preview
        self.level_preview.visual.setSurface(pygame.image.load(os.path.join('levels', 'bomber-out.png')))
        #
        # Re-center the preview
        self.level_preview.resizeTo(self.level_preview.visual.width, self.level_preview.visual.height)
        self.level_preview.moveTo(self.level_preview.x, self.level_preview.y)

    def selectLevel(self, obj, arg):
        """Select a level number"""
        self.log.info('Selected level')
        serge.sound.Sounds.play('click')
        world = self.engine.getWorld('main-screen')
        controller = world.findActorByName('main-screen')
        controller.current_level = 6
        controller.restartGame()
        common.tweenWorlds('main-screen')()
        common.LEVEL_IN_PROGRESS = True

    def updateActor(self, interval, world):
        """Update this actor"""
        super(RandomLevelScreen, self).updateActor(interval, world)
        #
        # Keypresses
        if self.keyboard.isClicked(pygame.K_RETURN):
            pass
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            common.tweenBackWorlds('level-screen')(None, None)
        #
        if self._take_screenshots:
            if time.time() - self._last_screenshot > self._screenshot_interval:
                filename = '%s-%s' % (self.name, time.strftime('%m-%d %H:%M:%S.png'))
                serge.blocks.utils.takeScreenshot(os.path.join(self._screenshot_path, filename))
                self._last_screenshot = time.time()
                self.log.debug('Taking screenshot - %s', filename)

            
def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = RandomLevelScreen(options)
    world = serge.engine.CurrentEngine().getWorld('random-level-screen')
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

