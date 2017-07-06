#! /usr/bin/python3
# -*- coding: utf-8 -*-

""" Mastermind
Auteur : Robert Vanden Eynde
Dernière mise à jour : 9 septembre 2013

Informations sur la doc :
    [Combinaison] signifie une combinaison correcte.
        C'est à dire une string tel que len(get_erreurs(comb,colors)) == 0
        Voir get_erreurs pour la liste des erreurs implémentées.
    
    [Colors] signifie une sequence (list, tuple...) de (initiale,nom).
        initiale (str) : initiale de couleur comme 'o' ou 'c'.
        nom (str) : nom complet de couleur comme 'Orange' ou 'blanC'.

Informations sur le code :
    Certaines fonctions proposent plusieurs implémentations différentes.
    Au niveau de la complexité ou au niveau de l'utilisation de certains
    éléments du langage python qui n'auraient peut-être pas été vus "lors des
    7 premiers TP's".
"""

import random

# Couleurs utilisées pour les exemples dans les docstring
DEFAULT_COLORS = (
    ("r", "Rouge"), ("j", "Jaune"), ("v", "Vert"), ("b", "Bleu"),
    ("o", "Orange"), ("c", "blanC"), ("t", "violeT"), ("f", "Fuchsia")
)

# Messages d'input
MESSAGE_REJOUER = "Voulez-vous rejouer ? (O/n) : "
MESSAGE_DEVINER = "Devinez la combinaison : "

# Messages d'information, attendent une espace suivi d'un paramètre.
# Pour des affichages plus personnalisés, str.format est recommandé.
MESSAGE_CHOIX = "Vos choix :"
MESSAGE_ESSAIS = "Nombre d'essais restants :"
MESSAGE_COMBINAISON = "Vous avez joué :"

MESSAGE_BIEN_PLACE = "Nombre de pions de la bonne couleur bien placés :"
MESSAGE_BONNE_COULEUR = "Nombre de pions de la bonne couleur mais mal placés :"
MESSAGE_AUCUN = "Aucun pion bien placé." # Pas de paramètre ici

MESSAGE_GAGNE = "Bravo !" # Pas de paramètre ici
MESSAGE_PERDU = "Dommage, vous avez perdu, la combinaison était :"

# Messages d'erreur
MESSAGE_ERREUR_TAILLE = 'Veuillez entrer une combinaison de taille 4 !'
MESSAGE_ERREUR_EXISTANTES = 'Veuillez entrer uniquement des couleurs existantes !'
MESSAGE_ERREUR_DIFFERENTES = 'Veuillez entrer uniquement des couleurs différentes !'

def join(separateur, str_iterable):
    """Implémentation de la fonction str.join au cas où on ne peut pas
    l'utiliser. Tappez help(str.join) pour plus de détails. Cependant str.join
    est utilisée dans le code pour des raisons de performances.
    """
    sep = ''
    res = ''
    for s in str_iterable:
        res += sep + s
        sep = separateur
    return res

def mastermind():
    """ Lance le jeu au moins une fois et se termine lorsque le joueur ne veut
    plus rejouer.
    """
    colors = DEFAULT_COLORS
    
    partie(colors)
    while input(MESSAGE_REJOUER).lower() != 'n':
        partie(colors)
        
def partie(colors):
    """ Lance une partie avec les <colors> sélectionnées.
    
    Paramètres :
        colors (Colors) : les couleurs disponibles
    """
    guess,essais,comb = generate_guess(colors), 10, '????'
    # '???' est une fausse combinaison qui ne passera jamais le test check_win
    
    # guess = 'cbjt' # Triche
    # afficher_combinaison(guess, colors) # Triche
    
    while not check_win(guess, comb) and essais > 0:
        afficher_nouveau_tour()
        afficher_essais(essais)
        
        comb = demander_comb(colors)
        essais -= 1
        
        afficher_combinaison(comb, colors)
        afficher_reponse(guess, comb)
        
    afficher_resultat(guess, comb, colors)
    
