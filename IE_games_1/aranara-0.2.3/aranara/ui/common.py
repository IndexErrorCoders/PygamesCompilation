"""Some common UI components"""

from pymunk import Vec2d

from .. import engine
from .. import settings
from .. import sound


class HideableComponent(engine.MountableActor):
    """An item that is hideable"""

    # Override these
    on_screen_position = Vec2d(0, 0)
    off_screen_position = Vec2d(0, 0)
    hide_duration = 1

    # Tween to hide and show
    tween = None

    def hide(self):
        """Hide the control"""
        #
        # Handle the case where we are hiding and showing at the same time
        if self.tween:
            self.world.tweens.remove(self.tween)
            start = Vec2d(self.x, self.y)
        else:
            sound.Sounds.door.play()
            start = self.on_screen_position
            #
        self.world.tweens.append(
            engine.Tween(self, 'position',
                         start, self.off_screen_position,
                         self.hide_duration, engine.Tween.sinOut, after=self._finishedTween,
                         set_immediately=False)
        )
        self.showing = False
        self.tween = self.world.tweens[-1]

    def show(self):
        """Hide the control"""
        #
        # Handle the case where we are hiding and showing at the same time
        if self.tween:
            self.world.tweens.remove(self.tween)
            start = Vec2d(self.x, self.y)
        else:
            sound.Sounds.door.play()
            start = self.off_screen_position
        #
        self.world.tweens.append(
            engine.Tween(self, 'position',
                         start, self.on_screen_position,
                         self.hide_duration, engine.Tween.sinOut, after=self._finishedTween,
                         set_immediately=False)
        )
        self.showing = True
        self.tween = self.world.tweens[-1]

    def toggle(self):
        """Toggle whether we are shown or not"""
        if self.showing:
            self.hide()
        else:
            self.show()

    def _finishedTween(self):
        """Finished our tween"""
        self.tween = None