#!/usr/bin/env python


"""Distutils distribution file"""


from setuptools import setup, find_packages

import game.common
import sys

if sys.argv[1] == 'install':
    print '** Do not install from setup.py. Just run the game by typing "python %(name_lower)s.py"'
    sys.exit(1)

setup(name='%(name)s',
      version=game.common.version,
      scripts=['%(name_lower)s.py'], 
      entry_points = {
        'console_scripts' : [
            '%(name_lower)s = %(name_lower)s.%(name_lower)s',
        ]
      },      
      description='GAMEDESCRIPTION',
      author='AUTHOR',
      author_email='EMAIL',
      url='URL',
      download_url=('URLTOGAME-%%s.tar.gz' %% game.common.version),

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
%(name)s
%(under)s

Requires: Python 2.6+ and pygame 1.9+

''',
         )
     
