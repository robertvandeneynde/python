"""
@deprecated, see rubik/
"""
import random

# quick functions

def revmove(b):
    """
    R' : R
    R2 : R2
    R2' : R2'
    R : R'
    """
    return b if "2" in b else b[0] if "'" in b else b[0] + "'"

def split(string):
    """
    R'U2LU2' : ["R'", "U2", "L'", "U2'"]
    """
    return re.compile("[RLUDFB][2']{0,2}").findall(string)

def rev(string):
    """
    R'U2LU2' : U2'L'U2R'
    """
    return ''.join(reversed(list(map(revblock, split(string)))))

# model

class Carre:
    def __init__(self, couleur, position, face):
        self.couleur = couleur
        self.position = position
        self.face = face

    def __repr__(self):
        return repr(self.couleur) + repr(self.position)

class Matrice:
    def __init__(self, X, Y, default_function=None):
        if X <= 0 or Y <= 0:
            raise ValueError("Wrond input X or Y creating matrix")
        self.X,self.Y = X,Y
        if default_function is None:
            default_function = lambda x,y:None
        self.donnees = [[default_function(x,y) for y in range(Y)] for x in range(X)]

    def __iter__(self):
        for l in self.donnees:
            for v in l:
                yield v
    
    def __getitem__(self, item):
        x,y = item
        return self.donnees[x][y]

    def __setitem__(self, item, d):
        x,y = item
        self.donnees[x][y] = d

    def __repr__(self):
        M = max(len(repr(v)) for v in self)
        return "\n".join(",".join(repr(self[x,y]).center(M) for x in range(self.X)) for y in range(self.Y))

class Face(Matrice):
    def __init__(self, couleur_initiale):
        fill = lambda x,y:Carre(couleur_initiale, (x,y), face=self)
        Matrice.__init__(self, 3, 3, fill)

    def _rotate_pos(self, positions, right=True):
        new = positions[1:] + [positions[0]] if right else \
              [positions[-1]] + positions[0:-1]
        back = [self[p] for p in positions]
        for p,b in zip(new,back):
            self[p] = b
            
    def rotate(self, sens):
        for e in [ [(1,0),(2,1),(1,2),(0,1)] ,
                   [(0,0),(2,0),(2,2),(0,2)] ]:
            self._rotate_pos(e, sens)
        self.mettre_a_jour()
        
    def rotate_twice(self):
        for e in [ [(1,0),(1,2)],[(2,1),(0,1)] ,
                   [(0,0),(2,2)],[(2,0),(0,2)] ]:
            self._rotate_pos(e, True)
        self.mettre_a_jour()

    def mettre_a_jour(self):
        for pos in ((i,j) for i in range(3) for j in range(3)):
            self[pos].position = pos
            self[pos].face = self

class Cube:

    UP = ['+','2D','B','-','U','2F']
    DOWN = ['-','2U','2F','+','D','B']
    LEFT = ['F','R','-','B','L','+']
    RIGHT = ['B','L','+','F','R','-']

    COORD = [ (+1,0,0),(0,+1,0),(0,0,+1),(-1,0,0),(0,-1,0),(0,0,-1) ]
    COORD_REV = {v:i for i,v in enumerate(COORD)}
    NOMS = ['R','B','U','L','F','D']
    NOMS_REV = {v:i for i,v in enumerate(NOMS)}
    TO_SEE = {'R':RIGHT, 'L':LEFT, 'U':UP, 'D':DOWN}
    TO_SEE_OPPOSITE = {'R':LEFT, 'L':RIGHT, 'U':DOWN, 'D':UP}
    
    def __init__(self):
        self.faces = [Face(n) for n in 'owyrbg']
        
    def __getitem__(self,item):
        if isinstance(item,str):
            return self.faces[ Cube.NOMS_REV[item] ]
        else:
            return self.faces[ Cube.COORD_REV[item] ]
    
    def see(self, lettre_face):
        if lettre_face == 'F':
            return
        comb = Cube.TO_SEE[lettre_face]
        autres = []
        for face,c in zip(self.faces, comb):
            if '-' in c:
                face.rotate(True)
            if '+' in c:
                face.rotate(False)
            if '2' in c:
                face.rotate_twice()
            for carac in c:
                if carac in Cube.NOMS:
                    autres.append(self[carac])
                    break
            else:
                autres.append(face)
        self.faces = autres
    
    #Longueur 1
    def U(self,sens):
        self['U'].rotate(sens)
        
        texte = 'FLBR'
        cibles = [self[n] for n in (texte if sens else reversed(texte))]
        for j in range(3):
            save = cibles[-1][j,0]
            for i in range(3,0,-1):
                cibles[i][j,0] = cibles[i-1][j,0]
            cibles[0][j,0] = save

        for cible in cibles:
            cible.mettre_a_jour()

    def D(self,sens):
        self['D'].rotate(sens)
        
        texte = 'FLBR'
        cibles = [self[n] for n in (texte if sens else reversed(texte))]
        for j in range(3):
            save = cibles[-1][j,2]
            for i in range(3,0,-1):
                cibles[i][j,2] = cibles[i-1][j,2]
            cibles[0][j,2] = save

        for cible in cibles:
            cible.mettre_a_jour()

    # Longueur 3
    def F(self,sens):
        self.see('D')
        self.U(sens)
        self.see('U')

    # Longueur 3
    def B(self,sens):
        self.see('U')
        self.U(sens)
        self.see('D')
        
    #Longueur 5    
    def R(self,sens):
        self.see('R')
        self.F(sens)
        self.see('L')

    #Longueur 5
    def L(self,sens):
        self.see('L')
        self.F(sens)
        self.see('R')
    
    def onemove(self,n,sens):
        if n == 'U':
            self.U(sens)
        elif n == 'F':
            self.F(sens)
        elif n == 'R':
            self.R(sens)
        elif n == 'L':
            self.L(sens)
        elif n == 'D':
            self.D(sens)
        elif n == 'B':
            self.B(sens)
    
    def move(self,move):
        for i,n in enumerate(move):
            try:
                sens = move[i+1] != "'"
            except IndexError:
                sens = True
            self.onemove(n,sens)

    @staticmethod
    def randommove(N=100):
        return ''.join(random.choice(Cube.NOMS) for i in range(N))
        
    def __repr__(self):
        return "\n\n".join(nom + "\n" + repr(self[nom]) \
            for nom in 'FRBLUD')
