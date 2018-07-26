from itertools import product, repeat, combinations, groupby, accumulate
from fractions import Fraction
from functools import reduce, partial

def messe(sac, N=4, list_to_print=False, only_print=True, percentage_float=False):
    """
        sac : iterable de string contenant tous les membres non moines dans le sac :
            Exemples:
                'rrb'
                'r1 r2 b'.split()
        N : nombre de personnes à prendre
        
        list_to_print = True:
            Output : tab, G.
            tab = [['r', 'r', 'b', '-', 53.3] for i in range(G)]
        
        only_print = True:
            Output : None, pretty print to console
            
        only_print = False:
            Output : the pretty string, G
        
    """
    sac = list(sac)
    
    placement = '-' * max(map(len,sac))
    
    sac = [placement if all(c == '-' for c in s) else s for s in sac]
    
    D = [placement] * 4 + sac
    
    def special_underscore(string):
        return (0,) if string == placement else (1,string)
    
    L = sorted(map(partial(sorted,key=special_underscore), combinations(D,N)))
  
    G = sorted(
        (
            (sum(1 for u in b), len(L), v)
            for v,b in groupby(L)
        ),
        reverse = True,
        key = lambda t: (t[0], t[2])
    )
    to_percentage = float if percentage_float else int
    
    if list_to_print:
        return [
            v + [to_percentage(float(num) / float(den) * 100)]
            for num, den, v in G
        ], len(G)
    
    widths = (
        max(len(str(num)) for num, den, v in G),
        max(len(str(Fraction(num,den).numerator)) for num, den, v in G),
        max(len(str(Fraction(num,den).denominator)) for num, den, v in G),
    )
    
    format_text = "| {value} | {pourcent:2}%% | {num:%d}/{den} | {snum:%d}/{sden:%d} |" % widths
    format_value = "{:>%d}" % max(map(len,sac))
    
    res = '\n'.join(
        format_text.format(
            num = num,
            den = den,
            snum = Fraction(num,den).numerator,
            sden = Fraction(num,den).denominator,
            pourcent = to_percentage(float(num) / float(den) * 100),
            value = ' '.join(map(format_value.format, v))
        )
        for num, den, v in G
    ), len(G)
        
    if only_print:
        print(res[0])
    else:
        return res
  
def generate_all():
    colors = 'ABCDEFGHIJ'
    
    def chaine_for_possib(possib):
        '''
        Input: possib (2,1,2,0)
        Output: AABCC
        '''
        return ''.join(c * p for c,p in zip(colors, possib))
    
    def n_different(possib):
        '''
        Input: possib (2,1,2,0)
        Output: 3
        '''
        return sum(bool(p) for p in possib)
    
    def filtre(possib):
        # return n_different(possib) in (2,)
        return True
    
    def tri(possib):
        n = n_different(possib)
        
        #return (n, sum(possib))
        
        return (
            max(messe(chaine_for_possib(possib),i,only_print=False)[1] for i in (1,2,3,4)),
            n,
            sum(possib)
        )
    
        if n == 1:
            return (n,)
        else:
            return (1000,sum(possib))
    
    height_head = 1
    height_line = 0.5
    
    affichage = 0
    
    all_choices = product(*repeat(range(5), 4))
    all_choices_set = (tuple(reversed(a)) for a,b in groupby(sorted(map(sorted, all_choices))))
    
    nt = 0
    for possib in sorted(filter(filtre, all_choices_set), key=tri):
        if affichage == 0:
            pretty_possib = ', '.join(
                str(p) + c
                for c,p in zip(colors,possib)
                if p != 0
            )
            print('{} + 4 moines'.format(pretty_possib))
        else:
            pretty_possib = ' '.join(map(str,possib))
            print('\n# Sac : {} + 4 moines #\n'.format(pretty_possib))
        
        nt += height_head
        
        n = 0
        saves = []
        for i in (1,2,3,4):
            text, m = messe(
                chaine_for_possib(possib),
                i,
                list_to_print = affichage == 0,
                only_print=False
            )
            saves.append(text)
            if affichage == 1:
                print("+ {}\n{}\n".format(i, text))
            n = max(n,m)
        
        nt += n * height_line
        
        if affichage == 0:
            print('\n'.join(
                ';'.join(reduce(
                    lambda x,y: x+y,
                    (
                        saves[j][i][:-1] + [str(saves[j][i][-1]) + '%']
                        if i in range(len(saves[j]))
                        else [''] * len(saves[j][0])
                        for j in range(len(saves))
                    )
                ))
                for i in range(n)
            ))
        
        if affichage in (1,2):
            print(n, 'lignes')
        if affichage in (1,2,3):
            print(nt, 'cm')

def get_binary_proba(my_mepples, other_meeples, number_to_take):
    ''' len(return) == min(N,i)'''
    return list(reversed(
        list(map(int, accumulate(
            (lambda L:L[:-1])(list(map(lambda x: x[-1],
                sorted(messe('a' * my_mepples + '-' * other_meeples, number_to_take, True, True, True)[0],
                       key=lambda l:l.count('a'),
                       reverse=True)
            )))
        )))
    ))

def generate_all_binary(M=15):
    for i in (1,2,3,4):
        for o in range(M+1):
            ligne = []
            for N in (4,3,2,1):
                ligne += get_binary_proba(i, o, N) + ['|']
            print(';'.join(map(str,ligne)))

import sys

if __name__ == '__main__':
    if 'generate' in sys.argv:
        generate_all()
    else:
        print("Examples of bag:\n  rrb\n  r1 r2 b\n  r--")
        while True:
            try:
                string = input('Bag ? ').strip()
                N = int(input('Number ? '))
                if ' ' in string:
                    messe(string.split(), N)
                else:
                    messe(string, N)
            except ValueError:
                pass

# messe('r1 r2 b'.split(), 2)
# for i in (1,2,3,4): messe('r' * 5, i)
# generate_all()