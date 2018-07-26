from threading import *
from time import sleep

ev = Event()

def logic():
    i = 0
    def get(msg, liste):
        ev.clear()
        choose_list(msg, liste)
        if liste:
            ev.wait()
            return ev.result
        else:
            return None
    
    n = get("Choisis le nombre de joueur", [2,3,4])
    
    sleep(1.0)
    
    print("Vous avez choisi", n, "joueurs")
    
    couleur = get("Choisis une couleur", ['red', 'blue'])
    
    sleep(1.0)
    
    print("Vous avez choisi", couleur)
    
    get("No more !", [])
    
    print("Bye !")

from tkinter import *
from functools import partial

app = Tk()
app.geometry("800x600")

def respond_message(x):
    ''' Will be called by graphical thread '''
    ev.result = x
    
    label['text'] = "Calcul en cours..."
    
    global frame
    frame.destroy()
    frame = Frame(app)
    frame.pack()
    
    ev.set()

def choose_list(msg, liste):
    ''' Will be called by logic thread '''
    label['text'] = msg
    
    global frame
    frame.destroy()
    frame = Frame(app)
    frame.pack()
    
    for a in liste:
        b1 = Button(frame, text=str(a), command=partial(respond_message, a))
        b1.pack()

frame = Frame(app)
frame.pack()

label = Label(app)
label.pack()

other = Thread(target=logic)
other.start()

app.mainloop()
