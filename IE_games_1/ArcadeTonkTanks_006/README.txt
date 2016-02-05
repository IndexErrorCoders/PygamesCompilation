Arcade Tonk Tanks v. 0.0.6

This game has been tested using Python 2.5 & 2.6.1 and Pygame 1.8 & 1.9.1
                                on Linux & windows XT/Vista.

Look for the latest version on: http://www.pygame.org/project-Arcade+Tonk+Tanks-1078-2271.html
                            or: http://code.google.com/p/arcade-tonk-tanks/

Credits:
    * Programming & game design by Koen Lefever (koen.lefever@gmail.com); License: GPL 3.0
    * Graphics & explosion sound (boom.wav) by Marc Carson (marc@marccarson.com); License: Creative Commons CC-BY-SA
	* Explosion Graphics by David Howe (http://homepage.ntlworld.com/david.howe50/page16a.html)
    * Music "Only Depth" by Vladislav Malkov a.k.a. Artsense (http://www.myspace.com/artsensepsy)

Version history:
    * 0.0.1   : 2009-01-14 : game created by Koen Lefever
    * 0.0.2   : 2009-03-31 : prompt to ask if you want to play in full screen or in a window
    * 0.0.3   : 2009-04-01 : corrected filenames to work on case sensitive systems (Linux/UNIX)
    * 0.0.4   : 2009-04-01 : replaced math.trunc() by int() - this works on both Python 2.5 and 2.6
    * 0.0.5   : 2009-09-25 : added graphics by Marc Carson & music by Artsense
	* 0.0.5Win: 2009-09-28 : use freesansbold.ttf font
                             created MS Windows executable with py2exe, Nullsoft NSIS & HM NIS Edit
	* 0.0.6   : 2009-10-29 : too many bullets bug solved
      0.0.6-4 : 2009-11-02 : moved all global variables into module GameData
      0.0.6-5 : 2009-11-03 : moved all game classes & functions to their own modules
      0.0.6-6 : 2009-11-04 : moved what is supposed to be the AI into module DefaultBot
      0.0.6-8 : 2009-12-06 : added BattleGround(), scenery, water
      0.0.6-9 : 2009-12-09 : debugging, re-organizing code & cleaning up
      0.0.6-11: 2009-12-14 : added David Howe's explosion graphics 
  
To Do 
    * some code cleanup (this is my very first program in Python, and my first program in an OO language)
    * add an editor to create new mazes
    * add high score lists
    * add "presets" and the possibility to save your favourite combination of options
    * rewrite the game completely to support client/server multi-player