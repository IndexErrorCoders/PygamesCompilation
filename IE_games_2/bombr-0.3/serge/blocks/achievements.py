"""Represents achievements

Achievements are badges that are assigned to the
player as they play the game. An achievement is
basically a condition that is met. When you meet
the condition you get the badge.

"""

import time
import pygame
import datetime
import sys
import os

import serge.serialize
import serge.common
import serge.events
import serge.actor
import serge.engine
import serge.blocks.actors
import serge.blocks.layout
import serge.blocks.utils
import serge.blocks.behaviours
import serge.blocks.visualblocks


# Events
E_ACHIEVEMENT_MET = 'achievement-met'


class DuplicateAchievement(Exception):
    """An achievement with this name already exists"""


class BadReport(Exception):
    """An error occurred while evaluating the report"""


class BadTestType(Exception):
    """The test type was not found"""


class BadCondition(Exception):
    """The condition was not valid"""


class Achievement(serge.serialize.Serializable):
    """Represents an achievement"""

    index = 0

    my_properties = (
        serge.serialize.S('name', '', 'the name of the achievement'),
        serge.serialize.S('description', '', 'the description of the achievement'),
        serge.serialize.S('badge', '', 'the badge sprite name of the achievement'),
        serge.serialize.B('secret', False, 'whether the achievement is secret or not'),
        serge.serialize.S('test_type', '', 'the test type for the achievement'),
        serge.serialize.O('condition', None, 'the condition test for the achievement'),
        serge.serialize.S('condition_string', '', 'the text of the condition test for the achievement'),
        serge.serialize.B('met', False, 'whether the achievement has been met'),
        serge.serialize.F('time', 0, 'when the achievement was met'),
    )

    def __init__(self, name, description, badge, secret, test_type, condition=None, condition_string=None):
        """Initialise the Achievement"""
        self.name = name
        self.description = description
        self.badge = badge
        self.secret = secret
        self.test_type = test_type
        self.met = False
        self.time = 0
        self.index = self.__class__.index
        self.__class__.index += 1
        #
        self.condition = condition
        self.condition_string = condition_string
        self.init()

    def init(self):
        """Initialise the achievement from pickling"""
        super(Achievement, self).init()
        if self.condition is None:
            if not self.condition_string:
                raise BadCondition('Must specify condition or condition_string for achievement "%s"' % self.name)
            else:
                try:
                    self._condition = eval('lambda %s' % self.condition_string)
                except Exception, err:
                    raise BadCondition('Cannot create lambda from "%s" for achievement "%s"' % (
                        self.condition_string, self.name))
        else:
            if self.condition_string:
                raise BadCondition(
                    'Cannot specify both condition and condition_string for achievement "%s"' % self.name)
            self._condition = self.condition

    def makeReport(self, **kw):
        """Make a report on this achievement"""
        # Short circuit if we are met
        if self.met:
            return False
        try:
            self.met = self._condition(**kw)
        except Exception, err:
            raise BadReport('Error evaluating achievement "%s" with %s: %s' % (self.name, kw, err))
        if self.met:
            self.time = time.time()
            return True
        else:
            return False

    def isMet(self):
        """Return True if the achievement was met"""
        return self.met

    def resetStatus(self):
        """Reset the status of the achievement"""
        self.met = False
        self.time = 0


class AchievementManager(serge.serialize.Serializable, serge.common.Loggable, serge.common.EventAware):
    """Manages all the achievements in the game"""

    my_properties = (
        serge.serialize.O('achievements', {}, 'the list of achievements'),
    )

    def __init__(self, ):
        """Initialise the AchievementManager"""
        self.achievements = {}
        self.init()

    def init(self):
        """Initialise"""
        super(AchievementManager, self).init()
        self.addLogger()
        self.initEvents()
        for achievement in self.getAchievements():
            achievement.init()
        self.filename = None

    def registerAchievement(self, achievement):
        """Register an achievement"""
        existing = self.achievements.setdefault(achievement.test_type, {})
        if achievement.name in existing:
            raise DuplicateAchievement('An achievement called "%s" with test "%s" already exists' % (
                achievement.name, achievement.test_type))
        else:
            self.log.info('Registering new achievement "%s" with test "%s"' % (achievement.name, achievement.test_type))
            existing[achievement.name] = achievement

    def safeRegisterAchievement(self, achievement):
        """Register an achievement and do not worry if it is already registered"""
        try:
            self.registerAchievement(achievement)
        except DuplicateAchievement:
            pass

    def makeReport(self, test_type, **kw):
        """Make a report on achievements"""
        try:
            achievements = self.achievements[test_type].values()
        except KeyError:
            raise BadTestType('The test type "%s" was not found' % test_type)
            #
        for achievement in achievements:
            if achievement.makeReport(**kw):
                self.log.info('Achievement "%s" has been met' % achievement.name)
                self.processEvent((E_ACHIEVEMENT_MET, achievement))
                if self.filename:
                    self.saveAchievements()

    def getAchievements(self):
        """Return the list of achievements"""
        ret = []
        for items in self.achievements.values():
            ret.extend(items.values())
        return sorted(ret, lambda a, b: cmp(a.index, b.index))

    def initialiseFromFile(self, filename):
        """Initialise from the file"""
        var = 'HOME' if not sys.platform.startswith('win') else 'HOMEPATH'
        the_filename = os.path.join(os.getenv(var), filename)
        if os.path.isfile(the_filename):
            self.log.info('Loading achievements from %s' % the_filename)
            new_manager = serge.serialize.Serializable.fromFile(the_filename)
            self.achievements = new_manager.achievements
        else:
            self.log.info('New achievements file at %s' % the_filename)
        self.filename = the_filename

    def resetAchievements(self):
        """Reset all the achievements so that they have not been met"""
        self.log.debug('Resetting status of achievements')
        for achievements in self.achievements.values():
            for achievement in achievements.values():
                achievement.resetStatus()
        if self.filename:
            self.saveAchievements()

    def saveAchievements(self):
        """Save achievements to a file"""
        self.toFile(self.filename)


