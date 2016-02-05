#!/usr/bin/env python
#coding=utf-8

def get_heur((x,y), (ex,ey)):
    return abs(ex - x) + abs(ey - y)

def get_indexes((x,y)):
    return ( (x,y-1),  (x+1,y),  (x,y+1), (x-1,y) )

def valid((x,y),layout):
    if 0 <= x < layout.x_len and 0 <= y < layout.y_len:
        return layout[x][y]
    else:
        return False

def get_g(n, pdict):
    n0 = pdict.get(pdict[n])
    if n0:
        if n0[0] == n[0] or n0[1] == n[1]:
            return 1

    return 6
def get_g(n, p):
    if p:
        if n[0] == p[0] or n[1] == p[1]:
            return 1
    return 6
    
def pathfind(layout, start, end):
    if not valid(start,layout) or not valid(end,layout):
        return []
    open = []
    openDict = {} #indexed py position, not in dict = not processed, True = on open, False = on closed
    parent = {}
    f = {}
    g = {}
    h = {}
    
    g[start] = 0
    h[start] = get_heur(start, end)
    f[start] = g[start] + h[start]
    open.append(start)
    openDict[start] = True
    
    while len(open):
        open = sorted(open, key = lambda i: f[i])
        current = open[0]
        if current == end:
            return traceback(end,parent)
        open.remove(current)
        openDict[current] = False
        for i in get_indexes(current):
            iopen = openDict.get(i)
            if iopen == None:
                if valid(i,layout):
                    parent[i] = current
                    g[i] = g[current] +get_g(i,parent.get(current))
                    h[i] = get_heur(i, end)
                    f[i] = g[i] + h[i]
                    open.append(i)
                    openDict[i] = True
            elif iopen == True:
                pending_g = g[current] + get_g(i,parent.get(current))
                if g[i] > pending_g:
                    parent[i] = current
                    g[i] = pending_g
                    f[i] = g[i] + h[i]
            
    return []
            
                    
        
def traceback(end, pdict):
    points = []
    next = end
    while next is not None:
        points.append(next)
        next = pdict.get(next)
    return points
        

