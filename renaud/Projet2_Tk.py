from tkinter import *
from tkinter import ttk

from Projet2 import *

IMAGES = {}

def creer_grille_tk(N, traiter_clic, root):
    """ """

    def creer_fonction_clic(l,c):
        return lambda :traiter_clic(l,c)
    
    grille_tk = ttk.Frame(root)
    grille_tk.grid()
  
    for j in range(N):
        label = Label(grille_tk, text=str(j+1))
        label.grid(row=0,column=j+1)
    for i in range(N):
        label = Label(grille_tk, text=chr(ord('A') + i))
        label.grid(row=i+1,column=0)
    
    matrice_boutons = []
    for i in range(N):
        ligne_boutons = []
        for j in range(N):
            button = Button(grille_tk, text=' ', width=4, height=2, command=creer_fonction_clic(i,j))
            button.grid(row=i+1, column=j+1)
            ligne_boutons.append(button)
        matrice_boutons.append(ligne_boutons)
    
    return grille_tk, matrice_boutons

def affichage_complet_grille_tk(grille_tk, matrice_boutons, grille_ocean, navires):
    for i in range(len(matrice_boutons)):
        for j in range(len(matrice_boutons)):
            contenu = affichage_complet_case(grille_ocean, navires, i,j)
            button = matrice_boutons[i][j]
            nom_bateau,est_touche = grille_ocean[i][j]
            button['text'] = contenu
            if nom_bateau is not None and est_touche:
                button['background'] = '#FF9999'
            else:
                if est_touche:
                    button['background'] = '#9999FF'
                else:
                    button['background'] = None
                if nom_bateau is None:
                    button['text'] = ''
            

def affichage_masque_grille_tk(grille_tk, matrice_boutons, grille_ocean, navires):
    for i in range(len(matrice_boutons)):
        for j in range(len(matrice_boutons)):
            button = matrice_boutons[i][j]
            nom_bateau,est_touche = grille_ocean[i][j]
            if nom_bateau is not None and est_touche:
                
                if navires[nom_bateau][LONGUEUR] == 0:
                    button['background'] = '#FF0000'
                else:
                    button['background'] = None #Couleur par défaut
                    
                button['image'] = IMAGES['bombe']
                button['width'] = button['height'] = 30
                button['text'] = ''
            else:
                if est_touche:
                    button['background'] = '#9999FF'
                else:
                    button['background'] = None

                button['text'] = ''
                button['image'] = None
                button['width'] = 4
                button['height'] = 2
                

def placement_bateaux_tk(grille_ocean, navires_complet, root):
    navires = dict(navires_complet)

    def refresh():
        combo['values'] = tuple(navires.keys())
        if len(combo['values']) > 0:
            nom_selectionne.set(combo['values'][0])
        affichage_complet_grille_tk(grille_tk, matrice_boutons, grille_ocean, navires)
                
    def traiter_clic_placement(l,c):
        #dx,dy = get_current_direction()
        nom_navire = nom_selectionne.get()
        dx,dy = (1,0) if choix_direction.get() == 'v' else (0,1)
        try:
            placer_bateau(grille_ocean, navires, nom_navire, l,c, dx,dy)
            del navires[nom_navire]
            refresh()
            if len(navires) == 0:
                root.destroy()
        except ExceptionRenaud as e:
            message_erreur['text'] = str(e)

    N = len(grille_ocean)
    grille_tk, matrice_boutons = creer_grille_tk(N, traiter_clic_placement, root)
        
    nom_selectionne = StringVar()
    combo = ttk.Combobox(root, state='readonly', textvariable=nom_selectionne)
    combo['values'] = tuple(navires.keys())
    combo.grid()
    nom_selectionne.set(combo['values'][0])
    
    choix_direction = StringVar()
    choix1 = ttk.Radiobutton(root, text='Horizontal', variable=choix_direction, value='h')
    choix2 = ttk.Radiobutton(root, text='Vertical', variable=choix_direction, value='v')
    choix1.grid()
    choix2.grid()
    choix_direction.set('h')

    message_erreur = Label(root)
    message_erreur.grid()

