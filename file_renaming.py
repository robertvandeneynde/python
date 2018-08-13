#! /usr/bin/env python3

import re
import os
import unicodedata

from pprint import pprint
import sys
assert sys.version_info >= (3,)

class Renamer:
    """ call renamer.rename instead of os.rename to have a safe guard.
    renamer ask confirmation for the first 5 files """
    def __init__(self, *, maxtry=5):
        self.trycount = 0
        self.renamed = 0
        self.maxtry = maxtry
    def rename(self, a, b):
        import os
        if a == b:
            return
        if self.trycount >= self.maxtry or input('Rename {!r} -> {!r}? [Y/n]'.format(a,b)).lower() not in ('n', 'no', 'non'):
            os.rename(a, b)
            self.renamed += 1
        else:
            self.trycount += 1


def pourcentEncoded(string,encoding='utf-8'):
    '''
    pourcentEncoded("Parl%c3%a9") == "Parlé"
    '''
    return re.sub(
        "(%[0-9a-fA-F]{2}){1,4}",
        lambda m: str(
            bytes(
                int(a,base=16)
                for a in re.findall("[0-9a-fA-F]{2}", m.group(0))
            ),
            encoding=encoding
        ),
        string
    )

HTML_SEQ_OTHER = '''
    8364;euro;
    160;nbsp;
    34;quot;
    38;amp;
    60;lt;
    62;gt;
    161;iexcl;
    162;cent;
    163;pound;
    164;curren;
    165;yen;
    166;brvbar;
    167;sect;
    168;uml;
    169;copy;
    170;ordf;
    172;not;
    173;shy;
    174;reg;
    175;macr;
    176;deg;
    177;plusmn;
    178;sup2;
    179;sup3;
    180;acute;
    181;micro;
    182;para;
    183;middot;
    184;cedil;
    185;sup1;
    186;ordm;
    187;raquo;
    188;frac14;
    189;frac12;
    190;frac34;
    191;iquest;
    192;Agrave;
    193;Aacute;
    194;Acirc;
    195;Atilde;
    196;Auml;
    197;Aring;
    198;AElig;
    199;Ccedil;
    200;Egrave;
    201;Eacute;
    202;Ecirc;
    203;Euml;
    204;Igrave;
    205;Iacute;
    206;Icirc;
    207;Iuml;
    208;ETH;
    209;Ntilde;
    210;Ograve;
    211;Oacute;
    212;Ocirc;
    213;Otilde;
    214;Ouml;
    215;times;
    216;Oslash;
    217;Ugrave;
    218;Uacute;
    219;Ucirc;
    220;Uuml;
    221;Yacute;
    222;THORN;
    223;szlig;
    224;agrave;
    225;aacute;
    226;acirc;
    227;atilde;
    228;auml;
    229;aring;
    230;aelig;
    231;ccedil;
    232;egrave;
    233;eacute;
    234;ecirc;
    235;euml;
    236;igrave;
    237;iacute;
    238;icirc;
    239;iuml;
    240;eth;
    241;ntilde;
    242;ograve;
    243;oacute;
    244;ocirc;
    245;otilde;
    246;ouml;
    247;divide;
    248;oslash;
    249;ugrave;
    250;uacute;
    251;ucirc;
    252;uuml;
    253;yacute;
    254;thorn;
'''

HTML_SEQ = {}

for line in HTML_SEQ_OTHER.strip().split('\n'):
    number, name = line.strip().split(';')[:2]
    HTML_SEQ[name] = chr(int(number))

def htmlSequence(string):
    '''
    &quote; => "
    &#33; => !
    '''
    return re.sub(
        '&(.*?);',
        lambda m:
            (lambda name:
                chr(int(name)) if all('0' <= c <= '9' for c in name) else
                HTML_SEQ.get(name, '')
            )(m.group(1)),
        string
    )
    
def onlyAscii(string):
    '''
    Parlé -> Parle
    '''
    return unicodedata.normalize("NFKD",string).encode('ASCII','ignore').decode()

def lowerTiret(string):
    '''
    Mon super document_2.txt -> mon-super-document-2.txt
    '''
    return re.sub("[ _]", "-", string).lower()

