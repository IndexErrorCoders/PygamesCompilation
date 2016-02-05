"""Runs the main terrain generation"""

from optparse import OptionParser
import os
import random

import loggable
import generator


parser = OptionParser()
parser.add_option("-b", "--base", dest="base", type="string", default="",
                  help="base directory for files")
parser.add_option("-i", "--input", dest="inputfile", type="string", default="terrain.xml",
                  help="input file with settings")
parser.add_option("-r", "--render", dest="renderfile", type="string", default="terrain.png",
                  help="rendered output file to generate")
parser.add_option("-n", "--render-name", dest="rendername", type="string", default="main",
                  help="renderer to use")
parser.add_option("-l", "--log", dest="log", default=40, type="int",
                  help="logging level")
parser.add_option("-s", "--seed", dest="seed", default=0, type="int",
                  help="seed for random number")
parser.add_option("-p", "--profile", dest="profile", default=False, action="store_true",
                  help="profile the application")


if __name__ == '__main__':
    options, args = parser.parse_args()
    loggable.logger.setLevel(options.log)

    log = loggable.getLogger("Terrain")
    log.info('Terrain is starting')

    if options.seed:
        log.debug('Using random seed %d' % options.seed)
        random.seed(options.seed)

    def J(filename):
        """Return path joined to the base"""
        return os.path.join(options.base, filename)

    gen = generator.Generator()

    if options.profile:
        import cProfile, pstats
        cProfile.run(
            'gen.generateLandscape(J(options.inputfile), J(options.renderfile), options.rendername)',
            'profile'
        )
        p = pstats.Stats('profile')
        print p.sort_stats('cumulative').print_stats(100)
    else:
        gen.generateLandscape(J(options.inputfile), J(options.renderfile), options.rendername)
