'''
TODO : add wraps component to those concepts 
'''
def _test():

    # as decorator
    @infix
    def f(X,Y):
        return sum(x*y for x,y in zip(X,Y))

    assert 32 == f((1,2,3), (4,5,6))

    assert 32 == (1,2,3) |f| (4,5,6)
    assert 34 == 2 + (1,2,3) *f* (4,5,6)
    
    # fraction
    from fractions import Fraction
    frac = infix(Fraction)

    assert 1 == Fraction(1,3) * 3
    assert 1 == (1 |frac| 3) * 3 # parenthesis
    assert 1 == 1 /frac/ 3 * 3   # precedence
    assert 1 |frac| 9 == 1 /frac/ 3 / 3 # precedence
    assert 1 |frac| 9 == 1/frac/3 / 3   # other style

    # numpy
    try:
        import numpy as np
        dot = infix(np.dot)
        cross = infix(np.cross)

        assert 32 == (1,2,3) |dot| (4,5,6)
        assert -2 == (1,2) |cross| (3,4)
        assert all((0,0,-2) == (1,2,0) |cross| (3,4,0))
        
        # use correct symbol, for precedence.
        # for |dot| or |cross|, "*" seems a good idea
        assert 2 + (1,2,3) *dot* (4,5,6)
        
        vec_eq = infix(lambda A,B: all(A == B))
        assert (5,7,9) |vec_eq| (1,2,3) + (4,5,6)
        assert (0,0,-2) |vec_eq| (1,2,0) *cross* (3,4,0) # beware precedence

        if sys.version_info >= (3,5):
            matmul = operator.matmul
    except ImportError:
        pass # numpy is not installed, that's alright

    as_s = prefix(str)
    to_s = postfix(str)
    be_s = unary(str)
    
    @postfix
    def zfill4(string):
        return string.zfill(4)

    assert "5" == as_s | 5
    assert "5" == 5 | to_s
    assert "0005" == 5 | to_s | zfill4 # chaining
    assert "5" == be_s | 5
    assert "5" == 5 | be_s 

    import operator
    add = partially(operator.add)
    assert 2+7 == add(2,7)
    assert 2+7 == add[2](7)
    assert 2+7 == add[2][7]()

    @partiallyauto
    def my_py_func(x,y):
        return x + y
    
    add = partiallyauto(operator.add, 2) # required "2" because operator.add has no __code__ (no spec)
    assert 2+7 == add(2,7)
    assert 2+7 == add(2)(7)
    
    def indef(*args):
        return sum(args)

    add = partiallyauto(indef)
    assert 2+7+8 == add(2,7,8)()
    assert 2+7 == add(2,7)()
    assert 2+7+7+8 == add(2)(7)(7,8)()

    add = partiallymulti(indef)
    assert 1+2+7+8 == add[1][2,7,8]()
    assert 1+2+7+8+7+2 == add[1][2,7,8](7,2)
    
class base:
    def __init__(self, function):
        self.function = function
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

class infix(base):
    '''
    @infix # as decorator
    def f(X,Y):
        return sum(x*y for x,y in zip(X,Y))
    
    r = f((1,2,3), (4,5,6)) # simple call
    r = (1,2,3) |f| (4,5,6) # infix call

    r = 2 + (1,2,3) *f* (4,5,6)   # use * for precedence
    
    dot = infix(np.dot) # from existing function
    r = 2 + (1,2,3) *dot* (4,5,6) # clear syntax

    r = (1,2,3) |infix(np.dot)| (4,5,6) # one liner
    I = infix
    r = (1,2,3) |I(np.dot)| (4,5,6) # other style
    
    beware, ** is RTL
    '''
    
    def __ror__(self, other):
        return infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    
    # __div__ for py2 compability
    __radd__ = __rsub__ = __rmul__ = __rmatmul__ = __div__ = __rtruediv__ = __rfloordiv__ = __rmod__ = __pow__ = __rand__ = __rxor__ = __rlshift__\
        = __ror__
    
    __add__ = __sub__ = __mul__ = __matmul__ = __rdiv__ = __truediv__ = __floordiv__ = __mod__ = __rpow__ = __and__ = __xor__ = __rshift__\
        = __or__

class postfix(base):
    __radd__ = __rsub__ = __rmul__ = __rmatmul__ = __div__ = __rtruediv__ = __rfloordiv__ = __rmod__ = __pow__ = __rand__ = __rxor__ = __rlshift__\
        = __ror__\
        = base.__call__

