"""Piano instrument"""

name = 'Piano'
description = 'Piano sounds from Garage Band'

# Notes
C = 'piano-c.wav'
D = 'piano-d.wav'
E = 'piano-e.wav'
F = 'piano-f.wav'
G = 'piano-g.wav'
A = 'piano-a.wav'
B = 'piano-b.wav'
#
LC = 'piano-low-c.wav'
LD = 'piano-low-d.wav'
LE = 'piano-low-e.wav'
LF = 'piano-low-f.wav'
LG = 'piano-low-g.wav'
LA = 'piano-low-a.wav'
LB = 'piano-low-b.wav'

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
    (-1, 4): 'LG',
    (-1, 5): 'LA',
    (-1, 6): 'LB',
    # Top
    (7, 0): 'LC',
    (7, 1): 'LD',
    (7, 2): 'LE',
    (7, 3): 'LF',
    (7, 4): 'LG',
    (7, 5): 'LA',
    (7, 6): 'LB',
}

