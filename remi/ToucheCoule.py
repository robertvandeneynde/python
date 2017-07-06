# -*- /usr/bin/python3 -*-
# -*- coding: utf-8 -*-

import random
NOM,RESTANTS,CASES = 0,1,2

DEMANDE_PLACEMENT = "Quelle la première case sur laquelle vous voulez poser ce bateau (exemple H11) ? "

DEMANDE_TIR = "Quelle est la case de votre tir ? "

DEMANDE_DIRECTION = "Voulez-vous placer le bateau à l'horizontale ou à la verticale (h/v)? "

FIN_JEU = "Le jeu est terminé!"

DEMANDE_LIGNES = 'Introduisez le nombre de lignes (compris entre 6 et 999): '
DEMANDE_COLONNES = 'Introduisez le nombre de colonnes (compris entre 6 et 26): '

def charger_navires():
    bateaux = open('navires.dat')
    navires = []
    for ligne in bateaux:
        bateau = ligne.split()
        navires.append( (bateau[0],int(bateau[2]) ))
    return navires

def initialisation():
    Y,X = lignes_colonnes()
    plateau_joueur, plateau_ordi = nouveau_plateau(X,Y), nouveau_plateau(X,Y)
    memoire_ordi = new_memoire_ordi()
    
    infos_joueur = placer_bateau(plateau_joueur, demander_placement_ordi)
    infos_ordi = placer_bateau(plateau_ordi, demander_placement_ordi)

    affichage_plateau_principal(plateau_joueur, infos_joueur, affichage_de_la_case_complet)
    affichage_plateau_cibles(plateau_ordi, infos_ordi, affichage_de_la_case_masque)
    
    resultat_ordi = ""
    while not fini_pour(infos_joueur) and not fini_pour(infos_ordi):
        x,y = tir_joueur(plateau_ordi, infos_ordi)
        resultat_joueur = traitement_tir(plateau_ordi, infos_ordi, x, y)      
        
        x,y = tir_ordi(plateau_joueur, infos_joueur, memoire_ordi, resultat_ordi)
        resultat_ordi = traitement_tir(plateau_joueur, infos_joueur, x, y)

        affichage_plateau_principal(plateau_joueur, infos_joueur, affichage_de_la_case_complet)
        affichage_plateau_cibles(plateau_ordi, infos_ordi, affichage_de_la_case_masque)
        
        afficher_resultat(resultat_joueur, "Joueur")
        afficher_resultat(resultat_ordi, "Ordi")
    fin_jeu(infos_ordi)

def fini_pour(infos):
    for bateau in infos:
        if bateau[RESTANTS] > 0:
            return False
    return True

def fin_jeu(infos):
    print('')
    if fini_pour(infos):
        print("Bien joué, vous avez GAGNE la partie!!!!!!!")
    else:
        print("Dommage, vous avez perdu la partie... Ce sera pour la prochaine fois")
    restart = input("Voulez-vous commencer une nouvelle partie (o/n)?: ")
    while restart != "o" and restart != "n":
        restart = input("Veuillez répondre par 'o' ou 'n'! Voulez-vous commencer une nouvelle partie?: ")
    if restart == "o":
        return initialisation()
    elif restart == "n":
        print(FIN_JEU)

def getXY(plateau):
    return len(plateau),len(plateau[0])

def traduire_coord(texte):
    """ Exemple texte = B11 => (1,10) """
    lettre,numero = texte[0],texte[1:]
    return ord(lettre.upper()) - ord('A'), (int(numero)-1 if numero.isdigit() else -1)

def lignes_colonnes():
    y,x = input(DEMANDE_LIGNES),input(DEMANDE_COLONNES)
    while not y.isdigit() or not x.isdigit() or not 6<int(y)<999 or not 6<int(x)<26:
        if not y.isdigit() or not x.isdigit():
            print ("Introduisez un nombre entier")
        else:
            print ("Introduisez un nombre de lignes 6<y<999 et un nombre de colonnes 6<x<26")
        y,x = input(DEMANDE_LIGNES),input(DEMANDE_COLONNES)
    return int(y),int(x)

def nouveau_plateau(X,Y):
    plateau = []
    for x in range(X):
        ligne = []
        for y in range(Y):
            ligne.append( [None,False] )
        plateau.append(ligne)
    return plateau

def nouvelle_info_bateaux(navires): # navires est une list de tuple nom:str, longueur:int
    info = []
    for nom,nombre in navires:
        info.append( [nom, nombre, []] ) #Le nombre changera au cours du temps dans la table d'infos
    return info

