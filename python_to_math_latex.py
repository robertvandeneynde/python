class T:
    def latex(self):
        return ''
    def __repr__(self):
        return self.latex()
    
class BinOp(T):
    def __init__(self, a, b, op):
        self.a = a
        self.b = b
        self.op = op
        
    def latex(self):
        return self.a.latex() + ' ' + self.op + ' ' + self.b.latex()
    
    def __truediv__(self, other):
        return Frac(self, other)
    
    def __mul__(self, other):
        return Product(self, other)
    
    def __add__(self, other):
        return BinOp(self, other, '+')
    
    def __sub__(self, other):
        return BinOp(self, other, '-')
    
class Frac(BinOp):
    def __init__(self, a, b):
        super().__init__(a, b, '')

    def latex(self):
        return '\\frac{' + self.a.latex() + '}{' + self.b.latex() + '}'

class Product(BinOp):
    NOTHING = ''
    CDOT = r'\cdot'
    TIMES = r'\times'
    SPACE = r'\,'

    DEFAULT = NOTHING # can be changed

    @classmethod
    def setdefault(cls, x):
        cls.DEFAULT = x

    def __init__(self, a, b, type=None):
        if type is None:
            type = self.DEFAULT
        super().__init__(a, b, type)

    def latex(self):
        return self.a.latex() + ' ' + self.op + ' ' * bool(self.op) + self.b.latex()

class Term(BinOp):
    def __init__(self, x):
        self.x = x
    
    def latex(self):
        return self.x

def populate_terms(*items, dictionary=None):
    if dictionary is None:
        dictionary = globals()
    for item in items:
        dictionary[item] = Term(item)

def test():
    assert Term('V_out').latex() == 'V_out'
    assert Term(r'V_{\text{out}}').latex() == r'V_{\text{out}}'

    V_out = Term(r'V_{\text{out}}')
    assert V_out.latex() == r'V_{\text{out}}'

    assert Frac(Term('x'), Term('y')).latex() == '\\frac{x}{y}'

    assert (Term('x') / Term('y')).latex() == '\\frac{x}{y}'

