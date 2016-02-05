"""flute instrument"""

name = 'Flute'
description = 'Flute sounds from Garage Band'

# Notes
C = 'flute-c.wav'
D = 'flute-d.wav'
E = 'flute-e.wav'
F = 'flute-f.wav'
G = 'flute-g.wav'
A = 'flute-a.wav'
B = 'flute-b.wav'
#
LC = 'flute-lc.wav'
LD = 'flute-ld.wav'
LE = 'flute-le.wav'
LF = 'flute-lf.wav'
LG = 'flute-lg.wav'
LA = 'flute-la.wav'
LB = 'flute-lb.wav'
#
PC = 'piano-c.wav'
PE = 'piano-e.wav'
PG = 'piano-g.wav'
#
SL = 'strings-l.wav'
SM = 'strings-m.wav'
SH = 'strings-h.wav'

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
    'PC': PC,
    'PE': PE,
    'PG': PG,
    #
    'SL': SL,
    'SM': SM,
    'SH': SH,
}

cells = {
    # Bottom
    (0, -1): 'C',
    (1, -1): 'D',
    (2, -1): 'E',
    (3, -1): 'F',
    (4, -1): 'G',
    (5, -1): 'A',
    (6, -1): 'B',
    # Top
    (0, 7): 'C',
    (1, 7): 'D',
    (2, 7): 'E',
    (3, 7): 'F',
    (4, 7): 'G',
    (5, 7): 'A',
    (6, 7): 'B',
    # Left
    (-1, 0): 'LC',
    (-1, 1): 'LD',
    (-1, 2): 'LE',
    (-1, 3): 'LF',
    (-1, 4): 'SL',
    (-1, 5): 'SM',
    (-1, 6): 'SH',
    # Top
    (7, 0): 'LC',
    (7, 1): 'LD',
    (7, 2): 'LE',
    (7, 3): 'LF',
    (7, 4): 'SL',
    (7, 5): 'SM',
    (7, 6): 'SH',
}

