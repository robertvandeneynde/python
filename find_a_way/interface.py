"""Module: interface.py
Overview: The core of the GUI for the A* demo.
Classes:
    Interface(object):
        Methods:
            __init__(self)
            make_background(self)
            reset(self,full=True)
            setup_barriers(self)
            render_text(self,specific=None)
            get_target(self)
            get_event(self,event)
            left_button_clicked(self)
            right_button_clicked(self)
            hotkeys(self,event)
            toggle_animate(self)
            toggle_piece(self,ind=None)
            add_barriers(self)
            update(self,Surf)
            found_solution(self)
            fill_cell(self,cell,color,Surf)
            center_number(self,cent,string,color,Surf)
            draw(self,Surf)
            draw_solve(self,Surf)
            draw_start_end_walls(self,Surf)
            draw_messages(self,Surf)"""
            
import pygame as pg
import solver
import heuristics as heuristics_module
from loader import settings as SETTINGS

import collections
import inspect
def getmodulefunctions(module):
    return [o for o in inspect.getmembers(module) if inspect.isfunction(o[1])]

class Interface(object):
    def __init__(self):
        self.target = (-1,-1)
        self.animate = True
        special_heuristic_choice = ("<self>", lambda name: SETTINGS.heuristics[name])
        self.heuristics = [special_heuristic_choice] + list(getmodulefunctions(heuristics_module))
        self.index_heuristic = 0
        self.current_heuristic = self.heuristics[0]
        self.options = list(SETTINGS.order)
        self.piece_type = self.options[0]
        self.image = self.make_background()
        self.reset()
        self.font = pg.font.SysFont("arial",13)
        self.rendered = {}
        self.render_text()

    def make_background(self):
        """Create grid image. Currently screen and cell size are hardcoded."""
        image = pg.Surface(SETTINGS.field_area.size, depth=32).convert_alpha()
        image.fill((255,0,255,0))
        (X,Y),(W,H),c = SETTINGS.size,SETTINGS.field_area.size,SETTINGS.cell_size
        red = pg.color.Color(255,0,0)
        for i in range(X+1):
            image.fill(red,(c*i,0, 2,H))
        for i in range(Y+1):
            image.fill(red,(0,c*i, W,2))
        return image

    def reset(self,full=True):
        """Allows both completely resetting the grid or resetting to an
        unsolved state."""
        if full:
            self.mode = "START"
            self.start_cell = None
            self.goal_cell = None
            self.barriers  = self.setup_barriers()
            self.Solver = None
            self.time_end = self.time_start = 0.0
            self.solution = []
        else:
            self.Solver = None
            self.mode = "BARRIER"

    def setup_barriers(self):
        """Initialize the boundary borders. Borders must be two cells thick to
        prevent knight pieces from leaving the grid."""
        self.add_barrier = False
        self.del_barrier = False
        barriers = set()
        X,Y = SETTINGS.size
        for i in range(-2,X+2):
            for j in (-2,-1,Y,Y+1):
                barriers.add((i,j))
        for j in range(-2,Y+2):
            for i in (-2,-1,X,X+1):
                barriers.add((i,j))
        return barriers

    def render_text(self,specific=None):
        """Prerender text messages. By default all are rendered. Single messages
        can be rerendered by passing a key corresponding to the below dictionary."""
        text = {
            "START"    : ["Place your start point:",(10,1)],
            "GOAL"     : ["Place your goal:",(10,1)],
            "BARRIER"  : ["Draw your walls or press spacebar to solve:",(10,1)],
            "ENTER"    : ["Press 'Enter' to restart.",(10,1)],
            "RESET"    : ["Press 'i' to reset.",(150,1)],
            "ANIM"     : [
                "Animation: {}".format(["Off","On"][self.animate]),
                (10,40)
            ],
            "HEURISTIC": [
                "Heuristic: {}".format(self.current_heuristic[0]),
                (10,60)
            ],
            "MOVE"     : [
                "Move type: {}".format(self.piece_type.capitalize()),
                (10,80)
            ],
            "TIME"     : [
                "Time (ms): {}".format(self.time_end - self.time_start),
                (100,20)
            ],
            "FAILED"   : [
                "No solution.",
                (20,20)
            ],
            "SOLVED"   : [
                "Steps: {}".format(len(self.solution)),
                (20,20)
            ]
        }
        rendered_names = (text.keys()
                          if specific is None
                          else [specific])
        
        W,H = SETTINGS.field_area.size
        for name in rendered_names:
            msg,(rx,ry) = text[name]
            rend = self.font.render(msg,1,(255,255,255))
            tx,ty = SETTINGS.field_area.bottomleft
            ty += 2 * SETTINGS.cell_size 
            rect = pg.Rect(rend.get_rect(topleft=(rx+tx,ry+ty)))
            self.rendered[name] = [rend,rect]

    def get_target(self):
        """Find both the exact mouse position and its position in graph cells."""
        c = SETTINGS.cell_size
        previous = self.target
        self.mouse = mx,my = pg.mouse.get_pos()
        self.target = (mx // c, my // c)
        if previous != self.target:
            self.target_changed()
            
    def get_event(self,event):
        """Receives events from the control class and passes them along as appropriate."""
        self.get_target()
        if event.type == pg.MOUSEBUTTONDOWN:
            hit = pg.mouse.get_pressed()
            if hit[0]:
                self.left_button_clicked()
            elif hit[1]:
                self.middle_button_clicked()
            elif hit[2]:
                self.right_button_clicked()
        elif event.type == pg.MOUSEBUTTONUP:
            self.add_barrier = False
            self.del_barrier = False
        elif event.type == pg.KEYDOWN:
            self.hotkeys(event)

    def left_button_clicked(self):
        """Left mouse button functionality for get_event method."""
        if SETTINGS.field_area.collidepoint(self.mouse):
            if self.mode == "START":
                if self.target != self.goal_cell and self.target not in self.barriers:
                    self.start_cell = self.target
                    self.mode = ("BARRIER" if self.goal_cell else "GOAL")
            elif self.mode == "GOAL":
                if self.target != self.start_cell and self.target not in self.barriers:
                    self.goal_cell = self.target
                    self.mode = "BARRIER"
            elif self.mode == "BARRIER":
                self.add_barrier = True
        elif self.rendered["MOVE"][1].collidepoint(self.mouse):
            self.toggle_piece()
        elif self.rendered["ANIM"][1].collidepoint(self.mouse):
            self.toggle_animate()
        elif self.rendered["HEURISTIC"][1].collidepoint(self.mouse):
            self.toggle_heuristic()
        elif self.mode == "BARRIER" and self.rendered["BARRIER"][1].collidepoint(self.mouse):
            self.mode = "RUN"
        elif self.mode in ("SOLVED","FAILED"):
            if self.rendered["ENTER"][1].collidepoint(self.mouse):
                self.reset()
            elif self.rendered["RESET"][1].collidepoint(self.mouse):
                self.reset(False)

    def right_button_clicked(self):
        """Right mouse button functionality for get_event method."""
        if SETTINGS.field_area.collidepoint(self.mouse):
            if self.mode != "RUN":
                if self.target == self.start_cell:
                    self.start_cell = None
                    self.mode = "START"
                elif self.target == self.goal_cell:
                    self.goal_cell = None
                    self.mode = ("GOAL" if self.start_cell else "START")
                elif self.mode == "BARRIER":
                    self.del_barrier = True
        elif self.rendered["MOVE"][1].collidepoint(self.mouse):
            self.toggle_piece(-1)
        elif self.rendered["HEURISTIC"][1].collidepoint(self.mouse):
            self.toggle_heuristic(-1)
            
     
    def middle_button_clicked(self):
        """Middle mouse button functionality for get_event method."""
        if self.mode in ("RUN", "SOLVED", "FAILED"):
            if self.target in self.Solver.closed_set:
                self.solution = self.Solver.get_path(self.target)

    def hotkeys(self,event):
        """Keyboard functionality for get_event method."""
        if pg.K_0 <= event.key <= pg.K_9:
            self.toggle_piece(index=(event.key - pg.K_0))
        elif event.key == pg.K_d:
            self.toggle_animate()
        elif event.key == pg.K_d:
            self.toggle_heuristic()
        elif self.mode == "BARRIER" and event.key == pg.K_SPACE:
            self.mode = "RUN"
        elif self.mode in ("SOLVED","FAILED"):
             if event.key == pg.K_RETURN:
                self.reset()
             elif event.key == pg.K_i:
                self.reset(False)

    def toggle_animate(self):
        """Turns animation mode on and off."""
        if self.mode != "RUN":
            self.animate = not self.animate
            self.render_text("ANIM")

    def toggle_heuristic(self,diff=1):
        if self.mode != "RUN":
            self.index_heuristic += diff
            self.index_heuristic %= len(self.heuristics)
            self.current_heuristic = self.heuristics[self.index_heuristic]
            self.render_text("HEURISTIC")

    def toggle_piece(self,diff=1,index=None):
        """Change to next piece or to a specific piece if ind is supplied."""
        if self.mode != "RUN":
            if index is None:
                index = ( (self.options.index(self.piece_type) + diff)
                          % len(self.options) )
            self.piece_type = self.options[index]
            self.render_text("MOVE")

    def add_barriers(self):
        """Controls both adding and deleting barrier cells with the mouse."""
        if self.mode == "BARRIER":
            self.get_target()
            if SETTINGS.field_area.collidepoint(self.mouse):
                if self.target not in (self.start_cell,self.goal_cell):
                    if self.add_barrier:
                        self.barriers.add(self.target)
                    elif self.del_barrier:
                        self.barriers.discard(self.target)

    def target_changed(self):
        if pg.mouse.get_pressed()[1]:
            self.middle_button_clicked()

    def update(self,surf):
        """Primary update logic control flow for the GUI."""
        self.add_barriers()
        if self.mode == "RUN":
            if not self.Solver:
                self.time_start = pg.time.get_ticks()

                self.Solver = solver.Star(
                    start=self.start_cell,
                    end=self.goal_cell,
                    move=SETTINGS.moves[self.piece_type],
                    barriers=self.barriers,
                    heuristic=(self.current_heuristic[1]
                               if self.current_heuristic[0] != '<self>'
                               else self.current_heuristic[1](self.piece_type))
                )
                
            if self.animate:
                self.Solver.evaluate()
            else:
                while not self.Solver.solution:
                    self.Solver.evaluate()
            if self.Solver.solution:
                self.found_solution()
        if self.mode != "RUN" or self.animate:
            self.draw(surf)

    def found_solution(self):
        """Sets appropriate mode when solution is found (or failed)."""
        self.time_end = pg.time.get_ticks()
        if self.Solver.solution == "NO SOLUTION":
            self.mode = "FAILED"
        else:
            self.solution = self.Solver.solution
            self.mode = "SOLVED"
            self.render_text("SOLVED")
        self.render_text("TIME")

    def fill_cell(self,cell,color,surf):
        """Fills a single cell given coordinates, color, and a target Surface."""
        (x,y),c = cell,SETTINGS.cell_size
        rect = pg.Rect(x*c,y*c, c,c)
        surf.fill(color,rect)
        return rect
    
    def center_number(self,cent,string,color,surf):
        """Used for centering numbers on cells."""
        rend = self.font.render(string,1,color)
        rect = pg.Rect(rend.get_rect(center=cent))
        rect.move_ip(1,1)
        surf.blit(rend,rect)

    def draw(self,surf):
        """Calls draw functions in the appropraite order."""
        surf.fill(0)
        self.draw_solve(surf)
        self.draw_start_end_walls(surf)
        surf.blit(self.image,(0,0))
        self.draw_messages(surf)
        
    def draw_solve(self,surf):
        """Draws while solving (if animate is on) and once solved."""
        if self.mode in ("RUN","SOLVED","FAILED"):
            for cell in self.Solver.closed_set:
                cent = self.fill_cell(cell,(255,0,255),surf).center
                numero = self.Solver.gx[cell]
                self.center_number(cent,str(numero), (0xAA,0xAA,0xAA),surf)
            
            if self.mode == "SOLVED":
                for i,cell in enumerate(self.solution):
                    cent = self.fill_cell(cell,(0,255,0),surf).center
                    numero = self.Solver.gx[cell]
                    self.center_number(cent,str(numero),(0,0,0),surf)
    
    def draw_start_end_walls(self,surf):
        """Draw endpoints and barriers."""
        if self.start_cell:
            self.fill_cell(self.start_cell,(255,255,0),surf)
        if self.goal_cell:
            cent = self.fill_cell(self.goal_cell,(0,0,255),surf).center
            if self.mode == "SOLVED":
                numero = self.Solver.gx[self.goal_cell]
                self.center_number(cent,str(numero),(255,255,255),surf)
        for cell in self.barriers:
            self.fill_cell(cell,(255,255,255),surf)
            
    def draw_messages(self,surf):
        """Draws the text (not including cell numbers)."""
        for key in [self.mode,"MOVE","ANIM","HEURISTIC"]:
            try:
                surf.blit(*self.rendered[key])
            except KeyError:
                pass
            
        if self.mode in ("SOLVED","FAILED"):
            for rend in ("TIME","RESET","ENTER"):
                surf.blit(*self.rendered[rend])
