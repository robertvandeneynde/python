def devinette(a,b,indent=0):
    if b-a <= 1:
        return 0
    print(indent*'-',a,b)
    m,nm = 10**9,-1
    for n in range(a,b):
        s = m
        m = min(m, n + max(devinette(a,n,indent+1), devinette(n+1,b,indent+1)))
        if s != m:
            nm = n
    print(indent * '>',nm)
    return m

def fonction():
    a = """Cette fonction
    est cool
    et oui !"""
    return a

def new():
    print(1)

import sys, os
print(os.getcwd())
print(sys.argv[0])