class prefix(base):
    __add__ = __sub__ = __mul__ = __matmul__ = __rdiv__ = __truediv__ = __floordiv__ = __mod__ = __rpow__ = __and__ = __xor__ = __rshift__\
        = __or__\
        = base.__call__
    
class unary(postfix, prefix):
    pass

bothfix = unary

def _opmethod_base(method, cls):
    return property(lambda self: cls(_partial(method, self)))

def opmethod(method):
    '''
    class A:
        @opmethod
        def f(self, x):
            return self.p + x + 1
        def __init__(self, p):
            self.p = p
    a = A(8)
    m = a.f(1)  # simple call
    m = a.f | 1 # use postfixmethod
    m = 1 | a.f # use prefixmethod
    # NOT : a |f| 1 (calls function f) @see infixmethod
    '''
    return _opmethod_base(method, unary)

def prefixopmethod(method):
    return _opmethod_base(method, prefix)

def postfixopmethod(method):
    return _opmethod_base(method, postfix)

def infixmethod(methodname):
    '''
    append = infixmethod('append')
    L = []
    append(L, 5)
    L |append| 5
    
    # Don't do this :
    append = unary(list.append) # works, but does not apply on inheritance
    '''
    return infix(lambda self, param: getattr(self, methodname)(param))

def _unarymethod_base(methodname, cls):
    return cls(lambda self: getattr(self, methodname)())

def callmethod(methodname):
    '''
    keys = callmethod('keys')
    D = {'x': 1}
    print(keys(D))
    print(keys | D) # use postfixcallmethod to avoid this
    print(D | keys) # use prefixcallmethod to avoid this
    
    # not very practical if only used in (D | keys) notation (D.keys()) is better
    # but can be usefull to use keys(D) or keys | D
    '''
    return _unarymethod_base(methodname, unary)

def prefixcallmethod(methodname):
    return _unarymethod_base(methodname, prefix)

def postfixcallmethod(methodname):
    return _unarymethod_base(methodname, postfix)

from functools import partial as _partial, wraps as _wraps

curry = infix(_partial)
curry.__doc__

class partially(base):
    '''
    @partially
    def f(x,y,z):
        return x + y + z
    
    r = f(1,2,3)
    r = f[1](2,3)
    r = f[1][2][3]()
    # NOT: f[1,2] (which is give one argument : a tuple)
    '''
    def key(self, **kwargs):
        return partially(_partial(self, **kwargs))
    def val(self, *vals):
        return partially(_partial(self, **kwargs))
    def part(self, *args, **kwargs):
        return partially(_partial(self, *args, **kwargs))
    def __getitem__(self, item):
        return partially(_partial(self.function, item))

import inspect as _inspect

class partiallyauto(base):
    '''
    works only for methods with N fixed positional args
    
    @partiallyauto
    def f(x,y,z):
        return x + y + z
    
    r = f(1,2,3)
    r = f(1)(2)(3)
    r = f(1)(2,3)
    '''
    def __init__(self, function, N=None):
        base.__init__(self, function)
        
        try:
            spec = _inspect.getargspec(self.function)
        except TypeError:
            spec = None
        
        if spec:
            assert spec.keywords is None
            assert N is not None or not spec.defaults
            
        if N is not None:
            self.N = N
        else:
            if not spec or spec.varargs:
                self.N = 10 ** 5
            else:
                self.N = len(spec.args)
        
    def __call__(self, *args):
        if self.N - len(args) <= 0 or len(args) == 0:
            return base.__call__(self, *args)
        return partiallyauto(_partial(self.function, *args), N=self.N-len(args))

class partiallymulti(partially):
    ''' Beware, Does not work as expected for function that (may) take tuples !
    
    def f(x,y,z):
        return x + y + z
    
    r = f(1,2,3)
    r = f[1,2](3)
    r = f[1,2,3]()
    '''
    def __getitem__(self, item):
        if isinstance(item, tuple):
            return partiallymulti(_partial(self.function, *item))
        return partiallymulti(_partial(self.function, item))

import functools

@infix
def compose(*functions):
    """
    compose(hex, ord)(x) == hex(ord(x))
    """
    return functools.reduce(lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)), functions, lambda x: x)

circle = infix(compose) # (hex |circle| ord)(x) == hex(ord(x))
