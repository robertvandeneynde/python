"""Author: Sean McKiernan (Mekire)
Purpose: Exploring A* pathfinding.
License: Free for everyone and anything (no warranty expressed or implied)
Module: main.py
Overview: Primary driver for entire program.
Classes:
    Control(object):
        Methods:
            __init__(self)
            event_loop(self)
            game_loop(self)
Functions:
    main()"""
import sys,os
import pygame as pg
import interface

class Control(object):
    """Driver class for the whole program."""
    def __init__(self):
        self.Screen = pg.display.get_surface()
        self.done = False
        self.Clock = pg.time.Clock()
        self.fps = 50
        self.State = interface.Interface()
        
    def event_loop(self):
        """Check event queue and pass events to states as necessary."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            if self.State.mode != "RUN":
                self.State.get_event(event)
                
    def game_loop(self):
        """Main game loop of entire program."""
        while not self.done:
            self.event_loop()
            self.State.update(self.Screen)
            self.Clock.tick_busy_loop(self.fps)
            pg.display.flip()

###
def main():
    """Initialize the display and create an instance of Control."""
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption("A* Demonstration")
    pg.display.set_mode((900,700))
    RunIt = Control()
    RunIt.game_loop()
    pg.quit();sys.exit()

###
if __name__ == "__main__":
    main()

