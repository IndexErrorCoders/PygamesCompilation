#!/usr/bin/env python


"""Distutils distribution file"""


from setuptools import setup, find_packages

import game.common
import sys

if sys.argv[1] == 'install':
    print '** Do not install from setup.py. Just run the game by typing "python qanat.py"'
    sys.exit(1)
    
setup(name='qanat',
      version=game.common.version,
      scripts=['qanat.py'], 
      entry_points = {
        'console_scripts' : [
            'qanat = galaxian.qanat',
        ]
      },      
      description='A shoot-em-up inspired by the classic Galaxians game. Repel waves of invaders using your gun turret. Manage the temperature of the turret to avoid overheating and watch your ammo level to avoid running out in the later levels.',
      author='Paul Paterson',
      author_email='ppaterson@gmail.com',
      url='http://perpetualpyramid.com/qanat.html',
      download_url=('http://perpetualpyramid.com/qanat-%s.tar.gz' % game.common.version),

      include_package_data=True,
      zip_safe=False,

      packages=[
        'serge', 'serge.blocks', 'serge.tools', 'serge.tools.template', 'game',
        'serge.blocks.concurrent', 'serge.blocks.concurrent.futures'
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
QANAT
-----

A shoot-em-up inspired by the classic Galaxians game. Repel waves of invaders using your gun turret. Manage the temperate of the turret to avoid overheating and watch your ammo level to avoid running out in the later levels.

Requires: Python 2.6+ and pygame 1.9+

''',
         )
     
