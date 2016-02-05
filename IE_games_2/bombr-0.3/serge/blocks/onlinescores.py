"""Interface to the online high-score system"""

import json
import urllib

import serge.common
import serge.actor
from serge.blocks import concurrent
import serge.blocks.concurrent.futures
import serge.blocks.actors


class OnlineMethodCallFailed(Exception):
    """Calling the online method resulted in an error"""


class BaseHighScoreInterface(object):
    """Base class for interacting with the high score system"""

    def __init__(self, app_url, secret_user=False):
        """Initialise the interface"""
        self.app_url = app_url
        self.secret_user = secret_user

    def _getResult(self, method_url, parameters):
        """Returns the result of calling the web method url with the given parameters"""
        parameter_list = list(parameters.iteritems())
        if self.secret_user:
            parameter_list.append(('secretUser', 1))
        params = urllib.urlencode(parameter_list)
        url = '%s/%s?%s' % (self.app_url, method_url, params)
        url_file = urllib.urlopen(url)
        result = url_file.read()
        try:
            return json.loads(result)
        except ValueError, err:
            raise OnlineMethodCallFailed('JSON result invalid (%s). URL "%s" returned "%s"' % (err, url, result))


class OnlineScoreTable(BaseHighScoreInterface):
    """Simple interface to the online high score table"""

    def __init__(self, app_url, game):
        """Initialise the table connection"""
        super(OnlineScoreTable, self).__init__(app_url)
        #
        self.game = game

    def recordScore(self, player, category, score):
        """Record a score"""
        result = self._getResult(
            'record_score',
            {
                'game': self.game,
                'player': player,
                'category': category,
                'score': score,
            }
        )
        if result['status'] == 'OK':
            return result['key']
        else:
            raise OnlineMethodCallFailed('Could not record score: %s' % result['reason'])

    def createPlayer(self, player):
        """Creates a new player"""
        result = self._getResult(
            'create_user',
            {
                'game': self.game,
                'name': player,
            }
        )
        if result['status'] == 'OK':
            return result['key']
        else:
            raise OnlineMethodCallFailed('Could not create user: %s' % result['reason'])

    def getCategories(self):
        """Return the category names"""
        result = self._getResult(
            'get_game_categories',
            {
                'game': self.game,
            }
        )
        if result['status'] == 'OK':
            return result['categories']
        else:
            raise OnlineMethodCallFailed('Could not get categories: %s' % result['reason'])

    def getScores(self, category, player, number):
        """Return the game scores for the given category and the given player (or * for all players)"""
        result = self._getResult(
            'get_scores',
            {
                'game': self.game,
                'category': category,
                'number': number,
                'player': player,
            }
        )
        if result['status'] == 'OK':
            return result['scores']
        else:
            raise OnlineMethodCallFailed('Could not get scores: %s' % result['reason'])


class AsyncOnlineScoreTable(OnlineScoreTable):
    """Asynchronous version of the high score table

    All the methods of the high score table return futures to
    the results. If you want callbacks then you can add
    a callback to the future once you get it back.

    """

    def __init__(self, app_url, game, max_workers=1):
        """Initialise the table"""
        super(AsyncOnlineScoreTable, self).__init__(app_url, game)
        #
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers)

    def recordScore(self, player, category, score):
        """Record a score"""
        return self._executor.submit(
            super(AsyncOnlineScoreTable, self).recordScore, player, category, score)

    def createPlayer(self, player):
        """Create a new player"""
        return self._executor.submit(
            super(AsyncOnlineScoreTable, self).createPlayer, player)

    def getCategories(self):
        """Return the categories for a game"""
        return self._executor.submit(
            super(AsyncOnlineScoreTable, self).getCategories)

    def getScores(self, category, player, number):
        """Return the scores for a game"""
        return self._executor.submit(
            super(AsyncOnlineScoreTable, self).getScores, category, player, number)

    def recordScore(self, player, category, score):
        """Record the score for a game"""
        return self._executor.submit(
            super(AsyncOnlineScoreTable, self).recordScore, player, category, score)


