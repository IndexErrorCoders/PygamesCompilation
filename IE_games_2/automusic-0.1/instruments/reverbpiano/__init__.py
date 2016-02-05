"""Piano instrument"""

name = 'Reverb Piano'
description = 'Piano sounds from Garage Band with some echo added'

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
    (1, -1): 'E',
    (2, -1): 'G',
    (3, -1): 'LC',
    (4, -1): 'LE',
    (5, -1): 'LG',
    # Top
    (0, 7): 'C',
    (1, 7): 'E',
    (2, 7): 'G',
    (3, 7): 'LC',
    (4, 7): 'LE',
    (5, 7): 'LG',
    # Left
    (-1, 0): 'C',
    (-1, 1): 'E',
    (-1, 2): 'G',
    (-1, 3): 'LC',
    (-1, 4): 'LE',
    (-1, 5): 'LG',
    # Top
    (7, 0): 'C',
    (7, 1): 'E',
    (7, 2): 'G',
    (7, 3): 'LC',
    (7, 4): 'LE',
    (7, 5): 'LG',
}

