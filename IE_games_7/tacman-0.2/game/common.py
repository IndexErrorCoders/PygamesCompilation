"""Common elements"""

import pygame
import os
import sys

import serge.engine
import serge.common
import serge.blocks.scores

log = serge.common.getLogger('Game')
from theme import G

version = '0.2' 


# Check networkx
try:
    import networkx
except ImportError:
    print '\n\n\nError: networkx must be installed.\n\ntry: easy_install networkx\n\nor visit http://networkx.lanl.gov/download.html\n\n'
    sys.exit(1)
    
