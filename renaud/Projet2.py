
import random
LONGUEUR = 0

class ExceptionRenaud(Exception):
    pass

def charger_dico_navires(nom_fichier="navires.dat"):
    d = open(nom_fichier)
    dico = {}
    for elem in d:
        donnee = elem.strip('\n').split(' ')
        dico[donnee[0]] = [ int(donnee[2]) ]
    return dico

# grille[ligne][colonne] = grille[l][c] = grille[i][j]
def new_grille_ocean(n):
    matrice = []
    for ligne in range(n):
        liste = []
        for colone in range(n):
            liste.append( [None, False] )
        matrice.append(liste)
    return matrice

def traduire_en_cases(l,c, dx,dy, longueur):
    liste_coord = []
    for i in range(longueur):
        liste_coord.append( (l+i*dx, c+i*dy) )
    return liste_coord

def traduire_en_cases_autour(l,c, dx,dy, longueur):
    liste_coord = []
    
    liste_coord.append( (l-dx, c-dy) )
    for i,j in traduire_en_cases(l,c, dx,dy, longueur):
        liste_coord += [ (i+dy, j+dx), (i-dy, j-dx) ]
    liste_coord.append( (l+longueur*dx, c+longueur*dy) )

    return liste_coord

def demande_placer_bateau(grille_ocean, navires):
    """ Demande au joueur de placer un bateau de navires sur la grille_ocean """
    print("Navires dispo :")    
    for noms in navires:
        print("-",noms,navires[noms][LONGUEUR])     

    nom_navire = input("Entrez le nom du navire: ")
    if nom_navire not in navires:
        raise ExceptionRenaud("Le nom du navire est incorrect (déjà placé ou inexistant)")
    l, c = traduit_coord(input("Entrez les coordonnées où vous désirez placer votre navire: "))
    dx,dy = ((1,0) if input("Entrez le sens (H ou V)").upper() == 'V' else (0,1))
    return nom_navire,l,c,dx,dy
    
def placer_bateau(grille_ocean, navires, nom_navire, l,c, dx,dy):
    """ Place le bateau nom_navire en l,c,dx,dy sur grille_ocean
        Lance une ExceptionRenaud si erreur """
    N = len(grille_ocean)
    les_cases = traduire_en_cases(l,c, dx,dy, navires[nom_navire][LONGUEUR])

    for i,j in les_cases:
        if not (0 <= i < N and 0 <= j < N):
            raise ExceptionRenaud("Entrez des coordonnées correctes!")
        if grille_ocean[i][j][0] is not None:
            raise ExceptionRenaud("Emplacement non libre!")

    for i,j in traduire_en_cases_autour(l,c, dx,dy, navires[nom_navire][LONGUEUR]):
        if 0 <= i < N and 0 <= j < N:
            if grille_ocean[i][j][0] is not None:
                raise ExceptionRenaud("Vous touchez un bateau déjà placé")
    # On est assuré que le placement
    for i,j in les_cases:
        grille_ocean[i][j][0] = nom_navire

def traduit_coord(string):
    lettre = string[0].lower()
    nombre = string[1:]
    return ord(lettre) - ord('a'), int(nombre) - 1

def placer_bateaux(grille_ocean, navires):
    navires_non_places = dict(navires)
    navires_places = {}
    while len(navires_non_places) > 0:
        try:
            nom_place,l,c,dx,dy = demande_placer_bateau(grille_ocean, navires_non_places)
            placer_bateau(grille_ocean,navires_non_places,nom_place,l,c,dx,dy)
            navires_places[nom_place] = navires_non_places[nom_place]   
            del navires_non_places[nom_place]
            affichage(grille_ocean, navires, affichage_complet_case)
        except ExceptionRenaud as e:
            print("Erreur placement : ", e)


def placer_bateaux_ordi(grille_ocean, navires):
    for nom_navire in navires:
        arret = False
        while arret == False:
            l,c = random.randrange(len(grille_ocean)), random.randrange(len(grille_ocean))
            dx,dy = ((1,0) if random.randint(1,2) == 1 else (0,1))
            try:
                placer_bateau(grille_ocean, navires, nom_navire, l,c,dx,dy)
                arret = True
            except ExceptionRenaud:
                arret = False

STRING_TOUCHE,STRING_COULE,STRING_EAU = "Touche !", "Coule !", "Coup dans l'eau..."
def cible(grille, navires, l, c):
    """ Tire sur l,c dans grille
        Lance une ExceptionRenaud si la cible avait déjà été visée
        Renvoie une str parmi STRING_TOUCHE,STRING_COULE,STRING_EAU """
    if grille[l][c][1] == True:
        raise ExceptionRenaud("Vous avez déjà tiré là !")
    else:
        grille[l][c][1] = True
        nom_bateau = grille[l][c][0]
        if nom_bateau is None:
            return STRING_EAU
        else:
            navires[nom_bateau][LONGUEUR] -= 1
            if navires[nom_bateau][LONGUEUR] == 0:
                return STRING_COULE
            else:
                return STRING_TOUCHE

