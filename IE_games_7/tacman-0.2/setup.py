#!/usr/bin/env python


"""Distutils distribution file"""


from setuptools import setup, find_packages

import game.common


setup(name='tacman',
      version=game.common.version,
      scripts=['tacman.py'], 
      entry_points = {
        'console_scripts' : [
            'tacman = tacman.tacman',
        ]
      },
      description='A tactical, turn-based clone on PACMAN',
      author='Paul Paterson',
      author_email='ppaterson@gmail.com',
      url='http://www.perpetualpyramid/tacman.html',
      download_url=('http://perpetualpyramid.com/tacman-%s.tar.gz' % game.common.version),

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
         'pygame', 'networkx',
       ],
       long_description='''\
TACMAN
------

A turn-based, tactical version of PACMAN.

Play a PACMAN clone where the action is turn based. You move and then the 
ghosts move. The turn-based action adds additional tactical elements to the
game and allows you to plan ahead and outwit the ghosts!

Requires: Python 2.6+, pygame 1.9+, networkx

''',
         )
     