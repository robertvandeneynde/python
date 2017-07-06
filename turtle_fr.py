from turtle import *

def translate(*args):
    if len(args) < 2:
        raise TypeError('Missing arguments')
    
    frs, en = args[:-1], args[-1]
    
    for fr in frs:
        globals()[fr] = globals()[en]
        setattr(Turtle, fr, getattr(Turtle, en))

def translate_color(*args):
    if len(args) < 2:
        raise TypeError('Missing arguments')
    
    frs, en = args[:-1], args[-1]
    
    for fr in frs:
        globals()[fr] = make_color_global(en)
        setattr(Turtle, fr, make_color_method(en))

def add_numbers(D, n=4):
    for x,y in dict(D).items():
        for i in range(n):
            D[x + str(i+1)] = y + str(i+1)

COULEURS_SIMPLE = {
    "snow",
    "ghost white",
    "white smoke",
    "gainsboro",
    "floral white",
    "old lace",
    "linen",
    "antique white",
    "papaya whip",
    "blanched almond",
    "bisque",
    "peach puff",
    "navajo white",
    "moccasin",
    "cornsilk",
    "ivory",
    "lemon chiffon",
    "seashell",
    "honeydew",
    "mint cream",
    "azure",
    "alice blue",
    "lavender",
    "lavender blush",
    "misty rose",
    "white",
    "black",
    "dark slate gray",
    "dim gray",
    "slate gray",
    "light slate gray",
    "gray",
    "light grey",
    "midnight blue",
    "navy",
    "cornflower blue",
    "dark slate blue",
    "slate blue",
    "medium slate blue",
    "light slate blue",
    "medium blue",
    "royal blue",
    "blue",
    "dodger blue",
    "deep sky blue",
    "sky blue",
    "light sky blue",
    "steel blue",
    "light steel blue",
    "light blue",
    "powder blue",
    "pale turquoise",
    "dark turquoise",
    "medium turquoise",
    "turquoise",
    "cyan",
    "light cyan",
    "cadet blue",
    "medium aquamarine",
    "aquamarine",
    "dark green",
    "dark olive green",
    "dark sea green",
    "sea green",
    "medium sea green",
    "light sea green",
    "pale green",
    "spring green",
    "lawn green",
    "green",
    "chartreuse",
    "medium spring green",
    "green yellow",
    "lime green",
    "yellow green",
    "forest green",
    "olive drab",
    "dark khaki",
    "khaki",
    "pale goldenrod",
    "light goldenrod yellow",
    "light yellow",
    "yellow",
    "gold",
    "light goldenrod",
    "goldenrod",
    "dark goldenrod",
    "rosy brown",
    "indian red",
    "saddle brown",
    "sienna",
    "peru",
    "burlywood",
    "beige",
    "wheat",
    "sandy brown",
    "tan",
    "chocolate",
    "firebrick",
    "brown",
    "dark salmon",
    "salmon",
    "light salmon",
    "orange",
    "dark orange",
    "coral",
    "light coral",
    "tomato",
    "orange red",
    "red",
    "hot pink",
    "deep pink",
    "pink",
    "light pink",
    "pale violet red",
    "maroon",
    "medium violet red",
    "violet red",
    "magenta",
    "violet",
    "plum",
    "orchid",
    "medium orchid",
    "dark orchid",
    "dark violet",
    "blue violet",
    "purple",
    "medium purple",
    "thistle",
}

# Colors that do not have variant 4
COULEURS_NON_4 = {
 'alice blue',
 'beige',
 'black',
 'blanched almond',
 'blue violet',
 'cornflower blue',
 'dark green',
 'dark khaki',
 'dark salmon',
 'dark slate blue',
 'dark turquoise',
 'dark violet',
 'dim gray',
 'floral white',
 'forest green',
 'gainsboro',
 'ghost white',
 'gold',
 'gray',
 'green yellow',
 'lavender',
 'lawn green',
 'light coral',
 'light goldenrod yellow',
 'light grey',
 'light sea green',
 'light slate blue',
 'light slate gray',
 'lime green',
 'linen',
 'medium aquamarine',
 'medium blue',
 'medium sea green',
 'medium slate blue',
 'medium spring green',
 'medium turquoise',
 'medium violet red',
 'midnight blue',
 'mint cream',
 'moccasin',
 'navy',
 'old lace',
 'pale goldenrod',
 'papaya whip',
 'peru',
 'powder blue',
 'saddle brown',
 'sandy brown',
 'violet',
 'white',
 'white smoke',
 'yellow green'
}

def camelToSpace(x): import re; return re.sub('[A-Z]', lambda m:' ' + m.group(0).lower(), x).strip()
def spaceToCamel(x): import re; return re.sub('(\\s+|^)([a-z])', lambda m:m.group(2).upper(), x)

# colors that have the variant '4'
# beware, multi word colors like "orange red" have OrangeRed1 ... OrangeRed4
COULEURS_4 = {
    'snow',
    'seashell',
    'antique white',
    'bisque',
    'peach puff',
    'navajo white',
    'lemon chiffon',
    'cornsilk',
    'ivory',
    'honeydew',
    'lavender blush',
    'misty rose',
    'azure',
    'slate blue',
    'royal blue',
    'blue',
    'dodger blue',
    'steel blue',
    'deep sky blue',
    'sky blue',
    'light sky blue',
    'slate gray',
    'light steel blue',
    'light blue',
    'light cyan',
    'pale turquoise',
    'cadet blue',
    'turquoise',
    'cyan',
    'dark slate gray',
    'aquamarine',
    'dark sea green',
    'sea green',
    'pale green',
    'spring green',
    'green',
    'chartreuse',
    'olive drab',
    'dark olive green',
    'khaki',
    'light goldenrod',
    'light yellow',
    'yellow',
    'goldenrod',
    'dark goldenrod',
    'rosy brown',
    'indian red',
    'sienna',
    'burlywood',
    'wheat',
    'tan',
    'chocolate',
    'firebrick',
    'brown',
    'salmon',
    'light salmon',
    'orange',
    'dark orange',
    'coral',
    'tomato',
    'orange red',
    'red',
    'deep pink',
    'hot pink',
    'pink',
    'light pink',
    'pale violet red',
    'maroon',
    'violet red',
    'magenta',
    'orchid',
    'plum',
    'medium orchid',
    'dark orchid',
    'purple',
    'medium purple',
    'thistle',
}
# add_numbers(COULEURS_4, 4)

COULEURS = {
    'rouge': 'red',
    'bleu': 'blue',
    'vert': 'green',
    'jaune': 'yellow',
    'brun': 'brown',
    'orange': 'orange',
    'corail': 'coral',
    'violet': 'violet',
}
add_numbers(COULEURS, 4)

GRIS = {'gris': 'gray'}
add_numbers(GRIS, 99)

COULEURS.update(GRIS)

def make_color_function(func):
    return lambda *args: func(*tuple(COULEURS.get(x,x) for x in args))

def make_color_global(funcname):
    return make_color_function(globals()[funcname])

def make_color_method(funcname):
    return lambda self, *args: make_color_function(getattr(self, funcname))(*args)

ALIAS = [
    'av go avancer forward',
    're reculer back',
    'lc levercrayon penup',
    'dc descendrecrayon pendown',
    'bc baissercrayon pendown',
    'tg gauche left', 
    'td droite right', 
]

ALIAS_COLOR = [
    'couleur color',
    'couleurremplissage fillcolor',
    'couleurcrayon pencolor',
]

for l in ALIAS:
    translate(*l.split())

for l in ALIAS_COLOR:
    translate_color(*l.split())
