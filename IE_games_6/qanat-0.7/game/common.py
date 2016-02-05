"""Common elements"""

import serge.engine
import serge.common
import serge.blocks.scores

log = serge.common.getLogger('Game')


version = '0.7'

# The remote high score table - gets set by the online scores screen
HIGH_SCORE_TABLE = None
CURRENT_HIGH_SCORE = 0

# Events
E_PLAYER_DESTROYED = 'player-destroyed'
E_ALIEN_DESTROYED = 'alien-destroyed'
E_NEW_LEVEL = 'new-level'
E_LEVEL_REWIND = 'level-rewind'
E_RESTART_GAME = 'restart-game'
E_LOST_GAME = 'lost-game'
