"""Settings for the game"""

import text
import sound


BASE_TEXT_FONT = 'LiberationSerif-Regular.ttf'
BASE_BOLD_FONT = 'LiberationSerif-Bold.ttf'
FANCY_FONT = 'ScorchedEarthDEMO-KCFonts.otf'


class Screen:
    width = 1024
    height = 768
    background_colour = (255, 0, 0)
    fps = 40


class Sound:
    number_audio_channels = 16


class Card:
    front_image = '%s-card-front.png'
    back_image = 'base-card-back.png'

    name_offset = (50, 103)
    description_offset = (50, 116)
    hp_offset = (80, 12)
    dp_offset = (15, 12)
    picture_offset = (50, 65)

    name_font = text.Fonts.getFont(BASE_BOLD_FONT, 15)
    description_font = text.Fonts.getFont(BASE_TEXT_FONT, 9)
    hp_font = text.Fonts.getFont(BASE_BOLD_FONT, 26)
    dp_font = text.Fonts.getFont(BASE_BOLD_FONT, 26)

    name_colour = (0, 0, 0)
    description_colour = (0, 0, 0)
    hp_colour = (0, 0, 0)
    dp_colour = (255, 255, 255)

    description_line_height = 10
    description_pad_bottom = 10
    description_max_chars = 24

    highlight_image = 'card-highlight.png'
    grey_image = 'card-greyed.png'


class Contract:
    size = (80, 80)
    name_offset = (40, 70)
    image_offset = (40, 40)
    name_font = text.Fonts.getFont(BASE_TEXT_FONT, 15)
    name_colour = (0, 0, 0)

    won_image = 'contract-won.png'
    lost_image = 'contract-lost.png'
    active_image = 'contract-active.png'

    scale = 0.75

class Dice:
    roll_duration = 2
    roll_interval = 0.05
    randomness = (-1.0, 1.0)


class StartingHands:

    hit_man_locations = 3
    hit_man_weapons = 3
    hit_man_attacking = 3

    mark_defending = 3


class Board:
    hitman_slots = (512, 90, 100, 200, 9, 105, 'hitman-slots')
    mark_slots = (95, 468, 100, 200, 3, 10, 'mark-slots')

    mark_play_slots = (
        [
            (132, 664 - 370),
            (391, 478),
            (524, 478),
            (640, 478),
        ],
        100, 200,
        'mark-play-slots'
    )

    hitman_play_slots = (
        [
            (391, 292),
            (523, 292),
            (667, 292),
            (774, 292),
        ],
        100, 200,
        'hitman-play-slots'
    )

    num_hitman_dice = 3
    num_mark_dice = 2

    hitman_dice_slots = (914, 388, 50, 50, 5, 73, 'hitman-dice-slots')
    mark_dice_slots = (914, 508, 50, 50, 2, 53, 'mark-dice-slots')

    contract_slots = (
        [
            (48, 610 - 375),
            (48, 660 - 375),
            (48, 710 - 375),
            (222, 610 - 375),
            (222, 660 - 375),
            (222, 710 - 375),
        ],
        50, 50,
        'contract-slots')

    policemen_slots = (
        [
            (391, 670),
            (501, 670),
            (611, 670),
            (721, 670),
        ],
        100, 200,
        'policemen-slots'
    )

    pass_button_position = (910, 184)
    exit_button_position = (930, 716)
    play_again_button_position = (512, 388)
    continue_button_position = (512, 194)
    roll_dice_button_position = (512, 194)
    game_complete_button_position = (512, 194)

    dp_gauge_position = (88, 399 + 180)
    dp_gauge_number = 30
    dp_gauge_gap = 12

    hp_gauge_position = (182, 399 + 180)
    hp_gauge_number = 30
    hp_gauge_gap = 12

    contract_result_position = (146, 424)


class UIFont:
    font = text.Fonts.getFont(BASE_TEXT_FONT, 23)
    colour = (255, 255, 255)

class UIFontBlack(UIFont):
    colour = (0, 0, 0)


class LargeUIFont:
    font = text.Fonts.getFont(BASE_TEXT_FONT, 50)
    colour = (255, 255, 255)


class InstructionFont:
    font = text.Fonts.getFont(FANCY_FONT, 40)
    colour = (0, 0, 0)

class DealerFont:
    font = text.Fonts.getFont(FANCY_FONT, 20)
    colour = (255, 255, 255)


class VersionFont:
    font = text.Fonts.getFont(FANCY_FONT, 15)
    colour = (100, 100, 100)


class CreditFont:
    font = text.Fonts.getFont(BASE_TEXT_FONT, 14)
    colour = (255, 255, 255)


class UIText:
    hp_target_font = UIFont
    hp_target_position = (197, 194)

    dp_max_font = UIFont
    dp_max_position = (101, 194)

    hp_board_font = UIFontBlack
    hp_board_position = (155, 194)

    dp_board_font = UIFont
    dp_board_position = (88, 194)

    result_font = LargeUIFont
    result_position = (512, 200)

    detection_font = LargeUIFont
    detection_position = (512, 500)

    instructions_text_position = (512, 194)
    instructions_text_font = InstructionFont

    dealer_text_position = (512, 575)
    dealer_text_font = DealerFont

    version_text_position = (930, 660)


class Game:
    max_contracts = 6

class CardDisplay:

    button_slots = (512 + 80, 180, 50, 50, 6, 160, 'cards-buttons')

    card_slot_1 = (562, 350, 50, 50, 8, 110, 'card-slot-1')
    card_slot_2 = (562, 550, 50, 50, 8, 110, 'card-slot-2')

    add_card_time = 1000

    back_button_position = (512, 700)


class StartScreen:

    logo_position = (512, 50)
    sub_logo_position = (512, 100)

    play_button_position = (512, 470)
    resume_button_position = (512, 550)
    rules_button_position = (412, 650)
    cards_button_position = (612, 650)

    next_button_position = (712, 700)
    previous_button_position = (312, 700)

    quit_button_position = (900, 700)
    credits_button_position = (100, 700)

    text_position = (512, 768 / 2)

    max_pages = 4

    display_slots = (512, 300, 100, 200, 5, 135, 'display-slots')
    display_frequency = (1000, 2000)

    version_text_position = (970, 740)

    credit_text_position = (512, 740)


class AI:

    pass_probability = 0


class Music:

    start_music = 'Chris_Zabriskie_-_09_-_Oxygen_Garden.ogg'
    game_music = 'Chris_Zabriskie_-_14_-_I_Am_a_Man_Who_Will_Fight_for_Your_Honor.ogg'

class Sounds:

    click = '215772__otisjames__click.wav'


class Timing:

    dealer_action = 10000
    after_dealer_action = 10000

    short_delay = 1000