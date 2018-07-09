#!coding:utf-8
import unicodedata
import sys

__all__ = ('uniname', 'hexord', 'hexaord', 'uord', 'uordname', 'uniline', 'unicontext', 'unibasecat', 'unilinecat', 'unibasecatverbose', 'unicatverbose', 'unilineverbose')

lmap = map if sys.version_info[0] < 3 else lambda *a, **b: list(map(*a, **b))

COLOR_TERMINAL = True

def greenize(s):
    return "\033[32m{}\033[0m".format(s) if COLOR_TERMINAL else s

def greenizebold(s):
    return "\033[32;1m{}\033[0m".format(s) if COLOR_TERMINAL else s

# decorator
def multiple_makes_lmap(f):
    # return lambda s: f(s) if len(s) == 1 else lmap(f, s)
    # return lambda s, *args: f(s, *args) if len(s) == 1 else [f(x, *args) for x in s]
    
    from functools import wraps
    @wraps(f)
    def new(s, *args):
        if not hasattr(s, '__iter__'):
            return f(s, *args)
        R = [f(x, *args) for x in s]
        if len(R) == 1:
            return R[0]
        return R
    
    return new
    
@multiple_makes_lmap
def uniname(s):
    """
    >>> uniname('é')
    'LATIN SMALL LETTER E WITH ACUTE'
    >>> uniname('αβγ')
    ['GREEK SMALL LETTER ALPHA', 'GREEK SMALL LETTER BETA', 'GREEK SMALL LETTER GAMMA']
    """
    return unicodedata.name(s, '?')
    
@multiple_makes_lmap
def hexord(s):
    """
    >>> hexord('é')
    '0xe9'
    >>> hexord('αβγ')
    ['0x3B1', '0x3B1', '0x3B1']
    """
    return hex(ord(s))

@multiple_makes_lmap
def hexaord(s):
    """
    >>> hexaord('é')
    'e9'
    >>> hexaord('αβγ')
    ['3B1', '3B1', '3B1']
    """
    return hex(ord(s))[2:]

@multiple_makes_lmap
def uord(s):
    """
    >>> uord('é')
    'U+00E9'
    >>> hexaord('αβγ')
    ['U+03B1', 'U+03B1', 'U+03B1']
    """
    return 'U+' + hex(ord(s))[2:].zfill(4).upper()

@multiple_makes_lmap
def uordname(s):
    """
    >>> uordname('é')
    'U+00E9 LATIN SMALL LETTER E WITH ACUTE'
    >>> uordname('αβγ')
    ['U+03B1 GREEK SMALL LETTER ALPHA', 'U+03B2 GREEK SMALL LETTER BETA', 'U+03B3 GREEK SMALL LETTER GAMMA']
    """
    return '{} {}'.format(uord(s), uniname(s))

@multiple_makes_lmap
def uniline(s):
    """
    >>> uniline('é')
    'U+00E9 é LATIN SMALL LETTER E WITH ACUTE'
    >>> uniline('αβγ')
    ['U+03B1 α GREEK SMALL LETTER ALPHA', 'U+03B2 β GREEK SMALL LETTER BETA', 'U+03B3 γ GREEK SMALL LETTER GAMMA']
    """
    return '{} {} {}'.format(uord(s), s, uniname(s))

@multiple_makes_lmap
def unilinecat(s):
    """
    >>> unilinecat('é')
    'Ll U+00E9 é LATIN SMALL LETTER E WITH ACUTE'
    """
    
    return '{} {}'.format(unicodedata.category(s), uniline(s))

@multiple_makes_lmap
def unibasecat(s):
    """
    >>> unibasecat('é')
    'L'
    """
    return unicodedata.category(s)[0]

CATEGORY_BASE_VERBOSE = {
    'L': 'Letter',
    'M': 'Mark',
    'N': 'Number',
    'P': 'Punctuation',
    'S': 'Symbol',
    'Z': 'Separator',
    'C': 'Other',
}

@multiple_makes_lmap
def unibasecatverbose(s):
    """
    >>> unibasecatverbose('é')
    'L: Letter'
    """
    cat = unicodedata.category(s)
    return '{}: {}'.format(cat[0], CATEGORY_BASE_VERBOSE[cat[0]])

CATEGORY_SECOND_VERBOSE = {
    'Lu': 'uppercase',
    'Ll': 'lowercase',
    'Lt': 'titlecase',
    'Lm': 'modifier',
    'Lo': 'other',
    'Mn': 'nonspacing',
    'Mc': 'spacing combining',
    'Me': 'enclosing',
    'Nd': 'decimal digit',
    'Nl': 'letter',
    'No': 'other',
    'Pc': 'connector', 
    'Pd': 'dash', 
    'Ps': 'open', 
    'Pe': 'close', 
    'Pi': 'initial quote', 
    'Pf': 'final quote', 
    'Po': 'other', 
    'Sm': 'math', 
    'Sc': 'currency',
    'Sk': 'modifier',
    'So': 'other',
    'Zs': 'space',
    'Zl': 'line',
    'Zp': 'paragraph',
    'Cc': 'control',
    'Cf': 'format',
    'Cs': 'surrogate',
    'Co': 'private use',
    'Cn': 'not assigned',
}

@multiple_makes_lmap
def unicatverbose(s):
    """
    >>> unicatverbose('é')
    'Ll: Letter, lowercase'
    """
    cat = unicodedata.category(s)
    return '{}: {}, {}'.format(cat, CATEGORY_BASE_VERBOSE[cat[0]], CATEGORY_SECOND_VERBOSE[cat])
    # won't raise a KeyError 

@multiple_makes_lmap
def unilineverbose(s):
    """
    >>> unilineverbose('é')
    'U+00E9 é LATIN SMALL LETTER E WITH ACUTE (Ll: Letter, lowercase)'
    """
    return '{} ({})'.format(uniline(s), unicatverbose(s))

@multiple_makes_lmap
def unicontext(s, width=5):
    name = unicodedata.name(s, '?')
    print('U+' + hex(ord(s))[2:].zfill(4).upper(), s, name)
    b = ord(s) >> 4 << 4
    print('       ' + ' '.join('v' if i == ord(s) % 16 else ' ' for i in range(16)))
    print('       ' + ' '.join(hex(i)[2:].upper() for i in range(16)))
    for n in (b + i * 16 for i in range(-width,+width+1)):
        if n >= 0x10:
            print(('U+' if n != b else '>>') + hex(n)[2:].zfill(4).upper() + ' ' +
                   ' '.join((greenizebold if n + i == ord(s) else lambda x:x)(chr(n + i))
                            for i in range(16)))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
