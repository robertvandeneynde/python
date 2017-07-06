data = {
    "Latin Grec":[
        "5. FRANCAIS                  ",
        "4. NEERLANDAIS               ",
        "4. ANGLAIS                   ",
        "4. LATIN                     ",
        "2. GREC                      ",
        "5. MATHEMATIQUE              ",
        "1. BIOLOGIE                  ",
        "1. PHYSIQUE                  ",
        "1. CHIMIE                    ",
        "2. HISTOIRE                  ",
        "1. GEOGRAPHIE                ",
        "2. EDUCATION PHYSIQUE        ",
        "2. MORALE / RELIGION         ",
    ],
    "Latin Sciences":[
        "5. FRANCAIS                  ",
        "4. NEERLANDAIS               ",
        "4. ANGLAIS                   ",
        "4. LATIN                     ",
        "5. MATHEMATIQUE              ",
        "1. BIOLOGIE                  ",
        "2. PHYSIQUE                  ",
        "2. CHIMIE                    ",
        "2. HISTOIRE                  ",
        "1. GEOGRAPHIE                ",
        "2. EDUCATION PHYSIQUE        ",
        "2. MORALE / RELIGION         ",
    ],
    "Sciences":[
        "5. FRANCAIS                  ",
        "4. NEERLANDAIS               ",
        "4. ANGLAIS                   ",
        "6. MATHEMATIQUE              ",
        "1. BIOLOGIE                  ",
        "2. PHYSIQUE                  ",
        "2. CHIMIE                    ",
        "2. PRATIQUE DE LABO          ",
        "2. GEOGRAPHIE                ",
        "2. HISTOIRE                  ",
        "2. EDUCATION PHYSIQUE        ",
        "2. MORALE / RELIGION         ",
    ],
    "Sciences Humaines":[
        "5. FRANCAIS                  ",
        "4. NEERLANDAIS               ",
        "4. ANGLAIS                   ",
        "5. MATHEMATIQUE              ",
        "1. BIOLOGIE                  ",
        "1. PHYSIQUE                  ",
        "1. CHIMIE                    ",
        "4. SCIENCES SOCIALES         ",
        "2. GEOGRAPHIE                ",
        "3. HISTOIRE                  ",
        "2. EDUCATION PHYSIQUE        ",
        "2. MORALE / RELIGION         ",
    ],
}

data_t = {                                                       
    k:[ [y.strip() for y in x.split(".")] for x in v]
    for k,v in data.items()
}

data_u = {                                               
    k: dict((val,int(num)) for num,val in v)
    for k,v in data_t.items()
}

def comp(X,Y):
    return {
        k:Y.get(k,0) - X.get(k,0)
        for k in (X.keys() | Y.keys())
        if Y.get(k,0) - X.get(k,0)
    }

sections = L = list(data_u.keys())
matieres = set(m for section in sections for m,n in data_u[section].items())

A = [
    ((k,k2), comp(data_u[k], data_u[k2]))
    for i in range(len(L))
    for j in range(i+1,len(L))
    for k,k2 in [(L[i], L[j])]
]

import json
from pprint import *


'''
headers = list(matieres)
D = dict(A)
for section in sections:
    print(section, "vs all")
    data = [
        [v.get(h,0) for h in headers]
        for s in sections
        if s != section
        for v in [D.get((s,section), D.get((section,s)))]
    ]
    print(headers)
    pprint(data)


print(json.dumps(A, indent=2))

print("Abs Variations")
pprint(set(
    ((x,abs(y)) for B in A for C in B[1].items() for x,y in [C])
))

'''

simple_graph = [
    (
        k1 if b > 0 else k2,
        k2 if b > 0 else k1,
        a,
        abs(b)
    )
    for X in A
    for (k1,k2),V in [X]
    for a,b in V.items()
]

'''print("digraph {\n%s\n}" % "\n".join(
    '"%s" -> "%s" [label="%s %s"];' % (a,b,c,d)
    for a,b,c,d in simple_graph
))'''

# assert not(set(matieres) & set(sections))

from itertools import groupby, count

ids = count(1)

a_cd_b = [
    (a,cd,b)
    for a,b,c,d in simple_graph
    for cd in ["%s %s %s" % (c,d,next(ids))]
]

compound_graph_edges = [
    v
    for a,cd,b in a_cd_b
    for v in [
        (a, cd),
        (cd,b)
    ]
]

# transform (A -> math 2 x -> B) & (A -> math 2 y -> C) into (A -> math 2 x -> (B|C))
# transform (A -> math 2 x -> B) & (A -> math 2 y -> C) into (A -> math 2 x -> (B|C))
compound_graph_edges_simpl = [
    v
    for (a,cd),it in groupby(
        sorted(a_cd_b), key=lambda t:(t[0],' '.join(t[1].split()[:-1]))
    )
    for L in [list(it)]
    for v in [(a,L[0][1])] + [
        (L[0][1], b) for b in (l[2] for l in L)
    ]
]
    
# canonical repr of "SA -> Math 5-7 -> LS"
# with repr "Math 2"
ccc = [
    (
        k1 if d > 0 else k2,
        k2 if d > 0 else k1,
        h,
        abs(d),
        na if d > 0 else nb,
        nb if d > 0 else na,
    )
    for (k1,k2), D in A
    for h,d in D.items()
    if d
    for na in [data_u[k1].get(h,0)]
    for nb in [na + d]
]

ddd = [
    v
    for k1,k2,h,d,na,nb in ccc
    for v in [
        (k1, "%s %s %s" % (h, na, nb)),
        ("%s %s %s" % (h, na, nb), k2)
    ]
]
print("digraph {\n%s\n%s\n}" % ("\n".join(set(
    '"%s" -> "%s";' % (a,b)
    for a,b in ddd
)), "\n".join(
    '"%s %s %s"[label="%s %s", shape=box];' % (h,na,nb, h,d)
    for k1,k2,h,d,na,nb in ccc
)
))
    
'''
print("digraph {\n%s\n%s\n}" % ("\n".join(
    '"%s" -> "%s";' % (a,b)
    for a,b in compound_graph_edges_simpl
), "\n".join(
    '"%s"[label="%s"];' % (cd, ' '.join(cd.split()[:-1]))
    for a,cd,b in a_cd_b
)))
'''