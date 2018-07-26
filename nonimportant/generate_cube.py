def minus(V):
    return [-v for v in V]

def unit(i):
    return [int(i == j) for j in range(3)]

def from_dim(i):
    D = unit(i)
    yield D[:]
    D[(i+1)%3] = 1
    yield D[:]
    D[(i+1)%2] = 1
    yield D[:]
    D[(i+1)%3] = 0
    yield D[:]
    D[(i+1)%2] = 0
    
def make():
    ''' Return 2 lists : 6*4 points, 6 normals '''
    L = [list(from_dim(i)) for i in range(3)]
    for i in range(3):
        L.append(L[i][::-1])
        for i in range(4):
            L[-1][i] = list(L[-1][i])
            L[-1][i] = 1

    Ns = [unit(i) for i in range(3)] + [minus(unit(i)) for i in range(3)]
    return L, Ns