def affichage_complet_case(grille_ocean, navires, l, c):
    """ Renvoie l'affichage complet de <> sur 2 caractères """
    nom_bateau, est_touche = grille_ocean[l][c]
    if nom_bateau is None:
        if est_touche:
            return '--'
        else:
            return '  '
    else:
        if est_touche:
            return nom_bateau[0:2].upper()
        else:
            return nom_bateau[0:2].lower()

def affichage_masque_case(grille_ocean, navires, l, c):
    """ Renvoie l'affichage masqué de <> sur 2 caractères """
    nom_bateau, est_touche = grille_ocean[l][c]
    if not est_touche:
        return '  '
    else:
        if nom_bateau is None:
            return '--'
        else:
            return '<>'

def affichage(grille_ocean, navires, affichage_case):
    """ Vue du plateau """
    print('    ', end='')
    for k in range(len(grille_ocean)):
        print('|' + str(k+1).center(2), end='')
    print("|")
    for i in range(len(grille_ocean)):
        print("+---+", end='')
        for j in range(len(grille_ocean)):
            print("--+", end='')
        print("")
        print('|', chr(ord('A')+i), '|', end='')
        for j in range(len(grille_ocean[i])):
            print( affichage_case(grille_ocean, navires, i, j) + '|', end='')
        print(""); #On passe a la ligne

def affiche_liste_de_positions(grille, navires, H):
    H = set(H)
    fonction = lambda grille,nav,i,j: ('!!' if (i,j) in H else '  ')
    affichage(grille,navires, fonction)

def essais_joueur(cible,):
    l = int(input("Entrez le numéro de la ligne visée: "))
    c = int(input("entrez le numéro de la colonne visée: "))
    return cible(grille, navires, l, c)

TAILLE_GRILLE, \
HASARD_RESTANT, \
CASES_LIBRES_BATEAU, \
CASES_BATEAU,\
COUP_PRECEDENT, \
RESULTAT_PRECEDENT = 0,1,2,3,4,5

def creer_memoire_ordi(n):
    """ Renvoie une mémoire d'ordi :
    HASARD_RESTANT : list de cases restantes du hasard
    CASES_LIBRES_BATEAU : liste des cases possibles du bateau en cours
    CASES_BATEAU : liste des cases du bateau en cours
    COUP_PRECEDENT : None au début ou case du coup precedent
    RESULTAT_PRECEDENT : None au début str du résultat précédent (voir cible) """
    hasard_restant = []
    for i in range(n):
        for j in range(n):
            hasard_restant.append( (i,j) )
    return [ n, hasard_restant, [], [], None, None, None]

def remove_by_swap(liste, i):
    """ Cette fonction enlève liste[i] en échangeant [i] et [-1]
    Complexité : O(1) """
    liste[i],liste[-1] = liste[-1],liste[i] # O(1)
    return liste.pop() # O(1)

def recherche_dichotomique(L, valeur, bi, bs):
    """ Cherche valeur dans L dans l'intervalle range(b1,bs)
        Donc bi compris et bs non compris """
    while bs > bi:
        m = (bs + bi) // 2
        v = L[m]
        if valeur > v:
            bi = m+1
        elif valeur < v:
            bs = m
        else:
            return m
    raise ExceptionRenaud("N'appartient pas a la liste des cases possibles!")

def find_indices_intersections(A,B):
    """ assert A,B sorted
    Trie A et B, renvoie une liste d'indices dans A d'éléments qui se trouvent dans B"""
    liste_indices = []
    m = -1
    for case in B:
        try:
            m = recherche_dichotomique(A, case, m+1, len(A))
            liste_indices.append(m)
        except ExceptionRenaud:
            pass
    return liste_indices

def enlever_un(H,v):
    """ assert H sorted """
    del H[recherche_dichotomique(H,v,0,len(H))]

def enlever(B,H):
    """ assert A,B sorted """
    liste_indices = find_indices_intersections(H,B)

    for i in range(len(liste_indices)-1,-1,-1):
        remove_by_swap(H, liste_indices[i])

def intersection(A,B):
    """ assert A,B sorted """
    liste_indices = find_indices_intersections(A,B)
    I = []
    for i in liste_indices:
        I.append(A[i])

    return I
        
def randindex(liste):
    return random.randrange( len(liste) )

def determiner_extremites(B):
    ligne_premier, colonne_premier = B[0]
    ligne_second, colonne_second = B[1]
    l_min,c_min, l_max,c_max = bornes(B)
    if ligne_premier == ligne_second:
        return [ (ligne_premier, c_min-1), (ligne_premier, c_max+1) ]
    else:
        return [ (l_min-1, colonne_premier), (l_max+1, colonne_premier) ]

def tir_hasard(liste):
    i = randindex(liste)
    choix = liste[i]
    remove_by_swap(liste,i)
    return choix

