from turtle_fr import *

shape('turtle')

def grille():
    zigzag()
    go(100)
    go(-100)
    tg(90)
    zigzag()
    go(100)
    
def zigzag():
    for i in range(5):
        go(100)
        td(90)
        go(10)
        td(90)
        go(100)
        tg(90)
        go(10)
        tg(90)
        
def hexa():
    begin_fill()
    for i in range(6):
        go(40)
        td(300)
    end_fill()

def ligne():
    for i in range(8):
        hexa()
        go(100)

def guirlande():
    ligne()
    tg(180)
    ligne()
    hexa()

