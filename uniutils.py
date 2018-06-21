#!coding:utf-8
import unicodedata
import sys

__all__ = ('uniname', 'hexord', 'hexaord', 'uord', 'uordname', 'uniline', 'unicontext')

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
    return unicodedata.name(s, '?')
    
@multiple_makes_lmap
def hexord(s):
    return hex(ord(s))

@multiple_makes_lmap
def hexaord(s):
    return hex(ord(s))[2:]

@multiple_makes_lmap
def uord(s):
    return 'U+' + hex(ord(s))[2:].zfill(4).upper()

@multiple_makes_lmap
def uordname(s):
    return uord(s) + ' ' + uniname(s)

@multiple_makes_lmap
def uniline(s):
    return uord(s) + ' ' + s + ' ' + uniname(s)

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
