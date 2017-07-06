class Graphe:
    def __init__(self,N):
        self.N = N
        self.V = [i for i in range(N)]
        self.c = [[None] * N for i in range(N)]
        self.p = [[0] * N for i in range(N)]
        
    def trymark(self,j):
        for i in filter(self.ismarked, self.V):
            v = self.c[i][j] - self.p[i][j]
            if v > 0:
                return (+1, self.x[i], v)
            v = self.p[j][i]
            if v > 0:
                return (-1, self.x[i], v)
        return None

    def mark(self):
        for j in filter(self.notmarked, self.V):
            m = self.trymark(j)
            if m is not None:
                return j,m
        return None,None

    def step(self):
        self.M = [(None,None,None)] * self.N
        while True:
            j,m = self.mark()
            if j is None:
                return True
            else:
                M[j] = m
                if self.ispuit(j):
                    return False

        s,j,v = self.M[self.N-1]
        path = [self.N - 1]
        while j is not None:
            path.append((s,j,v))
            s,j,v = self.M[j]
        
        amin = min(v for s,j,v in path)
        for i,j,s in reversed(path):
            self.p[j][i] += amin if s == 1 else -amin

    def ispuit(self,j):
        return j == N-1

    def ismarked(self,i):
        return self.M[i]

    def notmarked(self,i):
        return not self.M[i]    
