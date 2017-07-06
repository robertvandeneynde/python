def gagnant(tab):
    
    def f(ligne):
        for i in range(1,len(ligne)):
            if ligne[0] != ligne[i]:
                return None
        return ligne[0]

    toTest  = [[tab[i][j] for i in range(3)] for j in range(3)]
    toTest += [[tab[i][j] for j in range(3)] for i in range(3)]
    toTest += [[tab[i][i] for i in range(3)]]
    toTest += [[tab[2-i][i] for i in range(3)]]

    for ligne in toTest:
        joueur = f(ligne)
        if joueur is not None:
            return joueur
    return None

class Node:
    def __init__(self, tableau, joueur):
        self.tableau = tableau
        self.gagnant = gagnant(tableau)
        self.joueur = joueur
        self.enfants = []
        if self.gagnant is None:
            for i in range(3):
                for j in range(3):
                    if tableau[i][j] is None:
                        nouveau = [[a for a in l] for l in tableau]
                        nouveau[i][j] = joueur
                        self.enfants.append( Node(nouveau, not joueur) )
    def __repr__(self):
        return '\n'.join(
            ''.join(
                '?' if j is None else 'o' if j else 'x' \
                    for j in l
            ) for l in self.tableau
        )

def afficher(node, indent=0):
    if node is not None:
        print(indent * '-', node)
