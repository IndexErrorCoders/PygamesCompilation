import pygame, math, sys, os, random

class Menu(object):
    def __init__(self, items, f, location, dy, color):
        self.dy = dy + f.size(items[0])[1]
        self.length = len(items)
        self.loc = location

        self.width = 0
        self.widths = []
        for i, item in enumerate(items):
            self.widths.append(f.size(item)[0])
            if f.size(item)[0] > self.width:
                self.width = f.size(item)[0]
                bigwidth = i

        self.backrect = pygame.image.load(os.path.join("images", "backrect.png")).convert_alpha()
        self.highlight = 0
        self.surfs = []
        self.rects = []

        x = location[0]
        y = location[1]
        for i, item in enumerate(items):
            surf = f.render(item, 1, color)
            rect = pygame.Rect(x, y, self.widths[bigwidth], f.size(item)[1])
            self.surfs.append(surf)
            self.rects.append(rect)
            y += self.dy

    def checkmouse(self, point):
        for x, rect in enumerate(self.rects):
            if rect.collidepoint(point):
                self.highlight = x + 1
                break
            else:
                self.highlight = 0

    def movehighlight(self, x):
        self.highlight += x
        if self.highlight < 1:
            self.highlight = self.length
        elif self.highlight > self.length:
            self.highlight = 1

    def draw(self, screen):
        if self.highlight:
            screen.blit(self.backrect, ((self.loc[0] - 5), (self.loc[1] + (self.highlight - 1) * self.dy - 5)))
        for y, surf in enumerate(self.surfs):
            screen.blit(surf, ((self.loc[0] + (self.width - self.widths[y]) / 2), (self.loc[1] + y * self.dy)))