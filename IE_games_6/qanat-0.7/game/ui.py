"""Some ui stuff"""

import pygame
import sys
import os
import time

import serge.actor
import serge.visual
import serge.events
import serge.sound
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.utils
import serge.blocks.scores
import serge.blocks.achievements

from theme import G, theme
import common


class GameState(serge.blocks.actors.ScreenActor):
    """UI and other items related to the game"""

    def __init__(self, tag, name, options):
        """Initialise the state"""
        super(GameState, self).__init__(tag, name)
        self.options = options
        
    def addedToWorld(self, world):
        """We are added to the world"""
        super(GameState, self).addedToWorld(world)
        #
        self.setUpTable()
        self.dostop = False
        self.player = world.findActorByName('player')
        self.manager = world.findActorByName('behaviours')
        #
        # Lives display
        t = serge.blocks.utils.addVisualActorToWorld(world, 'lives', 'lives', 
            serge.visual.Text('Lives', G('lives-colour'), font_size=G('lives-size'), justify='left'),
            'ui', G('lives-position'))
        #
        # The display of the number of ships
        self.lives = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.RepeatedVisualActor('lives', 'lives', G('lives-initial'), G('lives-spacing')))
        self.lives.moveTo(*G('lives-position-ships'))
        self.lives.setLayerName('ui')
        self.lives.setSpriteName('player-ship-small')
        self.lives.visual.setCell(self.lives.visual.getNumberOfCells()-1)
        #
        # The score display
        self.score = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.NumericText('score', 'score', 'Score: %06d', G('score-colour'), font_size=G('score-size'),
                justify='left', value=0))
        self.score.setLayerName('ui')
        self.score.moveTo(*G('score-position'))
        #
        # The high score display
        current_high = self.table.getCategory('score')[0][0]
        self.high_score = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.NumericText('score', 'high-score', 'Best:   %06d', G('high-score-colour'), font_size=G('high-score-size'),
                justify='left', value=current_high))
        self.high_score.setLayerName('ui')
        self.high_score.moveTo(*G('high-score-position'))
        common.CURRENT_HIGH_SCORE = current_high
        #
        # The level display
        self.level = serge.blocks.utils.addActorToWorld(world,
            serge.blocks.actors.NumericText('level', 'level', 'Level: %02d', G('level-colour'), font_size=G('level-size'),
                justify='left', value=0))
        self.level.setLayerName('ui')
        self.level.moveTo(*G('level-position'))
        #
        # UI for game over
        self.game_over = serge.blocks.utils.addVisualActorToWorld(world, 'text', 'game-over', 
            serge.visual.Text('Game Over', G('game-over-colour'), font_size=G('game-over-size'), 
                font_name='CONTROL', justify='center'),
            'ui', (G('game-over-x'), G('game-over-y')))
        self.game_over_sub = serge.blocks.utils.addVisualActorToWorld(world, 'text', 'game-over', 
            serge.visual.Text('Press   ENTER   to   Replay', G('game-over-sub-colour'), font_size=G('game-over-sub-size'), 
                font_name='CONTROL', justify='center'),
            'ui', (G('game-over-sub-x'), G('game-over-sub-y')))
        self.game_over.active = False
        self.game_over_sub.active = False
        #
        # Version
        self.version = serge.blocks.utils.addVisualActorToWorld(world, 'text', 'version', 
            serge.visual.Text('v %s' % common.version, G('version-colour'), font_size=G('version-size'), 
                font_name='CLEAR', justify='left'),
            'ui', G('version-position'))
        self.credits = serge.blocks.utils.addVisualActorToWorld(world, 'text', 'credits', 
            serge.visual.Text('Credits', G('credits-colour'), font_size=G('credits-size'), 
                font_name='CLEAR', justify='center'),
            'ui', G('credits-position'))
        self.credits.linkEvent(serge.events.E_LEFT_CLICK, self.showCredits)
        self.achievements_button = serge.blocks.utils.addVisualActorToWorld(world, 'text', 'achievements', 
            serge.visual.Text('Achievements', G('achievements-colour'), font_size=G('achievements-size'), 
                font_name='CLEAR', justify='center'),
            'ui', G('achievements-position'))
        self.achievements_button.linkEvent(serge.events.E_LEFT_CLICK, self.showAchievements)
        self.web_high_score = serge.blocks.utils.addVisualActorToWorld(
            world, 'text', 'web-high-score',
            serge.visual.Text('High Scores', G('web-high-score-colour'), font_size=G('web-high-score-size'),
                              font_name='CLEAR', justify='center'),
            'ui', G('web-high-score-position'))
        self.web_high_score.linkEvent(serge.events.E_LEFT_CLICK, self.showHighScores)
        #
        # Titles
        self.main_title = serge.blocks.utils.addSpriteActorToWorld(world, 'title', 'main-title', 
            'logo', 'ui', G('logo-position'))
        self.sub_title = serge.blocks.utils.addVisualActorToWorld(world, 'title', 'sub-title', 
            serge.visual.Text('Keys: LEFT, RIGHT, SPACE. P - Pauses, ESC - Quits',
                G('sub-title-colour'), font_size=G('sub-title-size'), 
                font_name='CLEAR', justify='center'),
            'ui', G('sub-title-position'))
        #
        # Achievements
        self.banner = serge.blocks.achievements.AchievementBanner('banner', 'banner', 
            'ground-overlay', 'ui', self.manager, theme)
        world.addActor(self.banner)
        self.banner.moveTo(*G('banner-position', 'achievements'))
        self.achievements = serge.blocks.achievements.getManager()
        self.achievements.linkEvent(serge.blocks.achievements.E_ACHIEVEMENT_MET, self.banner.meetAchievement)
        #
        # Listen for key events
        self.broadcaster.linkEvent(common.E_PLAYER_DESTROYED, self.playerDestroyed)
        self.broadcaster.linkEvent(common.E_ALIEN_DESTROYED, self.alienDestroyed)
        self.broadcaster.linkEvent(common.E_NEW_LEVEL, self.newLevel)
        self.broadcaster.linkEvent(common.E_RESTART_GAME, self.restartGame)
        #
        self.askUserToStartGame('Welcome', 'Press    ENTER    to    start')
        self.initial_start = True
        self.new_life_counter = G('lives-increase-after')
        self.level_starting = False # This is true when a level is just beginning
        
    def showCredits(self, obj, arg):
        """Show the credits"""
        self.log.info('Clicked show credits')
        self.engine.setCurrentWorldByName('credit-screen')

    def showHighScores(self, obj, arg):
        """Show the high scores"""
        self.log.info('Clicked show high scores')
        self.engine.setCurrentWorldByName('high-score-screen')

    def showAchievements(self, obj, arg):
        """Show the achievements"""
        self.log.info('Clicked show achievements')
        self.engine.setCurrentWorldByName('achievements-screen')
        
    def hideVersion(self, world, actor, interval):
        """Hide version and other UI elements"""
        self.version.active = False
        self.credits.active = False
        
    def playerDestroyed(self, (bullet, player), arg):
        """The player was destroyed"""
        #
        # Ignore bombs hitting the player during initial switch over from the intro
        if self.level_starting or self.options.cheat:
            return
        if not player.flashing and self.lives.getRepeat() > 0:
            self.log.info('Player died')
            if not self.options.cheat:
                self.lives.reduceRepeat()
                serge.sound.Sounds.play('player-explosion')
                if self.lives.getRepeat() == 0:
                    self.askUserToStartGame()
            
    def alienDestroyed(self, (bullet, alien), arg):
        """An alien was destroyed"""
        self.log.info('An alien died')
        self.score.value += alien.score
        #
        # Watch for achievements
        self.achievements.makeReport('score', score=self.score.value)
        #
        if self.score.value > self.high_score.value:
            self.high_score.value = self.score.value
            common.CURRENT_HIGH_SCORE = self.score.value
        #
        self.new_life_counter -= alien.score
        if self.new_life_counter <= 0:
            self.new_life_counter += G('lives-increase-after')
            self.lives.increaseRepeat()
            self.achievements.makeReport('life', lives=self.lives.getRepeat())        
            serge.sound.Sounds.play('life')
            self.lives.visual.resetAnimation(True)

    def newLevel(self, obj, arg):
        """The level was over"""
        self.level.value += 1

    def restartGame(self, obj, arg):
        """Restart the game"""
        self.score.value = 0
        self.new_life_counter = G('lives-increase-after')
        
    def askUserToStartGame(self, title='Game Over', subtitle='Press   ENTER   to   Replay'):
        """End of the game"""
        self.game_over.active = self.game_over_sub.active = True
        self.broadcaster.processEvent((common.E_LOST_GAME, self))
        self.table.addScore('score', self.score.value)
        self.table.toFile(self.score_filename)
        #
        # Record remote score
        if common.HIGH_SCORE_TABLE:
            common.HIGH_SCORE_TABLE.recordScore(self.score.value)
            common.HIGH_SCORE_TABLE.updateScores()
        #
        self.game_over.visual.setText(title)
        self.game_over_sub.visual.setText(subtitle)

    def isGameOver(self):
        """Return True when the game is over"""
        return self.game_over.active
                
    def updateActor(self, interval, world):
        """Update the actor"""
        super(GameState, self).updateActor(interval, world)
        self.level_starting = False
        #
        # Watch for the signal to stop
        if self.dostop:
            time.sleep(G('pre-stop-pause'))
            self.engine.stop()
        #
        if self.game_over.active and (self.keyboard.isClicked(pygame.K_RETURN) or self.keyboard.isClicked(pygame.K_KP_ENTER)):
            serge.sound.Sounds.play('click')
            self.game_over.active = self.game_over_sub.active = False
            self.broadcaster.processEvent((common.E_RESTART_GAME, self))
            self.level.value = 0
            self.lives.setRepeat(G('lives-initial'))
            #
            # If the first start then remove titles and set timed removal of credits
            if self.initial_start:
                self.manager.assignBehaviour(self, 
                    serge.blocks.behaviours.TimedOneshotCallback(G('version-hide-time')*1000, 
                        self.hideVersion), 'hiding')
                self.initial_start = False
                self.main_title.active = False
                self.sub_title.active = False
            #
            # Set the level starting to True, which allows us to ignore bombs hitting the player
            # during the switch from intro to the main game 
            self.level_starting = True
            #
        self.achievements_button.active = self.web_high_score.active = self.game_over.active
        #        
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            serge.sound.Sounds.play('click')
            self.askUserToStartGame('Goodbye', 'Thanks   for   playing')
            self.dostop = True
            serge.sound.Music.fadeout(G('pre-stop-pause')*1000)

            
    def setUpTable(self):
        """Set up the high score table"""
        var = 'HOME' if not sys.platform.startswith('win') else 'HOMEPATH'
        self.score_filename = os.path.join(os.getenv(var), '.galaxy.scores')
        if not self.options.reset and os.path.isfile(self.score_filename):
            self.log.info('Loading scores from %s' % self.score_filename)
            self.table = serge.serialize.Serializable.fromFile(self.score_filename)
        else:
            self.log.info('New scores file at %s' % self.score_filename)
            self.table = serge.blocks.scores.HighScoreTable()
            self.table.addCategory('score', 1, sort_columns=[0], directions=('ascending',))
            self.table.addScore('score', 10)
            self.table.toFile(self.score_filename)
            

