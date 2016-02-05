"""Simple way to create a template for a game"""

from optparse import OptionParser
import sys
import os
import shutil


sys.path.append(os.path.abspath('.'))
import serge

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-n", "--name", dest="name", default='game', type="str",
                      help="name of the game")
    parser.add_option("-l", "--location", dest="location", default=os.curdir, type="str",
                      help="location to place the game")
    parser.add_option("-f", "--force", dest="force", default=False, action="store_true",
                      help="overwrite existing folder (all folder contents will be deleted)")
    parser.add_option("-p", "--pymunk", dest="pymunk", default=False, action="store_true",
                      help="the game requires pymunk")
    parser.add_option("-w", "--width", dest="width", default=800, type="int",
                      help="width of the screen")
    parser.add_option("-v", "--height", dest="height", default=600, type="int",
                      help="height of the screen")


def getSergePath():
    """Return path to serge"""
    return os.path.dirname(serge.__file__)


def createFolderStructure(name, location, force):
    """Create the folders"""
    base = os.path.join(location, name.lower())
    #
    # Watch out for when the location is already there
    if os.path.exists(base):
        if not force:
            result = raw_input('"%s" already exists, overwrite (n)?' % base)
            if result.lower() != 'y':
                print 'Game not created'
                sys.exit(1)
        shutil.rmtree(base)
        #
    os.mkdir(base)
    for folder in ['design', 'game', 'graphics', 'sound', 'music', 'fonts', 'screenshots']:
        os.mkdir(os.path.join(base, folder))
    #
    # Put file in certain locations that could end up empty. This prevents errors during
    # packaging
    for folder in ['screenshots', 'music']:
        with file(os.path.join(base, folder, 'readme.txt'), 'w') as f:
            f.write('This file included to prevent folder being empty\n')
    #
    return base


def copyTemplate(path, src, dest, names=None, binary=False):
    """Copy a template file"""
    use_names = names if names else {}
    binary = 'b' if not names else ''
    with file(os.path.join(getSergePath(), *src), 'r' + binary) as f:
        text = f.read()
    with file(os.path.join(path, *dest), 'w' + binary) as f:
        if names:
            result = text % use_names
        else:
            result = text
        if not binary:
            result = result.replace('@', '%')
        f.write(result)


def createLicenseFile(path):
    """Create the license file"""
    copyTemplate(path, ['license.txt'], ['license.txt'])


def createReadMe(path, name):
    """Create the readme file"""
    copyTemplate(path, ['tools', 'template', 'README.txt'], ['README.txt'],
                 {'name': name, 'name_lower': name.lower(), 'under': '-' * len(name)})


def createEntryModule(path, name, pymunk):
    """Create the main entry module"""
    if pymunk:
        pymunk_code = '''if not serge.common.PYMUNK_OK:
    print 'Pymunk is required'
    sys.exit(1)
'''
    else:
        pymunk_code = ''
        #
    copyTemplate(path, ['tools', 'template', 'startup.py'], ['%s.py' % name.lower()],
                 {'name': name, 'pymunk_code': pymunk_code})

    copyTemplate(path, ['tools', 'template', '__init__.py'], ['game', '__init__.py'],
                 {'name': name, })
    copyTemplate(path, ['tools', 'template', '__init__.py'], ['__init__.py'],
                 {'name': name, })


def createMainModule(path, name):
    """Create the main module"""
    copyTemplate(path, ['tools', 'template', 'main.py'], ['game', 'main.py'],
                 {'name': name, })


def createCommonModule(path, name):
    """Create the common module"""
    copyTemplate(path, ['tools', 'template', 'common.py'], ['game', 'common.py'],
                 {'name': name, })


def createThemeModule(path, name, width, height):
    """Create the theme module"""
    copyTemplate(path, ['tools', 'template', 'theme.py'], ['game', 'theme.py'],
                 {'name': name, 'width': width, 'height': height})


def createWorldModule(path, world, name):
    """Create a world module"""
    copyTemplate(path, ['tools', 'template', '%sscreen.py' % world], ['game', '%sscreen.py' % world],
                 {'name': name, })


def createGraphicsFiles(path, name):
    """Create the graphics"""
    copyTemplate(path, ['tools', 'template', 'icon.png'], ['graphics', 'icon.png'])
    copyTemplate(path, ['tools', 'template', 'help-text.png'], ['graphics', 'help-text.png'], binary=True)
    copyTemplate(path, ['tools', 'template', 'music-1.png'], ['graphics', 'music-1.png'], binary=True)
    copyTemplate(path, ['tools', 'template', 'music-2.png'], ['graphics', 'music-2.png'], binary=True)
    copyTemplate(path, ['tools', 'template', 'achievement-1.png'], ['graphics', 'achievement-1.png'], binary=True)
    copyTemplate(path, ['tools', 'template', 'achievement-2.png'], ['graphics', 'achievement-2.png'], binary=True)


def createClickFile(path, name):
    """Create the click sound"""
    copyTemplate(path, ['tools', 'template', 'click.wav'], ['sound', 'click.wav'])


def createSetupModule(path, name):
    """Create the setup module"""
    copyTemplate(path, ['tools', 'template', 'setup.py'], ['setup.py'],
                 {'name': name, 'name_lower': name.lower(), 'under': '-' * len(name)})
    copyTemplate(path, ['tools', 'template', 'py2exe_setup.py'], ['py2exe_setup.py'],
                 {'name': name, 'name_lower': name.lower(), 'under': '-' * len(name)})
    copyTemplate(path, ['tools', 'template', 'MANIFEST.in'], ['MANIFEST.in'])


def createSergeLink(path):
    """Create the link to the serge folder"""
    os.symlink(getSergePath(), os.path.join(path, 'serge'))


def main(name, location, force, pymunk, width, height):
    """Create the template"""
    path = createFolderStructure(name, location, force)
    createLicenseFile(path)
    createReadMe(path, name)
    createEntryModule(path, name, pymunk)
    createMainModule(path, name)
    createCommonModule(path, name)
    createThemeModule(path, name, width, height)
    createWorldModule(path, 'main', name)
    createWorldModule(path, 'start', name)
    createWorldModule(path, 'help', name)
    createWorldModule(path, 'credits', name)
    createGraphicsFiles(path, name)
    createClickFile(path, name)
    createSetupModule(path, name)
    createSergeLink(path)
    print 'Game created'


if __name__ == '__main__':
    (options, args) = parser.parse_args()
    main(
        name=options.name,
        location=options.location,
        force=options.force,
        pymunk=options.pymunk,
        width=options.width,
        height=options.height,
    )