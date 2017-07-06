"""Module heuristics, define heuristics functions :
 - taking two positive integer (x,y)
 - returning the heuristic cost
 - whose names are directly accessible via json"""

def zero(x,y):
    return 0

def manhattan(x,y):
    """Optimum rook distance heuristic."""
    return x+y

def rook(x,y):
    return 1 if x == 0 or y == 0 else 2

def bishop(x,y):
    return 1 if x == y else 2

def queen(x,y):
    return min(rook(x,y),bishop(x,y))

def king(x,y):
    """Optimum king distance heuristic."""
    return max(x,y)

def knight(x,y):
    """Knight distance heuristic."""
    return max((x//2+x%2),(y//2+y%2))