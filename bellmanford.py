def bellmanford(debut, arcs, N, INFINITY=10**9):
    """N est l'ordre du graphe"""
    poids = [INFINITY] * N
    poids[debut] = 0
    preced = [] * N
    for i in range(N):
      for u,v,d in arcs:
          val = poids[u] + d
          if poids[v] > val:
              pred[v] = u
              poids[v] = val
    for u,d,d in arcs:
      if poids[u] + d < poids[v]:
          raise Exception("Cycle négatif")
    return poids

if __name__ == '__main__':
    arcs = [(0,1,3),(0,2,4),(2,1,-2)] #indice from, indice to, distance
    bellmanford(0, arcs, 3)