class AchievementBanner(serge.actor.MountableActor):
    """A banner to show an achievement"""

    def __init__(self, tag, name, background_layer, foreground_layer, behaviours, theme):
        """Initialise the AchievementBanner"""
        super(AchievementBanner, self).__init__(tag, name)
        G = self.G = theme.getTheme('achievements').getProperty
        self.background_layer = background_layer
        self.foreground_layer = foreground_layer
        self.hider = behaviours.assignBehaviour(
            self, serge.blocks.behaviours.TimedCallback(G('banner-duration') * 1000, self.hideMe), 'hiding')
        self.hider.pause()

    def addedToWorld(self, world):
        """Added the banner to the world"""
        super(AchievementBanner, self).addedToWorld(world)
        G = self.G
        #
        # Create the widgets
        bg = serge.actor.Actor('banner', 'background')
        bg.visual = serge.blocks.visualblocks.Rectangle(G('banner-size'),
                                                        G('banner-backcolour'))
        bg.setLayerName(self.background_layer)
        self.mountActor(bg, (0, 0))
        #
        self.name = name = serge.blocks.actors.StringText('banner', 'banner-name', 'Name',
                                                          colour=G('banner-font-colour'),
                                                          font_size=G('banner-name-size'),
                                                          font_name=G('banner-font-name'), justify='left')
        name.setLayerName(self.foreground_layer)
        self.mountActor(name, G('banner-name-position'))
        #
        self.description = description = serge.blocks.actors.StringText(
            'banner', 'banner-description',
            'Description of the achievement as it\nis written down.',
            colour=G('banner-font-colour'),
            font_size=G('banner-description-size'),
            font_name=G('banner-font-name'), justify='left'
        )
        description.setLayerName(self.foreground_layer)
        self.mountActor(description, G('banner-description-position'))
        #
        graphic = serge.actor.Actor('banner', 'banner-graphic')
        graphic.setSpriteName('achievement')
        graphic.setLayerName(self.foreground_layer)
        graphic.visual.setCell(1)
        self.mountActor(graphic, G('banner-graphic-position'))
        #
        self.visible = False

    def meetAchievement(self, achievement, arg):
        """An achievement is met"""
        self.name.value = achievement.name
        self.description.value = achievement.description
        if not self.hider.isRunning():
            self.hider.restart()
        self.log.debug('Showing achievement')
        self.visible = True

    def hideMe(self, world, actor, interval):
        """Hide this object"""
        self.hider.pause()
        self.log.debug('Hiding achievement')
        self.visible = False