def rejouerTk():

    if choix_rejouer == True:
        mainTk()
    else:
        print('Au revoir ^^ ')
        root.destroy()

    rejouerTk = Frame(root)
    rejouerTk.grid()
    
    choix_rejouer = StringVar()
    choixOk = ttk.Radiobutton(mainTk, text='Ok', variable=choix_rejouer, value='Ok')
    choixNo = ttk.Radiobutton(mainTk, text='No', variable=choix_rejouer, value='No')
    choix_rejouer.set(False)
    choixOk.grid()
    choixNo.grid()
    

def initTk():
    root = Tk()
    root.title("Placement des bateaux")

    grille_joueur,grille_ordi = new_grille_ocean(10),new_grille_ocean(10)
    navires_joueur,navires_ordi = charger_dico_navires(),charger_dico_navires()

    placer_bateaux_ordi(grille_ordi, navires_ordi)
    placement_bateaux_tk(grille_joueur, navires_joueur, root)
    
    root.mainloop()
    
    return grille_joueur,navires_joueur, grille_ordi,navires_ordi


def mainTk():
    grille_joueur,navires_joueur, grille_ordi,navires_ordi = initTk()
    memoire_ordi = creer_memoire_ordi( len(grille_joueur) )
    
    root = Tk()
    root.title("Jeu Toucher Couler")

    IMAGES['bombe'] = PhotoImage(file='bombe.gif')
    

    def fonction_clic_joueur(l,c):
        pass
    
    def fonction_clic_ordi(l,c):
        try:
            
            resultat = cible(grille_ordi, navires_ordi, l,c)
            affichage_masque_grille_tk(grille_tk_ordi, matrice_boutons_ordi, grille_ordi, navires_ordi)
            message_joueur['text'] = resultat

            l,c = choix_tir_ordi(memoire_ordi)
            resultat_ordi = cible(grille_joueur, navires_joueur, l,c)
            message_ordi['text'] = resultat_ordi

            memoire_ordi[COUP_PRECEDENT] = (l,c)
            memoire_ordi[RESULTAT_PRECEDENT] = resultat_ordi

            affichage_complet_grille_tk(grille_tk_joueur, matrice_boutons_joueur, grille_joueur, navires_joueur)

            if fini(grille_joueur, navires_joueur):
                message_ordi['text'] = "L'ordinateur a gagné *_*!"
                message_joueur['text'] = "Le joueur a perdu !"
                
            if fini(grille_ordi, navires_ordi):
                message_joueur['text'] = "Le joueur a gagné ^^!"
                message_ordi['text'] = "L'ordinateur a perdu !"
                return rejouerTk()
        
        except ExceptionRenaud as e:
            message_joueur['text'] = str(e)
 
    les_grilles = Frame(root)
    grille_tk_joueur,matrice_boutons_joueur = creer_grille_tk(len(grille_joueur), fonction_clic_joueur, les_grilles)
    grille_tk_ordi,matrice_boutons_ordi = creer_grille_tk(len(grille_ordi), fonction_clic_ordi, les_grilles)

    grille_tk_joueur.grid(row=0,column=0)
    grille_tk_ordi.grid(row=0,column=1)
    
    affichage_complet_grille_tk(grille_tk_joueur, matrice_boutons_joueur, grille_joueur, navires_joueur)
    affichage_masque_grille_tk(grille_tk_ordi, matrice_boutons_ordi, grille_ordi, navires_ordi)
    
    les_grilles.grid()

    message_joueur = Label(root)
    message_joueur.grid()

    message_ordi = Label(root)
    message_ordi.grid()
    
    root.mainloop()

if __name__ == '__main__':
    mainTk()
