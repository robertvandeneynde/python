import math
import itertools
import operator
import time

from itertools import *
from math import *

from functools import reduce
from fractions import Fraction
from pprint import pprint
from collections import namedtuple

Phi = frozenset()

def eqrange(*args):
    '''
    eqrange(b) == range(b + 1)
    eqrange(a, b) == range(a, b + 1)
    eqrange(a, b, c) == range(a, b + 1, c)
    '''
    r = range(*args)
    return range(r.start, r.stop + 1, r.step)

def produit(iterable):
    return reduce(operator.mul, iterable, 1)

def reducesum(iterable):
    return reduce(operator.add, iterable)

def reducemul(iterable):
    return reduce(operator.mul, iterable)

def multi(N, gen):
    '''
    multi(5, {1,2,3}) == product({1,2,3}, {1,2,3}, {1,2,3}, {1,2,3}, {1,2,3})
    '''
    return itertools.product(*itertools.repeat(gen,N))

def multirange(N,*range_args):
    '''
    multirange(3, 10) == product(range(10), range(10), range(10))
    '''
    return itertools.product(*itertools.repeat(range(*range_args), N))

def productrange(*maxs, min=0):
    '''
    productrange(5,2,3) == product(range(5), range(2), range(3))
    productrange(5,2,3, min=1) == product(range(1,5), range(1,2), range(1,3))
    productrange(5,1,(2,3)) == product(range(5), range(2), range(2,3))
    '''
    return product(*(range(min, a) if not isinstance(a,tuple) else range(*a) for a in maxs))

def compte(iterable):
    '''
    compte(i for i in range(100) if is_prime(i)) == 25
    '''
    return sum(1 for a in iterable)

def ilen(iterable):
    '''
    ilen(i for i in range(100) if is_prime(i)) == 25
    '''
    return sum(1 for a in iterable)

def choose(n, k):
    # return produit(eqrange(max(k, n-k), n)) //  factorial(min(k, n-k))
    return factorial(n) // factorial(n-k) // factorial(k)

def implies(a,b):
    return not a or b

class PredicateSet:
    def __init__(self, predicate=lambda self, x: x in self):
        self.predicate = predicate
        
    def __and__(self, other):
        return PredicateSet(lambda s, x: x in self and x in other)
    
    def __or__(self, other):
        return PredicateSet(lambda s, x: x in self or x in other)

class ZClass(PredicateSet):
    def __iter__(self):
        yield 0
        i = 1
        while True:
            yield i
            yield -i
            i += 1
        
    def __contains__(self, i):
        return int(i) == i
    
    def __call__(self, i):
        return range(-i,i+1)

class Z0Class(PredicateSet):
    def __iter__(self):
        i = 1
        while True:
            yield i
            yield -i
            i += 1
            
    def __contains__(self, i):
        return int(i) == i and i != 0

class NClass(PredicateSet):
    def __iter__(self):
        yield from count(0)
            
    def __contains__(self, i):
        return int(i) == i and i >= 0
    
    def __call__(self, i):
        return range(0,i+1)

class N0Class(PredicateSet):
    def __iter__(self):
        yield from count(1)
    
    def __contains__(self, i):
        return int(i) == i and i > 0
    
    def __call__(self, i):
        return range(1,i+1)

Z = ZClass()
Z0 = Z0Class()

N = NClass()
N0 = N0Class()

def totient(n):
    return int(n * produit(1 - Fraction(1,s) for s in set(prime_factors(n))))

def number_digits(a):
    n = 0
    while a != 0:
        a //= 10
        n += 1
    return n

def sum_digits(a):
    s = 0
    while a != 0:
        s += a % 10
        a //= 10
    return s

def all_couples_with_sum(n):
    '''
    all_couples_with_sum(5) -> (5,0) (4,1) (3,2) (2,3) (1,4) (0,5)
    '''
    if n == 0:
        yield (0,0)
    else:
        for i in range(n + 1):
            yield (i - j, j)

def parite_assertion():
    print('(a*b)%2 == (a%2) & (b%2)')
    print('(a+b)%2 == (a%2) ^ (b%2)')
    for a,b in multirange(2,30):
        assert (a*b)%2 == (a%2) & (b%2)
        assert (a+b)%2 == (a%2) ^ (b%2)
        for N in range(1,10):
            assert (a+b) % N == (a%N + b%N) % N
            assert (a*b) % N == a%N * b%N

def mesure(f):
    def g(*args,**kwargs):
        begin = time.clock()
        ret = f(*args,**kwargs)
        print(time.clock() - begin, 's')
        return ret
    return g

def is_prime(N):
    '''
    return True if N is prime
    Complexity : O(log(N))
    
    All primes greater than 3 can be written in the form 6 k +- 1
    '''
    if N < 2:
        return False
    for i in range(2, 1 + floor(sqrt(N))):
        if N % i == 0:
            return False
    return True

def divisors(N):
    '''
    divisors(16) => 1, 16, 2, 8, 4, 4
    O(sqrt(N))
    '''
    for i in range(1, 1 + floor(sqrt(N))):
        if N % i == 0:
            yield i
            yield N // i

def proper_divisors(N):
    '''
    proper_divisors(16) => 1, 2, 8, 4
    O(sqrt(N))
    '''
    yield 1
    for i in range(2, 1 + floor(sqrt(N))):
        if N % i == 0:
            b = N // i
            yield i
            if i != b:
                yield b

def primes(N):
    '''
    Yield primes < N without 0 and 1
    The sieve of Eratosthenes
    '''
    def algo1():
        L = [True] * N
        for i in range(2, N): #Pour tous les nombres de 2 à N
            if L[i]:
                yield i
            for a in range(i+i, N, i): #Pour tous les multiples de i (sans i)
                L[a] = False # étant un multiple de i, a n'est pas un nombre premier
    def algo2():
        L = [True] * N #Même si nous n'utilisons pas les pairs, une list de taille N // 2 ralentirait
        lim = 1 + floor(sqrt(N))
        if 2 < N:
            yield 2
        for i in range(3, lim, 2): #Évitons les pairs...
            if L[i]:
                yield i
            # On commence à barrer à partir de i*i
            # C'est donc pour ça qu'on s'arrête à sqrt(N)
            # Car au delà, il n'y aura plus de nombres à barrer
            for a in range(i*i, N, i):
                L[a] = False
        for i in range(lim + (1 if lim%2 == 0 else 0), N, 2):
            if L[i]:
                yield i
    # Sieve of Atkin
    # http://en.wikipedia.org/wiki/Sieve_of_Atkin
    # Code pas très bon..
    def algo3():
        assert N > 3
        yield 2
        yield 3
        # arbitrary search limit
        # initialize the sieve
        L = [False] * N

        # put in candidate primes: 
        # integers which have an odd number of
        # representations by certain quadratic forms
        sqrt_N = floor(sqrt(N))
        for (x, y) in multirange(2, 1, 1+sqrt_N):
            x2, y2 = x*x, y*y
            n = 4 * x2 + y2
            if (n < N) and (n % 12 == 1 or n % 12 == 5):
                L[n] = not L[n]
            n = 3 * x2 + y2
            if (n < N) and (n % 12 == 7):
                L[n] = not L[n]
            n = 3 * x2 - y2
            if (x > y) and (n < N) and (n % 12 == 11):
                L[n] = not L[n]
          
        # eliminate composites by sieving
        for i in range(5, 1+sqrt_N):
            if L[i]:
                yield i
                # i is prime, omit multiples of its square; this is
                # sufficient because composites which managed to get
                # on the list cannot be square-free
                for k in range(i*i, N, i*i):
                    L[k] = False

        for i in range(i, N):
            if L[i]:
                yield i
    return algo2()