class AchievementStatus(serge.actor.MountableActor):
    """A banner to show an achievement"""

    def __init__(self, tag, name, background_layer, foreground_layer, achievement, G):
        """Initialise the AchievementStatus"""
        super(AchievementStatus, self).__init__(tag, name)
        self.G = G
        self.background_layer = background_layer
        self.foreground_layer = foreground_layer
        self.achievement = achievement

    def addedToWorld(self, world):
        """Added the banner to the world"""
        super(AchievementStatus, self).addedToWorld(world)
        G = self.G
        #
        # Create the widgets
        bg = serge.actor.Actor('banner', 'background')
        bg.visual = serge.blocks.visualblocks.Rectangle(G('banner-size'),
                                                        G('banner-backcolour'))
        bg.setLayerName(self.background_layer)
        self.mountActor(bg, (0, 0))
        #
        self.name = name = serge.blocks.actors.StringText(
            'banner', 'banner-name', 'Name',
            colour=G('banner-font-colour'),
            font_size=G('banner-name-size'),
            font_name=G('banner-font-name'), justify='left')
        name.setLayerName(self.foreground_layer)
        self.mountActor(name, G('banner-name-position'))
        #
        self.description = description = serge.blocks.actors.StringText(
            'banner', 'banner-description',
            'Description of the achievement as it\nis written down.',
            colour=G('banner-font-colour'),
            font_size=G('banner-description-size'),
            font_name=G('banner-font-name'), justify='left')
        description.setLayerName(self.foreground_layer)
        self.mountActor(description, G('banner-description-position'))
        #
        self.graphic = graphic = serge.actor.Actor('banner', 'banner-graphic')
        graphic.setSpriteName('achievement')
        graphic.setLayerName(self.foreground_layer)
        graphic.visual.setCell(1)
        self.mountActor(graphic, G('banner-graphic-position'))
        #
        self.time = time = serge.blocks.actors.StringText('banner', 'banner-time',
                                                          'Time achieved', colour=G('time-colour'),
                                                          font_size=G('time-size'), font_name=G('banner-font-name'),
                                                          justify='left')
        time.setLayerName(self.foreground_layer)
        self.mountActor(time, G('time-position'))
        #
        self.updateAchievement()

    def updateAchievement(self):
        """Update the achievement view"""
        self.name.value = self.achievement.name
        self.description.value = self.achievement.description
        self.graphic.visual.setCell(1 if self.achievement.isMet() else 0)
        if self.achievement.isMet():
            self.time.value = 'Achieved at %s' % str(datetime.datetime.fromtimestamp(int(self.achievement.time)))
        else:
            self.time.value = ''


class AchievementsGrid(serge.blocks.actors.ScreenActor):
    """A grid to show achievements"""

    def __init__(self, G):
        """Initialise the AchievementsGrid"""
        super(AchievementsGrid, self).__init__('achievements', 'grid')
        self.G = G
        self.manager = getManager()

    def addedToWorld(self, world):
        """Added the grid to the world"""
        super(AchievementsGrid, self).addedToWorld(world)
        G = self.G
        #
        # Logo
        logo = serge.blocks.utils.addSpriteActorToWorld(
            world, 'logo', 'logo', 'logo', 'ui', G('logo-position'))
        #
        # Bg
        bg = serge.blocks.utils.addSpriteActorToWorld(
            world, 'bg', 'bg', G('screen-background-sprite'), 'background', G('screen-background-position'))
        #
        # The grid
        self.grid = grid = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.layout.Grid(
                'grid', 'grid', size=G('grid-size'),width=G('grid-width'),
                height=G('grid-height')), center_position=G('grid-position'), layer_name='ui')
        #
        # Place things in grid
        for achievement in self.manager.getAchievements():
            grid.autoAddActor(AchievementStatus('status', 'status', 'background', 'ui', achievement, self.G))
        #
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.updateAchievements)
        #
        self.back = serge.blocks.utils.addActorToWorld(
            world,
            serge.blocks.actors.StringText(
                'back', 'back',
                'Back', colour=G('back-colour'),
                font_size=G('back-font-size'),
                font_name=G('back-font-name')
            ),
            center_position=G('back-position'), layer_name='ui')
        self.back.linkEvent(serge.events.E_LEFT_CLICK, serge.blocks.utils.backToPreviousWorld(G('back-sound')))

    def updateAchievements(self, obj, arg):
        """Update all achievements"""
        for status in self.grid.getChildren():
            status.updateAchievement()


def addAchievementsWorld(options, theme):
    """Add a world for the achievements"""
    G = theme.getProperty
    #
    # The behaviour manager
    engine = serge.engine.CurrentEngine()
    serge.blocks.utils.createWorldsForEngine(engine, ['achievements-screen'])
    world = engine.getWorld('achievements-screen')
    manager = serge.blocks.behaviours.BehaviourManager('behaviours', 'behaviours')
    world.addActor(manager)
    #
    # The screen actor
    s = AchievementsGrid(theme.getTheme('achievements').getProperty)
    s.options = options
    world.addActor(s)
    #
    # Snap shots
    if options.screenshot:
        manager.assignBehaviour(None,
                                serge.blocks.behaviours.SnapshotOnKey(key=pygame.K_s, size=G('screenshot-size')
                                    , overwrite=False, location='screenshots'), 'screenshot')


def addAchievementsBannerToWorld(world, front_layer, back_layer, theme, manager):
    """Add a banner for achievements to the world"""
    banner = AchievementBanner('banner', 'banner', back_layer, front_layer, manager, theme)
    world.addActor(banner)
    banner.moveTo(*theme.getProperty('banner-position', 'achievements'))
    getManager().linkEvent(E_ACHIEVEMENT_MET, banner.meetAchievement)


# A global achievements manager        
_Manager = AchievementManager()


def getManager():
    return _Manager


def initManager(name):
    """Initialise and return the manager"""
    manager = getManager()
    manager.initialiseFromFile('.%s.achievements' % name)
    return manager
