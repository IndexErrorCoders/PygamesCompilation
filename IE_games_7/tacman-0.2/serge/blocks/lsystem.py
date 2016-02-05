"""Implements an L-System generator

"""

import random

class LSystem(object):
    """Implements an L-System generator"""

    def __init__(self):
        """Initialise the LSystem"""
        self.rules = []
        self._steps = 0
        self.setAxiom(None)
        self.reset()
        
    def setAxiom(self, axiom):
        """Set the axiom"""
        self.axiom = axiom
        if self._steps == 0:
            self.reset()
                    
    def getState(self):
        """Return the current state"""
        return self.state
        
    def reset(self):
        """Reset the generator"""
        self.state = self.axiom
    
    def addRule(self, rule):
        """Add a rule to the system"""
        self.rules.append(rule)
    
    def addRules(self, rules):
        """Add multiple rules to the system"""
        for rule in rules:
            self.addRule(rule)
    
    def doStep(self):
        """Step the generation by one"""
        self._steps += 1
        new_state = ''
        state = self.getState()
        cursor = 0
        #
        while cursor < len(state):
            for rule in self.rules:
                production, cursor_offset = rule.process(state[cursor:])
                if production:
                    #
                    # This rule matched, so move on and try all the rules again
                    new_state += production
                    cursor += cursor_offset
                    break
            else:
                #
                # Nothing matched so move on to the next character
                new_state += state[cursor]
                cursor += 1
        #
        self.state = new_state

    def doSteps(self, number):
        """Do a number of steps all at once"""
        for i in range(number):
            self.doStep()
                    
        
class Rule(object):
    """A rule for the L-System"""

    def __init__(self, predecessor, successor, probability=1.0):
        """Initialise the Rule"""
        self.predecessor = predecessor
        self.successor = successor
        self.probability = probability
        
    def process(self, state):
        """Process the state
        
        If we match then return the pattern we generate and the length of the state that we consumed.
        If we do not match then return nothing and a zero cursor offset.
        
        """
        if state.startswith(self.predecessor) and random.random() <= self.probability:
            return self.successor, len(self.predecessor)
        else:
            return '', 0
            



