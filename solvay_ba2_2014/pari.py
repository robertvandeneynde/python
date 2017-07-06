from tkinter import *
from tkinter.messagebox import *
from functools import partial
from random import randint, shuffle, choice, randrange

class Parieur:
    def __init__(self, nom):
        self.nom = nom
        self.paris = []

class Pari:
    def __init__(self, parieur, montant, equipe, phase):
        self.parieur = parieur
        self.montant = montant
        self.equipe = equipe
        self.phase = phase
        
        self.parieur.paris.append(self)

class Equipe:
    def __init__(self, nom, force):
        self.nom = nom
        self.force = force
        
class Match:
    def __init__(self, equipe1, equipe2):
        self.equipe1 = equipe1
        self.equipe2 = equipe2
        self.vainqueur = None
        
    def determinerVainqueur(self):
        r = randint(1, self.equipe1.force + self.equipe2.force)
        if r <= self.equipe1.force:
            self.vainqueur = self.equipe1
        else:
            self.vainqueur = self.equipe2

class Championnat:
    def __init__(self):
        self.equipes = [
            Equipe("Looney Tunes", 8),
            Equipe("Pokemons", 8),
            Equipe("Profs", 3),
            Equipe("Footballers", 4),
            
            Equipe("Basketteurs", 4),
            Equipe("Étudiants", 6),
            Equipe("Musiciens", 4),
            Equipe("Youtubers", 4),
            
            Equipe("Mario brothers", 5),
            Equipe("Smash bros", 10),
            Equipe("Series Actors", 6),
            Equipe("Movies Actors", 8),
            
            Equipe("Vegetarians", 7),
            Equipe("Animals", 5),
            Equipe("Dj's", 6),
            Equipe("Dancers", 8),
        ]
        self.parieurs = []
        self.matches = []
        self.phase = 8 # 8ème de finale, 16 equipes
        
        self.nomsPhases = {
            8: "Huitième de finale",
            4: "Quart de finale",
            2: "Demi-finale",
            1: "Finale",
            0: "Fin",
        }
        
        shuffle(self.equipes)
        self.createMatches()
    
    def createMatches(self):
        self.matches = []
        i = 0
        while i < len(self.equipes):
            m = Match(self.equipes[i], self.equipes[i+1])
            self.matches.append(m)
            i += 2
    
    def playMatches(self):
        gagnants = []
        for match in self.matches:
            match.determinerVainqueur()
            gagnants.append(match.vainqueur)
        
        self.equipes = gagnants
    
    def etapeSuivante(self):
        self.playMatches()
        self.phase //= 2
        if self.phase > 0:
            self.createMatches()
        
        fenetre = Toplevel()
        Label(fenetre,
              text="Equipes qualifiées pour \"" + self.nomsPhases[self.phase] + "\"",
        ).pack()
        for equipe in self.equipes:
            Label(fenetre, text=equipe.nom).pack()
        
class Fenetre:
    def __init__(self):
        self.championnat = Championnat()
        self.fen = Tk()
        self.frame = Frame(self.fen)
        self.menuprincipal()
        self.fen.mainloop()
        
    def refreshFrame(self):
        self.frame.destroy()
        self.frame = Frame(self.fen)
        self.frame.pack()
        
    def menuprincipal(self):
        self.refreshFrame()
        
        Label(self.frame, text="Nom ?").pack()
        self.entryNom = Entry(self.frame)
        self.entryNom.pack()
        Button(self.frame,
               text="Parier pour \"" + self.championnat.nomsPhases[self.championnat.phase] + "\"",
               command=self.choixEquipe
        ).pack()
        
        Button(self.frame,
               text="Passer à \"" + self.championnat.nomsPhases[self.championnat.phase // 2] + "\"",
               command=self.etapeSuivante
        ).pack()
        
        Button(self.frame,
               text="Voir les gains",
               command=self.calculerGains).pack()
        
    def etapeSuivante(self):
        self.championnat.etapeSuivante()
        if self.championnat.phase == 0:
            self.calculerGains()
        else:
            self.menuprincipal()
        
    def choixEquipe(self):
        nom = self.entryNom.get()
        
        self.parieurEnCours = None
        for parieur in self.championnat.parieurs:
            if parieur.nom == nom:
                self.parieurEnCours = parieur
                
        if self.parieurEnCours == None:
            self.parieurEnCours = Parieur(nom)
            self.championnat.parieurs.append(self.parieurEnCours)
            showinfo("Login", "Bienvenue nouveau parieur " + nom)
        else:
            showinfo("Login", "Oooh yeah, welcome back " + nom + " !")
        
        self.refreshFrame()
        Label(self.frame, text="Montant").pack()
        self.montantEntry = Entry(self.frame)
        self.montantEntry.pack()
        Label(self.frame, text="Équipe").pack()
        for equipe in self.championnat.equipes:
            Button(self.frame,
                   text = equipe.nom,
                   command = partial(self.enregistrerPari,equipe)
            ).pack()
        
        Button(self.frame, text="Se déconnecter", command=self.menuprincipal).pack()
        
    def enregistrerPari(self, equipe):
        montant = int(self.montantEntry.get())
        Pari(self.parieurEnCours,
             montant,
             equipe,
             self.championnat.phase)
        showinfo("Pari", "Votre pari est enregistré !")
        
    def calculerGains(self):
        cagnotte = 0
        for parieur in self.championnat.parieurs:
            for pari in parieur.paris:
                cagnotte += pari.montant
        
        fenetre = Toplevel()
        Label(fenetre,
              text = "Cagnotte : " + str(cagnotte) + '€'
        ).pack()
        
        Label(fenetre,
              text = "Nombre de parieurs: " + str(len(self.championnat.parieurs))
        ).pack()
        
        tableau = Frame(fenetre)
        tableau.pack()
        
        totalGagnants = 0
        for parieur in self.championnat.parieurs:
            for pari in parieur.paris:
                if pari.equipe in self.championnat.equipes:
                    totalGagnants += pari.montant * pari.phase
        
        i = 1
        for parieur in self.championnat.parieurs:
            mesGagnants = 0
            for pari in parieur.paris:
                if pari.equipe in self.championnat.equipes:
                    mesGagnants += pari.montant * pari.phase
            
            if totalGagnants > 0:
                fraction = mesGagnants / totalGagnants
            else:
                fraction = 0
            
            Label(tableau, text = "Parieur").grid(row=i, column=1)
            Label(tableau, text = parieur.nom).grid(row=i, column=2)
            Label(tableau, text = "gagne").grid(row=i, column=3)
            Label(tableau, text = str(int(fraction * 100))).grid(row=i, column=4)
            Label(tableau, text = "% de").grid(row=i, column=5)
            Label(tableau, text = str(cagnotte)).grid(row=i, column=6)
            Label(tableau, text = "=").grid(row=i, column=7)
            Label(tableau, text = str(fraction * cagnotte)).grid(row=i, column=8)
            Label(tableau, text = "€").grid(row=i, column=9)
            
            i += 1
            
Fenetre()