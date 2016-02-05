"""Encapsulates the logic around saving the history of the player's caves"""

import sys
import os
import getpass
import time

import serge.actor
import serge.events

from theme import G, theme
import common 


class History(serge.actor.Actor):
    """Shows the history on the screen"""

    def __init__(self, tag, name):
        """Intialise the history"""
        super(History, self).__init__(tag, name)
        #
        # Find the place to put the files
        var = 'HOME' if not sys.platform.startswith('win') else 'HOMEPATH'
        self.score_filename = os.path.join(os.getenv(var), '.subterrex.scores')
        #
        self.registerHighScores()
        self.achievements = serge.blocks.achievements.getManager()

    def registerHighScores(self):
        """Setup a high score table""" 
        if os.path.isfile(self.score_filename):
            self.log.info('Loading scores from %s' % self.score_filename)
            self.scores = serge.serialize.Serializable.fromFile(self.score_filename)
        else:
            self.log.info('New scores file at %s' % self.score_filename)
            self.resetTable()

    def resetTable(self):
        """Reset the scores table
        
        The scores are:
            cave name, last visited
            
        """   
        self.scores = serge.blocks.scores.HighScoreTable()
        self.saveScores()
        
    def saveScores(self):
        """Save the high scores"""
        self.scores.toFile(self.score_filename)
        
        
    def visitCave(self, name):
        """Make a visit to the named cave"""
        #
        # Make a category for this cave
        if name not in self.scores.categories:
            self.scores.addCategory(name, number=20, sort_columns=[1], directions=['ascending'])
        #
        # Add this visit
        self.scores.addScore(name, getpass.getuser(), time.time())
        self.saveScores()

    def solveCave(self, name):
        """Store that we solved a cave"""
        #
        # Make a category for this cave
        category_name = 'solved-%s' % name
        if category_name not in self.scores.categories:
            self.scores.addCategory(category_name, number=20, sort_columns=[1], directions=['ascending'])
        #
        # Add this visit
        self.scores.addScore(category_name, getpass.getuser(), time.time())
        self.saveScores()

    def getSolvesForCave(self, name):
        """Return the number of times we have solved a cave"""
        try:
            category = self.scores.getCategory('solved-%s' % name)
        except serge.blocks.achievements.BadCategory:
            return 0
        else:
            return len(category)
    
    def getTotalSolves(self):
        """Return the total number of times we have solved caves"""
        total = 0
        for name, category in self.scores.categories.iteritems():
            if name.startswith('solved-'):
                total += 1
        return total

    def recordNamedCrystal(self, name, cave_description, cave_name):
        """Record that you found a named crystal"""
        self.ensureCrystalCategory()
        self.scores.addScore('crystals', getpass.getuser(), name, cave_description, cave_name, time.time())
        self.saveScores()
        #
        self.achievements.makeReport('named-crystals', 
            number=len(self.getNamedCrystals()))

    def getNamedCrystals(self):
        """Return the named crystals"""
        self.ensureCrystalCategory()
        return self.scores.getCategory('crystals')
          
    def ensureCrystalCategory(self):
        """Ensure that we have a crystal category"""
        if 'crystals' not in self.scores.categories:
            self.scores.addCategory('crystals', number=200, sort_columns=[1,2,3,4], 
                directions=['ascending','ascending','ascending','ascending'])
                
    def addedToWorld(self, world):
        """Added the history to the world"""
        super(History, self).addedToWorld(world)
        #
        # Make a bar to display the caves
        the_theme = theme.getTheme('name-screen')
        L = the_theme.getProperty
        self.layout = serge.blocks.utils.addActorToWorld(world, 
            serge.blocks.layout.VerticalBar('bar', 'bar', L('names-width'), L('names-height')),
            layer_name='ui-back',
            center_position=L('names-position'))
        #
        # Add all name slots
        self.slots = []
        for idx in range(L('names-number')):
            slot = self.layout.addActor(serge.blocks.actors.StringText('slot', 'slot-%d' % idx, 
                    '', '%s', L('names-colour'), L('names-font-name'), L('names-font-size')))
            slot.linkEvent(serge.events.E_LEFT_CLICK, self.nameClicked, idx)
            self.slots.append(slot)  
        #
        # The current page
        self.current_page = 0              
        #
        world.linkEvent(serge.events.E_ACTIVATE_WORLD, self.updateNames)

    def nameClicked(self, obj, idx):
        """A name was clicked on"""
        name = self.slots[idx].value
        self.log.info('Clicked on %s' % name)
        self.processEvent((common.E_CAVE_SELECTED, name))
        
    def updateNames(self, obj, arg):
        """Update the name list"""
        #
        # Get the cave names and their last visit. Then sort so that the most recent is at the top
        names = [(self.scores.getCategory(name)[0][1], name) for name in self.scores.categories 
                    if self.scores.getCategory(name) and not ((name.startswith('solved-') or name == 'crystals'))]
        names.sort()
        names.reverse()
        #
        # Place on the screen
        for idx, slot in enumerate(self.slots):
            true_index = idx + G('names-number', 'name-screen')*self.current_page
            slot.value = '' if true_index >= len(names) else names[true_index][1]
            
            
