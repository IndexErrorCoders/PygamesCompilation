"""Renders trees"""

import math
import random

import pygame

import serge.visual
import serge.blocks.visualeffects
import serge.blocks.lsystem

from theme import G, theme
import common 

class LTree(serge.visual.SurfaceDrawing):
    """A drawing of an L-Tree"""

    colour = (255, 255, 255, 50)
    init_angle = 90
    offset_angle = 25
    init_distance = 10
    blur_amount = 0
    circle_size = 3
    draw_circles = True
    overstuff = 2
    jitter = (-5, +5, 0)
    colour_jitter = (-100, +100, 0)
    
    def __init__(self, width, height, axiom, rules):
        """Initialise the LTree"""
        super(LTree, self).__init__(width, height)
        #
        self.log = serge.common.getLogger('LTree')
        #
        self.ltree = serge.blocks.lsystem.LSystem()
        self.ltree.setAxiom(axiom)
        self.ltree.addRules(rules)
        self.ltree.reset()

    def doStep(self, n=1):
        """Step the L-Tree"""
        self.ltree.doSteps(n)
        self.log.debug('Current is %s, length is %s' % (self.ltree.getState()[:30], len(self.ltree.getState())))
        #
        self.clearSurface()
        self.draw(self.width/2, self.height, self.init_angle, self.colour, self.init_distance, self.ltree.getState())
        self.doBlur()
    
    def draw(self, x, y, angle, colour, distance, string):
        """Draw the tree"""
        #
        # Stack to store positions
        stack = []
        #
        # Execute the string
        while string:
            char, string = string[0], string[1:]
            if char == 'F':
                at = serge.simplevecs.Vec2d((x, y)) 
                offset = serge.simplevecs.Vec2d((distance, 0)).rotated_degrees(-angle)
                nx, ny = at+offset
                pygame.draw.line(self.getSurface(), colour, (x, y), (nx, ny), 1)
                self.drawTrunk((x, y), (nx, ny), colour)
                x, y = nx, ny
            elif char == '-':
                angle -= self.offset_angle
            elif char == '+':
                angle += self.offset_angle
            elif char == '[':
                stack.append((x, y, angle, distance, colour))
            elif char == ']':
                x, y, angle, distance, colour = stack.pop()
            elif char == '/':
                distance = distance / 2.0
            elif char == '*':
                distance = distance * 2.0
            elif char == '<':
                angle = angle * 2.0
            elif char == '>':
                angle = angle / 2.0
            elif char == '%':
                pygame.draw.circle(self.getSurface(), colour, (int(x), int(y)), int(distance))

    def drawTrunk(self, (sx, sy), (ex, ey), colour):
        """Draw a trunk from the start to the end"""
        if not self.draw_circles:
            return
        #
        start = serge.simplevecs.Vec2d(sx, sy)
        end = serge.simplevecs.Vec2d(ex, ey)
        offset = end - start
        number = float(max(math.floor(offset.length/(float(self.circle_size)/2)), 1) * self.overstuff)
        step_offset = offset / number
        #
        for i in range(int(number)):
            px, py = start + step_offset*i
            px = px + random.triangular(*self.jitter)
            py = py + random.triangular(*self.jitter)
            pygame.draw.circle(self.getSurface(), self.getColour(colour), (int(px), int(py)), self.circle_size*2)
            
    def getColour(self, colour):
        """Return a colour adjusted to be random"""
        c = []
        for component in colour[:3]:
            actual = min(255, max(0, component + random.triangular(*self.colour_jitter)))
            c.append(actual)
        return tuple(c)
    
    def doBlur(self):
        """Blur the image"""
        if self.blur_amount != 0:
            self.log.debug('Bluring surface by %s' % self.blur_amount)
            self.setSurface(serge.blocks.visualeffects.gaussianBlur(self.getSurface(), self.blur_amount))
            
def getTree(name, L):
    """Return a tree"""
    t = serge.actor.Actor('tree', name)
    t.setLayerName('main')
    t.visual = LTree(L('tree-size'), L('tree-size'), 'X', L('tree-rules'))
    t.visual.init_distance = L('tree-distance')
    t.visual.blur_amount = L('tree-blur')
    t.visual.circle_size = L('tree-circle-size')
    t.visual.colour = L('tree-colour')
    #
    t.visual.doStep(L('tree-steps'))
    #
    return t
    
def addTrees(L, world):
    """Add some trees to a world"""
    for i in range(L('number-trees')):
        t = getTree('main-tree', L)
        t.moveTo(random.randrange(*L('tree-positions')), 400)
        world.addActor(t)

