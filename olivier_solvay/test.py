from Tkinter import *

fen = Tk()

monLabel = Label(fen, text="Encodez votre texte")
monLabel.pack()

fen.mainloop()

vitesse = 130
if vitesse > 130:
    amende = (vitesse - 130) * 100

def f(a, b=2, c=5):
    print a, b, c
   
int("Hello")

L = [ [1,2], [3,4] ]

for x in L:
    for n in x:
        print(n)
        
from random import randint

class Soldier:
    def __init__(self, the_name, the_health, the_skill):
        self.name = the_name
        self.health = the_health
        self.skill = the_skill
    
    def attack(self, attacked_soldier):
        damage = self.skill + randint(0,10)
        attacked_soldier.health = int(attacked_soldier.health - damage)
        
napoleon = Soldier("Napo'", 100, 5)
nelson = Soldier("Nel'", 80, 14)

napoleon.attack(nelson)
nelson.attack(napoleon)