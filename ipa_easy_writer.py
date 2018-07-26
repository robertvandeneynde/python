#!coding: utf-8
from __future__ import print_function

def print_info():
    import unicodedata

    r = '''
    \u028a \u026a \u00f8 \u025b \u0153 \u00e6 \u0259 \u025c \u0254 \u0251
    \u0283 \u0292 \u0280 \u0281 \u028c
    \u0272 \u0265
    \u014b
    '''.strip()

    print(r)
    print(' '.join(x + '\u0303'  for x in '\u0251\u025B\u0153\u0254'))

    for x in r.split():
        print('U+' + hex(ord(x))[2:].zfill(4).upper(), x, unicodedata.name(x))

if __name__ == '__main__':
    print_info()

class Dict:
    def __init__(self, dic):
        self.dic = dic
    def word(self, w):
        return '/{}/'.format(''.join(self.dic.get(x, x) for x in w.split()))
    __call__ = word

french = Dict({
    'e':'ə',
    'é':'e',
    'è':'ɛ',
    'ê':'ɛː',
    'oe':'œ',
    'eu':'ø', 
    'o':'ɔ',
    'ô':'o',
    'au':'o',
    'ou':'u',
    'u':'y',
    'â':'ɑ',
    # useless accents
    'ù': 'y',
    'î': 'i',
    'û': 'y',
    # nasals
    'in':'ɛ\u0303',
    'ain':'ɛ\u0303',
    'ein':'ɛ\u0303',
    'un':'œ\u0303',
    'on':'ɔ\u0303',
    'on':'ɔ\u0303',
    'an':'ɑ\u0303', 
    # consonants
    'r':  'ʁ',
    'ch': 'ʃ',
    'j':  'ʒ',
    'gn': 'ɲ',
    # semivowels
    'ui': 'ɥ',
    'y':  'j',
    # punctuation
    ':': 'ː',
    '--': '‿',
    # probable error
    'c': '?k,s?',
    'h': '??',
    'q': '?k?',
    'x': '?ks?',
})