def prime_factors(N, grouped_and_increasing=True):
    '''
    Yield N's prime factors, grouped, increasing values
    20 = 2 * 2 * 5
    '''
    def algo1(N):
        i = 2
        while N > 1:
            while N % i == 0:
                yield i
                N //= i
            i += 1
    # Autre idée : un nombre est premier si il n'est pas multiple des premiers
    # plus petits que lui. De plus, n > sqrt(N) => N % n != 0
    def algo2(N):
        for p in primes(1 + floor(sqrt(N))):
            if p*p > N:
                break
            while N % p == 0:
                yield p
                N //= p
        if N > 1:
            yield N
    # Yield N's prime factors, not neccesarly grouped and increasing
    def algo3(N):
        for s in range(floor(sqrt(N)), 1, -1):
            if N % s == 0:
                yield from algo3(s)
                yield from algo3(N // s)
                return
        # No one divides, N prime
        yield N
    return algo2(N) if grouped_and_increasing else algo3(N)
    
def prime_factors_tuples(N):
    '''
    Yields N's primes factors as tuples, increasing values
    18 = (2 ** 1) * (3 ** 2)
    '''
    for a,b in groupby(prime_factors(N, grouped_and_increasing=True)):
        yield a, sum(1 for c in b)
        
def prime_factors_tuples_2(N):
    i = 2
    while N > 1:
        c = 0
        while N % i == 0:
            N //= i
            c += 1
        if c != 0:
            yield (i,c)
        i += 1


def gcd(a,b):
    '''
    great common divisor Euclidean algorithm
    assert a <= b
    '''
    # assert a <= b
    return a if b == 0 else gcd(b, a % b)

def lcm(a,b):
    '''
    least common multiple
    '''
    # assert a < b and a > 0 and b > 0
    return a * b // gcd(a,b)

def extended_gcd(a, b):
    '''
    Returns:
    - bezout_coefficient :
    - gcd : 
    - quotients :
    '''
    s, old_s = 0, 1
    t, old_t = 1, 0
    r, old_r = b, a
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    
    return namedtuple('extended_gcd', ['bezout_coefficient', 'gcd', 'quotients'])(
        (old_s, old_t),
        old_r,
        (t, s)
    )

def modular_inverse(a, n):
    t, newt = 0,1
    r,newr = n,a
    while newr != 0:
        quotient = r // newr
        (t, newt) = (newt, t - quotient * newt) 
        (r, newr) = (newr, r - quotient * newr)
    return None if r > 1 else t + n if t < 0 else t

def modular_exp(a,b,n):
    if b == 0:
        return a % n
    else:
        if b % 2 == 0:
            x = modular_exp(a, b // 2, n)
            return (x * x) % n
        else:
            x = modular_exp(a, b // 2, n)
            return (x * x * a) % n
        
# chaine = "731671..."
def PE8(chaine):
    L = list(map(int, chaine))
    return max( reducemul(L[i:i+5]) for i in range(len(L)) )

def triangle_numbers(N):
    s = 0
    for i in range(1,N+1):
       s += i
       yield s

def PE14(M):
    longueur_cycle = {1:1}
    #longueur_cycle = [None] * M; longueur_cycle[1] = 1
    nombre_maxi = 1
    for i in range(M-1, 1, -1):
        ibase = i
        liste = []
        while i not in longueur_cycle: # while longueur_cycle[i]
            liste.append(i)
            i = i // 2 if i % 2 == 0 else 3*i+1
        c = longueur_cycle[i]
        # print(ibase," : ",liste,"(",c,")")
        for n in reversed(liste):
            c += 1
            longueur_cycle[n] = c
        if longueur_cycle[nombre_maxi] < c:
            nombre_maxi = n
        # for a,b in longueur_cycle.items():
        #    print(" ",a,":",b)
        # print("maxi = ",nombre_maxi," => ",longueur_cycle[nombre_maxi])
    return nombre_maxi, longueur_cycle[nombre_maxi]

def PE15(N):
    # arbre de pascal !
    cache = [[None for i in range(N+1)] for j in range(N+1)]
    def number(n,x):
        if x == 0 or n == 0:
            return 1
        if cache[n][x] is not None:
            return cache[n][x]
        a = cache[n][x-1] = number(n,x-1)
        b = cache[n-1][x] = number(n-1,x)
        return a + b
    return number(N,N)

def PE17(N):
    first = ['','one','two','three','four','five','six','seven','eight','nine',
             'ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen',
             'seventeen','eighteen','nineteen']
    dizaines = [None,None,'twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
    def in_words(x):
        if x < 100:
            if x < 20:
                return first[x]
            return dizaines[x // 10] + '' + first[x % 10]
        elif x % 100 == 0:
            return first[x // 100] + 'hundred'
        else:
            return first[x // 100] + 'hundred' + 'and' + in_words(x % 100)
        
    return sum(len(in_words(i)) for i in range(1,N))

def PE18(filename="pyramide.txt"):
    with open(filename) as f:
        L = [list(map(int, l.split(' '))) for l in f]

        for i in range(len(L)-2,-1,-1):
            for j in range(len(L[i])):
                L[i][j] += max(L[i+1][j], L[i+1][j+1])

        return L[0][0]

def PE19():
    j,m,a,d = 0,0,1900,0
    def leap_year(year):
        if year % 400 == 0:
            return True
        elif year % 100 == 0:
            return False
        elif year % 4 == 0:
            return True
        else:
           return False
    def get_days(an):
        return [31,(29 if leap_year(an) else 28),31,30,31,30,31,31,30,31,30,31]
    days = get_days(a)
    specials_sundays = 0
    while a < 2001:
        j += 1
        d += 1
        save = specials_sundays
        if d == days[m]:
            d = 0
            if 1901 <= a and j % 7 == 6:
                specials_sundays += 1
            m += 1
            if m == 12:
                m = 0
                a += 1
                days = get_days(a)
        if save != specials_sundays:
            print((d+1,m+1,a),'elapsed',j,('sunday' if j%7==6 else ''),'specials',specials_sundays)
    return specials_sundays

def PE21(N):
    def amicals(N):
        d = [sum(proper_divisors(i)) for i in range(N)]
        for i in range(N):
            if i != d[i] and d[i] < N and d[d[i]] == i:
                yield i
    return sum(amicals(N))

def PE22():
    with open("names.txt") as f:
        L = [l[:-1] for l in f] # Drop the \n
        # L = f.read().strip('"').split('","')
        f.close()
        L.sort()
        def value(name):
            return sum(ord(s) - ord('A') + 1 for s in name)
        return sum(value(L[i]) * (i+1) for i in range(len(L)))

def PE23():
    N = 28124
    d = [sum(proper_divisors(i)) for i in range(N)]
    abundants = []
    for i in range(12,N):
        if d[i] > i:
            abundants.append(i)
    
    sommes = [False] * N
    for i in range(len(abundants)): 
        for j in range(i,len(abundants)):
            S = abundants[i] + abundants[j]
            if S < N:
                sommes[S] = True
                
    return sum(0 if sommes[i] else i for i in range(len(sommes)))


def PE26(N=1000):
    def longueur_cycle(n):
        d,i,r = {1:0}, 0, 1
        # d = [None] * n; d[1] = 0
        while True:
            r *= 10
            r %= n
            if r == 0:
                return 0
            i += 1
            if r in d: # if d[r] is not None:
                return i - d[r]
            d[r] = i
    return max(range(1,N), key=longueur_cycle)

def PE28(N):
    def gen(rep):
        c,n = 1,1
        for i in range(rep):
            c += 1
            c += n
            yield c
            n += 1
            for j in range(3):
                c += n
                yield c        
            n += 1
    return 1 + sum(gen((N-1)//2))

def PE31(N):
    vals = [1, 2, 5, 10, 20, 50, 100, 200]

def pyt_triplet(m,n):
    return (m*m - n*n, 2*m*n, m*m + n*n)

def pyt_triplet_P(p,debug=False):
    # manque quelques données... (m,n coprimes et m%2 != n%2)
    # p = m² - n² + 2mn + m² + n²
    # => p = 2m² + 2mn
    # => p = 2m (m + n)
    # => n = p / 2m - m
    # 0 < n < m
    # => 0 < p / 2m - m et p / 2m - m < m
    # => 2m² < p et p < 4m²
    # => m² < p/2 et p/4 < m²
    # => p/4 < m² < p/2
    m_min,m_max = sqrt(p/(4*k)), sqrt(p/(2*k))
    i_min,i_max = 1+floor(m_min), ceil(m_max)
    if debug:
        print(m_min," < m < ",m_max)
        print("m = [",i_min,",",i_max,"[")
        print("Maximum de triplets :", i_max-i_min)
    for m in range(i_min,i_max):
        if p % (2*m) == 0: # Si non divisible, n non entier
            n = p // (2*m) - m
            yield pyt_triplet(m,n)

def PE39_rate(N):
    return max( (p for p in range(1,N)),
                key=lambda p: compte(pyt_triplet_P(p)) )

def PE39_bis(N):
    # p <= N
    # p = a + b + c
    # c² = a² + b²
    # a + b + sqrt(a² + b²) <= N
    pass

def hash_string(s):
    # if hash cached: return it
    l = len(s)
    p = 0
    x = s[p] << 7
    while p < l:
        x = (1000003 * x) ^ s[p]
        p += 1
    x = x ^ l
    return x
# De plus il existe un caching
# http://www.laurentluce.com/posts/python-dictionary-implementation/

def mul_mat(A,B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
        for j in range(len(B[0]))]
        for i in range(len(A))]

def mat_ligne(V):
    return [[a for a in V]]

def mat_colonne(V):
    return [[a] for a in V]

def vec_from_mat_ligne(M):
    return [a for a in M[0]]

def vec_from_mat_colonne(M):
    return [L[0] for L in M]

def mul_mat_vec(A,V):
    return vec_from_mat_colonne(mul_mat(A, mat_colonne(V)))

def PE39(N):
    class NodePerim:
        A = [[1,-2,2],[2,-1,2],[2,-2,3]]
        B = [[1,2,2],[2,1,2],[2,2,3]]
        C = [[-1,2,2],[-2,1,2],[-2,2,3]]
        def __init__(self, valeur, P_MAX):
            self.valeur = valeur
            self.enfants = []
            for M in (self.A, self.B, self.C):
                v = mul_mat_vec(M, valeur)
                if sum(v) <= P_MAX:
                    self.enfants.append( NodePerim(v, P_MAX) )
                    
        def print(self, key=lambda x:x, indent=0):
            print('-' * indent, key(self.valeur))
            for a in self.enfants:
                a.print(key,indent+1)
                
        def __iter__(self):
            yield self.valeur
            for a in self.enfants:
                yield from a

    def getAllPytTriples(P_MAX):
        for prime in NodePerim([3,4,5], P_MAX):
            a = prime
            while sum(a) <= P_MAX:
                yield a
                a = [sum(p) for p in zip(a,prime)] # a = vec_add(a,prime)
            
    sommes = sorted(sum(t) for t in getAllPytTriples(N))
    valeurs = [(a, len(list(b))) for a,b in itertools.groupby(sommes)]
    return max(valeurs, key=operator.getitem(1))[0]

def PE33(debug=True):
    def possibilites():
        for a,b,c,d in itertools.product(*itertools.repeat(range(1,10),4)):
            num,den = a + 10*b, c + 10*d
            if num >= den:
                continue
            frac = Fraction(num,den)
            tests = [(a,c,b,d), (a,d,b,c), (b,c,a,d), (b,d,a,c)]
            for i,j,k,l in tests:
                if i == j and Fraction(k, l) == frac:
                    yield frac
                    if debug:
                        print(num,'/',den,'=',k,'/',l,'by removing',i)
    return produit(possibilites()).denominator

def PE27(MAX):
    def consecutives_primes(a,b):
        n = 1 # We know that b is prime
        while is_prime(n*n + a*n + b):
            n += 1
        return n
    def possibilites():
        L = list(primes(MAX))
        for b in L:
            for a in L:
                yield a,b
                yield -a,b
    def possibilites_brute_force():
        for b in primes(MAX):
            for a in range(-MAX+1,MAX):
                yield a,b
    a_max,b_max = max(possibilites(), key=lambda t:consecutives_primes(t[0],t[1]))
    return a_max * b_max

def PE40():
    #Brute force... cependant une solution intelligente peut être trouvée
    def create(N_MAX):
        s = ''
        for i in range(N_MAX):
            s += str(i)
        return s
    d = create(1000000)
    return produit(int(d[10 ** n]) for n in range(7))

def PE31(M=200,max_affichage=0):
##    f(7,[5,2,1]): f(7-5, [5,2,1]) + f(7-2, [2,1]) + f(7-1, [1]) FAUX => f(7, [2,1])
##     f(2, [5,2,1]): f(2-5, [5,2,1]) + f(2-2, [2,1]) + f(2-1, [1]) FAUX => + f(2, [1])
##      f(-3, [5,2,1]): 0 car négatif
##      f(0, [2,1]): 1 car 0
##      f(1, [1]): f(1-1, []) FAUX => + f(1, [])
##      f(0, []): 1 car 0 (attention, même si vide !)
##      f(1, []): 0 car vide
##      f(2, [1]): f(2-1, [1]) FAUX => + f(2, [])
##       f(1, [1]): deja eu
##     f(5, [2,1]):
##     f(6, [1]): f(6-1, [1]) FAUX => + f(6, [])
##      => f(N, [1]): 1
    def f(M, C, r=1):
        if r <= max_affichage: print(r * '-', (M,C))
        S = 0 if M < 0 else \
            1 if M == 0 else \
            1 if C == [1] else \
            sum(f(M - C[i], C[i:], r+1) for i in range(len(C)))
        if r <= max_affichage: print(r * '=', S, (M,C))
        return S
    return f(M,[200,100,50,20,10,5,2,1])

def PE44():
    def pentagonal(n):
        return n*(3*n-1) // 2
    P = {pentagonal(i) for i in range(1,10000)} 
    # Brute force
    for i in range(1,10000):
        for j in range(i+1,10000):
            pi,pj = pentagonal(i), pentagonal(j)
            S,D = pi+pj,pj-pi
            if S in P and D in P:
                return D
def PE43(debug=True):
    def multiples(M):
        for n in range(0,1000,M):
            yield n // 100, (n // 10) % 10, n % 10
            
    def distincts(iterable):
        for a,b,c in iterable:
            if a != b != c != a:
                yield a,b,c
                
    def garder_chiffre(i, possib, iterable):
        return filter(lambda t:t[i] in possib, iterable)

    def runDown(possibilitesAB, possibilitesABC):
        for a,b,c in possibilitesABC:
            if (a,b) in possibilitesAB:
                yield a,b,c

    def runUp(possibilitesBC, possibilitesABC):
        for a,b,c in possibilitesABC:
            if (b,c) in possibilitesBC:
                yield a,b,c
    
##    d2,d3,d4 = possib[0] mul 2 => d4 = 0 2 4 6 8
##    d3,d4,d5 = possib[1] mul 3
##    d4,d5,d6 = possib[2] mul 5 => d6 = 0 5
##    d5,d6,d7 = possib[3] mul 7
##    d6,d7,d8 = possib[4] mul 11
##    d7,d8,d9 = possib[5] mul 13
##    d8,d9,d0 = possib[6] mul 17

    possib = [ list(distincts(multiples(N))) for N in (2,3,5,7,11,13,17) ]

    def affiche(msg='',complet=False):
        if debug:
            print(msg,":")
            for i,l in enumerate(possib):
                for a in range(1,4):
                    print(chr(ord('a') + i+a), end='')
                print(')', end='')
                if len(l) > 20 and complet == False:
                    print("...(",len(l),")")
                else:
                    print(*(str(a)+str(b)+str(c) for a,b,c in l))

    affiche('Multiples distincts')
    
    possib[1] = list( garder_chiffre(1, (0,2,4,6,8), possib[1]) )
    possib[2] = list( garder_chiffre(0, (0,2,4,6,8), possib[2]) )
    possib[3] = list( garder_chiffre(1, (0,5), possib[3]) )
    possib[4] = list( garder_chiffre(0, (0,5), possib[4]) )

    affiche('Enlèvement des chiffres impossibles')
    
##    for i in range(7-2, -1, -1):
##        possib[i] = list( runUp({(a,b) for a,b,c in possib[i+1]}, possib[i]) )
##
##    affiche('Élagage Down')
##
##    for i in range(1,7,1):
##        possib[i] = list( runDown({(b,c) for a,b,c in possib[i-1]}, possib[i]) )
##
##    affiche('Élagage Up')

    L = [len(l) for l in possib]
    while True:
        for i in range(1,7):
            inter = {(b,c) for a,b,c in possib[i-1]} \
                    & {(a,b) for a,b,c in possib[i]}
            possib[i-1] = list( runUp(inter, possib[i-1]) )
            possib[i] = list( runDown(inter, possib[i]) )
            
        affiche('Élagage')
        NL = [len(l) for l in possib]
        if NL == L:
            break
        else:
            L = NL

    affiche('Fin Élagage', complet=True)

    L = [sorted([((b,c),a) for a,b,c in niveau]) for niveau in possib]
    for i in range(len(L)):
        L[i] = {a:[v for k,v in b] for a,b in itertools.groupby(L[i], key=operator.itemgetter(0))}

    if debug:
        for a in L:
            for k,v in a.items():
                print(k,'>',v)
            print()

    Somme = [0] # Liste pour passage par référence
    def nouveau_niveau(a, b, i, utilises):
        if i == 0:
            chiffre_restant = sum(i for i in range(10)) - sum(utilises)
            nombre_final = [chiffre_restant] + utilises
            string = ''.join(str(d) for d in nombre_final)
            if debug:
                print(string)
            Somme[0] += int(string)
            return True
        else:
            bien_cree = False
            for n in L[i-1][a,b]:
                if n not in utilises:
                    bien_cree |= nouveau_niveau(n, a, i-1, [n] + utilises)
            return bien_cree

    for k,valeurs in L[-1].items():
        a,b = k
        for v in valeurs:
           nouveau_niveau(v, a, len(L)-1, [v,a,b])

    return Somme[0]

def PE38():

    def numbers(i):
        while i > 0:
            yield i % 10
            i //= 10
    
    def test(i):
        cible = []
        k = 1
        while True:
            for j in reversed(list(numbers(k * i))):
                if j == 0 or j in cible:
                    return False,k,cible
                cible.append(j)
            if len(cible) == 9:
                return True,k,cible
            k += 1

    maxi = [0]
    for i in range(1,100000):
        b,k,res = test(i)
        if b and k > 1:
            maxi = max(maxi,res)
    return int( ''.join(str(i) for i in maxi) )

def PE96(debug=False):
    with open('sudoku.txt', 'r') as fichier:
        Sudokus = [[[int(c) for c in fichier.readline().strip('\n')] for n in range(9)] for titre in fichier]

        class Solved(BaseException):
                pass
        
        def solve(S):
            grille = [[None for j in range(9)] for i in range(9)]
            cases_depart = []
            cases_balayees = set()
            for i,j in multirange(2,9):
                if S[i][j] == 0:
                    grille[i][j] = {i for i in range(1,10)}
                else:
                    grille[i][j] = {S[i][j]}
                    cases_depart.append((i,j))

            def parcours_lineaire_except(i):
                return itertools.chain(range(0,i), range(i+1,9))
                
            def parcours_A(i,j):
                for a in parcours_lineaire_except(i):
                    yield a,j
            def parcours_B(i,j):
                for a in parcours_lineaire_except(j):
                    yield i,a
            def parcours_C(i,j):
                ci,cj = 3 * (i // 3), 3 * (j // 3)
                for a,b in itertools.product(range(ci,ci+3), range(cj,cj+3)):
                    if (a,b) != (i,j):
                        yield a,b
                        
            def parcours(i,j):
                return itertools.chain(parcours_A(i,j), parcours_B(i,j), parcours_C(i,j))

            def balayer(i,j):
                N = next(iter(grille[i][j]))
                for a,b in parcours(i,j):
                    L = len(grille[a][b])
                    if L != 1:
                        grille[a][b].discard(N)
                        if len(grille[a][b]) == 1:
                            balayer(a,b)
                assert (i,j) not in cases_balayees
                cases_balayees.add((i,j))
                if len(cases_balayees) == 81:
                    raise Solved
                
                                
            def parcours_D():
                return (((i,j) for i in range(9)) for j in range(9))
            def parcours_E():
                return (((j,i) for i in range(9)) for j in range(9))
            def parcours_F():
                return ( ((ci+i,cj+j) for i,j in multirange(2,3)) \
                         for ci,cj in multirange(2,0,9,3) )
            def parcours_tot():
                return itertools.chain(parcours_D(), parcours_E(), parcours_F())

            class AloneInutile(BaseException):
                pass
            
            def alone():
                for neuf_cases in parcours_tot():
                    les_ensembles = [((a,b),grille[a][b]) for a,b in neuf_cases]
                    for i in range(9):
                        pos,ensemble = les_ensembles[i]
                        if len(ensemble) > 1:
                            acc = ensemble.copy()
                            for j in parcours_lineaire_except(i):
                                acc -= les_ensembles[j][1]
                            if len(acc) == 1:
                                if debug:
                                    print('Alone trouvé',ensemble,*(les_ensembles[j][1] for j in parcours_lineaire_except(i)))
                                ensemble.clear()
                                ensemble.add(next(iter(acc)))
                                if debug:
                                    print('>',ensemble)
                                balayer(*pos)
                                afficher()
                                return alone() # On reccommence
                raise AloneInutile


            class NotSolvable(BaseException):
                pass
            
            def next_empty_pos(i,j):
                while len(grille[i][j]) == 1:
                    i += 1
                    if i == 9:
                        j += 1
                        i = 0
                        if j == 9:
                            raise Solved
                return i,j

            def entre_en_collision(v,i,j):
                for a,b in parcours(i,j):
                    if len(grille[a][b]) == 1 and next(iter(grille[a][b])) == v:
                        return True
                return False

            def backtracking():
                positions = []
                for i,j in multirange(2,9):
                    if len(grille[i][j]) > 1:
                        positions.append((i,j))

                print('backtracking with',len(positions),'positions')
                        
                # positions.sort(key=lambda pos:len(grille[pos[0]][pos[1]]))
                
                def rec(N):
                    if N < 0:
                        raise Solved
                    i,j = positions[N]
                    valeurs = grille[i][j]
                    for v in valeurs:
                        if not entre_en_collision(v,i,j):
                            grille[i][j] = {v}
                            afficher()
                            try:
                                rec(N-1)
                            except NotSolvable:
                                if debug:
                                    print(N,"essaie un autre")
                                pass
                    grille[i][j] = valeurs
                    if debug:
                        print(N,"n'y arrive pas")
                    raise NotSolvable
                
                rec(len(positions)-1)

            def afficher():
                if debug:
                    D = [[''.join(map(str, sorted(grille[i][j]))).center(7) for j in range(9)] for i in range(9)]
                    it = iter(D)
                    for i in range(3):
                        for j in range(3):
                            print(*next(it),sep='|')
                        print()
                    print('-' * 80)

            try:
                try:
                    for a,b in cases_depart:
                        balayer(a,b)
                    afficher()
                    alone()
                except AloneInutile:
                    backtracking()
            except Solved:
                for i,j in multirange(2,9):
                    S[i][j] = next(iter(grille[i][j]))
                pprint(S)

        for i,S in enumerate(Sudokus):
            print('*' * 20)
            print('Sudoku #', i+1, sep='')
            solve(S)
        return sum((S[0][0]*100 + S[0][1]*10 + S[0][2]) for S in Sudokus)


def PE32():
    
    def pan(*iterable):
        return sorted(''.join(str(a) for a in iterable)) == [str(i) for i in range(1,10)]
    
    S = set()
    for v1,v2 in ((0,3),(1,2)):
        for a,b in product(range(10 ** v1,10 ** (v1+1)), range(10 ** v2, 10 ** (v2+1))):
            if pan(a,b,a*b):
                S.add(a*b)
    return sum(S)

def PE53():
    def C(r,n):
        # C(n-r,n) = C(r,n)
        return produit(a for a in range(r+1,n+1)) // math.factorial(n-r)
    s = 0
    for n in range(1,101):
        for r in range(1,n+1):
            if C(r,n) > 1000000:
                s += 1
    return s

def PE54():

    CARTE, PAIRE, DOUBLE_PAIRE, BRELAN, \
       SUITE, FLUSH, FULL_HOUSE, CARRE, QUINTE_FLUSH = range(9)

    Carte = namedtuple('C', ['valeur','couleur'])
    Assoc = namedtuple('A', ['nombre', 'valeur'])
    def et(iterable):
        '''
        all en vrai python :D
        '''
        return reduce(lambda x,y: x and y, iterable, True)
    
    def valeur(A):
        A = sorted(A,reverse=True)
        N = [ Assoc(nombre=len(list(b)), valeur=a) for (a,b) in groupby(A, key=operator.attrgetter('valeur')) ]
        N.sort(reverse=True)
        egalite = [a[1] for a in N]

        # assert egalite != [14,5,4,3,2]
        
        combi = CARTE
        if N[0].nombre == 2:
            combi = PAIRE
        if N[0].nombre == 2 and N[1].nombre == 2:
            combi = DOUBLE_PAIRE
        if N[0].nombre == 3:
            combi = BRELAN
        suite = len(N) == 5 and et(N[i].valeur == N[i+1].valeur + 1 for i in range(len(N)-1))
        if suite:
            combi = SUITE
        flush = et(A[i].couleur == A[i+1].couleur for i in range(len(A)-1))
        if flush:
            combi = FLUSH
        if N[0].nombre == 3 and N[1].nombre == 2:
            combi = FULL_HOUSE
        if N[0].nombre == 4:
            combi = CARRE
        if flush and suite:
            combi = QUINTE_FLUSH
            
        return (combi,egalite)
    
    with open('poker.txt') as f:
        to_numerics = {str(i):i for i in range(2,10)}
        to_numerics.update( {s:10+i for i,s in enumerate(('T','J','Q','K','A'))} )
        print(to_numerics)
        V = 0
        for ligne in f.read().split('\n'):
            if len(ligne):
                M = [ Carte(valeur=to_numerics[s[0]], couleur=s[1]) for s in ligne.split(' ')]
                if valeur(M[:5]) > valeur(M[5:]):
                    V += 1
        return V

def PE55():
    Number = namedtuple('Number', ('nombre', 'liste'))
    def number_from_int(a):
        return Number(a, [int(c) for c in str(a)])
    def number_from_list(L):
        return Number(int(''.join(str(a) for a in L)), L)
    def reversed_number(Nb):
        return number_from_list(list(reversed(Nb.liste)))
    def suivant(Nb, Nbr):
        return number_from_int(Nb.nombre + Nbr.nombre)
    def is_lychrel(N):
        A = number_from_int(N)
        R = reversed_number(A)
        for k in range(50):
            P = suivant(A,R)
            RP = reversed_number(P)
            if P.nombre == RP.nombre:
                return False
            else:
                A,R = P,RP
        return True
    return sum(is_lychrel(a) for a in range(0,10000))
    # return compte(filter(is_lychrel, range(0,10000)))

def PE56():
    return max(sum_digits(a ** b) for a,b in multirange(2,100))
    
def PE57():
    # 1 + 1/(2 + 1/(2 + 1/(2 + 1/(2 + 0))))
    cache = {}
    def terme(x):
        if x in cache:
            return cache[x]
        if x == 0:
            return Fraction(2)
        v = cache[x] = Fraction(2) + Fraction(1, terme(x-1))
        return v
    def expansion(x):
        return Fraction(1) + Fraction(1, terme(x-1))

    expansions = (expansion(i) for i in range(1,1001))
    return sum(number_digits(f.numerator) > number_digits(f.denominator) for f in expansions)

def PE59():
    encrypted = [int(a) for a in open("cipher1.txt").read().split(',')]
    def english_carac(c):
        return 32 <= c <= 125
    def contains_only_english_carac(message):
        for c in message:
            if not english_carac(c):
                return False
        return True
    def decrypt(message,key):
        n = 0
        for c in message:
            yield c ^ key[n]
            n = (n+1) % len(key)
    def as_text(message):
        return ''.join(chr(i) for i in message)
    with open("cipher1_res.txt", 'w') as res:
        for a,b,c in multirange(3, ord('a'), ord('z')+1):
            decrypted = list(decrypt(encrypted, (a,b,c)))
            if contains_only_english_carac(decrypted):
                res.write(as_text([a,b,c]) + ' ' + str(sum(decrypted)) + ' ')
                res.write(as_text(decrypted))
                res.write('\n')


def PE61():
    def nombres(gen_croissant):
        for a in gen_croissant:
            taille = len(str(a))
            if taille == 4:
                yield str(a)
            elif taille > 4:
                break
        
    class Node:
        def __init__(self, s, groupe):
            self.string = s
            self.cibles = []
            self.groupe = groupe
        def ajouterCible(self, cible):
            self.cibles.append(cible)
        def __repr__(self):
            return repr(self.string) + "(" + repr(self.groupe) + ")"

    groupe = 0
    def get(gen_croissant):
        nonlocal groupe
        s = set(Node(a, groupe) for a in nombres(gen_croissant))
        groupe += 1
        return s
    M = 10000
    A = get(n*(n+1)//2 for n in range(M))
    B = get(n*n for n in range(M))
    C = get(n*(3*n-1)//2 for n in range(M))
    D = get(n*(2*n-1) for n in range(M))
    E = get(n*(5*n-3)//2 for n in range(M))
    F = get(n*(3*n-2) for n in range(M))

    ensembles = (A,B,C,D,E,F)
    for i in range(len(ensembles)-1):
        for j in range(i+1, len(ensembles)):
            A1,A2 = ensembles[i], ensembles[j]
            for a in A1:
                for b in A2:
                    if a.string[2:] == b.string[:2]:
                        a.ajouterCible(b)
                    elif b.string[2:] == a.string[:2]:
                        b.ajouterCible(a)

    def chercher(base, noeud, groupes):
        for a in noeud.cibles:
            if a == base and len(groupes) == 6:
                return [a]
            if a.groupe in groupes:
                return []
            r = chercher(base, a, groupes | {a.groupe})
            if len(r) == 0:
                continue
            else:
                return r + [a]
        return []
    def chercher_depuis(noeud):
        r = chercher(noeud, noeud, frozenset({noeud.groupe}))
        if len(r) != 0:
            print(r)
    def afficher_arbre(noeud):
        def rec(noeud, deja, deja_groupe, i=0):
            # print(i * '-', noeud, ' '.join(a.string for a in deja))
            nouveau = deja + [noeud]
            nouveau_groupe = deja_groupe + [noeud.groupe]
            for a in noeud.cibles:
                if a in deja:
                    if a == deja[0] and i == 5:
                        print(sum(int(a.string) for a in nouveau), ' '.join(repr(a) for a in nouveau))
                    else:
                        pass #abandon
                elif a.groupe in deja_groupe:
                    pass #abandon
                else:
                    rec(a, nouveau, nouveau_groupe, i+1)
        rec(noeud, [], [])
    avec_cibles = []
    for e in ensembles:
        for v in e:
            if len(v.cibles):
                avec_cibles.append(v)
            chercher_depuis(v)
    for v in avec_cibles: 
        afficher_arbre(v)

def PE62():
    res = {}
    for a in count():
        v = tuple(sorted(c for c in str(a * a * a)))
        if v not in res:
            res[v] = [a,1]
        else:
            cib = res[v]
            cib[1] += 1
            if cib[1] == 5:
                return cib[0] ** 3

def PE63():
    cpt = 0
    for expo in count(1):
        # print("Expo",expo)
        for n in range(1,11):
            diff = len(str(n ** expo)) - expo
            if diff == 0:
                cpt += 1
                print('#', cpt, n, '**', expo, '=', n ** expo, '=>', len(str(n**expo)), 'vs', expo)
            if diff > 0:
                break

# yields all non squares numbers <= N
def non_carres(N):
    s = 0
    for i in range(N+1):
        if s * s == i:
            s += 1
        else:
            yield i

def PE64(N=10000):
    # http://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Continued_fraction_expansion
    def longueur_cycle(S, a0=None):
        if a0 is None:
            a0 = floor(sqrt(S))
        m,d,a = 0,1,a0
        cycle = {}
        for i in count():
            m = d*a - m
            d = (S - m*m) // d # mod = 0
            a = (a0 + m) // d # mod = ...
            if (m,d,a) in cycle:
                return i - cycle[m,d,a]
            cycle[m,d,a] = i
    
    return sum(x%2 == 1 for x in map(longueur_cycle, non_carres(N)))
##    def non_carres_floor(N):
##        s = 0
##        for i in range(N+1):
##            if s * s == i:
##                s += 1
##            else:
##                yield i,s-1
##    return sum(x%2 == 1 for x in (longueur_cycle(s,a0) for s,a0 in non_carres_floor(N)))

def PE65(N=100):
    a0 = 2
    def a(x): # x > 0 => a1,a2,a3, a4,a5,a6 = 1,2,1, 1,4,1
        return 1 if x%3 != 2 else ((x-2) // 3 + 1) * 2
    def frac(N):
        def buddy_a(n):
            return Fraction(0) if n == N else \
                   Fraction(1, Fraction(a(n+1)) + buddy_a(n+1))
        return Fraction(a0) + buddy_a(0)
    return sum_digits(frac(N-1).numerator)

def PE51(number_value=8, maximum=10**6):
    def is_the_one(Prime, debug=False):
        string = str(Prime)
        chiffres = map(int, sorted(set(string)))
        for i in takewhile(lambda x:x <= 10-number_value, chiffres):
            cpt = sum(is_prime( int(string.replace(str(i),str(j))) ) \
                          for j in range(i+1,10))
            if debug:
                print(string.replace(str(i),'*'), ':', cpt, 'primes')
            if cpt == number_value-1:
                return True
        return False
    return next(iter(filter(is_the_one, primes(maximum))))

def PE51_prograclassique(number_value=8, maximum=10**6):
    def is_the_one(Prime, debug=False):
        string = str(Prime)
        chiffres = map(int, sorted(set(string))) # caution : generator
        for i in chiffres:
            if i > 10 - number_value:
                break
            cpt = 0
            for j in range(i+1,10):
                if is_prime( int(string.replace(str(i), str(j))) ):
                    cpt += 1
            if cpt == number_value-1:
                return True
        return False
    for P in primes(maximum):
        if is_the_one(P):
            return P

def PE47(M=4):
    def algo1():
        # 15 secondes ! Peut faire bien mieux
        # (sans devoir faire compter(prime_factors_tuples(N))
        numbers = ((N,sum(1 for a in prime_factors_tuples(N))) for N in count(2))
        # numbers est un générateur infini
        for a,b in groupby(numbers, key=operator.itemgetter(1)):
            l = list(b)
            if a == M and len(l) == M:
                return l[0][0]
        # si on fait un print et non return, on aura tous les nombres

    # Une solution sur le thread => SIEVE !
    # Marcus Stuhr
    # Given an arbitrarily high limit, I take each prime number
    # (up until half the limit) and then sieve the entire range with it.
    # This, in the end, gives the number of distinct prime factors for
    # each number in the range except for the prime factors above half
    # the limit (which are irrelevant for our purposes anyway).
    # Then I simply return the index of the factor array containing [4,4,4,4].
    def algo2(lim=200000, dpf=4):
        L = [0] * lim
        for i in range(2, 1 + lim//2):
            if L[i] == 0: # Prime
                for j in range(i, lim, i):
                    L[j] += 1
        return ''.join(map(str,L)).index(str(dpf) * dpf)
    return algo2(dpf=M)

def PE58():
    def gen(rep):
        c,n = 1,1
        for i in range(rep):
            c += 1
            c += n
            yield c
            n += 1
            for j in range(3):
                c += n
                yield c        
            n += 1

    prim,total = 0,1
    it = iter(gen(100000))
    for i in range(100000):
        nbs = [next(it) for j in range(4)]
        prim += sum(is_prime(nbs[j]) for j in range(3))
        total += 4
        print(i, nbs, prim, total, prim / total)
        if prim / total < 0.10:
            return (i+1)*2+1
            break
        
def PE60():
    MAXI = 10000
    class Node:
        def __init__(self, N):
            self.N = N
            self.string = str(N)
            self.buddys = set()
        def __iter__(self):
            return iter(self.buddys)
        def __repr__(self):
            return repr( (self.string, len(self.buddys)) )
        def testerBuddy(self,other):
            if is_prime(int(self.string + other.string)) and \
               is_prime(int(other.string + self.string)):
                self.buddys.add(other)
        def ajouterReciproque(self,other):
            self.buddys.add(other)
            other.buddys.add(self)

    L = [Node(N) for N in primes(MAXI)]
    for a,b in combinations(L,2): # O(len(L) ** 2)
        a.testerBuddy(b)
    print('Graphe créé')
    # Temps de création très long
    
    def chercher(noeud, union_from_root, buddys):
        if len(buddys) == 5:
            yield buddys
            return
        union = union_from_root & noeud.buddys
        for a in union:
            yield from chercher(a, union & a.buddys, buddys + (a,))
    def chercher_depuis(noeud):
        yield from chercher(noeud, noeud.buddys, (noeud,))

    A = [Node(chr(ord('a') + N)) for N in range(6)]
    a,b,c,d,e,f = A
    a.buddys = {b,d,f,e}
    b.buddys = {a,c,d,e}
    c.buddys = {b,e}
    d.buddys = {a,b,e}
    e.buddys = {c,a,b,d}
    f.buddys = {a}

    a.buddys = {b,d,f,e}
    b.buddys = {c,d,e}
    c.buddys = {e}
    d.buddys = {e}
    e.buddys = set()
    f.buddys = set()

    for a in L:
        for ensemble in chercher_depuis(a):
            print(set(a.N for a in ensemble))

# V iterable of nodes
# Nodes are iterable (yields each destination)
# They have two fields index, lowlink
def tarjan(V):
    index = [0]
    S = []
    def strongconnect(v):
        # Set the depth index for v to the smallest unused index
        v.index = index[0]
        v.lowlink = index[0]
        index[0] += 1
        S.append(v)

        # Consider successors of v
        for w in v:
          if w.index == -1:
            # Successor w has not yet been visited; recurse on it
            strongconnect(w)
            v.lowlink = min(v.lowlink, w.lowlink)
          elif w in S:
            # Successor w is in stack S and hence in the current SCC
            v.lowlink = min(v.lowlink, w.index)

        # If v is a root node, pop the stack and generate an SCC
        if v.lowlink == v.index:
            SCC = [ S.pop() ]
            while SCC[-1] != v:
                SCC.append( S.pop() )
            yield SCC
            
    for v in V:
        if v.index == -1:
            yield from strongconnect(v)

def tarjan_test():
    V = [Node(N) for N in range(8)]
    a,b,c,d,e,f,g,h = V
    for x,y in [[a,b],[b,c],[b,e],[b,f],[c,d],[c,g],[d,c],[d,h],[e,a], \
                [e,f],[f,g],[g,f],[h,g],[h,d]]:
        x.buddys.append(y)
    for a in V:
        print(a,':',a.buddys)
    return list(tarjan(V))

def PE68():
    groups = [(i,i+5,(i+6)%5 + 5) for i in range(5)]
    mygroups = [[x] for x in range(5)] + [[x-5, (x-6)%5] for x in range(5,11)]

    somme_actuelle = None
    N = [10] + [None] * 9
    utilises = {10}
    def afficher(res):
        nonlocal somme_actuelle
        print('[somme_actuelle] :', somme_actuelle)
        hasNone = False
        for a,b,c in groups:
            print('G',res[a],res[b],res[c])

        def make_string():
            iMin = 0
            for i in range(1, len(groups)):
                for j in range(3):
                    if res[ groups[i][j] ] is None:
                        return ''
                if res[ groups[i][0] ] < res[ groups[iMin][0] ]:
                    iMin = i
            string_solution = ''
            for i in chain(range(iMin, len(groups)), range(iMin)):
                for j in range(3):
                    string_solution += str(res[ groups[i][j] ])
            return string_solution
        
        print('string_solution', make_string())
    def is_correct(group):
        s = 0
        for i in group:
            a = N[i]
            if a is None:
                return True
            s += a
        return somme_actuelle == s
    def are_correct(the_groups):
        for i in the_groups:
            if not is_correct( groups[i] ):
                return False
        return True
    def backtrack(a):
        if a == len(N):
            yield N
            return
        for i in range(1,11):
            if i not in utilises:
                utilises.discard(N[a])
                N[a] = i
                utilises.add(i)
                # afficher(N)
                if are_correct( mygroups[a] ):
                    yield from backtrack(a+1)
        utilises.discard(N[a])
        N[a] = None
        # print("Back")
        # afficher(N)
    
    for somme in range(1+2+3,10+9+8 + 1):
        somme_actuelle = somme
        utilises = {10}
        N = [10] + [None] * 9
        print('somme',somme,'?')
        for sol in backtrack(1):
            afficher(sol)


def PE74():
	Fac = [factorial(i) for i in range(10)]
	fac = lambda d:Fac[d]
	def gen(N):
		while True:
			yield N
			N = sum(map(fac, map(int, str(N))))
	
	non_repeating_terms = {}
	def compter_repetitions(N):
		l = []
		# print('N =', N )
		for a in gen(N):
			# print('a =',a)
			if a in non_repeating_terms:
				# print('or [',a,'] = ', non_repeating_terms[a], '!')
				n = non_repeating_terms[a] + 1 # 6
				for i in range(len(l)):
					non_repeating_terms[ l[i] ] = len(l) - 1 - i + n
					# print('[', l[i], '] = ', non_repeating_terms[ l[i] ], '!')
				return len(l) - 1 + n # == non_repeating_terms[ N ]
			elif a in l:
				# Si on a prérempli non_repeating_terms avec les Seuls nombres cyclant
				# cette étape coûteuse est inutile
				
				# print('a in l !')
				for i in range(len(l)):
					if l[i] == a:
						x = len(l) - i
						for i in range(i,len(l)):
							non_repeating_terms[ l[i] ] = x
							# print('[', l[i], '] = ', non_repeating_terms[ l[i] ], '!')
						break
					else:
						non_repeating_terms[ l[i] ] = len(l) - i
						# print('[', l[i], '] = ', non_repeating_terms[ l[i] ], '!')
				return len(l) # == non_repeating_terms[ N ]
			else:
				l.append(a)
				# print('l =',l)
	# return compter_repetitions(69)
	return sum(1 for i in range(10**6) if compter_repetitions(i) == 60)

def PE81(algo=1):
    with open('matrix.txt') as f:
        M = [list(map(int, l.split(','))) for l in f]
        
        if algo == 2:
            # Plusieurs départ équivaut à un seul noeud (fictif) de départ ayant
            #  un accès gratuit à tous les départs
            # Ici il suffit d'insérer une colonne de zéros à gauche
            M = [ [0] + l for l in M ]
        
        A,B = len(M), len(M[0])
        for m in M:
            assert len(m) == B
        
        def simple_dijkstra(begin):
            
            class Varis:
                def __init__(self, weight, previous, my_list):
                    self.weight = weight
                    self.previous = previous
                    self.my_list = my_list
            
            variables = [[Varis(None,None,None) for j in range(B)] for i in range(A)]
            OPEN,CLOSE = range(2)
            
            vari = lambda pos: variables[ pos[0] ][ pos[1] ]
            value = lambda pos: M[ pos[0] ][ pos[1] ]
            in_range = lambda pos: 0 <= pos[0] < A and 0 <= pos[1] < B
            
            def getter(s):
                return lambda pos: vari(pos).__getattribute__(s)
            
            if algo == 1:
                def voisins(i,j):
                    yield from ((i+1,j),(i,j+1))
            elif algo == 2:
                def voisins(i,j):
                    yield from ((i,j+1),(i+1,j),(i-1,j))
            else:
                def voisins(i,j):
                    yield from ((i+1,j),(i-1,j),(i,j+1),(i,j-1))
            
            def traiter(base):
                vari(base).my_list = CLOSE
                for voisin in filter(in_range, voisins(*base)):
                    if vari(voisin).my_list != CLOSE:
                        dist = vari(base).weight + value(voisin)
                        
                        def do_it():
                            vari(voisin).weight = dist
                            vari(voisin).previous = base
                        
                        if vari(voisin).my_list != OPEN:
                            vari(voisin).my_list = OPEN
                            open_list.add(voisin)
                            do_it()
                        else:
                            if dist < vari(voisin).weight:
                                do_it()
            
            if algo in (1,3):
                def condition_fin(cib):
                    return cib == (A-1,B-1)
            else:
                def condition_fin(cib):
                    return cib[1] == B-1
            
            open_list = {begin}
            vari(begin).weight = value(begin)
            vari(begin).my_list = OPEN
            
            cib = begin
            while len(open_list) and not condition_fin(cib):
                cib = min(open_list, key=getter('weight'))
                open_list.remove(cib)
                traiter(cib)
            
            def iter_from(cib):
                yield cib
                while vari(cib).previous:
                    cib = vari(cib).previous
                    yield cib
                    
            # print( list(reversed(list(map(value, iter_from(cib))))) )
            # assert vari(cib).weight == sum(map(value, iter_from(cib)))
            
            return vari(cib).weight
    
        return simple_dijkstra( (0,0) )
				

def PE82():
	return PE81Plus(algo=2)

def PE83():
	return PE81Plus(algo=3)

def PE66():
    # x2 - D y2 = 1 <=> (x2 - 1) / D = y2
    def gen():
        r = 2
        for i in count(2):
            if r*r == i:
                r += 1
            else:
                yield i

    def is_squared(N): 
        n = sqrt(N)
        return floor(n) == n

    def find_x(D):
        for x in count(2):
            num = x*x - 1
            if num % D != 0:
                continue
            if is_squared(num // D):
                return x
    m = 0
    for D in gen():
        if D > 1000:
            break
        m = max(m, find_x(D))
    return m

def PE71(M=10**6):
    def run():
        for d in range(1,1 + M):
            n = (d*3)//7
            f = Fraction(n,d)
            if f < Fraction(3,7): # if (d*3) % 7 != 0
                yield f
    return max(run()).numerator
        
def PE144():
    pass

def PE426(choix):
    from collections import deque
                
    def genS(N):
        s = 290797
        for i in range(N):
            yield s
            s = (s*s) % 50515093
    
    def t(s):
        return (s % 64) + 1
    
    def gen(N):
        return map(t, genS(N))
    
    #renvoie la partie fixe puis la partie qui se répète
    def analyser_gen():
        liste = []
        memory = {}
        for s in genS(10 ** 7 + 1):
            if s in memory:
                sep = memory[s]
                print(s, " in memory @", sep)
                return liste[:sep], liste[sep:]
            memory[s] = len(liste)
            liste.append( t(s) )
    
    def getAB(comb):
        for i in range(0,len(comb),2):
            a = comb[i]
            
            try:
                b = comb[i+1]
            except IndexError:
                b = 10 ** 9
                
            yield a,b
    
    def nextStep(comb):
        nouveau = []
        ra,rb = 0,0
        # arret = True
        for a,b in getAB(comb):
            if len(nouveau):
                nouveau.append(a + rb) #espaces
            a += ra
            
            # nouveau.append( min(a,b) )
            # ra,rb = max(a-b,0), max(b-a,0)
            # arret = (a > b) and arret
            
            if a > b: #trop de remplis
                nouveau.append(b) #remplis
                ra,rb = a-b,0
                # arret = False
            else: #trop d'espaces ou juste assez
                nouveau.append(a) #remplis
                ra,rb = 0,b-a
            
        return nouveau
   
    def arret(ancien,nouveau):
        for (a,b),(na,nb) in zip(getAB(ancien), getAB(nouveau)):
            if a != na or nb < b:
                return False
        return True
    
    def repres(comb):
        return "\t".join(str(a) + "(" + str(b) + ")" for a,b in getAB(comb))
        
    def final_simple(dep, afficher_debut=False, afficher_milieu=False):
        fin = False
        if afficher_debut:
            print(repres(dep))
        while not fin:
            nouveau = nextStep(dep)
            fin = arret(dep,nouveau)
            dep = nouveau
            if afficher_milieu:
                print(repres(dep))
        return dep
        
    def sumsquaredfinalsimple(comb):
        return sum(x*x for x in final_simple(comb)[::2])
        
    def sumsquaredfinal(comb):
        if len(comb) <= 11:
            return sumsquaredfinalsimple(comb)
        
        nombres = 0
        trous = 0
        somme = 0
        d = 0
        for i in range(0,len(comb)-1,2):
            nombres += comb[i]
            trous   += comb[i+1]
            if nombres < trous:
                somme += sumsquaredfinal( nextStep(comb[d:i+1]) )
                d = i+2
                nombres = 0
                trous = 0
                
        return somme + sumsquaredfinal( nextStep(comb[d:]) )
            
    # la,lb = analyser_gen()
    # print("Partie fixe :", la)
    # print("len Partie variable :", len(lb))
    # dep = la + lb * nombre. len(dep) == 10**7 + 1 => 10**7 + 1 = len(la) + len(lb) * nombre => nombre = 10 ** 7 + 1 - len(la) / len(lb)
    # nombre = (10 ** 7 + 1 - len(la)) / len(lb)
    # print("nombre", nombre)
    
    if isinstance(choix,int):
        if choix < 0:
            dep = tuple( gen(10**(-choix) + 1) )
        else:
            dep = [
                [2,2,2,1,2],
                [2,4,1,1,1,1],
                [3,2,2],
                [2,1,1,2,2,6,1,3,4,5,6]
            ][choix]
    else:
        dep = choix
    # print("Fin de génération de l'entrée, début de l'algo")

    print( sumsquaredfinal(dep) )
    # print(sumsquaredfinalsimple(dep))

def PE107():
    M = [[int(c) if c != '-' else None for c in line.strip().split(',')]
         for line in open("p107_network.txt")]
    '''M = [
        [ None ,16   ,12   ,21   ,None ,None ,None ],
        [ 16   ,None ,None ,17   ,20   ,None ,None ],
        [ 12   ,None ,None ,28   ,None ,31   ,None ],
        [ 21   ,17   ,28   ,None ,18   ,19   ,23   ],
        [ None ,20   ,None ,18   ,None ,None ,11   ],
        [ None ,None ,31   ,19   ,None ,None ,27   ],
        [ None ,None ,None ,23   ,11   ,27   ,None ],
    ]'''
    N = len(M)
    print('\n'.join(' '.join('    ' if x is None else str(x).zfill(4) for x in l) for l in M))
    
    def value(edge):
        i,j = edge
        return M[i][j]
    
    def exists(edge):
        return value(edge) is not None
    
    s = 0
    O = set(range(N))
    E = { O.pop() }
    while O:
        x,y = min(filter(exists, product(E, O)), key=value)
        s += M[x][y]
        E.add(y)
        O.remove(y)
    return sum(0 if x is None else x for l in M for x in l) // 2 - s

def P89():
    open('p089_roman.txt')
    
def P145():
    def is_reversible(i):
        return (str(i)[0] != '0' and str(i)[-1] != '0' and
                all(c in '13579' for c in str(i + int(str(i)[::-1]))))
    
def p102():
    [tuple(map(int,line.strip().split(','))) for line in open('p102_triangles.txt')]

def p79():
    D = [tuple(map(int,l[:3])) for l in open('p079_keylog.txt')]
    print("Prolog")
    print("find(List) :-")
    print('\n'.join("append(Left{i:02}, [{a}|Right{i:02}], List), append(Left2{i:02}, [{b}|Right2{i:02}], Right{i:02}), append(Left3{i:02}, [{c}|Right3{i:02}], Right2{i:02}){end}".format(i=i,a=a,b=b,c=c,end='.' if i == len(D) - 1 else ',') for i,(a,b,c) in enumerate(D)))
    print("\ncount(1).\ncount(N) :- count(G), N is G+1.")
    print("Query :")
    print("count(N), length(List,N), find(List), write(List), !.")