def demander_comb(colors):
    """ Demande à l'utilisateur une combinaison correcte parmi les <colors> et
    affiche les erreurs apparues.
    Boucle tant que la combinaison est erronée.
    
    Paramètres :
        colors (Colors) : les couleurs disponibles
        
    Renvoie :
        Une Combinaison correcte : len(get_erreurs(comb,colors)) == 0
    """
    errone = True
    while errone:
        afficher_choix(colors)
        comb = input(MESSAGE_DEVINER).lower()
        erreurs = get_erreurs(comb, colors)
        errone = len(erreurs) > 0
        if errone:
            afficher_erreurs(erreurs)
    return comb

    # Version avec while True:
    
    while True:
        afficher_choix(colors)
        comb = input(MESSAGE_DEVINER).lower()
        erreurs = get_erreurs(comb, colors)
        if len(erreurs) == 0:
            return comb
        else:
            afficher_erreurs(erreurs)
            
    # Version récursive tail rec
    
    afficher_choix(colors)
    comb = input(MESSAGE_DEVINER).lower()
    erreurs = get_erreurs(comb, colors)
    if len(erreurs) == 0:
        return comb
    else:
        afficher_erreurs(erreurs)
        return demander_comb(colors)

def get_erreurs(comb, colors):
    """Renvoie une liste d'erreur dans la string <comb>.
    
    Paramètres :
        comb (str) : une combinaison
        colors (Colors) : les couleurs disponibles
    
    Erreurs implémentées :
        MESSAGE_ERREUR_TAILLE : Taille de la combinaison différent de 4
        MESSAGE_ERREUR_EXISTANTES : Caractères non présents dans colors
        MESSAGE_ERREUR_DIFFERENTES : Combinaisons avec répétitions
        
    Exemples :
        get_erreurs('ofct', DEFAULT_COLORS) ->
            []
        get_erreurs('of', DEFAULT_COLORS) ->
            [MESSAGE_ERREUR_TAILLE]
        get_erreurs('o2l', DEFAULT_COLORS) ->
            [MESSAGE_ERREUR_TAILLE, MESSAGE_ERREUR_EXISTANTES]
        get_erreurs('oo', DEFAULT_COLORS) ->
            [MESSAGE_ERREUR_TAILLE, MESSAGE_ERREUR_DIFFERENTES]
    """
    erreurs = []
    if len(comb) != 4:
        erreurs.append(MESSAGE_ERREUR_TAILLE)
    if not valid_colors(comb, colors):
        erreurs.append(MESSAGE_ERREUR_EXISTANTES)
    if not check_unique(comb):
        erreurs.append(MESSAGE_ERREUR_DIFFERENTES)
    return erreurs

    # Version avec une list et une list comprehension
    
    tests = [
        (len(comb) == 4, MESSAGE_ERREUR_TAILLE),
        (valid_colors(comb, colors), MESSAGE_ERREUR_EXISTANTES),
        (check_unique(comb), MESSAGE_ERREUR_DIFFERENTES)
    ]
    return [message for condition,message in tests if not condition]

def afficher_nouveau_tour():
    """ Affiche une séparation nette entre l'ancien tour et le nouveau.
    
    Exemples possibles (l'affichage exact dépend de l'implémentation) :
        >>> afficher_nouveau_tour()
        -----------------------------------
    """
    print('-' * 80)

def afficher_choix(colors):
    """ Affiche les choix possibles que l'utilisateur peut tapper.
    
    Paramètres :
        colors (Colors) : les couleurs disponibles
        
    Exemples possibles (l'affichage exact dépend de l'implémentation) :
        >>> afficher_choix(DEFAULT_COLORS)
        Vos choix : r j v b o c t f
    """
    print(MESSAGE_CHOIX, ' '.join(get_possibilites(colors)))

def afficher_erreurs(erreurs):
    """ Affiche les <erreurs> de manière lisible.
    
    Paramètres :
        erreurs (list de str) : liste d'erreur
    
    Assertion (Préconditions) :
        len(erreurs) > 0
        
    Exemples possibles (l'affichage exact dépend de l'implémentation) :
        >>> afficher_erreurs( get_erreurs('ool', DEFAULT_COLORS) )
        Veuillez entrer une combinaison de taille 4 !
        Veuillez entrer uniquement des couleurs existantes !
        Veuillez entrer uniquement des couleurs différentes !
    """
    print('\n'.join(erreurs))

def afficher_essais(essais):
    """ Affiche le nombre d'essais restants.
    
    Paramètres :
        essais (int) : le nombre d'essais restants
    
    Exemples possibles (l'affichage exact dépend de l'implémentation) :
        >>> afficher_essais(10)
        Il vous reste 10 essais
    """
    print(MESSAGE_ESSAIS, essais)

