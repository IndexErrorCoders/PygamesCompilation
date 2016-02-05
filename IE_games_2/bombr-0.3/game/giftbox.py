"""UI and control for randomly creating items and adding to the board"""

import random

import serge.actor
import serge.sound
from serge.simplevecs import Vec2d
import serge.blocks.actors
import serge.blocks.animations

from theme import G, theme
import powerups


class GiftBox(serge.actor.MountableActor):
    """Handles showing and creating random items"""

    max_items_to_create = 5

    def __init__(self, name, tag):
        """Initialise the gift box"""
        super(GiftBox, self).__init__(name, tag)
        #
        self.board = None

    def addedToWorld(self, world):
        """Added to the world"""
        super(GiftBox, self).addedToWorld(world)
        self.world = world
        #
        # The timer that triggers when the gift choosing process starts
        self.wait_timer = world.addActor(serge.blocks.actors.Timer(
            'timer', 'gift-box-wait',
            G('random-item-low-time'), G('random-item-high-time'),
            self.startChoosingGift,
        ))
        #
        # The timer that shows the gift being chosen
        self.gift_chooser = world.addActor(serge.blocks.actors.Timer(
            'timer', 'gift-box-chooser',
            G('gift-box-cycle-time'),
            callback=self.cycleNewGift,
            started=False,
        ))
        self.gift_box_cycles = G('gift-box-cycles')
        self.gift_box_items = []
        self.current_item = None
        #
        # The potential gifts
        self.potential_gifts = [getattr(powerups, name) for name in G('random-item-names')]
        #
        # Display of the gift being chosen
        self.gift_sprite = serge.actor.Actor('gift', 'gift')
        self.mountActor(self.gift_sprite, G('gift-box-sprite-position'))
        self.gift_sprite.setLayerName('ui')
        self.gift_sprite.visible = False
        self.gift_sprite.setZoom(G('gift-box-sprite-zoom'))
        #
        # Sprite that will move to the new location
        self.moving_sprites = []
        for idx in range(self.max_items_to_create):
            moving_sprite = serge.blocks.animations.AnimatedActor('gift', 'moving-gift')
            moving_sprite.setLayerName('ui')
            moving_sprite.visible = False
            moving_sprite.setZoom(G('gift-box-sprite-zoom'))
            world.addActor(moving_sprite)
            self.moving_sprites.append(moving_sprite)

    def startChoosingGift(self):
        """Start choosing a gift"""
        self.log.info('Time to start choosing a gift')
        self.wait_timer.stopTimer()
        #
        # Set the gift displays
        number_cycles = random.randrange(*self.gift_box_cycles)
        self.gift_box_items = (self.potential_gifts * number_cycles)[:number_cycles]
        #
        # Start update timer
        self.gift_chooser.resetAndStartTimer()

    def cycleNewGift(self):
        """Cycle to a new gift"""
        if not self.gift_box_items:
            #
            # Create the item
            for idx in range(self.current_item.number_to_create):
                self.createItem(self.moving_sprites[idx])
            #
            # Stop showing box and start main timer again
            self.gift_sprite.visible = False
            self.gift_chooser.stopTimer()
            self.wait_timer.resetAndStartTimer()
            serge.sound.Sounds.play('choose-gift')
        else:
            #
            # Change which item is displayed
            self.current_item = self.gift_box_items.pop(0)
            self.gift_sprite.setSpriteName(self.current_item.name_of_sprite)
            self.gift_sprite.visible = True
            serge.sound.Sounds.play('cycle-gift')

    def giftInPlace(self, moving_sprite):
        """The gift arrived at the final location"""
        item = self.current_item(self.board)
        self.log.debug('Creating a new random item (%s) at (%s)' % (
            item.getNiceName(), moving_sprite.random_location))
        #
        # Now create the item
        if isinstance(item, powerups.Bomb):
            self.board.dropBombAt(moving_sprite.random_location)
        else:
            self.world.addActor(item)
            self.board.addManAt(item, moving_sprite.random_location)
        #
        moving_sprite.visible = False

    def createItem(self, moving_sprite):
        """Create an item"""
        #
        # Get a random item and a random location
        random_location = None
        while True:
            random_location = random.choice(self.board.random_locations)
            if not self.board.getOverlapping(random_location):
                break
            self.log.debug('Tried to put item at %s, %s but it was not blank' % random_location)
        #
        # Move the sprite to its location
        initial_position = Vec2d(
            self.gift_sprite.x + self.gift_sprite.width,
            self.gift_sprite.y + self.gift_sprite.height,
        )
        moving_sprite.addAnimation(
            serge.blocks.animations.MovementTweenAnimation(
                moving_sprite, initial_position,
                Vec2d(self.board.screenLocation(random_location)),
                duration=G('random-item-tween-time'),
                function=serge.blocks.animations.MovementTweenAnimation.sinInOut,
                after=lambda: self.giftInPlace(moving_sprite),
            ),
            'movement-tween'
        )
        moving_sprite.addAnimation(
            serge.blocks.animations.TweenAnimation(
                moving_sprite, 'setZoom', G('gift-box-sprite-zoom'), 1.0,
                duration=G('random-item-tween-time'),
                is_method=True,
            ),
            'zoom-tween'
        )
        moving_sprite.setSpriteName(self.gift_sprite.getSpriteName())
        moving_sprite.visible = True
        moving_sprite.random_location = random_location

    def stop(self):
        """Stop choosing gifts"""
        self.wait_timer.stopTimer()
        self.gift_chooser.stopTimer()
        self.gift_sprite.visible = False

    def restart(self, board):
        """Start choosing gifts again"""
        self.board = board
        self.wait_timer.resetAndStartTimer()