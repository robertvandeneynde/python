from tkinter import *
from tkinter.messagebox import *
from random import randint, randrange, shuffle, choice
from functools import partial

class Vote:
    def __init__(self, electeur):
        self.electeur = electeur
        self.candidat = None
        self.parti = None
        
    def voteTeteDeListe(self, parti):
        self.parti = parti
        self.parti.votes += 1
        
    def voteCandidat(self, candidat):
        self.candidat = candidat
        self.parti = candidat.parti
        self.parti.votes += 1
        self.candidat.votes += 1

class Electeur:
    def __init__(self, registre, prenom, nom, age):
        self.registre = registre
        self.prenom = prenom
        self.nom = nom
        self.age = age
    
class Parti:
    def __init__(self, nom, langue, couleur):
        self.nom = nom
        self.langue = langue
        self.couleur = couleur
        self.votes = 0
        self.candidats = []
    
class Candidat:
    def __init__(self, nom, parti):
        self.nom = nom
        self.parti = parti
        self.votes = 0
        self.parti.candidats.append(self)
    
class BureauDeVote:
    def __init__(self):
        self.electeurs = [
            Electeur("123456", "Alphonse", "Brown", 25),
            Electeur("234567", "Billy", "The kid", 17),
            Electeur("345678", "Alice", "Van Pieperzeel", 19),
            Electeur("456789", "Bob", "Django", 31),
            Electeur("567890", "Lola", "Donchant", 23),
            Electeur("010101", "Pete", "Thon", 45)
        ]
        
        profs = Parti("Profs", "FR", 'red')
        pokemons = Parti("Pokemon", "FR", 'blue')
        waarisdafeestje = Parti("Waar is da feestje", "NL", 'green')
        echtevrienden = Parti("Echte vrienden", "NL", 'yellow')
        
        self.partis = [profs, pokemons, waarisdafeestje, echtevrienden]
        
        Candidat("Bersini", profs)
        Candidat("Haelterman", profs)
        
        Candidat("Hier is da feestje", waarisdafeestje)
        Candidat("Disco pogo", waarisdafeestje)
        Candidat("Watskebeurt", waarisdafeestje)
        
        Candidat("Pikachu", pokemons)
        Candidat("Kaiminus", pokemons)
        Candidat("Lugia", pokemons)
        Candidat("Metamorph", pokemons)
        Candidat("Rattata Niveau 2", pokemons)
        
        Candidat("Piet", echtevrienden)
        Candidat("Jan", echtevrienden)
        Candidat("Koen", echtevrienden)
        
        self.votes = []

