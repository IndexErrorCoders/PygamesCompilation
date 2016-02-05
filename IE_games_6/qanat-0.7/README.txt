QANAT
-----

A shoot-em-up inspired by the classic Galaxians game. Repel waves of invaders using your gun turret. Manage the temperature of the turret to avoid overheating.


Music provided by:
    http://freemusicarchive.org/music/Anitek/Mind_Express/05_-_Light-year
    http://freemusicarchive.org/music/Anitek/Mind_Express/07_-_Contact
    http://freemusicarchive.org/music/Anitek/Mind_Express/01_-_Calling
    
Fonts provided by:
    http://openfontlibrary.org/font/ramasuri
    http://openfontlibrary.org/font/douar-outline
    http://openfontlibrary.org/font/berenika
    
Sounds provided by:
    http://www.freesound.org/people/Jovica/sounds/11453/
    http://www.freesound.org/people/Bertrof/sounds/131662/
    http://www.freesound.org/people/BMacZero/sounds/94130/
    http://www.freesound.org/people/mattpavone/sounds/76177/
    http://www.freesound.org/people/Bliss/sounds/8098/
    http://www.freesound.org/people/CGEffex/sounds/100773/
    http://www.freesound.org/people/Corsica_S/sounds/18634/
    http://www.freesound.org/people/belloq/sounds/41459/
    http://www.freesound.org/people/cfork/sounds/26875/
    http://www.freesound.org/people/unfa/sounds/156498/
    
Requires: Python 2.6+, pygame 1.9+

To run the game in a window:

    python qanat.py

For full screen mode

    python qanat.py -F


Thanks for playing!

Paul Paterson
http://perpetualpyramid.com



What's new
----------

0.1 
    First release
0.2
    Added "Fire Aliens" - keep their distance and fire directly at you
    Added four more waves
    Ammo regenerates now when you stay still
    Ammo usage increases every time you complete all the waves
    Reduced gun lockout time due to temperature to 5s
    Get new lives for every 10,000 points scored
0.3
    Added achievements to the game
0.4 
    Aliens now crash to earth after being shot. Crashing aliens will destroy your ship.
    Updated ship icon. Ship changes appearance when the gun is too hot.
    Can run the game in full screen mode (run with "python qanat.py -F").
    Fixed bug when starting the game. Bombs dropped during the intro could sometimes kill you.
0.5
    Removed restriction on ammo
    Changed the impact of overheating. Now the gun fires slower bullets which sometimes fragment
    Added sound and visual cue when extra life is gained
    Added animation when the player ship is destroyed
    Fixed bug where sounds might not play (too few pygame channels used)
    Tweaked alien motion
0.6
    Implemented online high score table system
0.7
    New "Mothership" levels - aliens gradually emerge from the mothership to attack you
    New "Bomber" alien - drops a bomb that explodes in fragments at a certain height
    Many extra levels - now 25 in total
    Added pause - Press P to pause gameplay