def lowerUnderscore(string):
    '''
    Mon super document-2.txt -> mon_super_document_2.txt
    '''
    return re.sub("[ -]", "_", string).lower()

def chainConversions(*fonctions):
    def g(string):
        for f in fonctions:
            string = f(string)
        return string
    return g

QUESTIONS,REPONSES,RAPPEL,INCONNU = range(4)
ENONCES = QUESTIONS
CORRIGES = REPONSES
def mystring(num, numero_type):
    TYPES = ["","-reponses","-rappel"]
    return "seance-{}{}.pdf".format(str(num).zfill(2), TYPES[numero_type])

def matcher(regex,fonction_si_match):
    def g(string):
        obj = re.match(regex, string)
        return fonction_si_match(*obj.groups()) if obj else string
    return g

# Transforme "S1r.pdf" en "seance-01-reponses.pdf"
courtLong = matcher("^S([0-9]*)(r?)\.pdf$",
    lambda num,r: mystring(num, REPONSES if r == 'r' else QUESTIONS)
)

#Transforme rpqstp1.pdf en "seance-01-reponses.pdf"
physiqueQuantique = matcher("^(r?)pqstp([0-9]*)\.pdf$",
    lambda num,r: mystring(num, REPONSES if r == 'r' else QUESTIONS)
)

analyse_types = {1:ENONCES,2:CORRIGES,4:RAPPEL}
analyse = matcher("^anii([0-9]*)s([0-9]*)t([0-9]*)\.pdf$",
    lambda annee,num,letype: mystring(num, analyse_types.get(int(letype), INCONNU))
)

def cleanupEpisodes(name):
    '''
    Anything wat the hell S11e29 Wazzuuup.ext -> S11E29.ext
    Anything wat the hell.ext -> Anything wat the hell.ext 
    '''
    regex = ".*[Ss](\d+)[Ee](\d+).*\.(.*)$"
    m = re.match(regex,name)
    return "S{0}E{1}.{2}".format(*m.groups()) if m else name

def renameFile(fonction, ancien, force=False, preview=False):
    '''
    takes a function filename -> filename and applies the transformation
    on the supplied file
    Optional Arguments:
       force : rename without prompt
       preview : only show what would be done
    '''
    try:
        nouveau = fonction(ancien)
        if preview:
            print(('{}\n[ == ]' if ancien == nouveau else '{}\n[ -> ] {}').format(ancien,nouveau))
        elif nouveau != ancien:
            if force or input("{} -> {} (O/n) ?".format(ancien,nouveau)).lower() in ('', 'o'):
                os.rename(ancien,nouveau)
    except Exception as e:
        print("Exception during {} : {}".format(ancien,e))
        
def renameInDir(fonction, directory='.', **kwargs):
    '''
    takes a function filename -> filename and applies the transformation
    in the supplied directory
    Optional Arguments: see renameFile
    '''
    for ancien in os.listdir(directory):
        renameFile(fonction, ancien, **kwargs)

if __name__ == '__main__':
    import argparse
    import os.path

    func_names = 'pourcentEncoded htmlSequence lowerTiret lowerUnderscore onlyAscii'.split()
    help_func = '\n'.join(name + ':' + globals()[name].__doc__ or '' for name in func_names)
    
    parser = argparse.ArgumentParser(description='Rename files or directories')

    parser.add_argument(
        'targets',
        nargs='*',
        default=['.'],
        help='Files or dirs to rename'
    )
    
    parser.add_argument(
        '--functions',
        nargs='+',
        choices=func_names,
        help=''
    )
    
    parser.add_argument('--force', action='store_true', help='')
    parser.add_argument('--preview', action='store_true', help='')
    
    args = parser.parse_args()
    pprint(vars(args))
    if args.functions:
        funcs = [globals()[name] for name in args.functions]
        func = chainConversions(*funcs)
        for target in args.targets:
            if os.path.isdir(target):
                renameInDir(func, target, force=args.force, preview=args.preview)
            elif os.path.isfile(target):
                renameFile(func, target, force=args.force, preview=args.preview)
            else:
                print('{} must be a file or directory'.format(target))

