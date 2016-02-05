"""Piano instrument"""

name = 'Organ'
description = 'Organ sounds from Garage Band'

# Notes
C = 'organ-hc.wav'
D = 'organ-hd.wav'
E = 'organ-he.wav'
F = 'organ-hf.wav'
G = 'organ-hg.wav'
A = 'organ-ha.wav'
B = 'organ-hb.wav'
#
LC = 'organ-lc.wav'
LD = 'organ-ld.wav'
LE = 'organ-le.wav'
LF = 'organ-lf.wav'
LG = 'organ-lg.wav'
LA = 'organ-la.wav'
LB = 'organ-lb.wav'
#
FC = 'flute-c.wav'
FE = 'flute-e.wav'
FG = 'flute-g.wav'

notes = {
    'C': C,
    'D': D,
    'E': E,
    'F': F,
    'G': G,
    'A': A,
    'B': B,
    #
    'LC': LC,
    'LD': LD,
    'LE': LE,
    'LF': LF,
    'LG': LG,
    'LA': LA,
    'LB': LB,
    #
    'FC': FC,
    'FE': FE,
    'FG': FG,
}

cells = {
    # Bottom
    (0, -1): 'C',
    (1, -1): 'E',
    (2, -1): 'G',
    (3, -1): 'LC',
    (4, -1): 'LE',
    (5, -1): 'LG',
    (6, -1): 'B',
    # Top
    (0, 7): 'E',
    (1, 7): 'G',
    (2, 7): 'C',
    (3, 7): 'LE',
    (4, 7): 'LG',
    (5, 7): 'LC',
    (6, 7): 'B',
    # Left
    (-1, 0): 'FC',
    (-1, 1): 'FE',
    (-1, 2): 'FG',
    (-1, 3): 'E',
    (-1, 4): 'G',
    (-1, 5): 'C',
    (-1, 6): 'B',
    # Top
    (7, 0): 'FE',
    (7, 1): 'FG',
    (7, 2): 'FC',
    (7, 3): 'LC',
    (7, 4): 'LE',
    (7, 5): 'LG',
    (7, 6): 'B',
}

