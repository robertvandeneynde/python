"""
Candy Crush Light
Author : Robert
"""

import random


GRILLE_DEFAUT = [
    ['@','@','#','&','@','@','@','@','@','&','&','@','#','@','&'],
    ['@','#','&','@','&','@','@','&','@','#','&','&','&','@','&'],
    ['@','&','#','@','&','&','@','@','&','#','&','&','#','#','&'],
    ['#','#','@','#','&','&','#','&','#','@','#','@','@','@','&'],
    ['#','#','&','@','#','#','&','#','#','#','@','&','@','@','&'],
    ['&','#','#','#','#','&','&','#','&','@','#','@','#','&','@'],
    ['@','@','#','&','#','#','&','&','&','@','@','&','#','&','&'],
    ['@','#','#','&','@','#','&','&','&','&','@','@','#','@','@'],
    ['@','#','@','@','#','#','&','@','@','#','#','@','#','#','#'],
    ['#','@','@','&','&','&','#','&','#','#','&','@','&','#','#']
]

SYMBOLS = "@#&"
ADJACENCES = [(0,1),(1,0),(0,-1),(-1,0)]

def grille_aleatoire():
    grille = []
    for i in range(10):
        grille.append([])
        for j in range(15):
            grille[i].append(random.choice(SYMBOLS))
    return grille

def main():
    print('Bienvenue')
    if input('Tappez 1 pour avoir la grille de la Figure 1, sinon la grille sera générée : ') == '1':
        grille = GRILLE_DEFAUT
    else:
        grille = grille_aleatoire()
    print_grille(grille)
    jouer(grille)

def print_entete(grille):
    print('-' * (7 + 2 * len(grille[0])))
    
    print(' ' * 3, end=' ')
    for j in range(len(grille[0])):
        print(chr(ord('A') + j), end=' ')
    print('')
    
    print('-' * (7 + 2 * len(grille[0])))

def print_contenu(grille):
    for i in range(len(grille)):
        print(chr(ord('A') + i), end=' | ')
        for j in range(len(grille[i])):
            print(grille[i][j], end=' ')
        print('| ' + chr(ord('A') + i))

def print_grille(grille):
    print_entete(grille)
    print_contenu(grille)
    print_entete(grille)

def get_position_valide(grille):
    while True:
        try:
            i,j = [ord(t) - ord('A') for t in input('Position ? (LigneColonne) ')]
        except:
            print('Mauvaise entrée. Réessayez.')
            
        if in_range(grille, i, j) and grille[i][j] != ' ' and has_adjacente(grille, i, j):
            return i,j
        else:
            print('La case doit être dans le plateau, non vide et avec au moins un voisin.')

def get_points(n):
    return (n * (n+1)) // 2

def in_range(grille, i, j):
    return 0 <= i < len(grille) and 0 <= j < len(grille[0])

def has_adjacente(grille, i, j):
    for di,dj in ADJACENCES:
        if in_range(grille, i+di, j+dj) and grille[i+di][j+dj] == grille[i][j]:
            return True
    return False

def partie_finie(grille):
    for i in range(len(grille)):
        for j in range(len(grille[i])):
            if grille[i][j] != ' ' and has_adjacente(grille, i, j):
                return False
    return True

def jouer(grille):
    total = 0
    
    while not partie_finie(grille):
        print_grille(grille)
        print('Score :', total)
        
        i,j = get_position_valide(grille)
        points = get_points( effacer(grille, i, j, grille[i][j]) )
        gravite(grille)    
        
        print('Points gagnés :', points)
        
        total += points

    print_grille(grille)    
    print('Fini. Score Final :', total)

def effacer(grille, i, j, carac):
    if in_range(grille, i, j) and grille[i][j] == carac:
        grille[i][j] = ' '
        total = 1
        for di,dj in ADJACENCES:
            total += effacer(grille, i+di, j+dj, carac)
        return total
    else:
        return 0

def swap_cases(grille, i1, j1, i2, j2):
    save = grille[i1][j1]
    grille[i1][j1] = grille[i2][j2]
    grille[i2][j2] = save

def gravite_case(grille, ligne, colonne):
    l = ligne+1
    while l < len(grille) and grille[l][colonne] == ' ':
        swap_cases(grille, l,colonne, l-1,colonne)
        l += 1

def gravite_colonne(grille, colonne):
    for l in range(len(grille)-1,-1,-1):
        if grille[l][colonne] != ' ':
            gravite_case(grille, l, colonne)

def gravite(grille):
    for colonne in range(len(grille[0])):
        gravite_colonne(grille, colonne)

if __name__ == '__main__':
    main()