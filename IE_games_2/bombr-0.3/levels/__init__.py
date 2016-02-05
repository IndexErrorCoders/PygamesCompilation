import glob
import os

# Music and names
LEVELS = [
    ('The Plus', 'main-1'),
    ('Curly', 'main-2'),
    ('Eye', 'main-3'),
    ('Checkers', 'main-4'),
    ('Big Boy', 'main-1'),
    ('Random', 'main-4'),
]

LEVEL_FILES = glob.glob(os.path.join('levels', 'level-*.tmx'))
LEVEL_FILES.sort()
LEVEL_FILES.append(os.path.join('levels', 'bomber-out.xml'))

RANDOM_LEVEL = len(LEVEL_FILES)