def afficher_combinaison(comb, colors):
    """ Affiche la combinaison choisie de manière lisible.
    
    Paramètres :
        comb (Combinaison) : une combinaison choisie
        
    Exemples possibles (l'affichage exact dépend de l'implémentation) :
        >>> afficher_combinaison('ofct', DEFAULT_COLORS)
        Vous avez choisi Orange Fushia blanC violeT
    """
    print(MESSAGE_COMBINAISON, to_colors_name(comb, colors))


def afficher_reponse(guess, comb):
    """ Affiche des informations sur la combinaison secrète <guess> :
    Nombre de bien placés et nombre de bonnes couleurs.
    
    Paramètres :
        guess (Combinaison) : la combinaison gagnante
        comb (Combinaison) : la combinaison de l'utilisateur
    
    Exemples possibles (l'affichage exact dépend de l'implémentation) :
        >>> afficher_reponse('ofct', 'oftv')
        Réponse : 2 bien placés et 1 de bonne couleur
    """
    bien_places = count_well_placed(guess, comb)
    bonnes_couleurs = count_colors(guess, comb)
    if bien_places > 0:
        print(MESSAGE_BIEN_PLACE, bien_places)
    if bonnes_couleurs > 0:
        print(MESSAGE_BONNE_COULEUR, bonnes_couleurs)
    if bien_places == 0 and bonnes_couleurs == 0:
        print(MESSAGE_AUCUN)

def afficher_resultat(guess, comb, colors):
    """ Affiche des détails sur le résultat de la partie (gagné ou perdu).
    
    Paramètres :
        guess (Combinaison) : la combinaison gagnante
        comb (Combinaison) : la dernière combinaison de l'utilisateur
        colors (Colors) : les couleurs disponibles

    Exemples possibles (l'affichage exact dépend de l'implémentation) :
        >>> afficher_resultat('ofct', 'oftv', DEFAULT_COLORS)
        Vous avez perdu, la combinaison secrète était Orange Fushia blanC violeT
        >>> afficher_resultat('ofct', 'ofct', DEFAULT_COLORS)
        Bravo !
    
    """
    if check_win(guess, comb):
        print(MESSAGE_GAGNE)
    else:
        print(MESSAGE_PERDU, to_colors_name(guess, colors))

def get_possibilites(colors):
    """ Renvoie une liste des couleurs possibles dans colors.
    Correspond à return [initiale for initiale,nom in colors].
    
    Paramètres :
        colors (Colors) : les couleurs disponibles
    
    Exemples :
        get_possibilites(DEFAULT_COLORS) ->
            ['r','j','v','b','o','c','t','f']
    """
    liste = []
    for initiale,nom in colors:
        liste.append(initiale)
    return liste
    
    # Version list comprehension
    
    return [initiale for initiale,nom in colors]

def generate_guess(colors):
    """ Génère aléatoirement une combinaison correcte parmi <colors>.
    
    Paramètres :
        colors (Colors) : les couleurs disponibles
    
    Renvoie :
        Une Combinaison correcte : len(get_erreurs(guess,colors)) == 0
    
    Complexité :
        O(M) où M = len(colors)
        
    Exemples possibles :
        generate_guess(DEFAULT_COLORS) -> 'ofct'
    """ 
    possibilites = get_possibilites(colors)
    random.shuffle(possibilites)
    return ''.join(possibilites[:4])
    
    # Version plus "bibliothèque standard"
    
    return ''.join(random.sample(get_possibilites(colors), 4))

def valid_colors(comb, colors):
    """ Renvoie True si toutes les couleurs de <comb> sont dans <colors>.
    
    Paramètres :
        comb (str) : la combinaison de l'utilisateur
        colors (Colors) : les couleurs disponibles 
    
    Complexité :
        O(N * M) où N = len(comb) et M = len(colors)
        Implémentation disponible en O(max(N,M)) amorti
        
    Exemples :
        valid_colors('ofct', DEFAULT_COLORS) -> True
        valid_colors('ofcx', DEFAULT_COLORS) -> False # x non présent
    """
    
    possibilites = get_possibilites(colors) #O(M)
    # Décommentez une des lignes suivantes pour avoir une complexité
    # en O(max(N,M)) amorti
    
    # possibilites = set(possibilites) #O(M) amorti
    # possibilites = dict(colors) #O(M) amorti
    for c in comb: # O(N)
        if c not in possibilites: # O(M) ou O(1) amorti
            return False
    return True