class Fenetre:
    def __init__(self):
        self.fen = Tk()
        self.fen.geometry("400x400")
        self.frame = Frame(self.fen)
        self.bureau = BureauDeVote()
        
        self.menuprincipal()
        
        self.fen.mainloop()
    
    def refreshFrame(self):
        self.frame.destroy()
        self.frame = Frame(self.fen)
        self.frame.pack()
    
    def menuprincipal(self):
        self.refreshFrame()

        Label(self.frame, text="Prenom ?").pack()
        self.prenom = Entry(self.frame)
        self.prenom.pack()
        
        Label(self.frame, text="Nom ?").pack()
        self.nom = Entry(self.frame)
        self.nom.pack()
        
        Label(self.frame, text="Age ?").pack()
        self.age = Entry(self.frame)
        self.age.pack()
        
        Label(self.frame, text="Numéro de registre national ?").pack()
        self.registre = Entry(self.frame)
        self.registre.pack()
        
        Button(self.frame, text="Valider", command=self.login).pack()
        
        Button(self.frame, text="Top 5", command=self.topFive).pack()
        Button(self.frame, text="Graphique", command=self.graphique).pack()
        
    def login(self):
        nom = self.nom.get()
        prenom = self.prenom.get()
        age = int(self.age.get())
        registre = self.registre.get()
        
        if age < 18:
            showinfo("Login", "Les mineurs ne peuvent pas voter !")
        else:
            self.electeurEnCours = None
            for electeur in self.bureau.electeurs:
                if (electeur.registre == registre and electeur.nom == nom and
                    electeur.prenom == prenom and electeur.age == age):
                    self.electeurEnCours = electeur
            
            dejaVote = False
            for vote in self.bureau.votes:
                if vote.electeur == self.electeurEnCours:
                    dejaVote = True
            
            if self.electeurEnCours == None:
                showinfo("Login", "Non trouvé")
            elif dejaVote == True:
                showinfo("Login", "On ne vote qu'une fois !")
            else:
                self.menulangue()
            
    def menulangue(self):
        self.refreshFrame()
        
        Label(self.frame, text="Choisissez votre langue").pack()
        for langue in ["FR", "NL"]:
            Button(self.frame,
                   text=langue,
                   command=partial(self.menupartis,langue)
            ).pack()
            
    def menupartis(self, langue):
        self.refreshFrame()
         
        Label(self.frame, text="Liste des partis").pack()
        for parti in self.bureau.partis:
            if parti.langue == langue:
                Button(self.frame,
                       text=parti.nom,
                       command=partial(self.menucandidats,parti)
                ).pack()
                 
    def menucandidats(self, parti):
        self.refreshFrame()

        Button(self.frame,
               text="Voter Tete de liste pour " + parti.nom,
               command=partial(self.enregistrervoteparti, parti)
        ).pack()
        Label(self.frame, text="Liste des candidats de " + parti.nom).pack()
        for candidat in parti.candidats:
            Button(self.frame,
                   text=candidat.nom,
                   command=partial(self.enregistrervotecandidat, candidat)
            ).pack()
    
    def enregistrervoteparti(self, parti):
         vote = Vote(self.electeurEnCours)
         vote.voteTeteDeListe(parti)
         self.bureau.votes.append(vote)
         showinfo("Vote", "Merci d'avoir voté !")
         self.menuprincipal()
     
    def enregistrervotecandidat(self, candidat):
         vote = Vote(self.electeurEnCours)
         vote.voteCandidat(candidat)
         self.bureau.votes.append(vote)
         showinfo("Vote", "Merci d'avoir voté !")
         self.menuprincipal()
         
    def topFive(self):
         candidats = []
         for parti in self.bureau.partis:
             for candidat in parti.candidats:
                 candidats.append(candidat)
         
         best = []
         for i in range(5):
             m = findBestCandidat(candidats)
             best.append(candidats[m])
             del candidats[m]
         
         fenetre = Toplevel()
         i = 1
         for candidat in best:
            if candidat.votes == 1:
                s = ''
            else:
                s = 's'
            Label(fenetre, text='#' + str(i)).grid(row=i, column=1)
            Label(fenetre, text=candidat.nom).grid(row=i, column=2)
            Label(fenetre, text=str(candidat.votes)).grid(row=i, column=3)
            Label(fenetre, text="vote" + s).grid(row=i, column=4)
            i += 1
     
    def graphique(self):
         somme = 0
         for parti in self.bureau.partis:
             somme += parti.votes
             
         if somme == 0:
             showinfo("Graphique", "Aucun vote enregistré")
         else:
            fenetre = Toplevel()
            fenetre.geometry("600x800")
            canvas = Canvas(fenetre, width=600, height=400)
            canvas.pack()
            canvas2 = Canvas(fenetre, width=600, height=400)
            canvas2.pack()
            
            x = 50
            y = 300
            angle = 0
            for parti in self.bureau.partis:
                fraction = parti.votes / somme
                canvas.create_rectangle(x, y, x + 50, y - fraction * 200, fill=parti.couleur)
                canvas.create_text(x + 25, y + 20, text=parti.nom)
                canvas.create_text(x + 25, y + 40,
                    text=str(parti.votes) + '/' + str(somme) + ' = ' + str(int(fraction * 100)) + '%'
                )
                
                extent = fraction * 360
                canvas2.create_arc(50,50,350,350, start=angle, extent=extent, fill=parti.couleur)
                
                angle += extent
                x += 100

def findBestCandidat(liste):
    m = 0
    for i in range(1, len(liste)):
        if liste[m].votes < liste[i].votes:
            m = i
    return m

laFenetre = Fenetre()
        