
import itertools
from fractions import Fraction

class Proba(Fraction):
    def __str__(self):
        return repr(self)
    def __repr__(self):
        le_format = "{2:>5.2f}%"
        return le_format.format(self.numerator, self.denominator, float(self*100))

def multirange(N,*args,**kwargs):
    yield from itertools.product(*itertools.repeat(range(*args,**kwargs), N))

def multi_des(N):
    yield from multirange(N,1,7)

def get_bataille(res_a, res_d):
    r = [0,0]
    for a,d in zip(sorted(res_a,reverse=True),sorted(res_d,reverse=True)):
        r[a > d] += 1
    return r

BACKUP_BATAILLE = {}
def bataille(A,D,detail=False):
    if (A,D) in BACKUP_BATAILLE:
        return BACKUP_BATAILLE[A,D]
    res = {}
    n = 0
    for att in multi_des(A):
        for defense in multi_des(D):
            r = tuple(get_bataille(att,defense))
            res[r] = res[r] + 1 if r in res else 1
            n += 1
            if detail:
                print(att, defense, '=> [', r, '] = ', res[r])
    r = sorted( (k,Proba(v,n)) for k,v in res.items() )
    BACKUP_BATAILLE[A,D] = r
    return r

class Envahissement: 
    def __init__(self, A, D, proba=Proba(1,1), proba_bataille=Proba(1,1), arret=(lambda x:False)):
        self.proba_bataille = proba_bataille
        self.A = A
        self.D = D
        self.bataille = None
        self.proba = proba
        self.possibilites = []
        
        if A > 1 and D > 0 and not arret(self):
            nA = min(3,A-1)
            nD = min(2,nA,D)
            self.bataille = (nA,nD)
            for (rA,rD),p in bataille(nA,nD):
                possib = Envahissement(A - rA, D - rD, Proba(p * self.proba), p)
                self.possibilites.append(possib)

    def get(self):
        return self.A,self.D
    
    def __getitem__(self, x):
        return self.possibilites[x]
    
    def __repr__(self):
        s = "-> {s.proba_bataille} : [{s.A:>2},{s.D:>2}] {sep[0]} {s.proba} {sep[1]}"
        sep = '||' if self.bataille is None else '<>'
        if self.bataille:
            s += " -> {s.bataille[0]},{s.bataille[1]}"
        return s.format(s=self, sep=sep) 

    def affiche(self,niveau_maxi=10e9,indent=0):
        print(indent*' |',self)
        if indent < niveau_maxi:
            for v in self.possibilites:
                v.affiche(niveau_maxi,indent+1)
    
    def iter_leafs(self):
        if len(self.possibilites) == 0:
            yield self
        else:
            for v in self.possibilites:
                yield from v.iter_leafs()

BACK = {}
def proba(A,D):
    if A == 1:
        return 0
    if D == 0:
        return 1
    if (A,D) in BACK:
        return BACK[A,D]
    nA = min(3,A-1)
    nD = min(2,nA,D)
    s = sum(p * proba(A - rA, D - rD) for ((rA,rD),p) in bataille(nA,nD))
    BACK[A,D] = s
    return s

def trier_simulation(root):
    L = [0,0,0]
    for x in root.iter_leafs():
        L[0 if x.D == 0 else 1 if x.A == 1 else 2] += x.proba
    return list(map(Proba,L))

STATS_COMBAT_2_2 = {}
def creer_stats(AM,DM):
    for A in range(2,AM):
        for D in range(1,DM):
            if (A,D) not in STATS_COMBAT_2_2:
                STATS_COMBAT_2_2[A,D] = trier_simulation( Envahissement(A,D) )[0]

def ecrire_stats(AM,DM):
    with open('risk.csv', 'w') as fichier:
        for A in range(2,AM):
            s = str(A)
            for D in range(1,DM):
                s += "," + str(float(100 * proba(A,D)))
            fichier.write(s + '\n')

