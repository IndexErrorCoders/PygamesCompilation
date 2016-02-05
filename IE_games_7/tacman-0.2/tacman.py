"""Main startup file for tacman"""

from optparse import OptionParser
import sys
import os

if sys.version_info[0] == 3:
    print 'Python 3 is not supported'
    sys.exit(1)
elif sys.version_info[1] <= 5:
    print 'Python 2.6+ is required'
    sys.exit(1)

import serge.common


parser = OptionParser()
parser.add_option("-f", "--framerate", dest="framerate", default=60, type="int",
                  help="framerate to use for the engine")
parser.add_option("-p", "--profile", dest="profile", default=False, action="store_true",
                  help="profile the game for speed")
parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true",
                  help="run in debug mode")
parser.add_option("-c", "--cheat", dest="cheat", default=False, action="store_true",
                  help="run in cheat mode - all levels are available right away")
parser.add_option("-m", "--music-off", dest="musicoff", default=False, action="store_true",
                  help="start with music silenced")
parser.add_option("-l", "--level", dest="level", default=1, type="int",
                  help="level to start on")
parser.add_option("-v", "--developer", dest="developer", default=False, action="store_true",
                  help="run in developer mode, showing developer information")
parser.add_option("-s", "--straight", dest="straight", default=False, action="store_true",
                  help="go straight to game, bypassing the start screen")
parser.add_option("-t", "--tutorial", dest="tutorial", default=False, action="store_true",
                  help="go straight to tutorial, bypassing the start screen")
parser.add_option("-n", "--number", dest="number", default=5, type="int",
                  help="number of moves the player can make")
                  
                 
(options, args) = parser.parse_args()

import game.main

if options.profile:
    import cProfile, pstats
    cProfile.run('game.main.main(options, args)', 'profile')
    p = pstats.Stats('profile')
    print p.sort_stats('cumulative').print_stats(100)
else:
    game.main.main(options, args)
