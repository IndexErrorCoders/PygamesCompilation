"""The entry screen for the game"""

from pymunk import Vec2d
import pyglet

import engine
import engine.utils
import levels
import settings
import common
import sound


class HelpScreen(engine.World):
    """The main help screen for the game"""

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
        help = engine.SpriteActor('help', 'help-image.png', batch=text, group=front_layer)
        help.position = settings.S.Help.help_img_position
        self.addTweenedActor(help)
        #
        logo = engine.SpriteActor('logo', 'logo.png', batch=text, group=front_layer)
        logo.position = settings.S.Start.logo_position
        self.addActor(logo)
        #
        back = engine.SpriteActor('back-button', 'back.png', batch=text, group=front_layer)
        back.position = settings.S.Level.back_btn_position
        back.linkEvent(engine.events.E_LEFT_CLICK, self.backClicked)
        self.addTweenedActor(back)

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

    def activateWorld(self):
        """The world was activated"""
        self.applyTweens(0, settings.S.Help.tween_in_offset_y, 0, 0)

    def backClicked(self, obj, arg):
        """Back was clicked"""
        self.log.info('Back was clicked')
        sound.Sounds.click_backward.play()
        self.applyTweens(0, 0, 0, settings.S.Help.tween_in_offset_y, after=self._backDone)

    def _backDone(self):
        """Back is ready to go"""
        self.engine.setCurrentWorld('start-screen')