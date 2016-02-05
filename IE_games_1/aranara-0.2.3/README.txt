Your Game Title
===============

Entry in PyWeek #12  <http://www.pyweek.org/12/>
URL: http://pyweek.org/e/aranara
Team: aranara (leave the "Team: bit")
Members: PaulPaterson (leave the "Members: bit")
License: see LICENSE.txt

Dependencies
------------

- pyglet
- pymunk
- avbin for the music

Running the Game
----------------

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Othewise open a terminal / console and "cd" to the game directory and run:

  python run_game.py


How to Play the Game
--------------------

- ESCAPE quits
- CTRL-S takes a screenshot
- CTRL-P pauses and unpauses the engine


Development notes 
-----------------

Creating a source distribution with::

   python setup.py sdist

You may also generate Windows executables and OS X applications::

   python setup.py py2exe
   python setup.py py2app

Upload files to PyWeek with::

   python pyweek_upload.py

Upload to the Python Package Index with::

   python setup.py register
   python setup.py sdist upload

