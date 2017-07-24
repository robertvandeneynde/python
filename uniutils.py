#!coding:utf-8
import unicodedata
import sys

_lmap = map if sys.version_info[0] < 3 else lambda *args: list(map(*args))

# decorator
def _multiple_makes_lmap(f):
    return lambda s: f(s) if len(s) == 1 else _lmap(f, s)
    
@_multiple_makes_lmap
def uniname(s):
    return unicodedata.name(s)
    
@_multiple_makes_lmap
def hexord(s):
    return hex(ord(s))

@_multiple_makes_lmap
def hexaord(s):
    return hex(ord(s))[2:]

@_multiple_makes_lmap
def uord(s):
    return 'U+' + hex(ord(s))[2:].zfill(4).upper()

@_multiple_makes_lmap
def uordname(s):
    return uord(s) + ' ' + uniname(s)

@_multiple_makes_lmap
def uniline(s):
    return uord(s) + ' ' + s + ' ' + uniname(s)

@_multiple_makes_lmap
def unicontext(s, width=5):
    print('U+' + hex(ord(s))[2:].zfill(4).upper(), s, unicodedata.name(s))
    b = ord(s) >> 4 << 4
    print('       ' + ' '.join(hex(i)[2:].upper() for i in range(16)))
    for n in (b + i * 16 for i in range(-width,+width+1)):
        if n >= 0x10:
            print(('U+' if n != b else '>>') + hex(n)[2:].zfill(4).upper() + ' ' +
                   ' '.join((greenizebold if n + i == ord(s) else lambda x:x)(chr(n + i))
                            for i in range(16)))
