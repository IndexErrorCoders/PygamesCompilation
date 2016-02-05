"""Our main visual theme"""

import os
import serge.blocks.themes

W, H = 800, 600

theme = serge.blocks.themes.Manager()

theme.load({
    'main': ('', {

    # Main properties
    'screen-height': H,
    'screen-width': W,
    'screen-title': 'bomberman',
    'screen-icon-filename': 'icon.png',
    'screenshot-size': (0, 0, W, H),
    'start-level': 4,

    # Ending screen
    'end-colour': (255, 255, 0),
    'end-size': 20,
    'end-font': 'main',
    'end-position': (W / 2, H / 2),
    'end-icon-position': (W / 2, H / 2 - 50),
    'pre-stop-pause': 1.5,
    'tween-world-time': 0.3,

    # Mute button
    'mute-button-alpha': 0.4,
    'mute-button-position': (W - 30, H - 30),

    # FPS display
    'fps-x': 50,
    'fps-y': H-30,
    'fps-colour': (255, 255, 0),
    'fps-size': 12,

    # Screenshot interval (s)
    'auto-screenshots': False,
    'screenshot-path': os.path.join('..', '..', '..', 'sandbox', 'screenshots'),
    'screenshot-interval': 5,

    # Simulation properties
    'simulation-on': False,
    'simulation-rtf': 10,
    'simulation-fps': 1,
    'simulation-auto-restart': False,
    'store-action-replay': True,

    # Board properties
    'board-size': (19, 19),
    'board-cell-size': (20, 20),
    'board-blanks': ['tiles-4', ],
    'board-destructible': ['tiles-2'],
    'board-position': (W / 2, H / 2),
    'board-replay-rectangle': (W / 2 - 200, H / 2 - 200, 400, 400),
    'board-replay-max-frames': 500,
    'footstep-h-sprite': 'tiles-15',
    'footstep-v-sprite': 'tiles-10',

    # Sprite names
    'bomb-sprite': 'tiles-11',
    'explosion-sprite': 'tiles-14',
    'gore-sprite': 'tiles-9',
    'number-gore': 4,

    # Bomb properties
    'bomb-fuse-time': 2,
    'explosion-time': 1,
    'explosion-propagation-time': 0.1,
    'explosion-propagation-distance': 3,
    'after-explosion-sprite': 'tiles-4',
    'explosion-sprites': ['tiles-%d' % i for i in range(21, 26)],
    'explosion-velocity': (10, 20),
    'explosion-angular': 0,
    'explosion-number': 6,
    'explosion-range': 20,
    'bomb-blast-sprite': 'tiles-14',
    'number-bomb-blasts': 4,

    # Block properties
    'block-sprites': ['tiles-%d' % i for i in range(26, 31)],
    'block-number': 6,
    'block-velocity': (180, 190),
    'block-angular-velocity': (-500, 500),
    'block-range': 400,
    'block-gravity': (0, +1000),

    # Result properties
    'result-colour': (255, 255, 0),
    'result-font-size': 42,
    'result-position': (W / 2, H / 2 - 40),
    'result-font': 'main',
    # Result properties
    'result-reason-colour': (255, 255, 0),
    'result-reason-font-size': 36,
    'result-reason-position': (W / 2, H / 2),
    'result-reason-font': 'main',
    # Next properties
    'next-colour': (255, 255, 0),
    'next-font-size': 25,
    'next-position': (W / 2, H / 2 + 80),
    'next-font': 'main',
    # Flag display properties
    'flag-status-position': (3 * W / 4 + 80, 55),
    'flag-time-limit': 20,
    'flag-sprite-name': 'tiles-34',
    'flag-zoom': 2.0,
    'flag-position-width': 75,
    'flag-position-offset-x': 10,
    'flag-position-offset-y': -4,

    # Player properties
    'player-colour': (255, 255, 0),
    'player-highlight-colour': (255, 0, 0),
    'player-highlight-time': 1100,
    'player-font-size': 25,
    'fixed-font-width': 20,
    'player-position': (W / 6 - 32, 16),
    'player-heart-position': (W / 6 + 46, 16),
    'player-font': 'main',
    'player-move-interval': 0.15,
    'ai-position': (W / 6 - 32, 70),
    'ai-heart-position': (W / 6 + 46, 70),
    'score-panel-position': (W / 6 - 22, 55),

    # AI properties
    'ai-move-interval': 0.25,
    'ai-wait-cycles': 0,
    'ai-bomb-probability': 0.5,
    'ai-squares-view': 2,
    'ai-look-ahead': 2,
    'all-ai': False,
    'ai-show-destinations': True,
    'ai-show-unsafe': True,
    'ai-unsafe-colour': (0, 0, 0, 100),
    'ai-strategy-flip-probability': 0.05,

    # Properties of the debug ui
    'ai-1-colour': (255, 0, 0),
    'ai-1-destination-colour': (255, 0, 0, 100),
    'ai-1-font-size': 12,
    'ai-1-position': (50, 200),
    'ai-1-font': 'DEFAULT',
    'ai-2-colour': (0, 255, 0),
    'ai-2-destination-colour': (0, 255, 0, 100),
    'ai-2-font-size': 12,
    'ai-2-position': (50, 250),
    'ai-2-font': 'DEFAULT',

    # Smack talk properties
    'smack-icon-position': (120, 520),
    'smack-bubble-position': (W / 2, 520),
    'smack-text-colour': (0, 0, 0),
    'smack-text-font-size': 15,
    'smack-text-position': (W / 2, 530),
    'smack-text-font': 'main',
    'smack-hide-interval': 5,
    'smack-line-length': 30,
    'smack-delay': 3,
    'smack-offset': 5,

    # Death animations
    'result-start-y': -100,
    'result-end-y': H / 2 - 40,
    'result-duration': 300.0,
    'result-delay': 100.0,
    'result-reason-start-y': 650,
    'result-reason-end-y': H / 2,
    'result-reason-duration': 300.0,
    'result-reason-delay': 100.0,
    'next-start-x': -1000,
    'next-end-x': W / 2,
    'next-duration': 350.0,
    'next-delay': 500.0,
    'chunk-number': 20,
    'chunk-velocity': (400, 600),
    'chunk-angular-velocity': (-500, 500),
    'chunk-gravity': (0, +1000),
    'chunk-sprites': ['tiles-%d' % i for i in range(16, 21)],

    # Random items creation
    # 'random-item-low-time': 10,
    # 'random-item-high-time': 15,
    'random-item-names': ['Bomb', 'Heart', 'Bomb', 'RedHeart', 'MultiBomb', 'Flag'],
    'random-item-low-time': 2,
    'random-item-high-time': 4,
    # 'random-item-names': ['MultiBomb'],
    'random-item-tween-time': 500.0,

    # Gift box
    'gift-box-position': (W / 2, 55),
    'gift-box-sprite-position': (-20, -20),
    'gift-box-sprite-zoom': 3.0,
    'gift-box-cycle-time': 0.5,
    'gift-box-cycles': (5, 10),
    'initial-number-hearts': 3,

    # Movement
    'default-movement-weight': 10.0,
    'heart-movement-weight': 0.1,
    'flag-movement-weight': 0.01,
    'heart-grab-distance': 10,
    'flag-grab-distance': 20,

    }),

    'start-screen': ('sub-screen', {
        # Version text
        'version-position': (W/2, H-10),
        'version-colour': (50, 50, 50),
        'version-font-size': 12,
        # Start button
        'start-position': (W/2, H-120),
        'start-colour': (255, 255, 0, 255),
        'start-font-size': 48,
        # Help button
        'help-position': (W-150, H-40),
        'help-colour': (0, 255, 0, 255),
        'help-font-size': 24,
        # Credits button
        'credits-position': (150, H-40),
        'credits-colour': (0, 255, 0, 255),
        'credits-font-size': 24,
        # Achievements button
        'achievements-position': (W/2, H-40),
        'achievements-colour': (0, 255, 0, 255),
        'achievements-font-size': 24,
        # Volume
        'volume': 0.1,
        # Face
        'face-position': (W / 2 - 150, H / 2 - 28),
        'face-probability': 0.4,
        # Smack talk properties
        'smack-icon-position': (-120, -520),  # Hide off screen
        'smack-bubble-position': (W / 2 + 150, H / 2 - 28),
        'smack-text-position': (W / 2 + 150, H / 2 - 28),
        'smack-delay': 1,
        'smack-offset': 3,
        # Appearing item sprite
        'item-start-position': (-150, H / 2 - 50),
        'item-end-position': (170, H / 2 - 50),
        'item-zoom': 5,
        'item-animation-time': 750,
    }),

    'sub-screen': ('main', {
        # Logo and title
        'logo-position': (W/2, 60),
        'title': 'A Bomberman Clone',
        'title-position': (W/2, 120),
        'title-colour': (213, 47, 41),
        'title-font-size': 25,
        'title-font': 'main',
        # Back button
        'back-colour': (255, 255, 0, 255),
        'back-font-size': 24,
    }),
    'help-screen': ('sub-screen', {
        # Help text
        'text-position': (W/2, H/2),
        'back-position': (W-100, H-40),
        # Key text
        'keys-title-position': (W/2, 180),
        'keys-title-colour': (212, 196, 148),
        'keys-title-font-size': 25,
        'keys-title-font': 'main',
        # Music text
        'music-title-position': (W/2, 450),
        'music-title-colour': (212, 196, 148),
        'music-title-font-size': 25,
        'music-title-font': 'main',
        # Volume
        'vol-down-position': (W / 2 - 80, 500),
        'vol-up-position': (W / 2 + 80, 500),
        'vol-position': (W / 2, 500),
        'volume-colour': (212, 196, 148),
        'volume-font': 'main',
        'volume-size': 40,
        'vol-change-amount': 10,

    }),
    'level-screen': ('start-screen', {
        # Help text
        'text-position': (W/2, H/2),
        # Grid properties
        'grid-size': (5, 1),
        'grid-width': 650,
        'grid-height': 200,
        'grid-position': (W / 2, H / 2 - 70),
        # Title properties
        'title-colour': (255, 255, 0, 255),
        'title-font-size': 15,
        'title-font': 'main',
        'title-offset-y': 70,
        # Random level button
        'random-level-position': (W / 2, H / 2 + 100),
        # Back button
        'back-position': (W/2, H-40),
        # Resume button
        'resume-position': (W/2, H-90),
    }),
    'random-level-screen': ('sub-screen', {
        # Back button
        'back-position': (W/2, H-40),
        # Resume button
        'resume-position': (W/2, H-90),
        # Generate button
        'generate-position': (680, H/2 - 20),
        # Select button
        'select-position': (680, H/2 + 40),
        # Size menu
        'size-width': 160,
        'size-height': 140,
        'size-item-width': 140,
        'size-item-height': 40,
        'size-position': (100, H/2 - 40),
        'size-font-size': 18,
        # Space menu
        'space-width': 160,
        'space-height': 100,
        'space-position': (100, H/2 + 130),
        'space-item-width': 150,
        'space-item-height': 40,
        'space-font-size': 18,
        # Menu properties
        'menu-on-colour': (89, 81, 77),
        'menu-off-colour': (89, 81, 77, 10),
        'menu-font-colour': (255, 255, 0),
        'menu-mouse-over-colour': (162, 146, 114),
        'menu-font-size': 18,
        'menu-font': 'main',
        # Level preview
        'level-preview-width': 300,
        'level-preview-height': 300,
        'level-preview-position': (W/2, H/2 + 35),
        # Size options
        'size-options': {
            'Small': (11, 11),
            'Medium': (15, 15),
            'Large': (19, 19),
        },
        # Space options
        'space-options': {
            'Open': (1, 1),
            'Blocked': (10, 4),
        },
    }),
    'action-replay-screen': ('start-screen', {
        # Transport bar
        'bar-width': 660,
        'bar-height': 80,
        'bar-background-colour': (0, 0, 0, 150),
        'bar-position': (W / 2, H - 80),
        # Replay display
        'replay-position': (W / 2, H / 2),
        'replay-slow-fps': 15,
        'replay-normal-fps': 50,
        'replay-fast-fps': 150,
        'replay-width': 400,
        'replay-height': 400,
        # Current frame display
        'current-colour': (255, 255, 0, 50),
        'current-font-size': 12,
        'current-position': (W / 2, 50),
        'current-font': 'main',
        # Slider properties
        'slider-back-position': (W / 2, 50)
    }),
    'credits-screen': ('sub-screen', {
        # Author
        'author-title-colour': (148, 8, 42),
        'author-title-font-size': 24,
        'author-title-position': (W/2, 170),
        'author-colour': (212, 196, 148),
        'author-font-size': 32,
        'author-position': (W/2, 210),
        'url-colour': (156, 140, 116),
        'url-font-size': 14,
        'url-position': (W/2, 230),
        # Music
        'music-title1-colour': (148, 8, 42),
        'music-title1-font-size': 20,
        'music-title1-position': (W/2, 260),
        'music-title2-colour': (148, 8, 42),
        'music-title2-font-size': 18,
        'music-title2-position': (W/2, 280),
        'music-colour': (212, 196, 148),
        'music-font-size': 16,
        'music-position': (W/2, 300),
        # Sound
        'sound-title1-colour': (148, 8, 42),
        'sound-title1-font-size': 20,
        'sound-title1-position': (W*3/4, 420),
        'sound-title2-colour': (212, 196, 148),
        'sound-title2-font-size': 18,
        'sound-title2-position': (W*3/4, 440),
        # Built using
        'built-title-colour': (148, 8, 42),
        'built-title-font-size': 20,
        'built-title-position': (W/4, 420),
        'built-colour': (212, 196, 148),
        'built-font-size': 16,
        'built-position': (W/4, 440),
        # Engine
        'engine-title-colour': (148, 8, 42),
        'engine-title-font-size': 20,
        'engine-title-position': (W/4, 480),
        'engine-colour': (212, 196, 148),
        'engine-font-size': 16,
        'engine-position': (W/4, 500),
        # Engine version
        'engine-version-colour': (156, 140, 116),
        'engine-version-font-size': 10,
        'engine-version-position': (W/4, 520),
        # Fonts
        'font-title1-colour': (148, 8, 42),
        'font-title1-font-size': 20,
        'font-title1-position': (W*3/4, 480),
        'font-title2-colour': (148, 8, 42),
        'font-title2-font-size': 18,
        'font-title2-position': (W*3/4, 500),
        'font-colour': (212, 196, 148),
        'font-font-size': 16,
        'font-position': (W*3/4, 520),
        #
        'back-position': (100, H-40),

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
        'banner-font-name': 'DEFAULT',
        'banner-graphic-position': (-125, 0),

        'time-colour': (255, 255, 255, 100),
        'time-size': 10,
        'time-position': (-100, 24),

        'logo-position': (400, 50),
        'screen-background-sprite': None,
        'screen-background-position': (400, 300),
        'grid-size': (2, 5),
        'grid-width': 800,
        'grid-height': 400,
        'grid-position': (400, 320),

        'back-colour': (255, 255, 255, 255),
        'back-font-size': 20,
        'back-font-name': 'DEFAULT',
        'back-position': (400, 560),
        'back-sound': 'click',
    }),

    '__default__': 'main',

})

G = theme.getProperty