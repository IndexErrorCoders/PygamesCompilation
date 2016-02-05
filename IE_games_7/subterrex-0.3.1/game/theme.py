"""Our main visual theme"""

import serge.blocks.themes
from serge.blocks.lsystem import Rule

CAVE_WIDTH, CAVE_HEIGHT = 20, 60
CAVE_VERTICAL_SCREENS = 4
CAVE_HORIZONTAL_SCREENS = 1

theme = serge.blocks.themes.Manager()
theme.load({
    'main' : ('', {
    
    # Main properties
    'screen-height' : 600,
    'screen-width' : 800,
    'screen-title' : 'SubTerrex',
    'screen-icon' : 'icon',
    'screenshot-size' : (0, 0, 800, 600),
    
    # Mute button
    'mute-button-alpha' : 0.4,
    'mute-button-position' : (30, 30),
    'pre-stop-pause' : 0.5,
    
    # Cave grid
    'cave-vertical-screens' : CAVE_VERTICAL_SCREENS,
    'cave-horizontal-screens' : CAVE_HORIZONTAL_SCREENS,
    'cell-size' : (800/CAVE_WIDTH*CAVE_HORIZONTAL_SCREENS, 600/CAVE_HEIGHT*CAVE_VERTICAL_SCREENS),
    'cave-width' : CAVE_WIDTH,
    'cave-height' : CAVE_HEIGHT,
    'cave-probability' : 0.41,
    'tile-scale' : 26.0/CAVE_WIDTH,
    'cave-fractals' : {'rock':(0, 0, 0)},
    'cave-sprites' : ['rock', 'surface', 'water', 'moss'],
    'cave-parallax-background' : True,
    'cave-parallax-amount' : 0.4,
    'cave-tree-parallax-background' : True,
    'cave-tree-parallax-amount' : 0.0,
    'fractal-num-steps' : 7,
    'fractal-distance' : 8.0,
    'fractal-decay' : 1.75,
    'fractal-overstuff' : 1.5,
    'fractal-blur' : 0,
    'fractal-sprite-cache-size' : 20,
    'surface-rows' : 2,
    'entrance-width' : 2,
    'entrance-buffer' : 2,
    'exit-width' : 2,
    'exit-buffer' : 2,
    
    # Sound texturing
    'dynamic-sound-damping' : 0.5,
    'water-fall-sound-dropoff' : 200,
    'crystal-sound-dropoff' : 250,
    'exit-sound-dropoff' : 500,
    'flare-sound-dropoff' : 200,
    'frog-sound-probability' : 0.02,
    'creature-sounds' : ['dino', 'bat', 'frog', ],
    
    # Cave visual
    'cave-position' : (CAVE_HORIZONTAL_SCREENS*800/2, CAVE_VERTICAL_SCREENS*600/2),
    
    # Water
    'water-amount' : 100,
    'number-sources' : (0, 6, 2),
    'foam-probability' : 0.08,
    'foam-speed' : (3, 6),
    'foam-x-jitter' : (-2, 2),
    'foam-x-offset' : -0.25,
    
    # Crystals etc
    'number-crystals' : (2, 6, 4),
    'number-trees' : (5, 20, 9),
    'fluorescent-light-factor' : (50, 50, 50, 50),
    'named-light-factor' : (0, 255, 0, 200),
    'named-light-tolerance' : 20,
    'luminescent-light-factor' : (10, 10, 50, 50),
    'do-moss' : False,
    'tree-size' : 500,
    'tree-steps' : 5,
    'tree-blur' : 3,
    'tree-circle-size' : 1,
    'tree-distance' : 5,
    'tree-colour' : (75, 75, 75),
    'tree-colour-randomize' : True,
    'tree-rules' : [
        Rule('F', 'FF'),
        Rule('X', 'F-[[X]+X]+F[+FX]-X', 0.2),
        Rule('X', 'F[-X][+X]', 0.4),
        Rule('X', 'F+F[+FX]-X', 0.4),
        Rule('X', 'F-F[-FX]+X', 0.8),
        Rule('X', 'F[F-X][F+X]'),
    ],
    
    # Light modeling
    'light-mask-colour' : (0, 0, 0, 0),
    'light-ambient' : 0, 
    'light-blur' : 20,
    'light-position-jitter' : 0,
    'light-blur-jitter' : 0,#1,
    'light-opacity-jitter-min' : 0,#25,
    'light-opacity-jitter' : 0,#10,
    'light-refresh-probability' : 0.25,
    'light-number-renders' : 1,
    'light-use-dirty-algorithm' : True,
    'light-dirty-boundary' : 75,
    #
    'entrance-light-colour' : (255, 255, 255),
    'entrance-light-strength' : 255,
    'entrance-light-distance' : 200,
    'exit-light-colour' : (255, 0, 0),
    'exit-light-strength' : 255,
    'exit-light-distance' : 100,
    
    # Player
    'player-initial-position' : (30, 60),
    'player-speed' : 1,
    'player-rotate-speed' : 5, 
    'player-walk-time' : 0.25,
    'player-effective-radius' : 24,
    'player-framerate-multiplier' : 0.25,
    #
    'player-jump-impulse' : 6000,
    'player-walk-impulse' : 700,
    'player-max-reach' : 20,
    'player-friction' : 0.7,
    'player-surface-detection-offset' : -13, # Tune to get the isOnSurface method to give the right answer
    #
    # Player acceleration
    'player-acceleration-silent' : 1.0,
    'player-acceleration-death' : 20.0,
    'player-death-camera-offset' : 200,

    # Rope
    'rope-damping-factor' : 20,
    'rope-segment-length' : 10,
    'rope-number-segments' : 15,
    'rope-anchor-size' : 2,
    'rope-anchor-colour' : (10, 10, 10),
    'rope-colour' : (100, 100, 100),
    'rope-width' : 2,
    'rope-quiescent-velocity' : 10.0,
    'physics-step-size' : 4,
    
    # FPS display
    'fps-x' : 40,
    'fps-y' : 550,
    'fps-size' : 12,
    'fps-colour' : (255, 255, 0),
    
    # Bugs
    'number-bugs' : 0,
    
    # Levels
    'level-seed' : None,
    'start-screen-seed' : 11115,
    
    # Camera
    'camera-damping' : 0.2,
    'camera-death-damping' : 0.1,
    
    # HUD
    'hud-width' : 250,
    'hud-display-width' : 220,
    'hud-height' : 80,
    'hud-position' : (680, 60),
    'hud-background-colour' : (50, 50, 50, 50),
    'hud-font-name' : 'DEFAULT',
    'hud-font-size' : 20,
    'hud-text-colour' : (255, 255, 255),
    #    
    'hud-light-font-size' : 24,
    'hud-yellow-colour' : (255, 255, 50),
    'hud-blue-colour' : (50, 50, 255),
    'hud-green-colour' : (50, 255, 50),
    #
    'hud-highlight-width' : 65,
    'hud-highlight-height' : 35,
    'hud-highlight-opacity' : 50,
    
    # Initial settings
    'player-initial-time' : 180,
    'player-initial-ropes' : 10,
    'initial-blue-lights' : 3,
    'initial-yellow-lights' : 5,
    'initial-green-lights' : 3, 
    'initial-selected-light' : 'yellow',

    # Music
    'music-fade-time' : 5,
    
    }),
    
    
    # Light settings
    'light' : ('main', {
        'colour' : (255, 255, 255),
        'strength' : 255,
        'distance' : 200,
        'smoke-probability' : 0.2,
        'smoke-x-velocity' : (-50, 50),
        'smoke-y-velocity' : (-50, -25),
        'smoke-x-range' : 40,
        'smoke-y-range' : 80,
        'smoke-y-offset' : -18,
        'max-evaluation-distance' : 400, # Short cut to ignoring lights
    }),
    'death' : ('light', {
        'colour' : (255, 102, 0),
        'strength' : 255,
        'distance' : 50,
    }),
    'yellow' : ('light', {
        'colour' : (255, 255, 0),
        'strength' : 255,
        'distance' : 50,
    }),
    'green' : ('light', {
        'colour' : (0, 255, 0),
        'strength' : 150,
        'distance' : 100,
    }),
    'blue' : ('light', {
        'colour' : (100, 100, 255),
        'strength' : 100,
        'distance' : 200,
    }),
    'red' : ('light', {
        'colour' : (255, 0, 0),
        'strength' : 255,
        'distance' : 50,
    }),
    
    
    'base-bug' : ('main', {
        'rotation-speed' : (-0.1, 0.1),
        'movement-speed' : (0.1, 0.5),
        'pause-time' : (10, 20),
        #
        'mass' : 1.0,
        #
        # Forces (min distance, force, distance power law)
        'wall-attraction' : (100, -200, 1),
        'player-attraction' : (100, -500.0, 1),
        'bug-attraction' : (50, -100, 1),
        #
        # Light sensitivity (target light level, force)
        'light-target' : (255, 1.0, 1),
        # 
        # Damping (min speed, damping force)
        'damping-force' : (0.05, -0.1),

    }),
    
    'start-screen' : ('main', {
        # Logo and title
        'logo-position' : (800/2, 100),
        'title' : 'Explore deep, subterranean caverns',
        'title-position' : (800/2, 220),
        'title-colour' : (128, 83, 22, 255),
        'title-font-size' : 40,
        'title2' : 'How deep can you go?',
        'title2-position' : (800/2, 260),
        'title2-colour' : (128, 83, 22, 255),
        'title2-font-size' : 30,
        # Version text
        'version-position' : (800/2, 600-10),
        'version-colour' : (50, 50, 50),
        'version-font-size' : 12,
        # Resume text
        'resume-position' : (800/2, 600-260),
        'resume-colour' : (255, 255, 0, 255),
        'resume-font-size' : 54,
        # Start button
        'start-position' : (800/2, 600-180),
        'start-colour' : (255, 255, 0, 255),
        'start-font-size' : 48,
        # Collection button
        'collection-position' : (800/2, 600-110),
        'collection-colour' : (0, 255, 255, 255),
        'collection-font-size' : 36,
        # Help button
        'help-position' : (800-100, 600-40),
        'help-colour' : (0, 255, 0, 255),
        'help-font-size' : 24,
        # Credits button
        'credits-position' : (100, 600-40),
        'credits-colour' : (0, 255, 0, 255),
        'credits-font-size' : 24,    
        # Achievements button
        'achievements-position' : (800/2, 600-40),
        'achievements-colour' : (0, 255, 0, 255),
        'achievements-font-size' : 24,  
        
        # Light sources
        'sources' : [
            [(600, 260), 'yellow'],
            [(260, 230), 'green'],
            [(160, 530), 'blue'],
            [(528, 1000), 'blue'],
            [(400, 780), 'yellow'],
        ],
        # Climber position
        'player-initial-position' : (140, 220),
        'rope-origin' : (140, 130),
        'rope-end' : (140, 260),
        'move-player-probability' : 0.005,
        
        # Camera movement
        'camera-y-amp' : 300,
        'camera-period' : 40,
    }),

    'sub-screen' : ('start-screen', {
        # Logo and title
        'logo-position' : (800/2, 40),
        'title-position' : (800/2+50, 40),
        'title-colour' : (255, 255, 255, 255),
        'title-font-size' : 36,
        # Back button
        'back-colour' : (255, 255, 0, 255),
        'back-font-size' : 24,
        'screen-background-position' : (400, 300),
        'screen-background-sprite' : 'background',
        # Trees
        'number-trees' : 3,
        'tree-positions' : (200, 600),
        'tree-size' : 800,
        'tree-colour-randomize' : False,
   }),
    'main-screen' : ('sub-screen', {
        # Main text
        'main-text-position' : (800/2, 250),
        'main-text-colour' : (255, 255, 255, 255),
        'main-text-font-size' : 48,
        # Sub text
        'sub-text-position' : (800/2, 300),
        'sub-text-colour' : (255, 255, 255, 255),
        'sub-text-font-size' : 36,
    }),
    'help-screen' : ('sub-screen', {
        # Help text
        'text-position' : (800/2, 600/2+50),
        # Tree
        'tree-steps' : 5,
        'tree-blur' : 3,
        'tree-circle-size' : 1,
        'tree-distance' : 8,
        'tree-colour' : (50,50,0),
    }),
    'name-screen' : ('sub-screen', {
        #
        # Static text items
        'random-position' : (800/2, 150),
        'random-colour' : (255, 255, 255, 255),
        'random-font-size' : 36,
        'random-small-position' : (800/2, 180),
        'random-small-colour' : (255, 204, 0),
        'random-small-font-size' : 20,
        'named-position' : (800/2, 250),
        'named-colour' : (255, 255, 255, 255),
        'named-font-size' : 36,
        'named-small-position' : (800/2, 280),
        'named-small-colour' : (255, 204, 0, 255),
        'named-small-font-size' : 20,
        #
        # Entry widget
        'entry-width' : 600,
        'entry-height' : 50,
        'entry-font-colour' : (255, 255, 255, 255),
        'entry-font-size' : 28,
        'entry-font-name' : 'DEFAULT',
        'entry-position' : (800/2, 330),
        'entry-bg-colour' : (50, 50, 50, 50),
        'entry-stroke-colour' : (255, 255, 255, 100),
        'entry-stroke-width' : 4,
        #
        # Previous
        'previous-position' : (800/2, 400),
        'previous-colour' : (255, 255, 255, 255),
        'previous-font-size' : 36,
        'previous-small-position' : (800/2, 430),
        'previous-small-colour' : (255, 204, 0, 255),
        'previous-small-font-size' : 20,
        #
        # History
        'history-position' : (800/2, 460),
        'names-width' : 200,
        'names-height' : 120,
        'names-position' : (800/2, 510),
        'names-number' : 6,
        'names-colour' : (255,255,255,255),
        'names-font-name' : 'DEFAULT',
        'names-font-size' : 18,
        #
        'back-position' : (30, 600-20),        
    }),
    'collection-screen' : ('sub-screen', {
        # Title
        'title-position' : (800/2, 120),
        'title-colour' : (0, 255, 255, 255),
        'title-font-size' : 40,
        # Labels
        't1-colour' : (255, 255, 0, 255),
        't1-font-size' : 20,
        't2-colour' : (255, 255, 255, 255),
        't2-font-size' : 16,
        # Grid
        'grid-size' : (3, 5),
        'grid-width' : 700,
        'grid-height' : 360,
        'grid-position' : (400, 350),
        # Slot
        'slot-width' : 200,
        'slot-height' : 60,
        'slot-background-colour' : (0, 0, 0, 50),
        'slot-active-background-colour' : (0, 0, 0, 255),
        # Details
        'detail-colour' : (255, 255, 255, 255),
        'detail-backcolour' : (0, 0, 0, 255),
        'detail-font-size' : 16,
        'detail-width' : 200,
        'detail-height' : 80,
        'detail-wrap' : 30,
        #
        'background-colour' : (0, 0, 0, 50),
        # Next
        'next-position' : (800-100, 600-50),        
        'next-colour' : (0, 255, 255, 255),
        'next-font-size' : 20,
        # Previous
        'previous-position' : (100, 600-50),        
        'previous-colour' : (0, 255, 255, 255),
        'previous-font-size' : 20,
        # Page
        'page-position' : (800/2, 600-50),        
        'page-colour' : (0, 255, 255, 255),
        'page-font-size' : 20,
        #
        'back-position' : (800/2, 600-20),   
        # Tree
        'tree-steps' : 5,
        'tree-blur' : 3,
        'tree-circle-size' : 3,
        'tree-distance' : 12,
        'tree-colour' : (0,50,50),     
    }),
    'overlay-screen' : ('sub-screen', {
        # Overlay
        'overlay-position' : (800/2, 600/2),
        'overlay-colour' : (255, 204, 0, 255),
        'overlay-font-size' : 48,
    }),
    'credits-screen' : ('sub-screen', {
        # Author
        'author-title-colour' : (0, 220, 220),
        'author-title-font-size' : 24,
        'author-title-position' : (800/2, 110),
        'author-colour' : (255, 255, 0),
        'author-font-size' : 32,
        'author-position' : (800/2, 150),
        'url-colour' : (255, 0, 0),
        'url-font-size' : 14,
        'url-position' : (800/2, 170),
        # Music
        'music-title1-colour' : (0, 220, 220),
        'music-title1-font-size' : 20,
        'music-title1-position' : (800/2, 220),
        'music-title2-colour' : (0, 220, 220),
        'music-title2-font-size' : 18,
        'music-title2-position' : (800/2, 240),
        'music-colour' : (255, 255, 0),
        'music-font-size' : 16,
        'music-position' : (800/2, 260),
        # Sound
        'sound-title1-colour' : (0, 220, 220),
        'sound-title1-font-size' : 20,
        'sound-title1-position' : (800/2, 340),
        'sound-title2-colour' : (0, 220, 220),
        'sound-title2-font-size' : 18,
        'sound-title2-position' : (800/2, 360),
        # Built using        
        'built-title-colour' : (0, 220, 220),
        'built-title-font-size' : 20,
        'built-title-position' : (800/4, 420),
        'built-colour' : (255, 255, 0),
        'built-font-size' : 16,
        'built-position' : (800/4, 440),
        # Engine
        'engine-title-colour' : (0, 220, 220),
        'engine-title-font-size' : 20,
        'engine-title-position' : (800/4, 480),
        'engine-colour' : (255, 255, 0),
        'engine-font-size' : 16,
        'engine-position' : (800/4, 500),
        # Fonts
        'font-title1-colour' : (0, 220, 220),
        'font-title1-font-size' : 20,
        'font-title1-position' : (800*3/4, 420),
        'font-title2-colour' : (0, 220, 220),
        'font-title2-font-size' : 18,
        'font-title2-position' : (800*3/4, 440),
        'font-colour' : (255, 255, 0),
        'font-font-size' : 16,
        'font-position' : (800*3/4, 460),
        #
        'back-position' : (100, 600-40),
        # Tree
        'tree-steps' : 6,
        'tree-blur' : 3,
        'tree-circle-size' : 1,
        'tree-distance' : 7,
        'tree-colour' : (0,50,0),
    }),
    
    'achievements' : ('sub-screen', {
        # Properties of the achievements system
        'banner-duration' : 5,
        'banner-position' : (175, 525),
        'banner-size' : (300, 50),
        'banner-backcolour' : (0, 0, 0, 50),
        'banner-font-colour' : (255, 255, 0, 255),
        'banner-name-size' : 20,
        'banner-description-size' : 14,
        'banner-name-position' : (-100, -18),
        'banner-description-position' : (-100, 0),
        'banner-font-name' : 'DEFAULT',
        'banner-graphic-position' : (-125, 0),
        
        'time-colour' : (255, 255, 255, 100),
        'time-size' : 14,
        'time-position' : (-100, 24),
        
        'logo-position' : (400, 50),

        'grid-size' : (2, 5),
        'grid-width' : 800,
        'grid-height' : 400,
        'grid-position' : (400, 320),
        
        'back-colour' : (255, 255, 255, 255),
        'back-font-size' : 20,
        'back-font-name' : 'DEFAULT',
        'back-position' : (400, 560),
        'back-sound' : 'click',
    }),
    'named-crystal' : ('sub-screen', {
        # Properties of the named crystal banner
        'banner-position' : (400, 300),
        'banner-size' : (300, 200),
        'banner-backcolour' : (50, 150, 50, 50),
        'banner-font-colour' : (255, 255, 0, 255),
        'banner-name-size' : 30,
        'banner-description-size' : 18,
        'banner-name-position' : (-100, -90),
        'banner-description-position' : (-100, -50),
        'banner-font-name' : 'DEFAULT',
        'banner-graphic-position' : (-125, -72),
        
        'banner-close-size' : 14,
        'banner-close-font-colour' : (255, 255, 255, 255),
        'banner-close-position' : (-100, 80),
        
        'time-colour' : (255, 255, 255, 100),
        'time-size' : 14,
        'time-position' : (-100, 24),
        
        'logo-position' : (400, 50),

        'grid-size' : (2, 5),
        'grid-width' : 800,
        'grid-height' : 400,
        'grid-position' : (400, 320),
        
        'back-colour' : (255, 255, 255, 255),
        'back-font-size' : 20,
        'back-font-name' : 'DEFAULT',
        'back-position' : (400, 560),
        'back-sound' : 'click',
        
        'banner-characters' : 30,
    }),


    '__default__' : 'main',

})

G = theme.getProperty
