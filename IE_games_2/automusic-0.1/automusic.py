"""Main startup file for automusic"""

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
parser.add_option("-l", "--log", dest="log", default=40, type="int",
                  help="logging level")
parser.add_option("-p", "--profile", dest="profile", default=False, action="store_true",
                  help="profile the game for speed")
parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true",
                  help="run in debug mode")
parser.add_option("-c", "--cheat", dest="cheat", default=False, action="store_true",
                  help="run in cheat mode - all levels are available right away")
parser.add_option("-m", "--music-off", dest="musicoff", default=False, action="store_true",
                  help="start with music silenced")
parser.add_option("-S", "--straight", dest="straight", default=False, action="store_true",
                  help="go straight into game, bypassing start screen")
parser.add_option("-s", "--screenshot", dest="screenshot", default=False, action="store_true",
                  help="allow screenshots of the screen by pressing 's' during gameplay")
parser.add_option("-t", "--theme", dest="theme", default='', type='str',
                  help="settings (a=b,c=d) for the theme")
parser.add_option("-M", "--movie", dest="movie", default='', type='str',
                  help="record a movie of the game with the given filename")
parser.add_option("-D", "--drop", dest="drop", default=False, action="store_true",
                  help="drop into debug mode on an unhandled error")
parser.add_option("-H", "--high-score", dest="high_score", default=False, action="store_true",
                  help="recreate the high score table")

(options, args) = parser.parse_args()
serge.common.logger.setLevel(options.log)

import game.main

if options.drop:
    serge.common.installDebugHook()
    
if options.profile:
    import cProfile, pstats
    cProfile.run('game.main.main(options, args)', 'profile')
    p = pstats.Stats('profile')
    print p.sort_stats('cumulative').print_stats(100)
else:
    game.main.main(options, args)