class SimpleHSTableView(serge.actor.MountableActor):
    """A simple view of a high score table utilizing a layout

    You can supply a theme and it will style using hs-font-colour,
    hs-font-size etc

    The format of the text should be a format string using the names
    num, player and score.

    """

    def __init__(self, tag, name, app_url, game_name, category_name,
                 player_name, max_scores, layout, theme,
                 fmt='%(num)d %(player)s %(score)s'):
        """Initialise the table"""
        super(SimpleHSTableView, self).__init__(tag, name)
        self.app_url = app_url
        self.game_name = game_name
        self.category_name = category_name
        self.player_name = player_name
        self.max_scores = max_scores
        self.layout = layout
        self.theme = theme
        self.fmt = fmt
        #
        self.normal_colour = self.theme.getPropertyWithDefault('hs-font-colour', (255, 255, 255))
        self.player_colour = self.theme.getPropertyWithDefault('hs-font-player-colour', (255, 255, 0))
        #
        # Create a table
        self.table = AsyncOnlineScoreTable(self.app_url, self.game_name)
        #
        self.results = None

    def addedToWorld(self, world):
        """Added the table to the world"""
        super(SimpleHSTableView, self).addedToWorld(world)
        #
        self.mountActor(self.layout, (0, 0))
        #
        # Create text entries to show scores
        L = self.theme.getPropertyWithDefault
        self.entries = serge.actor.ActorCollection()
        for idx in range(self.max_scores):
            entry = self.layout.addActor(
                serge.blocks.actors.FormattedText(
                    'hs-text', 'hs-text-%d' % idx, self.fmt,
                    colour=self.normal_colour,
                    font_name=L('hs-font-name', 'DEFAULT'),
                    font_size=L('hs-font-size', 20),
                    num=idx + 1, player='unknown', score=123,
                )
            )
            entry.active = False
            self.entries.append(entry)
        #
        # The callback used when we have updated our scores
        self.done = None

    def updateActor(self, interval, world):
        """Update the actor"""
        super(SimpleHSTableView, self).updateActor(interval, world)
        #
        # Check if we got new scores
        if self.results and self.results.done():
            self.log.info('Got high score result')
            try:
                result = self.results.result()
            except Exception, err:
                self.log.error('Could not get high scores: %s' % err)
            else:
                self.entries.forEach().active = False
                for idx, (player, score, category, date) in enumerate(result):
                    item = self.entries[idx]
                    item.setValue('player', player)
                    item.setValue('score', score)
                    item.active = True
                    item.visual.setColour(self.player_colour if player == self.player_name else self.normal_colour)
            #
            self.results = None
            #
            # Perform callback if we have one
            if self.done:
                self.done()

    def updateScores(self, done=None):
        """Try to update the scores"""
        self.log.info('Getting scores from remote site (%s)' %
                      ('no callback' if not done else 'with callback',))
        self.done = done
        self.results = self.table.getScores(self.category_name, '*', self.max_scores)

    def recordScore(self, score):
        """Record a new score"""
        return self.table.recordScore(self.player_name, self.category_name, score)

    def ensurePlayer(self):
        """Ensure that our player is defined"""
        return self.table.createPlayer(self.player_name)


class HighScoreSystem(BaseHighScoreInterface):
    """Wrapper for useful functions to manage the high score system"""

    def gameExists(self, name):
        """Return True if the named game exists"""
        try:
            self._getResult(
                'get_scores',
                {
                    'game': name
                }
            )
        except OnlineMethodCallFailed:
            return False
        else:
            return True

    def createGame(self, name):
        """Create a game"""
        result = self._getResult(
            'create_game',
            {
                'game': name,
            }
        )
        if result['status'] == 'OK':
            return result['key']
        else:
            raise OnlineMethodCallFailed('Could not create game: %s' % result['reason'])

    def deleteGame(self, name):
        """Delete a game"""
        result = self._getResult(
            'delete_game',
            {
                'game': name,
            }
        )
        if result['status'] == 'OK':
            return result['key']
        else:
            raise OnlineMethodCallFailed('Could not delete game: %s' % result['reason'])

    def renameGame(self, name, new_name):
        """Rename a game"""
        result = self._getResult(
            'rename_game',
            {
                'game': name,
                'new': new_name,
            }
        )
        if result['status'] == 'OK':
            return result['key']
        else:
            raise OnlineMethodCallFailed('Could not rename game: %s' % result['reason'])

    def categoryExists(self, game, category):
        """Return True if the named category exists for the named game"""
        try:
            result = self._getResult(
                'get_scores',
                {
                    'game': game,
                    'category': category,
                    'number': 1,
                    'player': '*',
                }
            )
        except OnlineMethodCallFailed:
            return False
        else:
            return result['status'] == 'OK'

    def createGameCategory(self, name, category, value_name, sort_ascending, max_player_scores):
        """Rename a game"""
        result = self._getResult(
            'create_game_category',
            {
                'game': name,
                'name': category,
                'value_name': value_name,
                'sort_ascending': int(sort_ascending),
                'max_player_scores': max_player_scores,
            }
        )
        if result['status'] == 'OK':
            return result['key']
        else:
            raise OnlineMethodCallFailed('Could not create category: %s' % result['reason'])