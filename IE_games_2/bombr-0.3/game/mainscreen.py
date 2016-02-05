"""The main screen for the game"""

import random
import math
import os
import time
import pygame


import serge.actor
import serge.visual
import serge.events
import serge.common
import serge.sound
import serge.blocks.utils
import serge.blocks.visualblocks
import serge.blocks.behaviours
import serge.blocks.actors
import serge.blocks.animations
import serge.blocks.textgenerator

from theme import G, theme
import common 
import board
import man
import player
import ai
import smacktalker
import giftbox
import flagstatus


# Score panel frames
F_TIE = 0
F_PLAYER = 1
F_AI = 2


class MainScreen(serge.blocks.actors.ScreenActor):
    """The logic for the main screen"""

    def __init__(self, options):
        """Initialise the screen"""
        super(MainScreen, self).__init__('item', 'main-screen')
        self.options = options
        self.current_level = G('start-level')
        self._take_screenshots = G('auto-screenshots')
        self._screenshot_path = G('screenshot-path')
        self._screenshot_interval = G('screenshot-interval')
        self._last_screenshot = time.time() - self._screenshot_interval + 1.0
        self._game_over = False
        self.music = None
        self.death_music = serge.sound.Music.getItem('death-music')
        self.success_music = serge.sound.Music.getItem('success-music')
        #
        self.generator = serge.blocks.textgenerator.TextGenerator()
        self.generator.addExamplesFromFile(os.path.join('game', 'smack-talk.txt'))

    def addedToWorld(self, world):
        """Added to the world"""
        super(MainScreen, self).addedToWorld(world)
        #
        # Background
        self.bg = serge.blocks.utils.addSpriteActorToWorld(
            world, 'bg', 'bg', 'very-dark-background',
            layer_name='background',
            center_position=(G('screen-width') / 2, G('screen-height') / 2),
        )
        #
        # Gift box
        self.gift_box = serge.blocks.utils.addActorToWorld(
            world,
            giftbox.GiftBox('gift-box', 'gift-box'),
            sprite_name='gift-box',
            layer_name='ui',
            center_position=G('gift-box-position'),
        )
        #
        # Initialise the level
        self.initLevel()
        #
        # Main result
        self.result = serge.blocks.utils.addTextToWorld(
            world, 'Result', 'result', theme, 'ui',
            actor_class=serge.blocks.animations.AnimatedActor,
        )
        self.result_reason = serge.blocks.utils.addTextToWorld(
            world, 'Reason', 'result-reason', theme, 'ui',
            actor_class=serge.blocks.animations.AnimatedActor,
        )
        self.next = serge.blocks.utils.addTextToWorld(
            world, 'Press RETURN to play again', 'next', theme, 'ui',
            actor_class=serge.blocks.animations.AnimatedActor,
        )
        score_format = '%(wins)02d'
        heart_format = '%(hearts)02d'
        self.player_score = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.FormattedText(
                'score', 'player-score',
                score_format,
                G('player-colour'),
                font_name=G('player-font'), font_size=G('player-font-size'),
                justify='left', fixed_char_width=G('fixed-font-width'),
                wins=0, hearts=0,
            ),
            layer_name='ui',
            center_position=G('player-position')
        )
        self.player_score_highlight = self.player_score.addAnimation(
            serge.blocks.animations.ColourText(
                self.player_score.visual, G('player-highlight-colour'), G('player-colour'), G('player-highlight-time'),
            ),
            'highlight-text'
        )
        self.player_score_highlight.pause()
        #
        self.player_hearts = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.FormattedText(
                'hearts', 'player-score',
                heart_format,
                G('player-colour'),
                font_name=G('player-font'), font_size=G('player-font-size'),
                justify='left', fixed_char_width=G('fixed-font-width'),
                wins=0, hearts=0,
            ),
            layer_name='ui',
            center_position=G('player-heart-position')
        )
        self.player_hearts_highlight = self.player_hearts.addAnimation(
            serge.blocks.animations.ColourText(
                self.player_hearts.visual, G('player-highlight-colour'), G('player-colour'), G('player-highlight-time'),
            ),
            'highlight-text'
        )
        self.player_hearts_highlight.pause()
        #
        self.ai_score = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.FormattedText(
                'score', 'ai-score',
                score_format,
                G('player-colour'),
                font_name=G('player-font'), font_size=G('player-font-size'),
                justify='left', fixed_char_width=G('fixed-font-width'),
                wins=0, hearts=0,
            ),
            layer_name='ui',
            center_position=G('ai-position')
        )
        self.ai_score_highlight = self.ai_score.addAnimation(
            serge.blocks.animations.ColourText(
                self.ai_score.visual, G('player-highlight-colour'), G('player-colour'), G('player-highlight-time'),
            ),
            'highlight-text'
        )
        self.ai_score_highlight.pause()
        #
        self.ai_hearts = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.FormattedText(
                'hearts', 'ai-score',
                heart_format,
                G('player-colour'),
                font_name=G('player-font'), font_size=G('player-font-size'),
                justify='left', fixed_char_width=G('fixed-font-width'),
                wins=0, hearts=0,
            ),
            layer_name='ui',
            center_position=G('ai-heart-position')
        )
        self.ai_hearts_highlight = self.ai_hearts.addAnimation(
            serge.blocks.animations.ColourText(
                self.ai_hearts.visual, G('player-highlight-colour'), G('player-colour'), G('player-highlight-time'),
            ),
            'highlight-text'
        )
        self.ai_hearts_highlight.pause()
        #
        # Flag status
        self.flag_status_panel = serge.blocks.utils.addActorToWorld(
            world,
            flagstatus.FlagStatus('flag-status', 'flag-status'),
            center_position=G('flag-status-position'),
            layer_name='ui',
        )
        self.flag_status_panel.linkEvent(common.E_FLAG_WON, self.flagGameWon)
        #
        self.score_panel = serge.blocks.utils.addSpriteActorToWorld(
            world, 'score-panel', 'score-panel',
            'score-panel',
            layer_name='ui',
            center_position=G('score-panel-position')
        )
        #
        # Group of actors to disable when the game is over
        self.gameplay_actors = serge.actor.ActorCollection()
        self.non_gameplay_actors = serge.actor.ActorCollection()
        #
        self.gameplay_actors.extend([self.player, self.ai])
        self.non_gameplay_actors.extend([self.result, self.next, self.result_reason])
        #
        self.non_gameplay_actors.forEach().visible = False
        #
        # Smack talking
        self.smack = smacktalker.RandomlyAppearingSmacker(
            'smack', 'smack', 'main', 'waiting-to-replay',  random_on=False)
        world.addActor(self.smack)
        self.smack.visible = False
        #
        # Events
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.activatedWorld)
        world.linkEvent(serge.events.E_DEACTIVATE_WORLD, self.deactivatedWorld)
        #
        # Initial load is not resumable
        common.LEVEL_IN_PROGRESS = False
        #
        # Cheating
        if self.options.cheat:
            fps = serge.blocks.utils.addActorToWorld(world,
                serge.blocks.actors.FPSDisplay(G('fps-x'), G('fps-y'), G('fps-colour'), G('fps-size')))

    def activatedWorld(self, obj, arg):
        """The world was activated"""
        self.music.play(-1)

    def deactivatedWorld(self, obj, arg):
        """The world was deactivated"""
        self.music.pause()

    def updateActor(self, interval, world):
        """Update this actor"""
        super(MainScreen, self).updateActor(interval, world)
        #
        # Watch for restarting game
        if self._game_over:
            if self.keyboard.isClicked(pygame.K_RETURN):
                self.restartGame()
        #
        # Take screenshot if needed
        if self._take_screenshots:
            if time.time() - self._last_screenshot > self._screenshot_interval:
                filename = '%s-%s' % (self.name, time.strftime('%m-%d %H:%M:%S.png'))
                serge.blocks.utils.takeScreenshot(os.path.join(self._screenshot_path, filename))
                self._last_screenshot = time.time()
                self.log.debug('Taking screenshot - %s', filename)
        #
        # Cheating options
        if self.options.cheat:
            if self.keyboard.isClicked(pygame.K_n):
                self.world.rtf = 1
                self.world.fps = 50
            if self.keyboard.isClicked(pygame.K_f):
                self.world.rtf = G('simulation-rtf')
                self.world.fps = G('simulation-fps')
            if self.keyboard.isClicked(pygame.K_k):
                self.playerDied('blew-up', None)
            if self.keyboard.isClicked(pygame.K_w):
                self.aiDied('no-hearts-left', None)
            if self.keyboard.isClicked(pygame.K_c):
                serge.sound.Sounds.play('hearts')
        #
        # Switch to replay
        if self.keyboard.isClicked(pygame.K_r):
            self.engine.setCurrentWorldByName('action-replay-screen')
        #
        # Escape
        if self.keyboard.isClicked(pygame.K_ESCAPE):
            if self.options.straight or pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.engine.stop(process_events=False)
            else:
                common.tweenBackWorlds(
                    'level-screen' if self.current_level != common.levels.RANDOM_LEVEL else 'random-level-screen')(None, None)

    def getDeathText(self, base_sentence, man):
        """Return some text for the death string"""
        return self.generator.getRandomSentence('@{%s-%s}@' % (man, base_sentence))

    def playerDied(self, obj, arg):
        """The player has died"""
        if not self.player.is_dead:
            serge.sound.Sounds.play('death')
            self.board.addGore(self.player)
            self.player.deathAnimation()
            self.player.is_dead = True
            self.log.info('The player has died')
        if not self._game_over:
            self.smack.deathOfPlayer()
            self.ai_score_highlight.restart()
            self.result.visual.setText('I won!')
            self.result_reason.visual.setText(self.getDeathText(obj, 'player'))
            self.ai_score.setValue('wins', self.ai_score.getValue('wins') + 1)
            self.gameOver()
            self.death_music.play(-1)

    def aiDied(self, obj, arg):
        """The AI has died"""
        if not self.ai.is_dead:
            serge.sound.Sounds.play('death')
            self.board.addGore(self.ai)
            self.ai.deathAnimation()
            self.ai.is_dead = True
            self.log.info('The AI has died')
        if not self._game_over:
            self.smack.deathOfAI()
            self.player_score_highlight.restart()
            self.result.visual.setText('You won!')
            self.result_reason.visual.setText(self.getDeathText(obj, 'ai'))
            self.player_score.setValue('wins', self.player_score.getValue('wins') + 1)
            self.gameOver()
            self.success_music.play(-1)

    def gameOver(self):
        """Mark the game as over"""
        common.LEVEL_IN_PROGRESS = False
        self.board.gameOver()
        self.gift_box.stop()
        if not G('simulation-auto-restart'):
            self.non_gameplay_actors.forEach().visible = True
            self.gameplay_actors.forEach().moving = False
            self._game_over = True
            self.result.addAnimation(
                serge.blocks.animations.TweenAnimation(
                    self.result, 'y', G('result-start-y'), G('result-end-y'),
                    G('result-duration'),
                    function=serge.blocks.animations.TweenAnimation.sinOut,
                ),
                'enter-motion',
            )
            self.result_reason.addAnimation(
                serge.blocks.animations.TweenAnimation(
                    self.result_reason, 'y', G('result-reason-start-y'), G('result-reason-end-y'),
                    G('result-reason-duration'),
                    function=serge.blocks.animations.TweenAnimation.sinOut,
                ),
                'enter-motion',
            )
            self.next.addAnimation(
                serge.blocks.animations.TweenAnimation(
                    self.next, 'x', G('next-start-x'), G('next-end-x'),
                    G('next-duration'),
                    function=serge.blocks.animations.TweenAnimation.sinOut,
                ),
                'enter-motion',
            )
            #
            # Set the panel showing who is leading
            player_score, ai_score = self.player_score.getValue('wins'), self.ai_score.getValue('wins')
            if player_score == ai_score:
                frame = F_TIE
            elif player_score > ai_score:
                frame = F_PLAYER
            else:
                frame = F_AI
            self.score_panel.visual.setCell(frame)
            self.log.debug('Scores are %d, %d. Set score panel frame to %d' % (player_score, ai_score, frame))
            #
            self.flag_status_panel.stopUpdating()
            self.music.pause()
            self.smack.enableRandomShowing()
        else:
            self.restartGame()

    def restartGame(self):
        """Restart the game"""
        #
        # Animate the text out of there
        self.result.addAnimation(
            serge.blocks.animations.TweenAnimation(
                self.result, 'y', G('result-end-y'), G('result-start-y'),
                G('result-duration'),
                function=serge.blocks.animations.TweenAnimation.sinOut,
            ),
            'exit-motion',
        )
        self.result_reason.addAnimation(
            serge.blocks.animations.TweenAnimation(
                self.result_reason, 'y', G('result-reason-end-y'), G('result-reason-start-y'),
                G('result-reason-duration'),
                function=serge.blocks.animations.TweenAnimation.sinOut,
            ),
            'exit-motion',
        )
        self.next.addAnimation(
            serge.blocks.animations.TweenAnimation(
                self.next, 'x', G('next-end-x'), G('next-start-x'),
                G('next-duration'),
                function=serge.blocks.animations.TweenAnimation.sinOut,
            ),
            'exit-motion',
        )
        #
        self.gameplay_actors.forEach().moving = True
        self._game_over = False
        self.smack.hideNow()
        self.smack.disableRandomShowing()
        self.player_hearts.setValue('hearts', G('initial-number-hearts'))
        self.ai_hearts.setValue('hearts', G('initial-number-hearts'))
        #
        self.music.play(-1)
        #
        # Find the actors to remove
        actors = self.world.findActorsByTag('man')
        actors.extend(self.world.findActorsByTag('board'))
        actors.extend(self.world.findActorsByTag('board-item'))
        actors.extend(self.world.findActorsByTag('debug'))
        #
        # Remove actors
        for actor in actors:
            self.world.removeActor(actor)
        #
        self.flag_status_panel.resetAndStart()
        #
        # And recreate
        self.initLevel()

    def initLevel(self):
        """Initialise the level"""
        #
        # The board
        this_board = board.Board('board', 'board', 'tiles', self.options)
        this_board.initFrom(common.levels.LEVEL_FILES[self.current_level - 1])
        self.board = serge.blocks.utils.addActorToWorld(
            self.world, this_board,
            layer_name='main',
            center_position=G('board-position'),
        )
        self.board.updateVisual()
        self.gift_box.restart(this_board)
        #
        # Music
        self.music = serge.sound.Music.getItem(common.levels.LEVELS[self.current_level - 1][1])
        #
        # Add the player
        self.player = serge.blocks.utils.addActorToWorld(
            self.world,
            man.Man('man', 'player', 'tiles-6', self.board,
                    ai.AI() if G('all-ai') else player.Player()),
            layer_name='men'
        )
        self.player.spawnMan()
        self.player.linkEvent(common.E_MAN_DIED, self.playerDied)
        #
        # Add the ai
        self.ai = serge.blocks.utils.addActorToWorld(
            self.world,
            man.Man('man', 'ai', 'tiles-7', self.board, ai.AI(self.player)),
            layer_name='men'
        )
        self.ai.spawnMan()
        self.ai.linkEvent(common.E_MAN_DIED, self.aiDied)
        self.player.controller.enemy = self.ai
        #
        if self.options.cheat:
            self.aiui1 = serge.blocks.utils.addActorToWorld(
                self.world, ai.AIUI(self.ai.controller, self.board, 'ai-1'),
            )
            if G('all-ai'):
                self.aiui2 = serge.blocks.utils.addActorToWorld(
                    self.world, ai.AIUI(self.player.controller, self.board, 'ai-2'),
                )
        #
        self.gameplay_actors = serge.actor.ActorCollection()
        self.gameplay_actors.extend([self.player, self.ai])
        #
        common.LEVEL_IN_PROGRESS = True

    def heartIncrement(self, man, increment, self_taken):
        """A heart was taken by a man"""
        if self_taken:
            if man == self.player:
                the_target = self.player_hearts
                the_man = self.player
                the_animation = self.player_hearts_highlight
            else:
                the_target = self.ai_hearts
                the_man = self.ai
                the_animation = self.ai_hearts_highlight
        else:
            if man == self.ai:
                the_target = self.player_hearts
                the_man = self.player
                the_animation = self.player_hearts_highlight
            else:
                the_target = self.ai_hearts
                the_man = self.ai
                the_animation = self.ai_hearts_highlight
        #
        # Change the number of hearts
        the_target.setValue('hearts', the_target.getValue('hearts') + increment)
        #
        # Death condition of no hearts
        if the_target.getValue('hearts') == 0:
            the_man.processEvent((common.E_MAN_DIED, 'no-hearts-left'))
        #
        the_animation.restart()
        serge.sound.Sounds.play('hearts')

    def flagGameWon(self, winner, arg):
        """The flag game was won"""
        self.log.info('Flag game is won by "%s"' % winner)
        if winner == 'player':
            self.aiDied('flag-lost', None)
        else:
            self.playerDied('flag-lost', None)


def main(options):
    """Create the main logic"""
    #
    # The screen actor
    s = MainScreen(options)
    world = serge.engine.CurrentEngine().getWorld('main-screen')
    world.addActor(s)
    #
    # The behaviour manager
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    if options.cheat:
        manager.assignBehaviour(None, serge.blocks.behaviours.KeyboardQuit(pygame.K_q), 'keyboard-quit')
    #
    # Screenshots
    if options.screenshot:
        manager.assignBehaviour(None, 
            serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                , overwrite=False, location='screenshots'), 'screenshots')