def placer_bateau(plateau, demander_placement): 
    """ place tous les bateaux sur plateau en utilisant la fonction demander_placement  
    - demander_placement est une fonction qui prend en paramètre (plateau, infos, numero) et renvoyant un tuple (x,y,d)
        où x,y sont des int et d un str == 'h' ou 'v'
    + Renvoie les infos complétées """
    navires = charger_navires() # navires est une list de tuple nom:str, longueur:int
    infos = nouvelle_info_bateaux(navires)
    for i in range(len(navires)):
        for x,y in demander_cases_correctes(plateau, infos, demander_placement, i):
            plateau[x][y][0] = i
            infos[i][CASES].append( (x,y) )
    return infos

def demander_placement_joueur(plateau, infos, numero):
    print("Voici votre plateau :")
    affichage(plateau,infos,affichage_de_la_case_complet)
    print ("Veuillez placer le bateau numéro", numero, ":", infos[numero][NOM])
    case_x,case_y = traduire_coord(input(DEMANDE_PLACEMENT))
    direction = input(DEMANDE_DIRECTION)
    correct = direction in ('h','v') and not placement_incorrect(plateau, infos, numero, case_x, case_y, direction)
    if not correct:
        print("Veuillez choisir un placement correct !")
        return demander_placement_joueur(plateau, infos, numero)
    else:
        return int(case_x), int(case_y), direction

def demander_placement_ordi(plateau, infos, numero):
    X,Y = getXY(plateau)
    x,y,d = random.randrange(X), random.randrange(Y), ('h' if random.randrange(2) == 0 else 'v')
    return (x,y,d)

def traduire_en_cases(x0,y0,direction,longueur):
    case = [x0,y0]
    cases = []
    cases.append( list(case) )
    longueur_bateau = longueur
    
    for j in range(longueur_bateau-1):
        if direction == "v":
            case[1] += 1
        elif direction == "h":
            case[0] += 1
        cases.append( list(case) )
            
    return cases

def traduire_en_cases_autour_bateau(x0,y0,direction,longueur):
    cases = []
    case = [x0,y0]
    if direction == 'h':
        cases.append( [x0-1,y0] )
        for x,y in traduire_en_cases(x0,y0,direction,longueur):
            cases.append( [x,y+1] )
            cases.append( [x,y-1] )
        cases.append( [x0+longueur,y0] )
    else:
        cases.append( [x0,y0-1] )
        for x,y in traduire_en_cases(x0,y0,direction,longueur):
            cases.append( [x+1,y] )
            cases.append( [x-1,y] )
        cases.append( [x0,y0+longueur] )
    
    return cases

def demander_cases_correctes(plateau, infos, demander_placement, i):
    x0,y0,d = demander_placement(plateau, infos, i)
    while placement_incorrect(plateau, infos, i, x0,y0,d):
        x0,y0,d = demander_placement(plateau, infos, i)
    return traduire_en_cases(x0, y0, d, infos[i][RESTANTS])

def placement_incorrect(plateau, infos, i, x0,y0,d):
    cases = traduire_en_cases(x0, y0, d, infos[i][RESTANTS])
    return mauvaises_bornes(plateau, cases) or touche_bateau(plateau, x0, y0, d, infos[i][RESTANTS])

def mauvaises_bornes(plateau, cases):
    X,Y = getXY(plateau)    
    for x,y in cases:
        if not(0 <= x < X and 0 <= y < Y):
            return True
    return False

def touche_bateau(plateau, x0,y0,direction,longueur):
    X,Y = getXY(plateau)
    for x,y in traduire_en_cases(x0,y0,direction,longueur):
        if plateau[x][y][0] is not None:
            return True
    for x,y in traduire_en_cases_autour_bateau(x0,y0,direction,longueur):
        if 0 <= x < X and 0 <= y < Y:
            if plateau[x][y][0] is not None:
                return True
    return False

def affichage_plateau_principal(plateau,infos,affichage_de_la_case):
    print('')
    print("Voici votre plateau de jeu principal contenant vos navires et indiquant les endroits où l'adversaire a déjà tiré:")
    print('')
    affichage(plateau, infos, affichage_de_la_case)
    
def affichage_plateau_cibles(plateau,infos,affichage_de_la_case):
    print('')
    print('Voici le plateau indiquant les cases déjà prises pour cible:')
    print('')
    affichage(plateau, infos, affichage_de_la_case)

