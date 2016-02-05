"""Module to help publish games"""

from optparse import OptionParser
import sys
import os
import re
import subprocess
import shutil


def stopWith(msg):
    """Stop with a message"""
    print 'Failed: %s' % msg
    sys.exit(1)
    
parser = OptionParser()
parser.add_option("-d", "--dist", dest="dist", default=False, action='store_true',
                  help="create the dist file now")
parser.add_option("-g", "--game", dest="game", default=None, type='str',
                  help="the game to work with")
parser.add_option("-v", "--version", dest="version", default=None, type='str',
                  help="the version to work with")
parser.add_option("-t", "--test", dest="test", default=False, action='store_true',
                  help="test mode - continues through some failures")
parser.add_option("-b", "--base", dest="base", default='', type='str',
                  help="base folder for game")
parser.add_option("-x", "--type", dest="dist_type", default='sdist', type='str',
                  help="type of distribution, could be bdist_egg")                 
parser.add_option("-l", "--link", dest="link_folders", default='', type='str',
                  help="comma separated list of folders to link into the game folder to create dist (eg serge)")
parser.add_option("-p", "--public", dest="public", default='', type='str',
                  help="whether to copy resulting zip file to the public location")

(options, args) = parser.parse_args()

#
# Base location for the game folder
if not options.base:
    stopWith('Base folder must be set with -b option')
ROOT = options.base

#
# Get the right game
if not options.game:
    stopWith('Game must be set with -g option')

#
# Link folders
if options.link_folders:
    for folder_name in options.link_folders.split(','):
        name = folder_name.strip()
        src, dst = os.path.join(ROOT, name), os.path.join(ROOT, options.game, os.path.split(name)[1])
        print 'Linking %s: %s :: %s' % (name, src, dst)
        os.symlink(src, dst)

try:
    #
    # Import game
    root = os.path.join(ROOT, options.game)
    tmp = os.path.join(ROOT, 'publisher')
    sys.path.append(ROOT)
    os.chdir(root)
    print 'Inside %s' % root
    game_common = __import__('%s.game.common' % options.game).game.common
    version = game_common.version
    print 'Located game at %s' % game_common.__file__
    print 'Current version is %s' % game_common.version
    if options.version:
        print 'Using version %s' % options.version
        version = options.version
    #
    # Get the name from the setup file
    setup_text = file(os.path.join(root, 'setup.py'), 'r').read()
    name = re.match('.*name=\'(\w+)\'.*', setup_text, re.M+re.DOTALL).groups()[0]
    print 'Game name is "%s"' % name
    #
    # Check if we need to create the dist file
    if options.dist:
        print 'Updating egg info'
        result = subprocess.call(['python', os.path.join(root, 'setup.py'), 'egg_info'])
        if result != 0:
            stopWith('Updating egg info failed')
        print 'Making source distribution'
        result = subprocess.call(['python', os.path.join(root, 'setup.py'), options.dist_type])
        if result != 0:
            stopWith('Creating dist failed')

    #
    # Find dist files
    dist_base_name = ('%s-%s' % (name, version))
    dist_name = '%s-%s.tar.gz' % (name, version)
    dist_file = os.path.join(root, 'dist', dist_name)
    if not os.path.exists(dist_file):
        stopWith('The distribution file "%s" could not be found' % dist_file)
    print 'Found dist file "%s"' % dist_file

    #
    # Copying to public folder
    if options.public:
        print 'Copying distribution file to "%s"' % options.public
        shutil.copyfile(dist_file, os.path.join(options.public, dist_name))

finally:
    #
    # Make sure to clean up linked folders
    if options.link_folders:
        for folder_name in options.link_folders.split(','):
            name = folder_name.strip()
            print 'Unlinking %s' % name
            os.unlink(os.path.join(ROOT, options.game, os.path.split(name)[1]))