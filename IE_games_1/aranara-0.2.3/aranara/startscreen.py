"""The entry screen for the game"""

from pymunk import Vec2d
import pyglet

import engine
import engine.utils
import levels
import settings
import common
import sound


class StartScreen(engine.World):
    """The main start screen for the game"""

    def worldCreated(self):
        """The screen was created"""
        #
        # Create the batches
        text = self.addBatch('text')
        self.tweened_objects = []
        #
        back_layer = pyglet.graphics.OrderedGroup(0)
        front_layer = pyglet.graphics.OrderedGroup(1)
        #
        bg = engine.SpriteActor('bg', 'start-bg.jpg', batch=text, group=back_layer)
        bg.position = settings.S.Start.bg_position
        self.addActor(bg)
        #
        # self.tweens.append(
        #     engine.Tween(bg, 'opacity', 255, engine.utils.RandomGenerator(150, 200),
        #                  engine.utils.RandomGenerator(3, 5),
        #                  engine.Tween.sinInOut, repeat=True)
        # )
        #
        welcome = engine.TextActor(
            'welcome',
            pyglet.text.decode_html(
                '<font size="3" color="white">A game for PyWeek '
                'by Paul Paterson (v%s)</font>' % common.version
            ),
            width=500,
            multiline=True,
            batch=text, group=front_layer
        )
        welcome.x, welcome.y = settings.S.Start.credit_position
        self.addTweenedActor(welcome)
        #
        logo = engine.SpriteActor('logo', 'logo.png', batch=text, group=front_layer)
        logo.position = settings.S.Start.logo_position
        self.addActor(logo)
        #
        title = engine.SpriteActor('title', 'title.png', batch=text, group=front_layer)
        title.position = settings.S.Start.title_position
        self.addTweenedActor(title)
        #
        start = engine.SpriteActor('start-button', 'start-btn.png', batch=text, group=front_layer)
        start.position = settings.S.Start.start_btn_position
        start.linkEvent(engine.events.E_LEFT_CLICK, self.startClicked)
        self.addTweenedActor(start)
        self.tweens.append(
            engine.Tween(start, 'color', [255, 255, 255], [255, 100, 100], 0.2,
                         engine.Tween.colourTween, repeat=True)
        )
        #
        help = engine.SpriteActor('help-button', 'help-btn.png', batch=text, group=front_layer)
        help.position = settings.S.Start.help_btn_position
        help.linkEvent(engine.events.E_LEFT_CLICK, self.helpClicked)
        self.addTweenedActor(help)
        #
        #sound.Music.sinister.play()
        #
        self.came_from = 'start'
        self.age = 0

    def addTweenedActor(self, actor):
        """Add an actor to the world and get it ready for tweening on"""
        self.addActor(actor)
        self.tweened_objects.append(actor)
        actor.target_x, actor.target_y = actor.x, actor.y

    def applyTweens(self, start_offset_x, start_offset_y, end_offset_x, end_offset_y, after=None):
        """Apply the tweens to bring items on the screen"""
        self.log.info('Tweening objects on or off the screen')
        #
        # Tween in the image
        for idx, item in enumerate(self.tweened_objects):
            self.tweens.append(
                engine.Tween(
                    item, 'position', Vec2d(item.target_x + start_offset_x, item.target_y + start_offset_y),
                    Vec2d(item.target_x + end_offset_x, item.target_y + end_offset_y),
                    settings.S.Level.tween_in_duration, engine.Tween.sinOut,
                    delay=float(settings.S.Level.tween_in_delay),
                    after=after if idx == 0 else None
                )
            )

    def onKeyRelease(self, symbol, modifier):
        """Handle key presses"""
        if symbol in (pyglet.window.key.ENTER, pyglet.window.key.SPACE):
            self.startClicked(None, None)
        elif symbol == pyglet.window.key.ESCAPE:
            return pyglet.event.EVENT_HANDLED

    def onKeyPress(self, symbol, modifier):
        """Handle key presses"""
        if symbol == pyglet.window.key.ESCAPE:
            self.engine.stopEngine('ESCAPE pressed')

    def startClicked(self, obj, arg):
        """The start button was clicked"""
        self.log.info('Start was clicked')
        sound.Sounds.click_forward.play()
        self.applyTweens(0, 0, settings.S.Start.tween_in_offset_x, 0, after=self._startReady)
        self.came_from = 'start'

    def _startReady(self):
        """Start is ready to go"""
        self.engine.setCurrentWorld('level-screen')

    def helpClicked(self, obj, arg):
        """The help button was clicked"""
        self.log.info('Help was clicked')
        sound.Sounds.click_forward.play()
        self.applyTweens(0, 0, 0, settings.S.Start.tween_out_offset_y, after=self._helpReady)
        self.came_from = 'help'

    def _helpReady(self):
        """Help is ready to go"""
        self.engine.setCurrentWorld('help-screen')

    def activateWorld(self):
        """The world was activated"""
        if self.came_from == 'start':
            self.applyTweens(settings.S.Start.tween_in_offset_x, 0, 0, 0)
        else:
            self.applyTweens(0, settings.S.Start.tween_out_offset_y, 0, 0)

    def updateWorld(self, dt):
        """Update the world"""
        super(StartScreen, self).updateWorld(dt)
        #
        # TODO: this is a hack because music seems to have an issue starting immediately
        self.age += dt
        if self.age > 1 and not sound.Music.sinister.playing:
            sound.Music.sinister.play()
