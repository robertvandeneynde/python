""" Module loader
Overview:
    Contains files transalted to ready-to-use python objects.
    the 'position' type has the interface of a 2-int-tuple
Exception:
    LoadError: class(Exception)
Classes:
    Move(object):
        directions: list<position>
        portee: iterable<int> (may be infinite)
Variables:
    pieces: objects
        heuristics: dict<name:str, heuristic:function>
        moves: list<Move>"""

import json
import heuristics as heuristics_module

import itertools
import collections

from sys import version_info as PYVERSION

if PYVERSION >= (3,):
    xrange = range

class LoadError(Exception):
    pass

class Move:
    """
    directions: list<position>
    intrange: int | None (infinite)
    range(): iterable<int> (may be infinite)
    """
    def __init__(self, directions, intrange=None):
        self.directions = directions
        self.intrange = intrange
    
    def range(self):
        return xrange(1,1+self.intrange) if type(self.intrange) is int else \
               itertools.count(1)

class _Settings:
    def __init__(self, filename):
        self.heuristics = collections.OrderedDict()
        self.moves = collections.OrderedDict()
        self.order = []
        
        full_moves = set()
        waitings = []
        
        self.tree = tree = json.load(open(filename, 'r'))
        self.size = X,Y = tuple(tree["size"])
        self.cell_size = c = 20
        
        from pygame import Rect
        self.field_area = Rect(0,0, c*X,c*Y)
        
        self.order = [str(s) for s in tree["order"] if s in tree["pieces"]]
        for name,piece in tree["pieces"].items():
            
            (h_name,directions,rang) = (piece[s] for s in 
                ("heuristic","directions","range"))
            
            h_name,name = map(str,
                (h_name,name)) # python2 unicode
            
            self.heuristics[name] = getattr(heuristics_module,h_name)
            self.moves[name] = Move([], rang if type(rang) is int else None)
            
            if type(directions) is not list:
                directions = [directions]
            
            waiting = []
            for d in directions:
                if type(d) is list:
                    assert len(d) == 2
                    self.moves[name].directions.append(tuple(d))
                else:
                    waiting.append(str(d))
            
            if len(waiting) == 0:
                full_moves.add(name)
            else:
                waitings.append( (name,waiting) )
                
        while waitings:
            changed = False
            
            new_waitings = []
            for name,waiting in waitings:
                new_waiting = []
                for target in waiting:
                    if target in full_moves:
                        self.moves[name].directions += self.moves[target].directions
                        changed = True
                    else:
                        new_waiting.append(target)
                
                if len(new_waiting) == 0:
                    full_moves.add(name)
                    changed = True
                else:
                    new_waitings.append( (name,new_waiting) )
            
            waitings = new_waitings
            
            if not changed:
                raise LoadError("Infinite Loop in json!")
            
settings = _Settings("settings.json")