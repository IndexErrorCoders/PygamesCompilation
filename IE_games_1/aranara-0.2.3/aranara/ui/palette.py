"""The palette of objects that the player can put on the screen"""

import pymunk
import pyglet

from .. import engine
from .. import settings
from .. import sound
import common
from gerty import *

# TODO: add text to show the number of objects to the palette


class Palette(common.HideableComponent):
    """Represents the palette of objects that the player can play"""

    def __init__(self, name, *args, **kw):
        """Initialise the palette"""
        super(Palette, self).__init__(name, 'toolbar.png', *args, **kw)
        #
        # Hideable properties
        self.on_screen_position = settings.S.palette_on_screen_position
        self.off_screen_position = settings.S.palette_off_screen_position
        self.hide_duration = settings.S.palette_hide_duration
        #
        self.linkEvent(engine.events.E_LEFT_CLICK, self.leftClick, important=True)
        #
        self.buttons = []

    def addedToWorld(self, world):
        """We were added to the world"""
        super(Palette, self).addedToWorld(world)

    def leftClick(self, obj, arg):
        """Left click on the palette"""
        self.log.info('Toggling visual state of palette')
        sound.Sounds.click.play()
        self.toggle()
        self.world.gerty_state[W_CLICKED_PALETTE] = True

    def addButtons(self, buttons):
        """Add some buttons"""
        for idx, (image_name, item, number) in enumerate(buttons):
            btn = engine.SpriteActor(
                engine.getUID('btn-%s'), image_name, batch=self.batch, group=self.world.ui_front
            )
            self.mountActor(
                btn,
                (settings.S.palette_btn_offset_x,
                 settings.S.palette_btn_initial_y + settings.S.palette_btn_offset_y * len(self.buttons))
            )
            btn.linkEvent(engine.events.E_LEFT_CLICK, self.buttonClick, idx)
            self.buttons.append([btn, item, number])
        self.world.gerty_state[W_ITEMS_IN_PALETTE] = self._getNumberOfItems()

    def buttonClick(self, (x, y, buttons, modifiers), idx):
        """A button was clicked"""
        if self.buttons[idx][2] == 0:
            return
        self.log.info('Palette button %d was clicked' % idx)
        sound.Sounds.click.play()
        #
        # Make sure we are showing because the hide event will also fire
        # TODO: the event system should be smart enough to prevent this from occurring
        self.show()
        #
        # Create the object
        obj = self.buttons[idx][1](self.batch)
        #
        # Decrease the number of remaining objects
        self.buttons[idx][2] -= 1
        if self.buttons[idx][2] == 0:
            #
            # All done - remove the button
            img = self.buttons[idx][0].image = pyglet.resource.image('blank-btn.png')
            img.anchor_x = img.width / 2
            img.anchor_y = img.height / 2
        self.world.addActor(obj)
        obj.position = pymunk.Vec2d(x, y) + settings.S.palette_btn_object_offset
        obj.syncPhysics()
        #
        self.world.gerty_state[W_ITEMS_IN_PALETTE] = self._getNumberOfItems()

    def _getNumberOfItems(self):
        """Return the number of items still to be used in the palette"""
        total = 0
        for _, _, number in self.buttons:
            total += number
        return total