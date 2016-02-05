"""This file contains the main settings that are used in the game"""

from pymunk import Vec2d
import engine
import engine.utils


# TODO: rationalise settings, Gerty into his own class

class Settings(object):
    """The main settings"""

    # How long to fade between screens
    fade_screen_delay = 2

    # The level to start on
    start_level = 0

    # Opacity while dragging
    dragging_opacity = 100

    # Gerty UI
    # gerty_on_screen_position = Vec2d(250, 700)
    # gerty_off_screen_position = Vec2d(250, 900)
    gerty_on_screen_position = Vec2d(250, 200)
    gerty_off_screen_position = Vec2d(250, -200)
    gerty_hide_duration = 0.35
    gerty_bg_offset = (245, -29)
    gerty_text_offset = (425, 0)
    gerty_number_buttons = 3
    gerty_button_origin_offset = Vec2d(250, -50)
    gerty_button_offset = Vec2d(100, 0)
    gerty_conversation_check_interval = 0.5
    gerty_short_short_text = 5
    gerty_level_screen_wait = 4
    gerty_width = 700
    gerty_impairment_time = 60

    # Gun properties
    gun_rocket_offset = Vec2d(55, 10)
    gun_chamber_offset = Vec2d(0, 10)

    # Defaults
    normal_harvester_capacity = 30

    # Level complete banner
    complete_position = Vec2d(1024 / 2, 768 / 2)
    complete_tween_delay = 2,

    # Small harvester
    small_harvester_collector_scale = 0.5
    small_harvester_collector_offset = Vec2d(55, -22)
    small_right_harvester_collector_scale = 0.5
    small_right_harvester_collector_offset = Vec2d(-55, -22)
    small_harvester_poly = [
        (0, 0),
        (0.96, 0),
        (0.75, 0.84),
        (0.41, 1),
        (0.1, 1),
        (0, 0.85),
    ]
    small_right_harvester_poly = [
        (1.0 - 0, 0),
        (1.0 - 0.96, 0),
        (1.0 - 0.75, 0.84),
        (1.0 - 0.41, 1),
        (1.0 - 0.1, 1),
        (1.0 - 0, 0.85),
    ]
    large_harvester_poly = [
        (0, 0.15),
        (0.1, -0.07),
        (1, -0.08),
        (1, 0.52),
        (0.56, 0.86),
        (0.07, 0.79),
    ]

    small_harvester_contents_offset = Vec2d(-46, -1)
    small_harvester_contents_width = 60
    small_harvester_contents_height = 7
    small_harvester_colour = [0, 255, 0, 200]

    # Large harvester
    large_harvester_collector_scale = 2.3
    large_harvester_collector_offset = Vec2d(-14, -7)

    # Standard attractor
    standard_repeller_1 = (-600, -4)
    standard_repeller_2 = (-600, -4)
    standard_repeller_3 = (-200, -4)

    standard_attractor_1 = (600, -4)
    standard_attractor_2 = (400, -4)
    standard_attractor_3 = (200, -4)

    attractor_angle_spread = 20
    attractor_velocity_spread = 100, 200
    attractor_particles_per_second = 5
    attractor_particle_lifetime = 0.5
    attractor_max_range = 200

    show_attractors = False
    show_particles = True

    # Rocket
    rocket_smoke_per_second = 100
    rocket_smoke_lifetime = 2.0
    rocket_explosion_helium = 5

    # Palette UI
    palette_on_screen_position = Vec2d(40, 400)
    palette_off_screen_position = Vec2d(-30, 400)
    palette_hide_duration = 0.2
    palette_btn_offset_x = 8
    palette_btn_initial_y = 114
    palette_btn_offset_y = -75
    palette_btn_object_offset = Vec2d(100, 0)

    # Main ground physics
    main_ground_physics = engine.PolygonSpritePhysics(
            0, 0.5, 0.5,
            [
                (0.00, 0.00),
                (1.00, 0.00),
                (1.00, 0.61),
                (0.65, 0.89),
                (0.00, 0.70),
            ]
    )

    emitter_rock_offset = (0, 20)

    class Level1:
        emitter_angular_spread = 10
        emitter_velocity = engine.RandomGenerator(50, 300)

    class Start:
        logo_position = 1024 / 2, 700
        start_btn_position = 1024 / 2, 300
        help_btn_position = 1024 / 2, 200
        bg_position = 1024 / 2, 768 / 2
        title_position = 1024 / 2, 550
        credit_position = 1024 / 2 + 100, 100

        tween_in_duration = 0.5
        tween_in_delay = engine.utils.RandomGenerator(0, 0.25)
        tween_in_offset_x = -1000
        tween_out_offset_y = -1000

    class Help:
        help_text_position = 1024 / 2 + 150, 600
        help_img_position = 1024 / 2, 350
        tween_in_offset_y = 1000

    class Level:
        back_btn_position = 1024 / 2, 50
        icons_per_row = 4
        icons_start_y = 550
        icons_start_x = 1024 / 2
        icons_rows_height = -130
        icons_width = 600
        icon_offset_y = 60

        tween_in_duration = 0.5
        tween_in_delay = engine.utils.RandomGenerator(0, 0.25)
        tween_in_offset_x = 1000
        tween_out_offset_y = -1000

    class ScoreHUD:
        on_screen_position = Vec2d(115, 688)
        off_screen_position = Vec2d(-200, 688)
        hide_duration = 2.0
        opacity = 255

        name_label_x = -100
        name_label_y = 55
        time_label_x = -100
        time_label_y = 8
        total_time_label_x = -100
        total_time_label_y = -39


class DebugSettings(Settings):
    """Debug version of settings"""

    fade_screen_delay = 0.1
    start_level = 12
    gerty_short_short_text = 2
    gerty_level_screen_wait = 4
    # show_attractors = True
    # show_particles = False
    gerty_impairment_time = 10

S = Settings()
D = DebugSettings()