def bornes(L):
    l_min,c_min = L[0]
    l_max,c_max = L[0]
    for i in range(1, len(L)):
        l,c = L[i]
        if c < c_min:
            c_min = c
        elif c > c_max:
            c_max = c
        if l < l_min:
            l_min = l
        elif l > l_max:
            l_max = l
    return l_min,c_min, l_max,c_max
        

def choix_tir_ordi(memoire):
    appliquer_resulat(memoire)
    return prochain_tir_ordi(memoire)
    
def appliquer_resulat(memoire):
    coup_precedent = memoire[COUP_PRECEDENT]
    resultat = memoire[RESULTAT_PRECEDENT]
    B = memoire[CASES_BATEAU]
    H = memoire[HASARD_RESTANT]

    if resultat == STRING_TOUCHE:
        B.append(coup_precedent)
    elif resultat == STRING_COULE:
        B.append(coup_precedent)
        # Enlever B de H
        # Enlever toutes les cases autour de B de H
        l_min,c_min, l_max,c_max = bornes(B)
        dl,dc = (0,1) if l_min == l_max else (1,0)
        B += traduire_en_cases_autour(l_min,c_min, dl,dc, len(B))
        H.sort()
        B.sort()
        enlever(B,H)
        memoire[CASES_BATEAU] = [] #VIDER B
        memoire[CASES_LIBRES_BATEAU] = [] #VIDER L

def creerLAdjacents(B,N,H):
    x,y = B[0]
    L = []
    for i,j in [(x-1,y),(x,y-1),(x,y+1),(x+1,y)]:
        if 0 <= i < N and 0 <= j < N:
            L.append( (i,j) )
    L.sort()
    return intersection(H,L)

def creerLExtremites(B,N,H):
    L = []
    E = determiner_extremites(B)
    for i,j in E:
        if 0 <= i < N and 0 <= j < N:
            L.append( (i,j) )
    L.sort()
    return intersection(H,L)

def prochain_tir_ordi(memoire):
    H = memoire[HASARD_RESTANT]
    B = memoire[CASES_BATEAU]
    L = memoire[CASES_LIBRES_BATEAU]
    N = memoire[TAILLE_GRILLE]
    
    if len(B) == 0:
        return tir_hasard(H)
    
    elif len(B) == 1:
        H.sort()
        if len(L) == 0:
            L = memoire[CASES_LIBRES_BATEAU] = creerLAdjacents(B,N,H)
        
        case = tir_hasard(L)
        enlever_un(H,case)
        return case
    
    else:
        L = memoire[CASES_LIBRES_BATEAU] = creerLExtremites(B,N,H)
        case = tir_hasard(L)
        enlever_un(H,case)
        return case


def main():
    grille_joueur,navires_joueur, grille_ordi,navires_ordi = init()
    memoire_joueur = creer_memoire_ordi( len(grille_ordi) )
    memoire_ordi = creer_memoire_ordi( len(grille_joueur) )
    affichage_joueur(grille_joueur,navires_joueur, grille_ordi,navires_ordi)
    
    while not fini(grille_joueur, navires_joueur) and not fini(grille_ordi, navires_ordi):
        l,c = traduit_coord(input("Entrez la position de votre tir ? "))
        resultat_joueur = cible(grille_ordi, navires_ordi, l,c)

        memoire_joueur[COUP_PRECEDENT] = (l,c)
        memoire_joueur[RESULTAT_PRECEDENT] = resultat_joueur

        l,c = choix_tir_ordi(memoire_ordi)
        resultat_ordi = cible(grille_joueur, navires_joueur, l,c)
        
        memoire_ordi[COUP_PRECEDENT] = (l,c)
        memoire_ordi[RESULTAT_PRECEDENT] = resultat_ordi

        affichage_joueur(grille_joueur,navires_joueur, grille_ordi,navires_ordi)
        
        print("Joueur :", resultat_joueur, "\n", "Ordi :", resultat_ordi)
        
    print("Fini !")

def init():
    grille_joueur,grille_ordi = new_grille_ocean(10),new_grille_ocean(10)
    navires_joueur,navires_ordi = charger_dico_navires(),charger_dico_navires()

    placer_bateaux_ordi(grille_joueur, navires_joueur)
    placer_bateaux(grille_ordi, navires_ordi)
    
    return grille_joueur,navires_joueur, grille_ordi,navires_ordi

def affichage_joueur(grille_joueur, navires_joueur, grille_ordi, navires_ordi):
    print("Joueur")
    affichage(grille_joueur, navires_joueur, affichage_complet_case)
    print("Ordi")
    affichage(grille_ordi, navires_ordi, affichage_masque_case)

def fini(grille,navires):
    """ Return true si il y a au moins un zéro """
    for clef in navires:
        if navires[clef][LONGUEUR] != 0:
            return False
    return True




if __name__ == '__main__':
    main()
