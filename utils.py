def bytes2human(n, format="{value}{symbol}"):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('B','K','M','G','T','P','E','Z','Y')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format.format(value=str(value)[:4], symbol=symbol) #locals()
    return format.format(symbol=symbols[0], value=n)

def simp(L):
    O = [ [] ]
    for i in range(len(L)):
        if i+1 in range(len(L)) and L[i]+1 == L[i+1]:
            O[-1].append(L[i])
        else:
            O[-1].append(L[i])
            O.append([])
    del O[-1] # always empty
    return O

def simp(L):
    """
    >>> simp([1,2,3, 7,8,9, 42])
    [[1,2,3], [7,8,9], [42]]
    """
    from itertools import zip_longest
    O = [ [] ]
    for cur, next in zip_longest(L, L[1:], fillvalue=object()):
        if cur+1 == next:
            O[-1].append(cur)
        else:
            O[-1].append(cur)
            O.append([])
    del O[-1] # always empty
    return O

def to_interv(Ll):
    from copy import deepcopy
    Ll = deepcopy(Ll)
    for l in Ll:
        if len(l) > 2:
            del l[1:-1]
    return Ll