def affichage(plateau, infos, affichage_de_la_case):
    """ """
    X,Y = getXY(plateau)
    print('| \ ', end='')
    for x in range(X):
        print("| ", chr( ord('A') + x ), " ", sep='', end='')
    print('|')
    print('+' + (X+1) * '---+')
    
    for y in range(Y):
        ligne = y+1
        print("|" + str(ligne).center(3), end='')       
        for x in range(X):
            contenu = affichage_de_la_case(plateau,infos,x,y)
            print('|' + contenu, end='')
        print('|')
        print('+' + (X+1) * '---+')

def affichage_de_la_case_complet(plateau,infos,x,y):
    num_bateau,touche = plateau[x][y]
    if num_bateau is None:
        if touche:
            return " O "
        else:
            return "   "
    else:
        bateau = infos[num_bateau]
        if touche:
            return bateau[NOM][:3].upper()
        else:
            return bateau[NOM][:3].lower()

def affichage_de_la_case_masque(plateau,infos,x,y):
    num_bateau,touche = plateau[x][y]
    if not touche:
        return "   "
    else:
        if num_bateau is None:
            return " O "
        else:
            return " X "

def tir_joueur(plateau, infos):
    X,Y = getXY(plateau)
    print('')
    print('A votre tour:')
    cible_x,cible_y = traduire_coord(input(DEMANDE_TIR))
    if not (0 <= cible_x < X and 0 <= cible_y < Y):
        print("Out of range")
        return tir_joueur(plateau,infos)
    elif plateau[cible_x][cible_y][1] == True:
        print("Vous avez déjà tiré à cet endroit, veuillez saisir d'autres coordonnées")
        return tir_joueur(plateau,infos)
    else:
        return cible_x, cible_y 

def hasard_parmi_restantes(plateau):
    X,Y = getXY(plateau)
    cible_x,cible_y = random.randrange(X), random.randrange(Y)
    if plateau[cible_x][cible_y][1] == True:
        return hasard_parmi_restantes(plateau)
    else:
        return cible_x,cible_y

def new_memoire_ordi():
    return [(-1,-1), []]

def quatre_cases_autour(x,y):
    return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

def deux_cases_autour(liste):
    (x1,y1),(x2,y2) = liste[0],liste[1]
    if x1 == x2:
        #Vertical
        y_min = y_max = y1
        for x,y in liste:
            if y < y_min:
                y_min = y
            elif y > y_max:
                y_max = y
        return [(x1, y_min-1), (x1, y_max+1)]
    else:
        #Horizontal
        x_min = x_max = x1
        for x,y in liste:
            if x < x_min:
                x_min = x
            elif x > x_max:
                x_max = x
        return [(x_min-1, y1), (x_max+1, y1)]

def tir_ordi(plateau, infos, memoire, resultat_precedent):
    X,Y = getXY(plateau)
    coup_prec_x,coup_prec_y = memoire[0]

    if resultat_precedent == "touche":
        memoire[1].append( (coup_prec_x,coup_prec_y) )
    elif resultat_precedent == "coule":
        memoire[1] = []

    if len(memoire[1]) == 0:
        cible_x,cible_y = hasard_parmi_restantes(plateau)
    else:
        
        if len(memoire[1]) == 1:
            x,y = memoire[1][0]
            autour = quatre_cases_autour(x,y)
        else:
            autour = deux_cases_autour(memoire[1])

        print(autour)
            
        cases = []
        for x,y in autour:
            if 0 <= x < X and 0 <= y < Y and plateau[x][y][1] == False:
                cases.append( (x,y) )
        cible_x,cible_y = random.choice(cases)

    memoire[0] = (cible_x, cible_y)

    return cible_x, cible_y

def traitement_tir(plateau, infos, x, y):
    num_bateau = plateau[x][y][0]   
    plateau[x][y][1] = True
    if num_bateau is None:
        return "eau"
    else: 
        infos[num_bateau][RESTANTS] -= 1
        if infos[num_bateau][RESTANTS] == 0:
            return "coule"
        else:
            return "touche"

def afficher_resultat(resultat,nom):
    dico = {'eau': "Dommage, vous avez tiré dans l'eau!",
            'touche': "Bien joué, vous avez touché un bateau!",
            'coule': "Bien joué, vous venez de couler un bateau!"}
    print(nom, ":", dico[resultat])

if __name__ == '__main__':
    initialisation()
