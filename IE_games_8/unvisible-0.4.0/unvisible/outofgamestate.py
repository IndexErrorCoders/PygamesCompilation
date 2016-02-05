"""Display state that is out of the game"""

import random
import pygame

import states
import drawable
import slots
import card
import sound
import text
import button
import common
import sprite
import settings as S


# Buttons
B_START = 'start-button'
B_RESUME = 'start-resume'
B_CARDS = 'cards-button'
B_BACK = 'back-button'
B_RULES = 'rules-button'
B_NEXT = 'next-button'
B_PREVIOUS = 'previous-button'
B_QUIT = 'quit-button'
B_CREDITS = 'credits-button'

# States
S_START_SCREEN = 'start_screen'
S_HELP_SCREEN = 'help_screen'
S_CARDS_SCREEN = 'cards_screen'
S_CREDITS_SCREEN = 'credits_screen'
S_PLAY_GAME = 'play_game'
S_GAME_SCREEN = 'game_screen'
S_NEW_GAME = 'new_game'
S_QUIT = 'quit'


class OutOfGame(states.StateMachine):
    """Controls the state when not inside the game"""

    verbose = False

    def __init__(self, speed=1):
        """Initialise the state"""
        super(OutOfGame, self).__init__(S_START_SCREEN, speed)
        self.sound_flip_card = sound.Sounds.getSound('240776__f4ngy__card-flip.wav')

    def initUI(self):
        """Initialise the UI"""
        self.background = drawable.DrawableGroup([
            sprite.Sprite('bare-table.png', S.Screen.width / 2, S.Screen.height / 2),
            sprite.Sprite('logo.png', S.StartScreen.logo_position[0], S.StartScreen.logo_position[1]),
            sprite.Sprite('sub-logo.png', S.StartScreen.sub_logo_position[0], S.StartScreen.sub_logo_position[1]),
        ])
        #
        self.resume_button = button.Button('resume-button.png', S.StartScreen.resume_button_position[0], S.StartScreen.resume_button_position[1], name=B_RESUME)
        self.resume_button.visible = False
        #
        self.buttons = drawable.DrawableGroup([
            button.Button('play-button.png', S.StartScreen.play_button_position[0], S.StartScreen.play_button_position[1], name=B_START),
            self.resume_button,
            button.Button('rules-button.png', S.StartScreen.rules_button_position[0], S.StartScreen.rules_button_position[1], name=B_RULES),
            button.Button('cards-button.png', S.StartScreen.cards_button_position[0], S.StartScreen.cards_button_position[1], name=B_CARDS),
        ])
        # Buttons on the cards screen
        self.cards = card.getCollections('cards.txt')
        self.card_display_buttons = drawable.DrawableGroup()
        self.cards_buttons = slots.HorizontalItemSlots(*S.CardDisplay.button_slots)
        names = self.cards.keys()
        names.sort()
        self.show_cards = 'mark'
        for name in names:
            new_button = button.OnOffButton('%s-button.png' % name, name=name)
            self.cards_buttons.addItem(new_button)
            self.card_display_buttons.append(new_button)
            if name == self.show_cards:
                self.selected_button = new_button
                new_button.setState(True)
        #
        self.card_slot_1 = slots.HorizontalItemSlots(*S.CardDisplay.card_slot_1)
        self.card_slot_2 = slots.HorizontalItemSlots(*S.CardDisplay.card_slot_2)
        self.card_slots = drawable.DrawableGroup([
            self.card_slot_1, self.card_slot_2
        ])
        #
        self.back_button = button.Button(
            'back-button.png',
            S.CardDisplay.back_button_position[0], S.CardDisplay.back_button_position[1]
        )
        self.card_display_buttons.append(self.back_button)
        #
        self.credits_button = button.Button(
            'credits-button.png',
            S.StartScreen.credits_button_position[0], S.StartScreen.credits_button_position[1]
        )
        self.buttons.append(self.credits_button)
        self.credits_buttons = drawable.DrawableGroup([
            self.back_button,
        ])
        self.credits_details = sprite.Sprite('credits.png', S.Screen.width / 2, S.Screen.height / 2)
        #
        self.quit_button = button.Button(
            'quit-button.png',
            S.StartScreen.quit_button_position[0], S.StartScreen.quit_button_position[1]
        )
        self.buttons.append(self.quit_button)
        #
        self.next_button = button.Button('next-page-button.png', S.StartScreen.next_button_position[0], S.StartScreen.next_button_position[1], name=B_NEXT)
        self.previous_button = button.Button('previous-page-button.png', S.StartScreen.previous_button_position[0], S.StartScreen.previous_button_position[1], name=B_PREVIOUS)
        self.help_buttons = drawable.DrawableGroup([
            self.back_button,
            self.next_button,
            self.previous_button,
        ])
        self.help_text = sprite.Sprite('instructions-1.png', S.StartScreen.text_position[0], S.StartScreen.text_position[1])
        #
        self.display_slots = slots.HorizontalItemSlots(*S.StartScreen.display_slots)
        self.all_cards = self.cards.getAllCards()
        for slot in self.display_slots.slots:
            slot.addItem(random.choice(self.all_cards))
        #
        self.click = sound.Sounds.getSound(S.Sounds.click)
        self.version = text.Text(
            S.StartScreen.version_text_position[0], S.StartScreen.version_text_position[1],
            'V%s %s %s' % tuple(common.__version__.split('.')), S.VersionFont.font,
            S.VersionFont.colour
        )
        self.credit = text.Text(
            S.StartScreen.credit_text_position[0], S.StartScreen.credit_text_position[1],
            'A    pyweek   19   game   by   Paul   Paterson', S.CreditFont.font,
            S.CreditFont.colour
        )
        #
        self.background.append(self.version)
        self.background.append(self.credit)

    def processClick(self, event_type, (x, y)):
        """Process clicks"""
        if self.state == S_START_SCREEN:
            return self.buttons.processClick(event_type, (x, y))
        elif self.state == S_CARDS_SCREEN:
            return self.card_display_buttons.processClick(event_type, (x, y))
        elif self.state == S_HELP_SCREEN:
            return self.help_buttons.processClick(event_type, (x, y))
        elif self.state == S_CREDITS_SCREEN:
            return self.credits_buttons.processClick(event_type, (x, y))

    def processKey(self, key):
        """Process a key press"""
        if key == pygame.K_ESCAPE:
            if self.state == S_START_SCREEN:
                return pygame.QUIT
            else:
                self.state = S_START_SCREEN

    def renderTo(self, screen):
        """Render this state"""
        self.background.renderTo(screen)
        if self.state == S_START_SCREEN:
            self.buttons.renderTo(screen)
            self.display_slots.renderTo(screen)
        elif self.state == S_CARDS_SCREEN:
            self.card_display_buttons.renderTo(screen)
            self.card_slots.renderTo(screen)
        elif self.state == S_HELP_SCREEN:
            self.help_buttons.renderTo(screen)
            self.help_text.renderTo(screen)
        elif self.state == S_CREDITS_SCREEN:
            self.credits_buttons.renderTo(screen)
            self.credits_details.renderTo(screen)

    def start_screen(self):
        """Showing the start screen"""
        countdown = random.uniform(*S.StartScreen.display_frequency)
        self.clock = pygame.time.Clock()
        while not self.clicked_on:
            #
            # Change cards on a certain frequency
            self.clock.tick()
            countdown -= self.clock.get_time()
            if countdown <= 0:
                self.sound_flip_card.play()
                random.choice(self.display_slots.slots).addItem(random.choice(self.all_cards))
                countdown = random.uniform(*S.StartScreen.display_frequency)
            #
            yield 0
        self.log.debug('Clicked on start screen item')
        if self.clicked_on.name == B_START:
            self.state = S_NEW_GAME
            self.click.play()
            sound.Sounds.playMusic(S.Music.game_music)
        elif self.clicked_on.name == B_RESUME:
            self.state = S_GAME_SCREEN
            self.click.play()
            sound.Sounds.playMusic(S.Music.game_music)
        elif self.clicked_on.name == B_CARDS:
            self.state = S_CARDS_SCREEN
            self.click.play()
        elif self.clicked_on.name == B_RULES:
            self.state = S_HELP_SCREEN
            self.click.play()
        elif self.clicked_on.name == B_QUIT:
            self.state = S_QUIT
        elif self.clicked_on.name == B_CREDITS:
            self.state = S_CREDITS_SCREEN

    def cards_screen(self):
        """Showing the cards screen"""
        #
        # Show cards
        for new_card in self.cards[self.show_cards]:
            slot = self.card_slot_1 if self.card_slot_1.hasFreeSlot() else self.card_slot_2
            slot.addItem(new_card)
            yield S.CardDisplay.add_card_time
        #
        while not self.clicked_on:
            yield 0
        self.click.play()
        #
        # Switch display
        self.card_slot_1.removeAll()
        self.card_slot_2.removeAll()
        if self.clicked_on.name == B_BACK:
            self.state = S_START_SCREEN
        else:
            self.selected_button.setState(False)
            self.selected_button = self.clicked_on
            self.clicked_on.setState(True)
            self.show_cards = self.clicked_on.name

    def help_screen(self):
        """Show the help screens"""
        current_page = 1
        while True:
            #
            # Button visibility
            self.previous_button.visible = current_page > 1
            self.next_button.visible = current_page < S.StartScreen.max_pages
            #
            if self.clicked_on:
                self.click.play()
                if self.clicked_on.name == B_BACK:
                    self.state = S_START_SCREEN
                    break
                elif self.clicked_on.name == B_NEXT:
                    current_page += 1
                elif self.clicked_on.name == B_PREVIOUS:
                    current_page -= 1
                current_page = max(1, min(current_page, S.StartScreen.max_pages))
                self.help_text.surface = self.help_text.loadImage('instructions-%d.png' % current_page)
            #
            yield 0

    def credits_screen(self):
        """Show the credits screen"""
        while True:
            if self.clicked_on and self.clicked_on.name == B_BACK:
                self.state = S_START_SCREEN
                break
            yield 0