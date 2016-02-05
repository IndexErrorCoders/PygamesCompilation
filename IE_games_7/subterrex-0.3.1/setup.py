#!/usr/bin/env python


"""Distutils distribution file"""


from setuptools import setup, find_packages

import game.common
import sys

if sys.argv[1] == 'install':
    print '** Do not install from setup.py. Just run the game by typing "python subterrex.py"'
    sys.exit(1)

setup(name='subterrex',
      version=game.common.version,
      scripts=['subterrex.py'], 
      entry_points = {
        'console_scripts' : [
        ]
      },      
      description='A pygame based game of subterranean exploration',
      author='Paul Paterson',
      author_email='ppaterson@gmail.com',
      url='http://perpetualpyramid.com/drupal/?q=subterrex_game',
      download_url=('URLTOGAME-%s.tar.gz' % game.common.version),

      include_package_data=True,
      zip_safe=False,

      packages=[
        'serge', 'serge.blocks', 'serge.tools', 'serge.tools.template', 'game',
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
SubTerrex
---------

Explore deep, dark caves and caverns.

Requires: Python 2.7+, pygame 1.9+, pymunk and sci-py

''',
         )
     