def check_unique(comb):
    """ Renvoie True si chaque couleur dans <comb> n'est indiquée qu'une fois.
    
    Paramètres :
        comb (str) : la combinaison de l'utilisateur
        
    Complexité :
        O(N²) où N = len(comb)
        Implémentation disponible en O(N log(N))
        Implémentation disponible en O(N) amorti
    
    Exemples :
        check_unique('ofct') -> True
        check_unique('ofco') -> False # deux 'o'
    """
    for i in range(len(comb)): # O(N)
        for j in range(i+1, len(comb)): # O(N)
            if comb[i] == comb[j]:
                return False
    return True

    # Voici un algo en O(N log(N))
    
    tri = sorted(comb) # O(N log(N))
    for i in range(len(tri) - 1): # O(N)
        if tri[i] == tri[i+1]:
            return False
    return True

    #Voici un algo en O(N) amorti
    
    deja = set()
    for c in comb: # O(N)
        if c in deja: # O(1) amorti
            return False
        deja.add(c) # O(1) amorti
    return True

def count_well_placed(guess, comb):
    """ Renvoie le nombre de pions de bonne couleur et bien placés de <comb>
    dans <guess>.
    
    Paramètres:
        guess (Combinaison) : la combinaison gagnante
        comb (Combinaison) : la combinaison de l'utilisateur
        
    Complexité :
        O(N) où N = len(guess) = len(comb)
    
    Exemples :
        count_well_placed('ofct', 'tcfo') -> 0
        count_well_placed('ofct', 'oftv') -> 2 # o et f
    """
    compteur = 0
    for i in range(4):
        if guess[i] == comb[i]:
            compteur += 1
    return compteur

def count_colors(guess, comb):
    """ Renvoie le nombre de pions de bonne couleur mais mal placés de <comb>
    dans <guess>.
    
    Paramètres:
        guess (Combinaison) : la combinaison gagnante
        comb (Combinaison) : la combinaison de l'utilisateur
    
    Complexité :
        O(N²) où N = len(guess) = len(comb)
    
    Exemples :
        count_colors('ofct', 'ofjv') -> 0
        count_colors('ofct', 'oftv') -> 1 # le 't'
    """
    compteur = 0
    for i in range(4): # O(N)
        for j in range(4): # O(N)
            if i != j:
                if guess[i] == comb[j]:
                    compteur += 1
    return compteur

def check_win(guess, comb):
    """ Renvoie True si <comb> fait gagner la partie par rapport à <guess>.
    
    Paramètres:
        guess (Combinaison) : la combinaison gagnante
        comb (Combinaison) : la combinaison de l'utilisateur
    
    Complexité :
        O(N) où N = len(guess) = len(comb)

    Exemples :
        check_win('ofct', 'ofjv') -> False
        check_win('ofct', 'ofct') -> True
    """
    return guess == comb

def dict_create(iterable):
    """ Implémentation du constructeur dict(iterable) dans le cas où on ne
    peut pas l'utiliser. Tappez help(dict) pour plus d'informations."""
    d = {}
    for k,v in iterable:
        d[k] = v
    return d

def to_colors_name(comb, colors):
    """ Renvoie une string contenant toutes les couleurs de <comb> de manière
    lisible.
    
    Paramètres:
        comb (Combinaison) : une combinaison
        colors (Colors) : les couleurs disponibles
        
    Exemples possibles (l'affichage exact dépend de l'implémentation) :
        to_colors_name('ofct', DEFAULT_COLORS) -> 
            'Orange Fushia blanC violeT'
    """
    
    # Version "TP"
    
    mapping = dict(colors) # ou dict_create(colors)
    liste = []
    for c in comb:
        liste.append(mapping[c])
    return ' '.join(liste)

    # Version avec generator expression
    
    mapping = dict(colors) # ou dict_create(colors)
    return ' '.join(mapping[c] for c in comb)

    # Version sans dict (O(N * M))
    
    liste = []
    for c in comb:
        for initiale,nom in colors:
            if initiale == c:
                liste.append(nom)
                break
    return ' '.join(liste)

if __name__ == '__main__':
    mastermind()