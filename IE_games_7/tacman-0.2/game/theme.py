"""Our main visual theme"""

import serge.blocks.themes

X = 'wall'
T = 'teleport'

theme = serge.blocks.themes.Manager()
theme.load({
    'main' : ('', {
    
    ### Start Screen Related Items ###
    
    # Titles
    'title-position' : (400, 100),
    'title-colour' : (255, 255, 0, 255),
    'title-height' : 100,
    'title-font-size' : 88,
    'subtitle-colour' : (255, 255, 0, 255),
    'subtitle-font-size' : 24,
    'version-colour' : (0, 255, 0, 255),
    'version-font-size' : 12,
    'version-position' : (770, 580),
    'url-colour' : (255, 255, 255, 255),
    'url-font-size' : 20,
    'url-position' : (400, 575),
    
    # Menu
    'menu-position' : (400, 230),
    'menu-width' : 600,
    'menu-height' : 50,
    'menu-colour' : (255, 0, 0, 255),
    'menu-font-size' : 52,
    
    # Sound menu
    'sound-menu-width' : 300,
    'sound-menu-height' : 80,
    'sound-menu-position' : (50, 540),

    ### Tutorial Screen Related Items ###
    
    # Menu
    'tutorial-menu-position' : (400, 530),
    'tutorial-menu-width' : 600,
    'tutorial-menu-height' : 50,
    'tutorial-menu-colour' : (255, 0, 0, 255),
    'tutorial-menu-font-size' : 52,

    ### Credit Screen Related Items ###
    
    # Menu
    'credits-menu-position' : (400, 550),
    'credits-bg-position' : (400, 330),

    ### Main Screen and Game Related Items ###
    
    # Main properties
    'screen-height' : 600,
    'screen-width' : 800,
    'screen-title' : 'TACMAN',
    'screen-icon' : 'icon',

    # Score
    'score-colour' : (255, 0, 0, 255),
    'score-position' : (175, 10),
    'score-size' : 36,
    
    # Moves
    'moves-colour' : (255, 0, 0, 255),
    'moves-position' : (476, 10),
    'moves-size' : 36,
    
    # Level over
    'level-over-colour' : (255, 255, 0, 255),
    'level-over-position' : (400, 300),
    'level-over-size' : 96,
    'restart-position' : (400, 400),
    'restart-size' : (200, 50),
    'restart-back-colour' : (0, 0, 0, 255),
    'restart-font-colour' : (255, 0, 0, 255),
    'restart-font-size' : 64,
    

    # Level over
    'dev-target-colour' : (255, 255, 255, 255),
    'dev-target-position' : (20, 560),
    'dev-target-time-position' : (20, 580),
    'dev-target-size' : 12,
    
    # Ghost properties
    'move-interval' : 300,
    'move-boost-interval' : 100,
    'mode-timings' : {
        'chase' : 6,
        'scatter' : 3,
        'fright' : 4,
        'freeze' : 2,
    },
    'mode-initial' : 'chase',
    'ghost-score' : 20,
    'red-speed' : 50,
    'pink-speed' : 50,
    'orange-speed' : 50,
    'blue-speed' : 50,
    'ghost-moves' : 4,
    'ghost-decision-time' : 500,
    'after-death-freeze' : 1,
    
    # Ghost start locations
    'red-start' : (0, 0),
    'pink-start' : (3, 0),
    'orange-start' : (14, 0),
    'blue-start' : (11, 0),
    
    # Ghost initial moves to skip
    'red-initial-frozen' : 0,
    'pink-initial-frozen' : 3,
    'orange-initial-frozen' : 6,
    'blue-initial-frozen' : 10,
    
    # Game settings
    'initial-lives' : 3,
    'lives-position' : (175, 560),
    'lives-offset' : 40,
    'player-speed' : 100,
    'player-moves' : 5,
    'player-boost-moves' : 10,
    
    # Snowflakes
    'initial-snowflakes' : 4,
    'snowflakes-position' : (650, 60),
    'snowflakes-offset' : 40,

    # Boosts
    'initial-boosts' : 3,
    'boosts-position' : (650, 230),
    'boosts-offset' : 40,
    
    # Background
    'bg-position' : None,
    
    # Level selection
    'active-levels' : ['level-1', 'level-2', 'level-3'],
    'level-block-width' : 500,
    'level-block-height' : 100,
    'level-block-position' : (400, 320),
    'level-title' : 'Unknown',
    'level-title-font-size' : 24,
    'level-title-colour' : (255, 255, 0, 255),
    'level-title-offset' : (0, 75),

    # Difficulty selection
    'difficulty-block-width' : 300,
    'difficulty-block-height' : 100,
    'difficulty-block-position' : (400, 200),
    'difficulty-font-size' : 18,
    'difficulty-colour' : (255, 255, 0, 255),
    
    }),

    ### Level Start ###
    
    'level-start' : ('main', {
        # Grid
        'background' : 'lstart-background',
        'grid-origin' : (245, 320),
        'grid-size' : (28, 28),        
        'bg-position' : (400, 390),
        
        # Start
        'start' : (5, 2), 
        'player-moves' : 5,

        'ghost-moves' : 5,

        # Ghost start locations
        'red-start' : (0, 0),
        'pink-start' : (0, 4),
        'orange-start' : (10, 0),
        'blue-start' : (10, 4),

        # Ghost initial moves to skip
        'red-initial-frozen' : 0,
        'pink-initial-frozen' : 0,
        'orange-initial-frozen' : 0,
        'blue-initial-frozen' : 0,
        
        # The game board
        'board' : [
            [2,1,1,1,1,1,1,1,1,1,2],
            [1,X,X,1,X,X,X,1,X,X,1],
            [1,1,1,1,X,1,X,1,1,1,1],
            [1,X,X,1,X,X,X,1,X,X,1],
            [2,1,1,1,1,1,1,1,1,1,2],
        ], 
    }),

    ### Level Tutorial ###
    
    'level-tutorial' : ('main', {
        
        # Help text
        'help-position' : (200, 130),
        'help-size' : (300, 100),
        'help-back-colour' : (255, 255, 255, 255),
        'help-font-size' : 20,
        'help-font-colour' : (0, 255, 0, 255),
        
        # Timing
        'tutorial-step-time' : 1000,
        
        # Score, moves and lives off the screen
        'score-position' : (175, -150),
        'moves-position' : (476, -150),
        'lives-position' : (175, -150),

        # Snowflakes
        'snowflakes-position' : (650, 160),
        # Boosts
        'boosts-position' : (650, 320),

        # Grid
        'background' : 'tutorial-background',
        'grid-origin' : (210, 180),
        'grid-size' : (28, 28),        
        'bg-position' : (395, 305),
        
        # Start
        'start' : (6, 8), 
        'player-moves' : 5,
        'initial-lives' : 10,
        'ghost-moves' : 5,

        # Ghost start locations
        'red-start' : (6, 4),
        'pink-start' : (6, 4),
        'orange-start' : (6, 4),
        'blue-start' : (6, 4),

        # Ghost initial moves to skip
        'red-initial-frozen' : 0,
        'pink-initial-frozen' : 2,
        'orange-initial-frozen' : 3,
        'blue-initial-frozen' : 4,
        
        # The game board
        'board' : [
            [2,1,1,1,1,1,1,1,1,1,1,1,2],
            [1,X,X,X,1,1,1,1,1,X,X,X,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,X,1,1,1,X,1,X,1,1,1,X,1],
            [1,X,X,X,1,X,1,X,1,X,X,X,1],
            [1,X,1,1,1,X,X,X,1,1,1,X,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,X,X,X,1,1,1,1,1,X,X,X,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1],
        ], 
    }),

    ### Level -1 Debugging level ###
    
    'level--1' : ('main', {
        # Grid
        'background' : 'l0-background',
        'grid-origin' : (183, 62),
        'grid-size' : (28, 28),        
        
        # Start
        'start' : (3, 7), 
        'player-moves' : 5,

        'ghost-moves' : 5,
        'mode-initial' : 'fright',

        # Ghost start locations
        'red-start' : (2, 4),
        'pink-start' : (6, 4),
        'orange-start' : (4, 0),
        'blue-start' : (6, 0),

        # Ghost initial moves to skip
        'red-initial-frozen' : 0,
        'pink-initial-frozen' : 3,
        'orange-initial-frozen' : 6,
        'blue-initial-frozen' : 8,
        
        # The game board
        'board' : [
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,2,X,1,1,1],
            [1,1,X,1,X,0,1,1],
            [1,1,X,1,X,1,1,1],
            [1,1,1,0,1,1,1,1],
        ], 
    }),

    ### Level -2 Debugging level ###
    
    'level--2' : ('level--1', {
        # The game board
        'board' : [
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,X,0,0,0],
            [0,0,0,0,X,0,0,0],
            [0,0,0,0,0,1,1,1],
        ], 
    }),
    

    ### Level 0 ###
    
    'level-0' : ('main', {
        # Grid
        'background' : 'l0-background',
        'grid-origin' : (183, 62),
        'grid-size' : (28, 28),        
        
        # Start
        'start' : (8, 9), 
        
        # The game board
        'board' : 17*[[1]*15], 
    }),
    

    ### Level 1 ###

    'level-1' : ('main', {
        # Grid
        'level-title' : 'Classic Maze',
        'background' : 'l1-background',
        'grid-origin' : (190, 62),
        'grid-size' : (28, 28),        
        
        # Start
        'start' : (7, 9),  
        
        # The game board
        'board' : [
            [1,1,1,1,1,1,1,X,1,1,1,1,1,1,1],
            [2,X,X,1,X,X,1,X,1,X,X,1,X,X,2],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,X,X,1,X,1,X,X,X,1,X,1,X,X,1],
            [1,1,1,1,X,1,1,X,1,1,X,1,1,1,1],
            [X,X,X,1,X,X,1,X,1,X,X,1,X,X,X],
            [X,X,X,1,X,1,1,1,1,1,X,1,X,X,X],
            [T,0,0,1,1,1,X,0,X,1,1,1,0,0,T],
            [X,X,X,1,X,1,X,X,X,1,X,1,X,X,X],
            [X,X,X,1,X,1,1,0,1,1,X,1,X,X,X],
            [1,1,1,1,1,1,1,X,1,1,1,1,1,1,1],
            [1,X,X,1,X,X,1,X,1,X,X,1,X,X,1],
            [1,2,X,1,1,1,1,1,1,1,1,1,X,2,1],
            [X,1,X,1,X,1,X,X,X,1,X,1,X,1,X],
            [1,1,1,1,X,1,1,X,1,1,X,1,1,1,1],
            [1,X,X,X,X,X,1,X,1,X,X,X,X,X,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],

        # Ghost start locations
        'red-start' : (7, 7),
        'pink-start' : (7, 7),
        'orange-start' : (7, 7),
        'blue-start' : (7, 7),
        
    }),
    
    ### Level 2 ###
    
    'level-2' : ('level-1', {
        'level-title' : 'Ghost Frenzy',
        'background' : 'l2-background',

        # Start
        'start' : (7, 8),  

        # Ghost start locations
        'red-start' : (7, 2),
        'pink-start' : (7, 14),
        'orange-start' : (2, 8),
        'blue-start' : (12, 8),

        # Ghost initial moves to skip
        'red-initial-frozen' : 0,
        'pink-initial-frozen' : 2,
        'orange-initial-frozen' : 3,
        'blue-initial-frozen' : 4,

        # The game board
        'board' : [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,X,X,X,X,1,X,X,X,1,X,X,X,X,1],
            [1,1,2,X,1,1,X,0,X,1,1,X,2,1,1],
            [1,X,1,X,1,X,X,0,X,X,1,X,1,X,1],
            [1,X,1,1,1,1,1,1,1,1,1,1,1,X,1],
            [1,X,X,1,X,X,X,1,X,X,X,1,X,X,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,X,X,X,1,X,X,X,1,X,1,X,X,X,1],
            [1,X,0,0,1,X,1,0,1,X,1,0,0,X,1],
            [1,X,X,X,1,X,1,X,X,X,1,X,X,X,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,X,X,1,X,X,X,1,X,X,X,1,X,X,1],
            [1,X,1,1,1,1,1,1,1,1,1,1,1,X,1],
            [1,X,1,X,1,X,X,0,X,X,1,X,1,X,1],
            [1,1,2,X,1,1,X,0,X,1,1,X,2,1,1],
            [1,X,X,X,X,1,X,X,X,1,X,X,X,X,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],

    
    }),
    
    ### Level 3 ###
    
    'level-3' : ('level-1', {
        'level-title' : 'Corner Maze',
        'background' : 'l3-background',

        # Start
        'start' : (7, 8),  

        # Ghost start locations
        'red-start' : (2, 2),
        'pink-start' : (12, 14),
        'blue-start' : (2, 14),
        'orange-start' : (12, 2),

        # Ghost initial moves to skip
        'red-initial-frozen' : 0,
        'pink-initial-frozen' : 1,
        'orange-initial-frozen' : 2,
        'blue-initial-frozen' : 3,

        # The game board
        'board' : [
            [1,1,1,1,2,X,1,1,1,X,2,1,1,1,1],
            [1,X,X,X,1,X,1,X,1,X,1,X,X,X,1],
            [1,X,0,0,1,1,1,X,1,1,1,0,0,X,1],
            [1,X,X,X,1,X,1,1,1,X,1,X,X,X,1],
            [1,1,1,1,1,X,X,1,X,X,1,1,1,1,1],
            [X,X,1,X,1,X,1,1,1,X,1,X,1,X,X],
            [1,1,1,X,1,1,1,X,1,1,1,X,1,1,1],
            [1,X,X,X,X,1,X,X,X,1,X,X,X,X,1],
            [1,1,1,1,1,1,1,0,1,1,1,1,1,1,1],
            [X,X,X,X,1,X,1,X,1,X,1,X,X,X,X],
            [X,1,1,1,1,X,1,X,1,X,1,1,1,1,X],
            [X,1,X,X,X,X,1,X,1,X,X,X,X,1,X],
            [1,1,1,1,1,X,1,1,1,X,1,1,1,1,1],
            [1,X,X,X,1,X,1,X,1,X,1,X,X,X,1],
            [1,X,0,0,1,1,1,X,1,1,1,0,0,X,1],
            [1,X,X,X,1,X,1,X,1,X,1,X,X,X,1],
            [2,1,1,1,1,X,1,1,1,X,1,1,1,1,2],
        ],    
    }),

    '__default__' : 'main',

})

G = theme.getProperty
