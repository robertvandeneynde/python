"""Module: solver.py
Overview:
    Contains the astar algorithm itself which can be used completely
    independent of the rest of the program.
Gobal Constants:
    ADJACENTS
    HEURISTICS
Functions:
    rook(x,y)
    queen(x,y)
    knight(x,y)
Classes:
    Star(object):
        Methods:
            __init__(self)
            setup(self)
            get_neighbors(self)
            follow_current_path(self)
            get_path(self,cell)
            evaluate(self)"""

import itertools

class Star(object):
    """This class is the astar algorithm itself.  The goal is to make it
    flexible enough that it can be used in isolation."""
    def __init__(self,start,end,move,barriers,heuristic):
        """Arguments start and end are coordinates to start solving from and to.
        move_type is a string cooresponding to the keys of the ADJACENTS and
        HEURISTICS constant dictionaries. barriers is a set of cells which the
        agent is not allowed to occupy."""
        self.start = start
        self.end = end
        self.move = move
        self.heuristic = heuristic
        self.barriers = barriers
        self.setup()
        
    def setup(self):
        """Initialize sets,dicts and others"""
        self.closed_set = set({self.start}) #Set of cells already evaluated
        self.open_set   = set() #Set of cells to be evaluated.
        self.came_from = {} #Used to reconstruct path once solved.
        self.gx = {self.start:0} #Cost from start to current position.
        self.hx = {} #Optimal estimate to goal based on heuristic.
        self.fx = {} #Distance-plus-cost heuristic function.
        self.current = self.start
        self.current = self._follow_current_path()
        self.solution = []
        self.solved = False

    def _get_neighbors(self):
        """Find adjacent neighbors with respect to how our agent moves."""
        x,y = self.current
        for dx,dy in self.move.directions:
            for i in self.move.range():
                check = x + i*dx, y + i*dy
                if check in self.barriers:
                    break
                else:
                    if check not in self.closed_set:
                        yield check

    def _follow_current_path(self):
        """In the very common case of multiple points having the same heuristic
        value, this function makes sure that points on the current path take
        presidence.  This is most obvious when trying to use astar on an
        obstacle free grid."""
        next_cell = None
        for cell in self._get_neighbors():
            tentative_gx = self.gx[self.current]+1
            if cell not in self.open_set:
                self.open_set.add(cell)
                tentative_best = True
            elif cell in self.gx and tentative_gx < self.gx[cell]:
                tentative_best = True
            else:
                tentative_best = False

            if tentative_best:
                (cx,cy),(ex,ey) = cell, self.end
                dx,dy = abs(ex - cx), abs(ey - cy)
                self.came_from[cell] = self.current
                self.gx[cell] = tentative_gx
                self.hx[cell] = self.heuristic(dx,dy)
                self.fx[cell] = self.gx[cell] + self.hx[cell]
                if not next_cell or self.fx[cell] < self.fx[next_cell]:
                    next_cell = cell
        return next_cell
    
    def get_path(self,cell):
        """Recursively reconstruct the path. No real need to do it recursively."""
        try:
            return (cell,) + self.get_path(self.came_from[cell])
        except KeyError: # cell not in self.came_from
            return ()

    def evaluate(self):
        """Core logic for executing the astar algorithm."""
        if self.open_set and not self.solved:
            for cell in self.open_set:
                if (self.current not in self.open_set) or (self.fx[cell]<self.fx[self.current]):
                    self.current = cell
            if self.current == self.end:
                self.solution = self.get_path(self.current)
                self.solved = True
            self.open_set.discard(self.current)
            self.closed_set.add(self.current)
            self.current = self._follow_current_path()
        elif not self.solution:
            self.solution = "NO SOLUTION"
