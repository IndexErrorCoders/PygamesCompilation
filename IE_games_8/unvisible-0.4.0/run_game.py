import optparse
import unvisible.__main__

parser = optparse.OptionParser()
parser.add_option("-l", "--log", dest="log", default=40, type="int",
                  help="logging level")
parser.add_option("-m", "--mute", dest="mute", default=False, action="store_true",
                  help="mute all sound and music")
parser.add_option("-s", "--speed", dest="speed", default=10, type="float",
                  help="speedup factor")

(options, args) = parser.parse_args()

if __name__ == "__main__":
    unvisible.__main__.main(options, args)
