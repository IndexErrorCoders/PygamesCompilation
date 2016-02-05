"""Our main visual theme"""

import serge.blocks.themes

theme = serge.blocks.themes.Manager()
theme.load({
    'main': ('', {

        # Main properties
        'screen-height': 600,
        'screen-width': 800,
        'screen-title': 'QANAT',
        'screen-icon': 'icon',
        'bg-position': (400, 300),
        'screenshot-size': (0, 0, 800, 600),

        # Pause properties
        'pause-colour': (240, 17, 54, 255),
        'pause-font': 'CONTROL',
        'pause-size': 32,
        'pause-position': (400, 450),

        # Title and sub title
        'logo-position': (400, 160),
        'sub-title-position': (400, 450),
        'sub-title-size': 20,
        'sub-title-colour': (200, 236, 246, 255),

        # Ground properties
        'ground-position': (400, 570),
        'player-ground-speed': (0.5, 0),
        'ground-overlay-position': (400, 630),
        'player-ground-overlay-speed': (1.4, 0),

        # Player properties
        'player-ship-x': 400,
        'player-ship-y': 540,
        'player-ship-speed': 5,
        'player-bg-speed': (0.2, 0),

        # Player explosion properties
        'fragment-vx-range': (-200, 200),
        'fragment-vy-range': (-400, -300),
        'fragment-spin-range': (-400, 400),

        # Bullet properties
        'bullet-offset': -25,
        'bullet-speed': 10,
        'hot-bullet-speed': 5,
        'hot-bullet-explosion-probability': 0.2,
        'bullet-offscreen-lowy': 5,
        'bullet-offscreen-highy': 600,
        'bullet-offscreen-lowx': -50,
        'bullet-offscreen-highx': 850,
        'bullet-fragment-vx-range': (-6, 6),
        'bullet-fragment-vy-range': (4, 7),
        'bullet-fragment-force': 100.0,
        'bullet-fragment-explosion-zoom': 0.4,

        # Alien properties
        'alien-x': 400,
        'alien-y': 100,
        'alien-x-spacing': 45,
        'alien-y-spacing': 50,
        'alien-limit': 100,
        'alien-offscreen-highy': 560,
        'alien-falling-force': 500.0, # Force when crashing
        'alien-bomb-angle-multiplier': 6.0, # Angular impact of bomb
        'alien-falling-horizontal-force': -50, # Horizontal force based on offset from 0
        'alien-fracture-angle-range': (30, 140), # Change in angle when fracturing
        'alien-fracture-spin': (5, 20), # Range of spins when fracturing
        'alien-fracture-probability': 0.2, # Probablity that a second hit will fracture the alien
        'alien-explosion-zoom': (0.5, 1.0), # Range of possible zoom factors for the explosion

        # Smoke properties
        'smoke-lifetime-range': (0.2, 0.4), # Seconds, after which smoke will be removed
        'smoke-zoom-range': (0.6, 1.6), # Range of sizes to use for scaling

        # Explosion properties
        'explosion-y': 550,

        # Avoiding speeds
        'blue-alien-speed': 2,
        'blue-alien-avoid-alien': 4,
        'blue-alien-avoid-bullet': 4,
        'red-alien-speed': 4,
        'red-alien-avoid-alien': 8,
        'red-alien-avoid-bullet': 8,

        # Descenging wave properties
        'descend-time-multiplier': 0.01,
        'descend-time-x-start': 100,
        'descend-time-y-start': 0,
        'descend-speed': 5,
        'descend-probability': 0.1,
        'descend-max-number': 1,
        'descend-bomb-prob-multiplier': 10,

        # Timed wave properties
        'timed-wave-initial-delay': 0.5,
        'timed-wave-delay': 3.0,
        'timed-wave-initial-y': 10,
        'timed-wave-target-y': 300,

        # Lives properties
        'lives-initial': 3,
        'lives-colour': (255, 255, 0),
        'lives-size': 20,
        'lives-position': (20, 20),
        'lives-position-ships': (120, 28),
        'lives-spacing': 20,
        'lives-increase-after': 10000,

        # Score properties
        'score-position': (620, 20),
        'score-colour': (255, 255, 0),
        'score-size': 20,

        # High score properties
        'high-score-position': (620, 50),
        'high-score-colour': (125, 125, 0),
        'high-score-size': 20,

        # Achievements button
        'achievements-colour': (255, 255, 255, 255),
        'achievements-size': 20,
        'achievements-position': (400, 560),

        # Level properties
        'level-position': (20, 50),
        'level-colour': (125, 125, 0),
        'level-size': 20,

        # Version properties
        'version-position': (385, 580),
        'version-colour': (255, 255, 0),
        'version-size': 8,
        'version-hide-time': 20,

        # Credits properties
        'credits-position': (60, 580),
        'credits-colour': (255, 255, 255),
        'credits-size': 20,

        # Web high score properties
        'web-high-score-position': (720, 580),
        'web-high-score-colour': (255, 255, 255),
        'web-high-score-size': 20,

        # Credits screen properties
        'credits-bg-position': (400, 300),
        'credits-menu-position': (60, 580),
        'menu-height': 40,
        'menu-width': 100,
        'menu-colour': (255, 255, 255),
        'menu-font-size': 20,

        # Game over properties
        'game-over-x': 400,
        'game-over-y': 270,
        'game-over-colour': (255, 81, 6, 255),
        'game-over-size': 36,
        'game-over-sub-x': 400,
        'game-over-sub-y': 330,
        'game-over-sub-colour': (255, 144, 28, 255),
        'game-over-sub-size': 28,

        # Level over properties
        'level-over-x': 400,
        'level-over-y': 270,
        'level-over-colour': (255, 81, 6, 255),
        'level-over-size': 36,
        'level-over-time': 2,

        # Get ready properties
        'get-ready-x': 290,
        'get-ready-y': 330,
        'get-ready-colour': (255, 144, 28, 255),
        'get-ready-size': 28,
        'get-ready-time': 3,

        # Gun properties
        'gun-grid-width': 200,
        'gun-grid-height': 120,
        'gun-grid-position': (400, 48),
        'gun-label-colour': (255, 255, 0, 255),
        'gun-label-size': 20,
        'gun-bar-size': (80, 20),
        'gun-bar-border-colour': (255, 255, 0, 255),
        'gun-bar-border-size': 1,
        'gun-counter-size': 12,
        'gun-counter-offset-x': 50,
        'gun-counter-offset-y': -5,
        'gun-max-ammo': 10,
        'gun-max-temp': 100,
        'gun-regen-rate': 0.1,
        'gun-fire-rate': 1,
        'gun-fire-temp': 4,
        'gun-temp-cool-rate': 0.2,
        'gun-temp-fast-cool-rate': 0.02,
        'gun-temp-lockout-time': 5,
        'gun-bar-ammo-range': [
            (0, 20, (255, 0, 0, 255)),
            (20, 40, (255, 125, 0, 255)),
            (40, 100, (0, 0, 255, 255))
        ],
        'gun-bar-temp-range': [
            (0, 60, (0, 255, 0, 255)),
            (60, 80, (255, 125, 0, 255)),
            (80, 100, (255, 0, 0, 255))
        ],

        # Rain
        'rain-probability': 0.0,
        'rain-x': (-20, 820),
        'rain-y': (-20, -10),
        'rain-vx': (-5, +5),
        'rain-vy': (-2, +2),
        'rain-limit-x': (-40, 840),
        'rain-limit-y': (-100, 620),

        # Quiting
        'pre-stop-pause': 2,

        # Level over
        'level-over-title': 'Prepare to battle',
        'start-level': 1,
        'demo-level': 7,

    }),


    'achievements': ('main', {
        # Properties of the achievements system
        'banner-duration': 5,
        'banner-position': (175, 525),
        'banner-size': (300, 50),
        'banner-backcolour': (0, 0, 0, 50),
        'banner-font-colour': (255, 255, 0, 255),
        'banner-name-size': 14,
        'banner-description-size': 8,
        'banner-name-position': (-100, -18),
        'banner-description-position': (-100, 0),
        'banner-font-name': 'CLEAR',
        'banner-graphic-position': (-125, 0),

        'time-colour': (255, 255, 255, 100),
        'time-size': 10,
        'time-position': (-100, 24),

        'logo-position': (400, 50),
        'screen-background-sprite': 'background',
        'screen-background-position': (400, 300),
        'grid-size': (2, 5),
        'grid-width': 800,
        'grid-height': 400,
        'grid-position': (400, 320),

        'back-colour': (255, 255, 255, 255),
        'back-font-size': 20,
        'back-font-name': 'CLEAR',
        'back-position': (400, 560),
        'back-sound': None,
    }),

    'high-score-screen': ('achievements', {
        # Title
        'title-colour': (255, 255, 255),
        'title-size': 32,
        'title-position': (400, 160),
        # Back
        'back-position': (720, 580),
        # App
        'app-url': 'http://perpetualpyramidhighscores.appspot.com',
        #'app-url': 'http://localhost:8000',
        'app-game': 'QANAT',
        'app-category': 'default',
        # Table
        'max-scores': 10,
        'table-width': 200,
        'table-item-height': 30,
        'table-position': (400, 200),
        # Table text
        'hs-font-colour': (200, 200, 200),
        'hs-font-player-colour': (255, 255, 0),
        'hs-table-font-size': 12,
        # Best
        'best-font-size': 20,
        'best-font-name': 'DEFAULT',
        'best-position': (400, 550),
        # Refresh
        'refresh-colour': (200, 200, 200),
        'refresh-size': 20,
        'refresh-name': 'CLEAR',
        'refresh-position': (80, 580),
    }),

    'alien': ('main', {
        # Base alien properties
        'repulsive-force': 200,
        'attractive-force': 10,
        'player-force': 0.5,
        'max-player-force-diff': 300,
        'vertical-force': 0.6,
        'bullet-force': 1000,
        'descend-prob': 0.0,
        'descend-amount': 0,
        'bomb-prob': 0.001,
        'target-offset': 0,
        'point-at-player': False,
        # Bomb properties
        'bomb-speed': 5,
        'bomb-offset': 10,
        'bomb-direction': -1,
        'bomb-sprite': 'yellow-bomb',
        'bomb-interval': 0,
        'bomb-delay': 0,
    }),

    'blue': ('alien', {
    }),

    'red': ('alien', {
        'player-force': 2.0,
        'vertical-force': 0.2,
        'bullet-force': 5000,
        'bomb-prob': 0.01,
    }),

    'yellow': ('alien', {
        'repulsive-force': 300,
        'attractive-force': 5,
        'player-force': 2.0,
        'vertical-force': 1.0,
        'bullet-force': 7000,
        'descend-prob': 0.005,
        'descend-amount': 300,
        'bomb-prob': 0.03,
    }),

    'green': ('alien', {
        'bomb-speed': 10,
        'bomb-prob': 0.005,
        'bomb-sprite': 'green-bomb',
    }),

    'fire': ('alien', {
        'target-offset': 200,
        'player-force': 1.5,
        'point-at-player': True,
        'bomb-prob': 0.008,
        'bomb-speed': 3,
        'bomb-sprite': 'red-bomb',
    }),

    'violet': ('alien', {
        'target-offset': 200,
        'player-force': 1.5,
        'bomb-prob': 0.008,
        'bomb-speed': -3,
        'bomb-sprite': 'violet-bomb',
        'bomb-direction': +5,
    }),
    'bomb': ('alien', {
        'player-force': 1.5,
        'bomb-prob': 0.008,
        'bomb-sprite': 'bomb-bomb',
        'repulsive-force': 100,
        'attractive-force': 30,
        'bomb-prob': 0.0,
        'bomb-interval': 3,
        'bomb-delay': 1.0,
        'bomb-speed': 7,
        'explosion-possibles': [
            (300, 5),
            (350, 4),
            (400, 3),
        ],
    }),

    '0': ('main', {
        'wave-controller': 'normal',
        'alien-waves': [],
    }),
    '1': ('0', {
        'level-over-title': 'Level Over',
        'alien-waves': ['b', 'b', 'b'],
    }),
    '2': ('1', {
        'alien-waves': ['b', 'bb', 'brb', 'bb', 'b'],
    }),

    '3': ('1', {
        'alien-waves': ['brb', 'bbrrbb', 'bbrrbb', 'brb'],
    }),
    '4': ('1', {
        'level-over-title': 'Mothership coming',
        'alien-waves': ['bbb', 'yry', 'bbb'],
    }),
    '5': ('1', {
        'wave-controller': 'time-based',
        'ship-y': 0,
        'alien-waves': [
            (0.5, 'y y'),
            (3.0, 'r       '),
            (6.0, '       r'),
            (9.0, 'r y r'),
            (12.0, 'r y r'),
            (15.0, 'r y r'),
        ],
    }),
    '6': ('1', {
        'alien-waves': ['B', 'b B b', 'bb bb'],
    }),
    '7': ('1', {
        'alien-waves': ['ryr', 'yry', 'rrr', 'bb'],
    }),
    '8': ('1', {
        'alien-waves': ['r r r', 'B bb B', 'b', 'b b b'],
    }),
    '9': ('1', {
        'alien-waves': ['gbgbg', 'bb', 'bbb'],
        'level-over-title': 'Mothership coming',
    }),
    '10': ('5', {
        'alien-waves': [
            (0.5, 'y y'),
            (2.0, 'ry       '),
            (3.0, '       yr'),
            (6.0, 'r g r'),
            (9.0, 'r y r'),
            (12.0, 'r y r'),
            (15.0, 'g   g   g'),
            (17.0, 'B'),
            (20.0, 'B'),
            (23.0, 'B'),
        ],
    }),
    '11': ('1', {
        'alien-waves': ['gbgbg', 'r r', 'bb bb'],
    }),
    '12': ('1', {
        'alien-waves': ['gbgbg', 'yy', 'bbb'],
    }),
    '13': ('1', {
        'alien-waves': ['B', 'g b g b g', 'y y y', 'bb r bb'],
    }),
    '14': ('1', {
        'alien-waves': ['rrr', 'y y y', 'g g g g g', 'bb'],
        'level-over-title': 'Mothership coming',
    }),
    '15': ('5', {
        'alien-waves': [
            (0.5, 'y y'),
            (2.0, 'ry       '),
            (3.0, '       yr'),
            (6.0, 'r g r'),
            (6.2, 'f        '),
            (6.5, '        f'),
            (9.0, 'r y r'),
            (12.0, 'r y r'),
            (15.0, 'g   g   g'),
            (17.0, 'B B B'),
            (19.0, 'B B B'),
            (22.0, 'ff        '),
            (24.0, '        ff'),
            (27.0, 'B B B'),
            (30.0, 'r y r'),
        ],
    }),
    '16': ('1', {
        'alien-waves': ['frf', 'bbb', 'bb'],
    }),
    '17': ('1', {
        'alien-waves': ['B', 'frf', 'byyb', 'f bb f'],
    }),
    '18': ('1', {
        'alien-waves': ['g g g', 'frf', 'b', 'f yy f'],
    }),
    '19': ('1', {
        'alien-waves': ['f g g g f', 'fg gf', 'f   f'],
        'level-over-title': 'Mothership coming',
    }),
    '20': ('5', {
        'alien-waves': [
            (0.5, 'y y'),
            (2.0, 'ry       '),
            (3.0, '       yr'),
            (6.0, 'r g r'),
            (6.2, 'f        '),
            (6.5, '        f'),
            (9.0, 'r y r'),
            (12.0, 'r y r'),
            (15.0, 'g   g   g'),
            (17.0, 'B B B'),
            (19.0, 'B B B'),
            (22.0, 'ff        '),
            (24.0, '        ff'),
            (27.0, 'g   g   g'),
            (30.0, 'B B B'),
            (33.0, 'B B B'),
            (36.0, 'ff        '),
            (39.0, '        ff'),
        ],
    }),
    '21': ('1', {
        'alien-waves': ['B g B', 'f g g f', 'yry', 'bbb'],
    }),
    '22': ('1', {
        'alien-waves': ['y y y', 'B bbb B', 'yry', 'r b b r'],
    }),
    '23': ('1', {
        'alien-waves': ['f B B f', 'f B B f', 'f B B f', 'b r r b', 'y  y  y  y'],
    }),
    '24': ('1', {
        'alien-waves': ['b bb b bb b', 'ff B B ff', 'y y B B y y', 'b r g r b', 'y  y g g y  y'],
        'level-over-title': 'Mothership coming',
    }),
    '25': ('5', {
        'level-over-title': 'Restarting',
        'alien-waves': [
            (0.5, 'y y'),
            (2.0, 'ry       '),
            (3.0, '       yr'),
            (4.0, 'r g r'),
            (4.0, 'f        '),
            (4.5, '        f'),
            (8.0, 'r y r'),
            (12.0, 'r y r'),
            (15.0, 'g   g   g'),
            (17.0, 'B B B'),
            (19.0, 'B B B'),
            (22.0, 'ff        '),
            (24.0, '        ff'),
            (26.0, 'r y r'),
            (30.0, 'r y r'),
            (34.0, 'g   g   g'),
            (37.0, 'fg   g   gf'),
            (40.0, 'fg   g   gf'),
            (43.0, 'y y y'),
            (46.0, 'y y y'),
        ],
    }),

    '99': ('1', {
        'wave-controller': 'time-based',
        'ship-y': 0,
        'alien-waves': [
            (0.5, 'y y'),
            (2.0, 'rrr     '),
            (3.0, '     rrr'),
            (4.0, 'r y r'),
            (4.1, 'y y'),
            (5.2, 'y r r y'),
            (6.3, 'y y'),
            (9.0, 'g g'),
            (11.0, 'B    '),
            (11.5, '    B')
        ],
    }),


    '__default__': 'main',


})

G = theme.getProperty
