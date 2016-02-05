from optparse import OptionParser

import aranara.__main__
import aranara.engine.common

parser = OptionParser()
parser.add_option("-f", "--framerate", dest="framerate", default=60, type="int",
                  help="framerate to use for the engine")
parser.add_option("-l", "--log", dest="log", default=40, type="int",
                  help="logging level")
parser.add_option("-c", "--cheat", dest="cheat", default=False, action="store_true",
                  help="run in cheat mode - all levels are available right away")
parser.add_option("-m", "--music-off", dest="musicoff", default=False, action="store_true",
                  help="start with music silenced")
parser.add_option("-S", "--straight", dest="straight", default=False, action="store_true",
                  help="go straight into game, bypassing start screen")

(options, args) = parser.parse_args()
aranara.engine.common.LEVEL = options.log


if __name__ == "__main__":
    aranara.__main__.main(options)
