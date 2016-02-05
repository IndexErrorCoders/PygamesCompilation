'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    return os.path.join(data_dir, filename)

def picpath(object, animation, frame = None):
    if (frame == None):
      return os.path.join(data_dir, "pictures", object + "_" + animation + ".png")
    else:
      return os.path.join(data_dir, "pictures", object + "_" + animation + "_" + str(frame) + ".png")

def animpath(object, animation):
    return os.path.join(data_dir, "pictures", object + "_" + animation + ".txt")

def levelpath(levelname):
    return os.path.join(data_dir, "levels", levelname + ".txt")

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

