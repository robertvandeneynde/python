def tri_selection(liste):
    for i in range(len(liste)):
        swap(liste, i, find_max(liste, i, len(liste)))

def swap(liste, i1, i2):
    liste[i1], liste[i2] = liste[i2], liste[i1]

def find_max_indice(liste, debut, fin):
    max_i = debut
    for i in range(debut,fin):
        if operateur_plus_grand(liste[i], liste[max_i]):
            max_i = i
    return max_i

def operateur_plus_grand(elem1, elem2):
    # pour des entiers:
    return elem1 > elem2


def tri_insertion(liste):
    for i in range(len(liste)):
        insere_gauche(liste, i, find_place_dans_triee(liste, 0, i, liste[i]))

def find_place_dans_triee(liste, debut_tri, fin_tri, elem):
    for i in range(debut_tri,fin_tri):
        if liste[i] > elem:
            return i

def insere_gauche(liste, ancien_i, nouveau_i):
    valeur = liste[ancien_i]
    for i in range(ancien_i, nouveau_i, -1):
        liste[i] = liste[i-1]
    liste[nouveau_i] = valeur

# trie une liste d'entier appartenant à [0,valeur_maximum_non_incluse[
def tri_comptage(liste, valeur_maximum_non_incluse):
    compteurs = [0 for i in range(valeur_maximum_non_incluse)]
    # compteurs[0] contient le nombre de '0'
    # compteurs[1] contient le nombre de '1'
    # compteurs[n] contient le nombre de 'n'
    for n in liste:
        compteurs[n] += 1 #Il y a un 'n' de plus
    nouvelle = []
    for i in range(len(compteurs)):
        for j in range(compteurs[i]):
            nouvelle.append(i)
    return nouvelle

