#!/usr/bin/env python
#coding=utf-8
# A* Pathfinding :)

class PtfManager(object):
    def __init__(self, layout):
        self.layout = layout
        Node.ref = self
        
    def pathfind(self,(sx,sy), (ex,ey)):
        #if not self.layout[sx][sy] or not self.layout[ex][ey]:
            #return None
        
        Node.ex = ex
        Node.ey = ey
        self.open = []
        closed = []
        self.siDict = {} #spatially indexed dict
        
        
        self.open.append(Node(Start((sx,sy)),(sx,sx)))
        goal_found = False
        while len(self.open) and not goal_found:
            self.current = self.open[-1]
            closed.append(self.current)
            self.open.remove(self.current)
            self.current.on_closed = True
            if self.current.pos == (ex,ey):
                goal_found = True
            for i in self.get_indexes(self.current.pos):
                c = self.siDict.get(i)
                if c:
                    if not c.on_closed:
                        if self.current.g > c.g:
                            self.current.recalc(c)
                            self.open = sorted(self.open,key = lambda obj: obj.f)
                else:
                    if self.check_pos(i):
                        self.insert(i)
        traceback = True
        node = self.current
        poslist = []
        if goal_found:
            while traceback:
                poslist.append(node.pos)
                node = node.parent
                if isinstance(node, Start):
                    traceback = False
        
        return poslist
        
    def check_pos(self,(x,y)):
        if 0 <= x < self.layout.x_len and 0 <= y < self.layout.y_len:
            return self.layout[x][y]
        else:
            return False
        
    def get_indexes(self, (x,y)):
        return ( (x,y-1),  (x+1,y),  (x,y+1), (x-1,y) )
    
    def insert(self,new):
        p = self.current
        n =  Node(p,new)
        self.siDict[new] = n
        if n.f > p.f:
            self.open.append(n)
        else:
            self.open.append(n)
            self.open = sorted(self.open,key = lambda obj: obj.f)
            
class Node(object):
    def __init__(self, parent, (x,y)):
        self.parent = parent
        self.g = parent.g +1
        self.pos = (x,y)
        self.h = abs(self.ex - x) + abs(self.ey - y)
        self.f = self.g + self.h
        self.on_closed = False
        
    def recalc(self, new_parent):
        self.parent = new_parent
        self.g = self.parent.g + 1
        self.f = self.g + self.h
        
class Start(object):
    def __init__(self,pos):
        self.pos = pos
        self.g = 0

