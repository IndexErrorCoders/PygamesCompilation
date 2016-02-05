#!/usr/bin/env python


"""Distutils distribution file"""


from setuptools import setup, find_packages

import game.common
import sys

if sys.argv[1] == 'install':
    print '** Do not install from setup.py. Just run the game by typing "python bombr.py"'
    sys.exit(1)

setup(name='bombr',
      version=game.common.version,
      scripts=['bombr.py'],
      entry_points = {
        'console_scripts' : [
            'bombr = bomberman.bombr',
        ]
      },      
      description='A Bomberman Clone',
      author='Paul Paterson',
      author_email='ppaterson@gmail.com',
      url='URL',
      download_url=('bomberman-%s.zip' % game.common.version),

      include_package_data=True,
      zip_safe=False,

      packages=[
        'serge', 'serge.blocks', 'serge.tools', 'serge.tools.template', 'game',
        'serge.blocks.concurrent', 'serge.blocks.concurrent.futures',
        'serge.blocks.fysom', 'levels', 'terrain', 'terrain.builders', 'terrain.renderers'
      ],
      package_dir={'':'.'},

      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Puzzle Games",
        ],
       install_requires=[
       # 'pygame', 'networkx', 'pymunk',
       ],
       long_description='''\
BOMBR
-----

A Bomberman clone. Play against the smack-talking AI over
5 levels of frantic bombing action.


Requires: Python 2.6+, pygame 1.9+, NetworkX 1.8 (included)

To run the game:

    python bombr.py


Thanks for playing!

''',
         )
     
