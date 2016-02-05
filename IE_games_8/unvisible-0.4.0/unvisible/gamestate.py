"""Manages the state of the game"""

import random
import pygame
import math

import drawable
import states
import slots
import card
import sound
import text
import dice
import button
import contract
import sprite
import outofgamestate
import gauge
import  common
import settings as S


# Buttons
B_PASS_BUTTON = 'pass-button'
B_CONTINUE_BUTTON = 'continue-button'
B_EXIT_BUTTON = 'exit-button'
B_PLAY_AGAIN_BUTTON = 'play-again-button'
B_ROLL_DICE_BUTTON = 'roll-dice-button'
B_GAME_COMPLETE_BUTTON = 'game-complete-button'

# States
S_SETUP_START = 'setup_start'
S_SETUP_SHUFFLING_CARDS = 'setup_shuffling_cards'
S_SETUP_DEALING_CONTACTS = 'setup_dealing_contacts'
S_SETUP_DEALING_PLAYER_HAND = 'setup_dealing_player_hand'
S_SETUP_DEALING_COMPUTER_HAND = 'setup_dealing_computer_hand'
S_SETUP_PICK_NEXT_CONTACT = 'setup_pick_next_contact'
S_SETUP_CHOOSING_LOCATION = 'setup_choosing_location'
S_SETUP_CHOOSING_WEAPON = 'setup_choosing_weapon'
S_SETUP_PLAYING_DEFENSIVE = 'setup_playing_defensive'
S_ATTACKING_ATTACK_1 = 'attacking_attack_1'
S_ATTACKING_DEFENSE_1 = 'attacking_defense_1'
S_ATTACKING_ATTACK_2 = 'attacking_attack_2'
S_ATTACKING_DEFENSE_2 = 'attacking_defense_2'
S_REVEAL_DEFENSIVE_CARD = 'reveal_defensive_card'
S_REVEAL_SUM_HP = 'reveal_sum_hp'
S_REVEAL_SUM_DP = 'reveal_sum_dp'
S_ATTEMPT_ROLL_DICE = 'attempt_roll_dice'
S_ATTEMPT_SUM_DICE = 'attempt_sum_dice'
S_ATTEMPT_CONTRACT_RESULT = 'attempt_contract_result'
S_DETECTION_ROLL_DICE = 'detection_roll_dice'
S_DETECTION_SUM_DICE = 'detection_sum_dice'
S_DETECTION_DETECTION_RESULT = 'detection_detection_result'
S_WAITING_CONTINUE_CONFIRMATION = 'waiting_continue_confirmation'
S_REDRAW_LOCATION_CARD = 'redraw_location_card'
S_REDRAW_WEAPON_CARD = 'redraw_weapon_card'
S_REDRAW_ATTACKING_CARD = 'redraw_attacking_card'
S_REDRAW_DEFENSIVE_CARD = 'redraw_defensive_card'
S_REDRAW_POLICEMAN_CARD = 'redraw_policeman_card'
S_GAME_OVER = 'game_over'


