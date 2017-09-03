import os

def couleur01(r,g,b):
    """
    >>> couleur01(255,0,204)
    [1.0, 0.0, 0.8]
    """
    return [r/255, g/255, b/255]

def couleur(s):
    """
    >>> couleur('#ff0000')
    [1, 0, 0]
    >>> couleur('#f00')
    [1, 0, 0]
    >>> couleur('yellow')
    [1, 1, 0]
    >>> importColors('color.txt')
    >>> couleur('fancystuff')
    [1, 1, 0.8]
    """
    if s in COLOR_DATA:
        r,g,b = COLOR_DATA[s]
        return couleur01(r,g,b)
    
    if s.startswith('#'):
        s = s[1:]
    
    if len(s) == 6: # "ffc030"
        r,g,b = s[0:2], s[2:4], s[4,6]
    elif len(s) == 3: # "fc9"
        r,g,b = s
        r,g,b = r * 2, g * 2, b * 2
    else:
        raise ValueError('string {} is not a color'.format(s))
    return couleur01(int(r, 16), int(g, 16), int(b, 16))

COLOR_DATA = {
    'yellow':     (255, 255, 0),  
    'honeydew':   (240, 255, 240),
    'magenta':    (255, 0,   255),
    'cornsilk':   (255, 248, 220),
    'peru':       (205, 133, 63), 
    'black':      (0,   0,   0),  
    'linen':      (250, 240, 230),
    'brown':      (165, 42,  42), 
    'cyan':       (0,   255, 255),
    'coral':      (255, 127, 80), 
    'orchid':     (218, 112, 214),
    'orange':     (255, 165, 0),  
    'aquamarine': (127, 255, 212),
    'white':      (255, 255, 255),
    'turquoise':  (64,  224, 208),
    'green':      (0,   255, 0),  
    'blue':       (0,   0,   255),
    'chocolate':  (210, 105, 30), 
    'lavender':   (230, 230, 250),
    'moccasin':   (255, 228, 181),
    'seashell':   (255, 245, 238),
    'khaki':      (240, 230, 140),
    'firebrick':  (178, 34,  34), 
    'maroon':     (176, 48,  96), 
    'tan':        (210, 180, 140),
    'gainsboro':  (220, 220, 220),
    'violet':     (238, 130, 238),
    'pink':       (255, 192, 203),
    'burlywood':  (222, 184, 135),
    'azure':      (240, 255, 255),
    'tomato':     (255, 99,  71), 
    'grey':       (190, 190, 190),
    'thistle':    (216, 191, 216),
    'gray':       (190, 190, 190),
    'gold':       (255, 215, 0),  
    'bisque':     (255, 228, 196),
    'beige':      (245, 245, 220),
    'wheat':      (245, 222, 179),
    'chartreuse': (127, 255, 0),  
    'red':        (255, 0,   0),  
    'snow':       (255, 250, 250),
    'ivory':      (255, 255, 240),
    'plum':       (221, 160, 221),
    'purple':     (160, 32,  240),
    'goldenrod':  (218, 165, 32), 
    'navy':       (0,   0,   128),
    'sienna':     (160, 82,  45), 
    'salmon':     (250, 128, 114),
}

def importColors(filename):
    if os.path.isfile(filename):
        with open(filename) as f:
            for l in f:
                try:
                    l = l.split()
                    name = ' '.join(l[:-3])
                    r,b,g = l[-3:]
                    couleur.DATA[name] = int(r) / 255, int(g) / 255, int(b) / 255
                except:
                    pass
                
def couleurHexNumber(x):
    """
    >>> couleurHexNumber(0xff0000)
    [1, 0, 0]
    """
    return couleur01((x & 0xFF0000) >> 16, (x & 0xFF00) >> 8, x & 0xFF)

def couleurHexNumberAlpha(x):
    """
    >>> couleurHexNumberAlpha(0xff0000ff)
    [1, 0, 0, 1]
    """
    r,g,b,a = (x & 0xFF000000) >> 8*3, (x & 0xFF0000) >> 8*2, (x & 0xFF0000) >> 8*2, x & 0xFF
    return [r / 255, g / 255, b / 255, a / 255]
