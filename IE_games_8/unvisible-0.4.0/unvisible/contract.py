"""Handles contracts"""

import pygame

import drawable
import sprite
import text
import settings as S

# States
S_NONE = 'not-played'
S_WON = 'won'
S_LOST = 'lost'
S_ACTIVE = 'active'


class ContractCard(drawable.Drawable):
    """Represents a contract card"""

    def __init__(self, card, x=0, y=0):
        """Initialise the card"""
        #
        self.face = sprite.Sprite(card.picture, S.Contract.image_offset[0], S.Contract.image_offset[1])
        self.base_width, self.base_height = w, h = S.Contract.size
        #
        surface = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        #
        super(ContractCard, self).__init__(x, y, surface=surface, name=card.name)
        #
        self.contract_won = sprite.Sprite(S.Contract.won_image, self.width / 2, self.height / 2)
        self.contract_lost = sprite.Sprite(S.Contract.lost_image, self.width / 2, self.height / 2)
        self.contract_active = sprite.Sprite(S.Contract.active_image, self.width / 2, self.height / 2)
        self.state = S_NONE
        #
        self.items = drawable.DrawableGroup([self.face])
        self.card = card
        self.createCardImage()

    def createCardImage(self):
        """Create the image of the card"""
        w, h = self.base_width, self.base_height
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        #
        if self.state == S_ACTIVE:
            self.contract_active.renderTo(self.surface)
        self.items.renderTo(self.surface)
        if self.state == S_WON:
            self.contract_won.renderTo(self.surface)
        elif self.state == S_LOST:
            self.contract_lost.renderTo(self.surface)
        #
        # Rescale
        self.surface = pygame.transform.scale(self.surface, (int(w * S.Contract.scale), int(h * S.Contract.scale)))
        self.width, self.height = self.surface.get_size()

    def setState(self, state):
        """Set the state"""
        self.state = state
        self.createCardImage()

