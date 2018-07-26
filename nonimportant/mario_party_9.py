
terrain = (
    ('.', (0,0,0,0)),
    ('.', (0,0,0,0)),
    ('?', (3,3,0,0)),
    ('?', (0,0,0,0)),
    ('.', (0,0,0,0)),
    ('?', (0,0,0,0)),
    ('?', (0,5,5,0)),
    ('.', (0,0,0,0)),
    ('?', (0,0,10,10))
)

def permute_tuple(t):
    return t[1:] + t[0:1]

def permute(terrain):
    return tuple((a, permute_tuple(b)) for a,b in terrain)

#returns (nouveau_terrain, gains)
def nouveau_terrain(terrain, numero):
    numero = min(numero, len(terrain))
    nouveau = terrain[numero:]
    if terrain[numero][0] == '?':
        nouveau = permute(nouveau)
    gains = [0,0,0,0]
    for a,b in terrain[:numero]:
        for i in range(4):
            gains[i] += b[i]
    return nouveau,tuple(gains)

def enumerations(N):
    if N <= 0:
        yield ()
    else: 
        a,b = 1,N-1
        while a <= 6:
            for possib in enumerations(b):
                yield (a,) + possib
            a,b = a+1,b-1

def gains_of(terrain, resultats):
    gains = [0,0,0,0]
    for n in resultats:
        terrain, nouveaux_gains = nouveau_terrain(terrain, n)
        for i in range(4):
            gains[i] += nouveaux_gains[i]
    return gains

# Return liste de (Proba, (Gain0, Gain2, Gain3, Gain4))
def analyse(terrain, init_analyse=()):
    liste = []
    for n in range(1,7):
        nouveau,gains = nouveau_terrain(terrain, n)
        if fini(nouveau):
            liste.append( () )
