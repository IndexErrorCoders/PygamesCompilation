"""Our main visual theme"""

import serge.blocks.themes

theme = serge.blocks.themes.Manager()
theme.load({
    'main' : ('', {
    
    # Main properties
    'screen-height' : %(height)d,
    'screen-width' : %(width)d,
    'screen-title' : '%(name)s',
    'screen-icon' : 'icon',
    'screenshot-size' : (0, 0, %(width)d, %(height)d),
    
    # Mute button
    'mute-button-alpha' : 0.4,
    'mute-button-position' : (30, 30),
    'pre-stop-pause' : 0.5,
    
    # FPS display
    'fps-x' : 50,
    'fps-y' : %(height)d-30,
    'fps-colour' : (255, 255, 0),
    'fps-size' : 12,
    
    }),
    
    'start-screen' : ('main', {
        # Logo and title
        'logo-position' : (%(width)d/2, 140),
        'title' : '%(name)s',
        'title-position' : (%(width)d/2, 300),
        'title-colour' : (255, 255, 255, 255),
        'title-font-size' : 36,
        # Version text
        'version-position' : (%(width)d/2, %(height)d-10),
        'version-colour' : (50, 50, 50),
        'version-font-size' : 12,
        # Start button
        'start-position' : (%(width)d/2, %(height)d-120),
        'start-colour' : (255, 255, 0, 255),
        'start-font-size' : 48,
        # Help button
        'help-position' : (%(width)d-100, %(height)d-40),
        'help-colour' : (0, 255, 0, 255),
        'help-font-size' : 24,
        # Credits button
        'credits-position' : (100, %(height)d-40),
        'credits-colour' : (0, 255, 0, 255),
        'credits-font-size' : 24,    
        # Achievements button
        'achievements-position' : (%(width)d/2, %(height)d-40),
        'achievements-colour' : (0, 255, 0, 255),
        'achievements-font-size' : 24,    
    }),

    'sub-screen' : ('start-screen', {
        # Logo and title
        'logo-position' : (%(width)d/2-50, 40),
        'title-position' : (%(width)d/2+50, 40),
        'title-colour' : (255, 255, 255, 255),
        'title-font-size' : 36,
        # Back button
        'back-colour' : (255, 255, 0, 255),
        'back-font-size' : 24,
    }),
    'help-screen' : ('sub-screen', {
        # Help text
        'text-position' : (%(width)d/2, %(height)d/2),
    }),
    'credits-screen' : ('sub-screen', {
        # Author
        'author-title-colour' : (0, 220, 220),
        'author-title-font-size' : 24,
        'author-title-position' : (%(width)d/2, 110),
        'author-colour' : (255, 255, 0),
        'author-font-size' : 32,
        'author-position' : (%(width)d/2, 150),
        'url-colour' : (255, 0, 0),
        'url-font-size' : 14,
        'url-position' : (%(width)d/2, 170),
        # Music
        'music-title1-colour' : (0, 220, 220),
        'music-title1-font-size' : 20,
        'music-title1-position' : (%(width)d/2, 220),
        'music-title2-colour' : (0, 220, 220),
        'music-title2-font-size' : 18,
        'music-title2-position' : (%(width)d/2, 240),
        'music-colour' : (255, 255, 0),
        'music-font-size' : 16,
        'music-position' : (%(width)d/2, 260),
        # Sound
        'sound-title1-colour' : (0, 220, 220),
        'sound-title1-font-size' : 20,
        'sound-title1-position' : (%(width)d/2, 340),
        'sound-title2-colour' : (0, 220, 220),
        'sound-title2-font-size' : 18,
        'sound-title2-position' : (%(width)d/2, 360),
        # Built using        
        'built-title-colour' : (0, 220, 220),
        'built-title-font-size' : 20,
        'built-title-position' : (%(width)d/4, 420),
        'built-colour' : (255, 255, 0),
        'built-font-size' : 16,
        'built-position' : (%(width)d/4, 440),
        # Engine
        'engine-title-colour' : (0, 220, 220),
        'engine-title-font-size' : 20,
        'engine-title-position' : (%(width)d/4, 480),
        'engine-colour' : (255, 255, 0),
        'engine-font-size' : 16,
        'engine-position' : (%(width)d/4, 500),
        # Engine version
        'engine-version-colour' : (75, 75, 0),
        'engine-version-font-size' : 10,
        'engine-version-position' : (%(width)d/4, 520),
        # Fonts
        'font-title1-colour' : (0, 220, 220),
        'font-title1-font-size' : 20,
        'font-title1-position' : (%(width)d*3/4, 420),
        'font-title2-colour' : (0, 220, 220),
        'font-title2-font-size' : 18,
        'font-title2-position' : (%(width)d*3/4, 440),
        'font-colour' : (255, 255, 0),
        'font-font-size' : 16,
        'font-position' : (%(width)d*3/4, 460),
        #
        'back-position' : (100, %(height)d-40),

    }),
    
    'achievements' : ('main', {
        # Properties of the achievements system
        'banner-duration' : 5,
        'banner-position' : (175, 525),
        'banner-size' : (300, 50),
        'banner-backcolour' : (0, 0, 0, 50),
        'banner-font-colour' : (255, 255, 0, 255),
        'banner-name-size' : 14,
        'banner-description-size' : 8,
        'banner-name-position' : (-100, -18),
        'banner-description-position' : (-100, 0),
        'banner-font-name' : 'DEFAULT',
        'banner-graphic-position' : (-125, 0),
        
        'time-colour' : (255, 255, 255, 100),
        'time-size' : 10,
        'time-position' : (-100, 24),
        
        'logo-position' : (400, 50),
        'screen-background-sprite' : None,
        'screen-background-position' : (400, 300),
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

    '__default__' : 'main',

})

G = theme.getProperty
