"""Represents cards that get displayed on the screen"""

import os
import pygame
import textwrap

import drawable
import sprite
import text
import settings as S


class Card(drawable.Drawable):
    """Represents a card"""

    def __init__(self, card_type, name, description, picture, hp, dp, x=0, y=0):
        """Initialise the card"""
        self.card_type = card_type
        self.name = name
        self.description = description
        self.picture = picture
        self.hp = hp
        self.dp = dp
        #
        self.front_card = sprite.Sprite(S.Card.front_image % card_type)
        self.back_card = sprite.Sprite(S.Card.back_image)
        self.name_text = text.Text(
            S.Card.name_offset[0], S.Card.name_offset[1], name,
            S.Card.name_font, S.Card.name_colour
        )
        self.description_text = text.Text(
            S.Card.description_offset[0], S.Card.description_offset[1], description,
            S.Card.description_font, S.Card.description_colour,
            line_height=S.Card.description_line_height,
            pad_bottom=S.Card.description_pad_bottom,
            anchor=drawable.A_TOP_MIDDLE
        )
        self.hp_text = text.Text(
            S.Card.hp_offset[0], S.Card.hp_offset[1], '%s' % hp,
            S.Card.hp_font, S.Card.hp_colour
        )
        self.dp_text = text.Text(
            S.Card.dp_offset[0], S.Card.dp_offset[1], '%s' % dp,
            S.Card.dp_font, S.Card.dp_colour
        )
        self.image = sprite.Sprite(picture, S.Card.picture_offset[0], S.Card.picture_offset[1])
        w, h = self.front_card.width, self.front_card.height
        self.front_card.x, self.front_card.y = w / 2, h / 2
        self.back_card.x, self.back_card.y = w / 2, h / 2
        #
        # Greying and highlighting
        self.highlighted_image = sprite.Sprite(S.Card.highlight_image, w / 2, h / 2)
        self.greyed_image = sprite.Sprite(S.Card.grey_image, w / 2, h / 2)
        #
        surface = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        #
        super(Card, self).__init__(x, y, self.front_card.width, surface=surface, name=name)
        #
        self.face_up = True
        self.selected = False
        self.greyed = False
        #
        self.face_up_objects = drawable.DrawableGroup([
            self.front_card, self.image, self.name_text, self.description_text, self.hp_text, self.dp_text,
        ])
        self.face_down_objects = drawable.DrawableGroup([self.back_card])
        #
        self.createCardImage()

    def createCardImage(self):
        """Create the image of the card"""
        if self.face_up:
            self.face_up_objects.renderTo(self.surface)
        else:
            self.face_down_objects.renderTo(self.surface)
        if self.selected:
            self.highlighted_image.renderTo(self.surface)
        if self.greyed:
            self.greyed_image.renderTo(self.surface)

    def setSelected(self, state):
        """Set the selected state"""
        #
        # Disabling this for initial release
        #self.selected = state
        #self.createCardImage()

    def setGreyed(self, state):
        """Set the greyed state"""
        self.greyed = state
        self.createCardImage()

    def setFaceUp(self, state):
        """Set the face up state"""
        self.face_up = state
        self.createCardImage()

    def handleClick(self, event_type):
        """Handle that we are clicked"""
        if not self.greyed:
            self.setSelected(not self.selected)
            return self


class CardCollection(list):
    """A collection of cards"""

    def setFaceUp(self, state):
        """Set the face up state"""
        for card in self:
            card.setFaceUp(state)


class CardSet(dict):
    """A set of cards"""

    def getAllCards(self):
        """Return all the cards"""
        cards = []
        for item in self.values():
            cards.extend(item)
        return cards

    def setVisible(self, state):
        """Set the visible state"""
        for card in self.getAllCards():
            card.visible = False


def getCollections(filename):
    """Return all the collections of cards"""
    with file(os.path.join('data', filename), 'r') as f:
        raw_text = f.read()
        collection = CardSet()
        for line in raw_text.splitlines():
            card_type, name, description, picture, dp, hp = line.split('\t')
            #
            # Wrap description
            description_wrapped = '\n'.join(textwrap.wrap(description, S.Card.description_max_chars))
            collection.setdefault(card_type.lower(), CardCollection()).append(Card(
                card_type.lower(), name, description_wrapped, picture, int(hp), int(dp)
            ))
    return collection