class GameState(states.StateMachine):
    """Manages the game state"""

    def __init__(self, other_screens, speed_factor=1):
        """Initialise the state"""
        self.board_totals = {}
        self.other_screens = other_screens
        #
        self.all_cards = card.getCollections('cards.txt')
        self.sound_play_card = sound.Sounds.getSound('240777__f4ngy__dealing-card.wav')
        self.sound_flip_card = sound.Sounds.getSound('240776__f4ngy__card-flip.wav')
        self.sound_click = sound.Sounds.getSound('215772__otisjames__click.wav')
        self.sound_increase = sound.Sounds.getSound('173000__keykrusher__bicycle-bell-2.wav')
        self.sound_decrease = sound.Sounds.getSound('173000__keykrusher__bicycle-bell-2-reverse.wav')
        self.sound_reset = sound.Sounds.getSound('238286__meroleroman7__clip.wav')
        self.sound_instruction = sound.Sounds.getSound('115363__theditor__drop.wav')
        self.sound_dice = sound.Sounds.getSound('185985__2bach__dice-6-shake-fast-in-cup.wav')
        self.sound_success = sound.Sounds.getSound('242501__gabrielaraujo__powerup-success.wav')
        self.sound_failure = sound.Sounds.getSound('66695__mad-monkey__power08.wav')
        self.sound_capture = sound.Sounds.getSound('165331__ani-music__tubular-bell-of-death.wav')
        self.sound_dealer = sound.Sounds.getSound('165206__metaepitome__water-drop-sound.wav')
        #
        super(GameState, self).__init__(S_SETUP_START, speed_factor)

    def pickCardOfType(self, card_type):
        #
        # Highlight location cards
        for slot in self.hitman_slots.slots:
            if slot.isOccupied():
                if slot.item.card_type != card_type:
                    slot.item.setGreyed(True)
        #
        while self.clicked_on is None:
            yield 0
        #
        if self.clicked_on.name == B_PASS_BUTTON:
            self.log.info('Clicked on the pass button')
            self.last_pick = None
        else:
            self.log.info('Chose card %s' % self.clicked_on.name)
            self.hitman_slots.removeItem(self.clicked_on)
            self.hitman_play_slots.addItem(self.clicked_on)
            self.clicked_on.setSelected(False)
            self.last_pick = self.clicked_on
        #
        for slot in self.hitman_slots.slots:
            if slot.isOccupied():
                slot.item.setGreyed(False)

    def sumCardTotals(self, total_type):
        """Sum the card totals"""
        self.board_totals[total_type] = 0
        for slot in self.hitman_play_slots.slots + self.mark_play_slots.slots[1:]:
            if slot.isOccupied():
                increase = getattr(slot.item, total_type)
                if increase:
                    self.incrementTotal(total_type, increase)
                    yield 1000
        yield 1000

    def incrementTotal(self, total_type, delta):
        """Increment on of the board totals"""
        self.board_totals[total_type] += delta
        getattr(self, '%s_board' % total_type).setText(
            '%d' % self.board_totals[total_type]
        )

    def sumDice(self, slots, total_type, colour):
        """Sum the dice that have been rolled"""
        for slot in slots:
            if slot.item.colour == colour:
                for i in range(slot.item.value):
                    for result in self.increaseGauge(total_type, getattr(self, '%s_gauge' % total_type), 1):
                        yield result
                yield 1000
        yield 1000

    def initUI(self):
        """Initialise the UI"""
        #
        # Every card
        self.every_card = self.all_cards.getAllCards()[:]
        #
        # Slots for cards
        self.hitman_slots = slots.HorizontalItemSlots(*S.Board.hitman_slots)
        #
        self.mark_slots = slots.HorizontalItemSlots(*S.Board.mark_slots)
        self.mark_slots.visible = False
        #
        self.hitman_play_slots = slots.PositionedSlots(*S.Board.hitman_play_slots)
        self.mark_play_slots = slots.PositionedSlots(*S.Board.mark_play_slots)
        #
        # Slots for dice
        self.hitman_dice_slots = dice.DiceSlots(*S.Board.hitman_dice_slots)
        self.mark_dice_slots = dice.DiceSlots(*S.Board.mark_dice_slots)
        #
        # The contract display
        self.contracts = slots.PositionedSlots(*S.Board.contract_slots)
        #
        # The policemen display
        self.policemen_display = slots.PositionedSlots(*S.Board.policemen_slots)
        #
        self.card_slots = drawable.DrawableGroup([
            self.hitman_slots, self.hitman_play_slots,
            self.mark_slots, self.mark_play_slots,
            self.contracts, self.policemen_display,
        ])
        #
        # Add the dice
        for i in range(S.Board.num_hitman_dice):
            self.hitman_dice_slots.addItem(dice.Dice())
        for i in range(S.Board.num_mark_dice):
            self.hitman_dice_slots.addItem(dice.Dice(colour='black'))
        self.dice = drawable.DrawableGroup([self.hitman_dice_slots, self.mark_dice_slots])
        #
        # Hide the dice until we need them
        self.hitman_dice_slots.visible = False
        self.mark_dice_slots.visible = False
        #
        # Buttons
        self.buttons = drawable.DrawableGroup()
        self.pass_button = button.Button(
            'pass-button.png',
            x=S.Board.pass_button_position[0],
            y=S.Board.pass_button_position[1],
            name=B_PASS_BUTTON
        )
        self.pass_button.visible = False
        #
        self.continue_button = button.Button(
            'continue-button.png',
            x=S.Board.continue_button_position[0],
            y=S.Board.continue_button_position[1],
            name=B_CONTINUE_BUTTON
        )
        self.continue_button.visible = False
        #
        self.exit_button = button.Button(
            'exit-button.png',
            x=S.Board.exit_button_position[0],
            y=S.Board.exit_button_position[1],
            name=B_EXIT_BUTTON
        )
        #
        self.play_again_button = button.Button(
            'play-again-button.png',
            x=S.Board.play_again_button_position[0],
            y=S.Board.play_again_button_position[1],
            name=B_PLAY_AGAIN_BUTTON
        )
        self.play_again_button.visible = False
        #
        self.roll_dice_button = button.Button(
            'roll-dice-button.png',
            x=S.Board.roll_dice_button_position[0],
            y=S.Board.roll_dice_button_position[1],
            name=B_ROLL_DICE_BUTTON
        )
        self.roll_dice_button.visible = False
        #
        self.game_complete_button = button.Button(
            'game-complete-button.png',
            x=S.Board.game_complete_button_position[0],
            y=S.Board.game_complete_button_position[1],
            name=B_GAME_COMPLETE_BUTTON
        )
        self.game_complete_button.visible = False
        #
        self.buttons.extend([
            self.pass_button, self.continue_button, self.exit_button,
            self.play_again_button, self.roll_dice_button,
            self.game_complete_button,
        ])
        #
        self.all_cards.setVisible(False)
        for deck in self.all_cards.values():
            random.shuffle(deck)
        #
        self.hitman_hand = card.CardCollection()
        #
        # Put cards into the hands
        for i in range(S.StartingHands.hit_man_locations):
            self.hitman_hand.append(self.all_cards['location'].pop())
        for i in range(S.StartingHands.hit_man_weapons):
            self.hitman_hand.append(self.all_cards['weapon'].pop())
        for i in range(S.StartingHands.hit_man_attacking):
            self.hitman_hand.append(self.all_cards['offensive'].pop())
        #
        # Contracts
        for i in range(len(self.contracts.slots)):
            self.contracts.addItem(contract.ContractCard(
                self.all_cards['mark'].pop()
            ))
        self.current_contract = 0
        #
        self.mark_hand = card.CardCollection()
        #
        for i in range(S.StartingHands.mark_defending):
            self.mark_hand.append(self.all_cards['defensive'].pop())
        #
        self.hitman_hand.setFaceUp(True)
        self.mark_hand.setFaceUp(False)
        #
        # Text items
        self.hp_target = text.Text(
            S.UIText.hp_target_position[0], S.UIText.hp_target_position[1],
            ' ', S.UIText.hp_target_font.font, S.UIText.hp_target_font.colour,
            anchor=drawable.A_LEFT_MIDDLE,
        )
        self.hp_target.visible = False
        #
        self.dp_max = text.Text(
            S.UIText.dp_max_position[0], S.UIText.dp_max_position[1],
            ' ', S.UIText.dp_max_font.font, S.UIText.dp_max_font.colour,
            anchor=drawable.A_LEFT_MIDDLE,
        )
        self.dp_max.visible = False
        #
        self.hp_board = text.Text(
            S.UIText.hp_board_position[0], S.UIText.hp_board_position[1],
            ' ', S.UIText.hp_board_font.font, S.UIText.hp_board_font.colour,
            anchor=drawable.A_LEFT_MIDDLE,
        )
        self.dp_board = text.Text(
            S.UIText.dp_board_position[0], S.UIText.dp_board_position[1],
            ' ', S.UIText.dp_board_font.font, S.UIText.dp_board_font.colour,
            anchor=drawable.A_LEFT_MIDDLE,
        )
        self.contract_result = text.Text(
            S.UIText.result_position[0], S.UIText.result_position[1],
            'Won the contract!', S.UIText.result_font.font, S.UIText.result_font.colour,
        )
        self.contract_result.visible = False
        self.detection_result = text.Text(
            S.UIText.detection_position[0], S.UIText.detection_position[1],
            'Not detected!', S.UIText.detection_font.font, S.UIText.detection_font.colour,
        )
        self.detection_result.visible = False
        #
        # Instructions to the user
        self.instructions_text = text.Text(
            S.UIText.instructions_text_position[0], S.UIText.instructions_text_position[1],
            'Pick a location card', S.UIText.instructions_text_font.font, S.UIText.instructions_text_font.colour,
        )
        self.instructions_back = sprite.Sprite(
            'instructions-back.png',
            S.UIText.instructions_text_position[0], S.UIText.instructions_text_position[1]
        )
        self.instructions = drawable.DrawableGroup([
            self.instructions_back, self.instructions_text,
        ])
        self.instructions.visible = False
        #
        # Indications on what the dealer is doing
        self.dealer_text = text.Text(
            S.UIText.dealer_text_position[0], S.UIText.dealer_text_position[1],
            'Pick a location card', S.UIText.dealer_text_font.font, S.UIText.dealer_text_font.colour,
        )
        self.dealer_back = sprite.Sprite(
            'dealer-back.png',
            S.UIText.dealer_text_position[0], S.UIText.dealer_text_position[1]
        )
        self.dealer = drawable.DrawableGroup([
            self.dealer_back, self.dealer_text,
        ])
        self.dealer.visible = False
        #
        self.version = text.Text(
            S.UIText.version_text_position[0], S.UIText.version_text_position[1],
            'V%s %s %s' % tuple(common.__version__.split('.')), S.VersionFont.font,
            S.VersionFont.colour
        )
        #
        self.ui = drawable.DrawableGroup()
        self.ui.extend([
            self.hp_target, self.dp_max, self.hp_board, self.dp_board,
            self.contract_result, self.detection_result,
            self.instructions, self.dealer,
            self.buttons,
            self.version,
        ])
        #
        self.background = drawable.DrawableGroup([
            sprite.Sprite('table.png', S.Screen.width / 2, S.Screen.height / 2),
        ])
        #
        # Gauges
        self.hp_gauge = gauge.Gauge(
            S.Board.hp_gauge_position[0], S.Board.hp_gauge_position[1],
            0, 0,
            'gauge-black-blank.png', 'gauge-black-filled.png',
            'gauge-black-grey.png', 'gauge-black-target.png',
            'gauge-black-target-filled.png',
            S.Board.hp_gauge_number, S.Board.hp_gauge_gap,
            'hp-gauge',
        )
        #
        self.dp_gauge = gauge.Gauge(
            S.Board.dp_gauge_position[0], S.Board.dp_gauge_position[1],
            0, 0,
            'gauge-blank.png', 'gauge-filled.png',
            'gauge-grey.png', 'gauge-target.png',
            'gauge-target-filled.png',
            S.Board.dp_gauge_number, S.Board.dp_gauge_gap,
            'dp-gauge',
        )
        self.gauges = drawable.DrawableGroup([
            self.hp_gauge, self.dp_gauge,
        ])
        #
        self.contract_won = sprite.Sprite(
            'contract-successful.png',
            S.Board.contract_result_position[0], S.Board.contract_result_position[1],
        )
        self.contract_won.visible = False
        self.ui.append(self.contract_won)
        #
        self.contract_failed = sprite.Sprite(
            'contract-failed.png',
            S.Board.contract_result_position[0], S.Board.contract_result_position[1],
        )
        self.contract_failed.visible = False
        self.ui.append(self.contract_failed)
        #
        self.hit_detected = sprite.Sprite(
            'hit-detected.png',
            S.Board.contract_result_position[0], S.Board.contract_result_position[1],
        )
        self.hit_detected.visible = False
        self.ui.append(self.hit_detected)
        #
        self.clickables = drawable.DrawableGroup()
        self.clickables.extend(self.every_card)
        self.clickables.extend(self.buttons)

    def renderTo(self, screen):
        """Render this state to the screen"""
        self.background.renderTo(screen)
        self.gauges.renderTo(screen)
        self.card_slots.renderTo(screen)
        self.dice.renderTo(screen)
        self.ui.renderTo(screen)

    def processClick(self, event_type, (x, y)):
        """Process click events"""
        self.log.debug('Clicked on something')
        clicked_card = self.clickables.processClick(event_type, (x, y))
        #
        # Only allow clicking on cards in the hand
        if isinstance(clicked_card, button.Button):
            return clicked_card
        else:
            for slot in self.hitman_slots.slots:
                if slot.isOccupied() and slot.item == clicked_card:
                    return clicked_card
            else:
                return None

    def processKey(self, key):
        """Process a key press"""
        if key == pygame.K_ESCAPE:
            self.returnToStart()

    def increaseGauge(self, total_type, target_gauge, increase):
        """Increase the gauge score"""
        for i in range(abs(increase)):
            delta = math.copysign(1, increase)
            if delta > 0:
                self.sound_increase.play()
            else:
                self.sound_decrease.play()
            self.incrementTotal(total_type, delta)
            target_gauge.value = min(S.Board.hp_gauge_number, target_gauge.value + delta)
            if increase > 0:
                target_gauge.showSlot(int(target_gauge.value))
            else:
                target_gauge.showSlot(int(target_gauge.value) + 1)
            yield 500

    def showInstructions(self, text):
        """Show the instructions"""
        self.instructions_text.setText(text)
        self.instructions_text.x = S.UIText.instructions_text_position[0] + 50
        self.instructions.visible = True
        self.sound_instruction.play()

    def updateState(self, clicked_on):
        """Update state"""
        if clicked_on and clicked_on.name == B_EXIT_BUTTON:
            self.returnToStart()
            self.sound_click.play()
        else:
            super(GameState, self).updateState(clicked_on)

    def hideInstructions(self):
        """Hide the instructions"""
        self.instructions.visible = False

    def returnToStart(self):
        """Return to the start menu"""
        self.other_screens.state = outofgamestate.S_START_SCREEN
        self.other_screens.resume_button.visible = True
        sound.Sounds.playMusic(S.Music.start_music)

    def showDealer(self, text):
        """Show the dealer actions"""
        self.dealer_text.setText(text)
        self.dealer_text.x = S.UIText.dealer_text_position[0] - 50
        self.dealer.visible = True
        self.sound_dealer.play()

    def hideDealerAction(self):
        """Hide the dealer action"""
        self.dealer.visible = False

    def setup_start(self):
        """Start of the setup"""
        self.state = S_SETUP_DEALING_PLAYER_HAND
        yield 0

    def setup_dealing_player_hand(self):
        """Deal the players hand"""
        for next_card in self.hitman_hand:
            self.hitman_slots.addItem(next_card)
            self.sound_play_card.play()
            yield 200
        self.state = S_SETUP_DEALING_COMPUTER_HAND
        yield 1000

    def setup_dealing_computer_hand(self):
        """Deal the computer hand"""
        for next_card in self.mark_hand:
            self.mark_slots.addItem(next_card)
            self.sound_play_card.play()
            yield 200
        self.state = S_SETUP_PICK_NEXT_CONTACT
        yield 1000

    def setup_pick_next_contact(self):
        """Pick the next contact"""
        self.board_totals['hp'] = 0
        self.board_totals['dp'] = 0
        #
        self.showDealer('New contract ')
        yield S.Timing.dealer_action
        #
        self.target_card = self.contracts.slots[self.current_contract].item.card
        self.mark_play_slots.addItem(self.target_card)
        self.sound_play_card.play()
        self.hp_target.setText(str(self.target_card.hp))
        self.dp_max.setText(str(self.target_card.dp))
        self.contracts.slots[self.current_contract].item.setState(contract.S_ACTIVE)
        #
        yield S.Timing.short_delay
        self.showDealer('New contract    %s' % self.target_card.name)
        #
        self.hp_gauge.value = 0
        self.hp_gauge.target = self.target_card.hp
        for i in range(1, self.hp_gauge.number + 1):
            self.hp_gauge.showSlot(i)
            if i <= self.hp_gauge.target:
                self.sound_reset.play()
            yield 100
        #
        #
        # Policemen points
        self.log.debug('Adding policemen points')
        total_policeman = 0
        for slot in self.policemen_display.slots:
            if slot.isOccupied():
                self.log.debug('Policemen present')
                total_policeman += slot.item.dp
        #
        self.dp_gauge.value = total_policeman
        self.incrementTotal('dp', total_policeman)
        self.incrementTotal('hp', 0)
        self.dp_gauge.target = self.target_card.dp
        for i in range(1, self.dp_gauge.number + 1):
            self.dp_gauge.showSlot(i)
            if i <= self.dp_gauge.target:
                self.sound_reset.play()
            yield 100
        #
        yield S.Timing.after_dealer_action
        self.hideDealerAction()
        #
        self.state = S_SETUP_CHOOSING_LOCATION

    def setup_choosing_location(self):
        """User is choosing a location"""
        self.showInstructions('Pick a location')
        for result in self.pickCardOfType('location'):
            yield result
        self.hideInstructions()
        card = self.clicked_on
        self.sound_flip_card.play()
        for result in self.increaseGauge('hp', self.hp_gauge, card.hp):
            yield result
        for result in self.increaseGauge('dp', self.dp_gauge, card.dp):
            yield result
        self.state = S_SETUP_CHOOSING_WEAPON

    def setup_choosing_weapon(self):
        """User is choosing a weapon"""
        self.showInstructions('Pick a weapon')
        for result in self.pickCardOfType('weapon'):
            yield result
        self.hideInstructions()
        card = self.clicked_on
        self.sound_flip_card.play()
        for result in self.increaseGauge('hp', self.hp_gauge, card.hp):
            yield result
        for result in self.increaseGauge('dp', self.dp_gauge, card.dp):
            yield result
        self.state = S_SETUP_PLAYING_DEFENSIVE

    def setup_playing_defensive(self):
        """Play a defensive card at the beginning of the game"""
        #
        self.showDealer('Dealer choosing defensive card')
        yield S.Timing.dealer_action
        #
        played_card = self.mark_slots.getItem()
        self.mark_slots.removeItem(played_card)
        self.mark_play_slots.addItem(played_card)
        self.sound_play_card.play()
        self.clicked_on = played_card
        #
        yield S.Timing.after_dealer_action
        self.hideDealerAction()
        #
        self.state = S_ATTACKING_ATTACK_1

    def attacking_attack_1(self):
        """First go at playing an attack card"""
        self.showInstructions('Round 1 Pick attack')
        self.pass_button.visible = True
        for result in self.pickCardOfType('offensive'):
            yield result
        self.hideInstructions()
        card = self.clicked_on
        if card.name != B_PASS_BUTTON:
            self.sound_flip_card.play()
            for result in self.increaseGauge('hp', self.hp_gauge, card.hp):
                yield result
            for result in self.increaseGauge('dp', self.dp_gauge, card.dp):
                yield result
            # Replace card
            self.all_cards[card.card_type].insert(0, card)
        else:
            self.sound_click.play()
        self.pass_button.visible = False
        self.state = S_ATTACKING_DEFENSE_1

    def attacking_attack_2(self):
        """Second go at playing an attack card"""
        if self.hitman_slots.hasItem('offensive'):
            self.pass_button.visible = True
            self.showInstructions('Round 2 Pick attack')
            for result in self.pickCardOfType('offensive'):
                yield result
            self.hideInstructions()
            card = self.clicked_on
            if card.name != B_PASS_BUTTON:
                self.sound_flip_card.play()
                for result in self.increaseGauge('hp', self.hp_gauge, card.hp):
                    yield result
                for result in self.increaseGauge('dp', self.dp_gauge, card.dp):
                    yield result
                self.all_cards[card.card_type].insert(0, card)
            else:
                self.sound_click.play()
            self.pass_button.visible = False
        else:
            self.log.info('No cards to play')
            self.last_pick = None
        #
        if self.last_pick is None and self.mark_passed:
            self.log.info('Two passes - round over')
            self.state = S_REVEAL_DEFENSIVE_CARD
        else:
            self.state = S_ATTACKING_DEFENSE_2

    def attacking_defense_1(self):
        """First go at playing a defensive card"""
        yield 1000
        if random.random() >= S.AI.pass_probability:
            #
            self.showDealer('Dealer plays ')
            yield S.Timing.dealer_action
            #
            self.log.info('Decided to play a card')
            played_card = self.mark_slots.getItem()
            played_card.setFaceUp(True)
            #
            self.all_cards[played_card.card_type].insert(0, played_card)
            self.mark_slots.removeItem(played_card)
            self.mark_play_slots.addItem(played_card)
            self.sound_play_card.play()
            #
            self.showDealer('Dealer plays   %s' % played_card.name)
            yield S.Timing.after_dealer_action
            #
            for result in self.increaseGauge('hp', self.hp_gauge, played_card.hp):
                yield result
            for result in self.increaseGauge('dp', self.dp_gauge, played_card.dp):
                yield result
            yield 1000
            self.state = S_ATTACKING_ATTACK_2
            self.mark_passed = False
            #
            yield S.Timing.after_dealer_action
            self.hideDealerAction()
            #
        else:
            #
            self.showDealer('Dealer passes this round')
            yield S.Timing.dealer_action
            self.hideDealerAction()
            yield S.Timing.after_dealer_action
            #
            self.log.info('Decided to pass')
            self.mark_passed = True
            if self.last_pick is None:
                self.log.info('Two passes - Round over')
                self.state = S_REVEAL_DEFENSIVE_CARD
            else:
                self.state = S_ATTACKING_ATTACK_2

    def attacking_defense_2(self):
        """Second go at playing a defensive card"""
        yield 1000
        if random.random() >= S.AI.pass_probability and self.mark_slots.hasItem():
            #
            self.showDealer('Dealer plays ')
            yield S.Timing.dealer_action
            #
            played_card = self.mark_slots.getItem()
            played_card.setFaceUp(True)
            #
            self.all_cards[played_card.card_type].insert(0, played_card)
            self.mark_slots.removeItem(played_card)
            self.mark_play_slots.addItem(played_card)
            self.sound_play_card.play()
            #
            self.showDealer('Dealer plays   %s' % played_card.name)
            yield S.Timing.after_dealer_action
            #
            for result in self.increaseGauge('hp', self.hp_gauge, played_card.hp):
                yield result
            for result in self.increaseGauge('dp', self.dp_gauge, played_card.dp):
                yield result
            #
            yield S.Timing.after_dealer_action
            self.hideDealerAction()
            #
        else:
            #
            self.showDealer('Dealer decides to pass')
            yield S.Timing.dealer_action
            self.hideDealerAction()
            yield S.Timing.after_dealer_action
            #
            self.log.info('Decided to pass')
        yield 1000
        self.state = S_REVEAL_DEFENSIVE_CARD

    def reveal_defensive_card(self):
        """Reveal the defensive card"""
        self.showDealer('Dealer showing hidden card')
        yield S.Timing.dealer_action
        #
        played_card = self.mark_play_slots.slots[1].item
        played_card.setFaceUp(True)
        self.sound_flip_card.play()
        for result in self.increaseGauge('hp', self.hp_gauge, played_card.hp):
            yield result
        for result in self.increaseGauge('dp', self.dp_gauge, played_card.dp):
            yield result
        #
        yield S.Timing.after_dealer_action
        self.hideDealerAction()
        #
        self.state = S_REVEAL_SUM_HP

    def reveal_sum_hp(self):
        """Reveal the amount of HP on the board"""
        yield 0
        self.state = S_REVEAL_SUM_DP

    def reveal_sum_dp(self):
        """Reveal the amount of DP on the board"""
        yield 0
        self.state = S_ATTEMPT_ROLL_DICE

    def attempt_roll_dice(self):
        """Roll the dice"""
        self.sound_instruction.play()
        self.roll_dice_button.visible = True
        while self.clicked_on is None or self.clicked_on.name != B_ROLL_DICE_BUTTON:
            yield 0
        self.roll_dice_button.visible = False
        #
        self.hitman_dice_slots.visible = True
        self.hitman_dice_slots.rollDice()
        self.sound_dice.play()
        while self.hitman_dice_slots.isRolling():
            yield 100
        self.state = S_ATTEMPT_SUM_DICE

    def attempt_sum_dice(self):
        """Sum the dice scores"""
        for result in self.sumDice(self.hitman_dice_slots.slots, 'hp', 'white'):
            yield result
        self.state = S_ATTEMPT_CONTRACT_RESULT

    def attempt_contract_result(self):
        """Show the result of the contract"""
        if self.board_totals['hp'] >= self.target_card.hp:
            result = self.contract_won
            self.contracts.slots[self.current_contract].item.setState(contract.S_WON)
            self.sound_success.play()
        else:
            result = self.contract_failed
            self.sound_failure.play()
            self.contracts.slots[self.current_contract].item.setState(contract.S_LOST)
        result.visible = True
        yield 10000
        result.visible = False
        yield 10000
        self.state = S_DETECTION_ROLL_DICE

    def detection_roll_dice(self):
        """Roll the dice for detection"""
        yield 0
        self.state = S_DETECTION_SUM_DICE

    def detection_sum_dice(self):
        """Sum the dice scores for detection"""
        for result in self.sumDice(self.hitman_dice_slots.slots, 'dp', 'black'):
            yield result
        self.state = S_DETECTION_DETECTION_RESULT

    def detection_detection_result(self):
        """Show the result of the detection"""
        if self.board_totals['dp'] >= self.target_card.dp:
            self.hit_detected.visible = True
            self.sound_capture.play()
            yield 30000
            self.hit_detected.visible = False
            yield 1000
            self.state = S_GAME_OVER
        else:
            self.state = S_WAITING_CONTINUE_CONFIRMATION

    def waiting_continue_confirmation(self):
        """Wait for the user to click confirmation"""
        self.sound_instruction.play()
        if self.current_contract == S.Game.max_contracts - 1:
            self.log.info('Beat the game')
            self.game_complete_button.visible = True
            while not self.clicked_on or self.clicked_on.name != B_GAME_COMPLETE_BUTTON:
                yield 0
            self.returnToStart()
        else:
            self.continue_button.visible = True
            while not self.clicked_on or self.clicked_on.name != B_CONTINUE_BUTTON:
                yield 0
            #
            # Clean up the board
            self.continue_button.visible = False
            self.contract_result.visible = False
            self.detection_result.visible = False
            self.board_totals['hp'] = 0
            self.board_totals['dp'] = 0
            self.incrementTotal('hp', 0)
            self.incrementTotal('dp', 0)
            self.current_contract += 1
            #
            # Remove dice
            self.hitman_dice_slots.visible = False
            self.mark_dice_slots.visible = False
            #
            # Remove cards
            self.hitman_play_slots.removeAll()
            self.mark_play_slots.removeAll()
            #
            self.state = S_REDRAW_LOCATION_CARD

    def redraw_location_card(self):
        """Redraw a location card"""
        self.showDealer('Dealing replacement cards')
        self.sound_play_card.play()
        self.hitman_slots.addItem(self.all_cards['location'].pop())
        yield 1000
        self.state = S_REDRAW_WEAPON_CARD

    def redraw_weapon_card(self):
        """Redraw a weapon card"""
        self.sound_play_card.play()
        self.hitman_slots.addItem(self.all_cards['weapon'].pop())
        yield 1000
        self.state = S_REDRAW_ATTACKING_CARD

    def redraw_attacking_card(self):
        """Redraw a attacking card"""
        if self.hitman_slots.hasFreeSlot():
            self.sound_play_card.play()
            self.hitman_slots.addItem(self.all_cards['offensive'].pop())
            yield 1000
        else:
            self.log.info('No free slots')
        self.state = S_REDRAW_DEFENSIVE_CARD

    def redraw_defensive_card(self):
        """Redraw a defensive card"""
        for i in range(2):
            if self.mark_slots.hasFreeSlot():
                next_card = self.all_cards['defensive'].pop()
                next_card.setFaceUp(False)
                self.mark_slots.addItem(next_card)
                yield 1000
            else:
                self.log.info('No free slots')
        #
        yield S.Timing.after_dealer_action
        self.hideDealerAction()
        self.state = S_REDRAW_POLICEMAN_CARD

    def redraw_policeman_card(self):
        """Redraw a new policeman card"""
        #
        if self.policemen_display.hasFreeSlot():
            self.showDealer('Adding detective ')
            yield S.Timing.dealer_action
            detective = self.all_cards['policeman'].pop()
            self.policemen_display.addItem(detective)
            self.showDealer('Adding detective   %s' % detective.name)
            yield S.Timing.after_dealer_action
            self.hideDealerAction()
        else:
            self.log.info('No space for policeman')

        self.state = S_SETUP_PICK_NEXT_CONTACT

    def game_over(self):
        """The game is over"""
        self.showInstructions('   Game Over   ')
        self.play_again_button.visible = True
        while self.clicked_on is None or self.clicked_on.name != B_PLAY_AGAIN_BUTTON:
            yield 0
        self.other_screens.state = outofgamestate.S_NEW_GAME
        self.sound_click.play()