"""
Always wanted to add custom operators ?
a = (1,2,3) /dot/ (4,5,6)  # a = 32

# works for existing functions, like numpy.dot
import numpy
dot = infix(numpy.dot)
a = (1,2,3) /dot/ (4,5,6)  # use as an infix
a = dot((1,2,3), (4,5,6))  # still works as a function

# or for custom functions as a decorator

@infix
def crunch(x,y):
    '''
    Do a super crunchy operation between two numbers.
    '''
    return x + 2 * y

a = 1 |crunch| 2  # a = crunch(1, 2)  # can use any binary operator like / | * % << >> (beware of ** that is right to left)
a = crunch(1, 2)  # still works
help(crunch.function)  # to get help about the initial function

## dot and cross product
import numpy
dot = infix(numpy.dot)

a = (1,2,3) /dot/ (4,5,6)  # use as an infix
a = (1,2,3) |dot| (4,5,6)  # can use any binary operator like / | + - * % << >> **... (beware of ** that is right to left)
r = 2 + (1,2,3) /dot/ (4,5,6)  # here "/" has priority over + like in normal python
r = 2 + (1,2,3) *dot* (4,5,6)  # for a dot PRODUCT, * seems logical
r = 2 + dot((1,2,3), (4,5,6))  # still works as a function

cross = infix(numpy.cross)
tau = (1,2) /cross/ (3,4)
Z = (1,2,3) /cross/ (4,5,6)

## using '|' for low priority
A + B |dot| C  # is parsed as (A + B) |dot| C

## fractions
from fractions import Fraction
frac = infix(Fraction)
a = 1 + 1 / 3       # floats are messy... 1.3333333333333333
a = 1 + 1 /frac/ 3  # just replace '/' by '/frac/' to use Fractions
b = 2 * (a + 3) /frac/ (a + 1)  # nicer complex expressions

## ranges, 2..5 in ruby ?
@infix
def inclusive(a,b):
    return range(a, b+1)

for i in 2 /inclusive/ 5:  # could also write |inclusive| or +inclusive+ or %inclusive% etc.
    print(i)  # 2 3 4 5

for i in inclusive(2, 5):  # can still be used as function
    print(i)  # 2 3 4 5
    
# range = infix(range)  # don't do that, it breaks code like isinstance(x, range).
exclusive = infix(range)  # now that's better

## isinstance (Java and Js instanceof)
isinstance = infix(isinstance)
assert 1 /isinstance/ int
assert [] /isinstance/ (list, tuple)
assert 1 / 2 |isinstance| float

## pipes:  postfix
@postfix
def no_zero(L):
    return [x for x in L if x != 0]

@postfix
def plus_one(L):
    return [x+1 for x in L]

Y = [1,2,7,0,2,0] |no_zero |plus_one
# Y == [2,3,8,3]
Y = plus_one(no_zero([1,2,7,0,2,0]))
# Y == [2,3,8,3]

## pipe factory
def filter_out(x):
    @postfix
    def f(L):
        return [y for y in L if y != x]
    return f

L = [1,2,7,0,2,0] | filter_out(0)

def mapwith(function):
    return postfix(lambda *its: map(function, *its))

s = '1 2 7 2'.split() | mapwith(int) | postfix(sum)  # s = 12 = sum(map(int, '1 2 7 2'.split()))

## unary, prefix, postfix
import math
fac = prefix(math.factorial)
x = fac(5)
x = 5-fac
x = 5|fac
fac = postfix(math.factorial)
x = fac(5)
x = fac-5
x = fac|5
fac = unary(math.factorial)
x = fac(5)
x = fac-5
x = 5-fac

## power
h = unary(hex)
o = unary(ord)
s = h ** o ** 'A'  # s = '0x41'

## function compose (alias circle)
s = hex(ord('A'))  # s = '0x41'

from funcoperators import compose
display = hex /compose/ ord
s = display('A')  # s = '0x41'

f = hex *circle* ord  # circle = compose

## partial syntax
def f(x,y):
    return x - y

from funcoperators import curry
g = f /curry/ 5
y = f(2)  # y = 3

from funcoperators import partially
@partially
def f(x,y,z):
    return x - y + 2 * z

r = f(1,2,3)
r = f[1](2,3)
r = f[1][2][3]()
# Notice that "f[1,2]" doesn't work because it gives only one argument: a tuple (@see partiallymulti)

g = f[1]  # gives positional arguments
g = f.val(1)  # gives positional arguments
g = f.key(z=3)  # gives keyword arguments
g = f.partial(1, z=3)  # gives positional and keyword arguments

# partiallyauto works only for methods with N fixed positional args

@partiallyauto
def f(x,y,z):
    return x - y + 2 * z

r = f(1,2,3)    # r = 6
r = f(1)(2)(3)  # r = 6
r = f(1)(2,3)   # r = 6
g = f(1)    # g = a function with two arguments 
r = g(2,3)  # r = 6
k = g(2)    # k = a function with one argument

# curry 
e = pow /curryleft/ 2  # e(x) = 2 ** x
y = e(5)  # y = 2 ** 5

s = pow /curryright/ 2  # s(x) = x ** 2
y = s(5)  # y = 5 ** 2)

p = infix(pow)  # p(x,y) = pow(x,y)
e = 2 / p  # e(x) = pow(2, x)
y = e(5)  # y = 2 ** 5

f = '{}/{}/{}'.format |curry| 1 | curry| 2
y = f(3)  # y = '1/2/3'

g = '{}/{}/{}'.format |curry| 1 |curry| 2 |curry| 3
y = g()  # '1/2/3'

# elipartial
tenexp = elipartial(pow, 10)  # = pow(10, something)
y = tenexp(2)  # 10 ** 2
square = elipartial(pow, ..., 2)  # = pow(something, 2)
y = square(5)  # 5 ** 2

# elicurry (alias with_arguments or deferredcall)
show = print |elicurry(1, ..., 3, sep='/')  # 'show' is 'print' with arguments '1, something, 3' and keyword argument 'sep="."'
show(2)  # prints 1/2/3

# see more examples in the test cases in source code

TODO: add Waiting for Left side like in pip install infix
TODO: figure out how to have help(infix(function)) prints help about function
"""
from __future__ import print_function  # for python2

__version__ = '1.1.3'
__author__ = 'Robert Vanden Eynde'

# __all__ = __all__

from functools import update_wrapper as _update_wrapper
import sys as _sys

import unittest

try:
    import numpy
    _NO_NUMPY = False
except ImportError:
    _NO_NUMPY = True
    
class _BasicTests(unittest.TestCase):
    def test_fundamentals(self):
        # as decorator
        @infix
        def f(X,Y):
            return sum(x*y for x,y in zip(X,Y))

        self.assertEqual(32, f((1,2,3), (4,5,6)))

        self.assertEqual(32, (1,2,3) |f| (4,5,6))
        self.assertEqual(34, 2 + (1,2,3) *f* (4,5,6))
        
        # fraction
        from fractions import Fraction
        frac = infix(Fraction)

        self.assertEqual(1, Fraction(1,3) * 3)
        self.assertEqual(1, (1 |frac| 3) * 3)  # parenthesis
        self.assertEqual(1, 1 /frac/ 3 * 3)    # precedence
        self.assertEqual(1 |frac| 9, 1 /frac/ 3 / 3)  # precedence
        self.assertEqual(1 |frac| 9, 1/frac/3 / 3)    # other style
    
    @unittest.skipIf(_NO_NUMPY, 'numpy must be installed')
    def test_numpy(self):
        import numpy
        
        dot = infix(numpy.dot)
        cross = infix(numpy.cross)
        array = numpy.array

        self.assertEqual(32, (1,2,3) |dot| (4,5,6))
        self.assertEqual(-2, (1,2) |cross| (3,4))
        self.assertTrue(all((0,0,-2) == (1,2,0) |cross| (3,4,0)))
        
        # use correct symbol, for precedence.
        # for |dot| or |cross|, "*" seems a good idea
        self.assertEqual(34, 2 + (1,2,3) *dot* (4,5,6))
        
        vec_eq = infix(lambda A,B: all(A == B))
        self.assertTrue((5,7,9) |vec_eq| array((1,2,3)) + array((4,5,6)))
        self.assertTrue((0,0,-2) |vec_eq| (1,2,0) *cross* (3,4,0))  # beware precedence

        with self.assertRaises(Exception):
            # numpy.array has a "|" operator!
            array((1,2,3)) + 5 |postfix(tuple)  # the left operand is called
        prefix(tuple)| array((1,2,3)) + 5  # the left operand is called

    def test_unary(self):
        to_s = postfix(str)
        as_s = prefix(str)
        be_s = unary(str)
        
        @postfix
        def zfill4(string):
            return string.zfill(4)

        self.assertEqual("5", 5 | to_s)
        self.assertEqual("0005", 5 | to_s | zfill4)  # chaining
        self.assertEqual("5", as_s | 5)
        self.assertEqual("5", 5 | be_s)
        self.assertEqual("5", be_s | 5)
        
        with self.assertRaises(Exception):
            to_s | 5 
            
        with self.assertRaises(Exception):
            5 | as_s

        import operator
        add = partially(operator.add)
        self.assertEqual(2+7, add(2,7))
        self.assertEqual(2+7, add[2](7))
        self.assertEqual(2+7, add[2][7]())

        @partiallyauto
        def my_py_func(x,y):
            return x + y
        
        add = partiallyauto(operator.add, 2)  # required "2" because operator.add has no __code__ (no spec)
        self.assertEqual(2+7, add(2,7))
        self.assertEqual(2+7, add(2)(7))
        
        def indef(*args):
            return sum(args)

        add = partiallyauto(indef)
        self.assertEqual(2+7+8, add(2,7,8)())
        self.assertEqual(2+7, add(2,7)())
        self.assertEqual(2+7+7+8, add(2)(7)(7,8)())

        add = partiallymulti(indef)
        self.assertEqual(1+2+7+8, add[1][2,7,8]())
        self.assertEqual(1+2+7+8+7+2, add[1][2,7,8](7,2))

    def test_variety(self):
        f = infix(lambda x,y:x-y)
        
        self.assertEqual(5 +f+ 2, 3)
        self.assertEqual(5 -f- 2, 3)
        self.assertEqual(5 *f* 2, 3)
        self.assertEqual(5 /f/ 2, 3)
        
        self.assertEqual(5 |f| 2, 3)
        self.assertEqual(5 &f& 2, 3)
        self.assertEqual(5 ^f^ 2, 3)
        
        self.assertEqual(5 << f << 2, 3)
        self.assertEqual(5 >> f >> 2, 3)
        
        self.assertEqual(5 **f** 2, -3)
    
    def test_pow(self):
        """
        ** is right to left, allowing hex(ord(x))
        to be written hex ** ord ** x
        or using postfix
        """
        h = unary(hex)
        o = unary(ord)
        self.assertEqual(h(o('a')), hex(ord('a')))
        self.assertEqual(h ** o ** 'a', hex(ord('a')))
        
        with self.assertRaises(Exception):
            h | o | 'a'

        f = infix(lambda x,y:x-y)
        self.assertEqual(5 **f** 2, -3)
    
    def test_pow_prefix(self):
        h = prefix(hex)
        o = prefix(ord)
        
        self.assertEqual(h(o('a')), hex(ord('a')))
        self.assertEqual(h ** o ** 'a', hex(ord('a')))
        
        with self.assertRaises(Exception):
            h | o | 'a'

    def test_shift(self):
        h = infix(lambda x,y:x - y)
        self.assertEqual(5 << h << 2, 3)
        self.assertEqual(5 >> h >> 2, 3)

        g = postfix(lambda x:x+1)
        self.assertEqual(1 << g, 2)
        self.assertEqual(1 >> g, 2)
        
        with self.assertRaises(Exception):
            g << 1
            g >> 1

        h = prefix(lambda x:x+1)
        self.assertEqual(h << 1, 2)
        self.assertEqual(h >> 1, 2)
        
        with self.assertRaises(Exception):
            1 << h
            1 >> h
    
    def test_curry(self):
        e = pow /curryleft/ 2  # e(x) = 2 ** x
        self.assertEqual(e(5), 2 ** 5)
        
        s = pow /curryright/ 2  # s(x) = x ** 2
        self.assertEqual(s(5), 5 ** 2)
        
        f = '{}/{}/{}'.format |curry| 1 | curry| 2
        self.assertEqual(f(3), '1/2/3')
        
        g = '{}/{}/{}'.format |curry| 1 |curry| 2 |curry| 3
        self.assertEqual(g(), '1/2/3')
    
    def test_not_enough(self):
        show = print | deferredcall(1, ..., 3, sep='/')
        with self.assertRaises(TypeError):
            show()
    
    def test_eli(self):
        f1 = lambda x: x ** 2
        f2 = elipartial(pow, ..., 2)
        self.assertTrue(all(f1(x) == f2(x) for x in range(-5,5)))
        
        tenexp = elipartial(pow, 10)  # = pow(10, something)
        self.assertEqual(tenexp(2), 100)
        
        square = elipartial(pow, ..., 2)  # = pow(something, 2)
        self.assertEqual(square(5), 25)
        
        self.assertEqual(elipartial(pow, ..., 2)(5), 5 ** 2)
        self.assertEqual(elipartial(pow, 2, ...)(5), 2 ** 5)
        self.assertEqual(elipartial('{}/{}/{}'.format, ..., 2, ...)(1,3), '1/2/3')
        
        f1 = lambda x: pow(2, x)
        f4 = pow |deferredcall(2, ...)
        f2 = pow |latercall(2, ...)
        f3 = pow |elicurryargs| (2, ...)
        self.assertTrue(all(f1(x) == f2(x) == f3(x) == f4(x) for x in range(-5,5)))
        
        self.assertIs(elicurry, latercall)
        self.assertIs(elicurry, deferredcall)
        
        square = pow /elicurryargs/ (..., 2)  # square(x) = x ** 2
        self.assertEqual(square(5), 5 ** 2)
        
        square = pow |elicurry(..., 2)  # square(x) = x ** 2
        self.assertEqual(square(5), 5 ** 2)
        
        square = pow |with_arguments(..., 2)  # square(x) = x ** 2
        self.assertEqual(square(5), 5 ** 2)
        
        square = pow |deferredcall(..., 2)  # square(x) = x ** 2
        self.assertEqual(square(5), 5 ** 2)
        
        self.assertIs(elicurry, with_arguments)
        
        gen = pow |with_arguments(2, 5)  # square(x) = x ** 2
        self.assertEqual(gen(), 2 ** 5)
        
        point = '{}/{}/{}'.format |elicurryargs| (..., 2)
        self.assertEqual(point(1,3), '1/2/3')
        
        point = '{}/{}/{}'.format |elicurryargs| (..., 2, ...)
        self.assertEqual(point(1,3), '1/2/3')
        
        def show(*args, **kwargs):
            return (args, kwargs)
        
        g = show | elicurry(1, ..., 3, sep='/')
        self.assertEqual(g(2), ((1,2,3), {'sep': '/'}))
        
        h = show | with_arguments(1, ..., 3, sep='/')
        self.assertEqual(h(2), ((1,2,3), {'sep': '/'}))
        
        self.assertIs(add_args, elicurryargs)
        self.assertIs(with_arguments, elicurry)
    
    def test_wraps(self):
        
        def f(x,y):
            """
            >>> f(5,2)
            3
            """
            return x - y
        
        @infix
        def g(x,y):
            """
            >>> f(5,2)
            3
            """
            return x - y
        
        h = infix(f)
        k = infix(g)
        
        self.assertEqual(f.__doc__, g.__doc__)
        self.assertEqual(f.__doc__, h.__doc__)
        self.assertEqual(f.__doc__, k.__doc__)
    
    def test_partiallybase(self):
        @bracket
        def f(x,y,z):
            return x - y + 2 * z
        
        g = f[..., 2]
        self.assertEqual(g(1,3), 5)
        
        with self.assertRaises(Exception):
            g(1)
        
        g = f[..., 2, ...]
        self.assertEqual(g(1,3), 5)
        
        with self.assertRaises(Exception):
            g(1)
            
        self.assertIs(bracket, elipartiallymulti)
            
    def test_partiallymulti(self):
        @partially
        def sum_plus(a_tuple, constant):
            return sum(a_tuple) + constant
        
        self.assertEqual(sum_plus((1,2,3), 10), 16)
        g = sum_plus[1,2,3]
        self.assertEqual(g(10), 16)
        
        @partially
        def f(x,y,z):
            return x - y + 2 * z
        
        with self.assertRaises(Exception):
            g = f[1,2]
            g(3)
    
class base:
    def __init__(self, function):
        self.function = function
        _update_wrapper(self, self.function)
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self):
        return repr(self.function)


class infix(base):
    """
    @infix  # as decorator
    def f(X,Y):
        return sum(x*y for x,y in zip(X,Y))
    
    r = f((1,2,3), (4,5,6))  # simple call
    r = (1,2,3) /f/ (4,5,6)  # infix call, can use any binary operator, like /, |, *, <<, ^, ...
    # if used with **, beware, it's RightToLeft (RTL): a ** b ** c == a ** (b ** c)

    r = 2 + (1,2,3) *f* (4,5,6)  # "*" has higher precedence than "+"
    
    dot = infix(np.dot)  # from existing function (recommended)
    r = 2 + (1,2,3) *dot* (4,5,6)  # clear syntax, for dot product, "*" makes sense
    """
    
    def __ror__(self, other):
        return infix(lambda x, self=self, other=other: self.function(other, x))

    def __or__(self, other):
        return self.function(other)
    
    # __div__ for py2 compability
    __radd__ = __rsub__ = __rmul__ = __rmatmul__ = __div__ = __rtruediv__ = __rfloordiv__ = __rmod__ = __pow__ = __rand__ = __rxor__ = __rlshift__ = __rrshift__\
        = __ror__
    
    __add__ = __sub__ = __mul__ = __matmul__ = __rdiv__ = __truediv__ = __floordiv__ = __mod__ = __rpow__ = __and__ = __xor__ = __rshift__ = __lshift__\
        = __or__

class postfix(base):
    __radd__ = __rsub__ = __rmul__ = __rmatmul__ = __div__ = __rtruediv__ = __rfloordiv__ = __rmod__ = __rpow__ = __rand__ = __rxor__ = __rlshift__ = __rrshift__\
        = __ror__\
        = base.__call__

to = postfix

class prefix(base):
    __add__ = __sub__ = __mul__ = __matmul__ = __rdiv__ = __truediv__ = __floordiv__ = __mod__ = __pow__ = __and__ = __xor__ = __rshift__ = __lshift__\
        = __or__\
        = base.__call__

class unary(postfix, prefix):
    pass

bothfix = unary

def _opmethod_base(method, cls):
    return property(lambda self: cls(_partial(method, self)))

def opmethod(method):
    """
    >>> class A:
    ...    @opmethod
    ...    def f(self, x):
    ...        return self.p + x + 1
    ...    def __init__(self, p):
    ...        self.p = p
    
    >>> a = A(8)
    >>> a.f(1)   # simple call
    10
    >>> a.f | 1  # use postfixmethod instead of opmethod if you only want this behavior
    10
    >>> 1 | a.f  # use prefixmethod instead of opmethod if you only want this behavior
    10
    >>> # Notice that "a |f| 1" doesn't work because it calls function f (@see infixmethod)
    """
    return _opmethod_base(method, unary)

def prefixopmethod(method):
    return _opmethod_base(method, prefix)

def postfixopmethod(method):
    return _opmethod_base(method, postfix)

def infixmethod(methodname):
    """
    append = infixmethod('append')
    L = []
    append(L, 5)
    L |append| 5
    
    # Don't do this:
    append = infix(list.append)  # works, but does not apply on inheritance
    """
    return infix(lambda self, param: getattr(self, methodname)(param))

def _unarymethod_base(methodname, cls):
    return cls(lambda self: getattr(self, methodname)())

def callmethod(methodname):
    """
    keys = callmethod('keys')
    D = {'x': 1}
    print(keys(D))
    print(keys | D)  # use postfixcallmethod if you don't want this behavior
    print(D | keys)  # use prefixcallmethod if you don't want this behavior
    
    # not very practical if only used in the parenthesized (D | keys) notation, in that case D.keys() is better
    # but can be usefull to use keys(D) or keys | D
    """
    return _unarymethod_base(methodname, unary)

def prefixcallmethod(methodname):
    return _unarymethod_base(methodname, prefix)

def postfixcallmethod(methodname):
    return _unarymethod_base(methodname, postfix)

from functools import partial as _partial

curry = infix(_partial)

@infix
def curryleft(function, arg):
    """
    # Only works with functions with two arguments, otherwise, choose curry
    >>> e = pow /curryleft/ 2  # e(x) = 2 ** x
    >>> e(5)  # 2 ** 5
    32
    """
    return lambda x: function(arg, x)

@infix
def curryright(function, arg):
    """
    >>> e = pow /curryright/ 2  # e(x) = x ** 2
    >>> e(5)  # 5 ** 2
    25
    """
    return lambda x: function(x, arg)

class partially(base):
    """
    >>> @partially
    ... def f(x,y,z):
    ...     return x - y + 2 * z
    
    >>> f(1,2,3)
    5
    >>> g = f[1]
    >>> g(2,3)
    5
    >>> f[1](2,3)
    5
    >>> f[1][2][3]()
    5
    >>> # Notice that "f[1,2]" doesn't work because it gives only one argument: a tuple (@see partiallymulti)
    >>> # If you don't like "[]", there is also a syntax with methods
    >>> g = f.val(1)  # provide the value 1
    >>> g(2,3)
    5
    >>> g = f.val(1, 2) # provide the values 1, 2
    >>> g(3)
    5
    >>> # keyword argument are nice too 
    >>> f(x=1, y=2, z=3)
    5
    >>> g = f.key(y=2)  # provide key argument y=2
    >>> g(x=1, z=3)
    5
    >>> g = f.partial(1, z=3)  # provide positional arguments 1, and keyword argument z=3
    >>> g(2)
    5
    >>> # f.partial(1) also aliases f.part(1), f.given(1), f.assuming(1), f.where(1)
    >>> g = f.val(1).key(z=3)  # provide positional arguments 1, and keyword argument z=3
    >>> g(2)
    5
    >>> myprint = partially(print).key(sep="/")
    >>> myprint(1,2,3)
    1/2/3
    >>> from functools import partial
    >>> myprint = partial(print, sep="/")
    >>> myprint(1,2,3)
    1/2/3
    """
    def key(self, **kwargs):
        return partially(_partial(self, **kwargs))

    def val(self, *vals):
        return partially(_partial(self, *vals))

    def partial(self, *args, **kwargs):
        return partially(_partial(self, *args, **kwargs))

    part = assuming = given = where = partial
    
    def __getitem__(self, item):
        return partially(_partial(self.function, item))

import inspect as _inspect

class partiallyauto(base):
    """
    Works only for methods with N fixed positional args
    
    >>> @partiallyauto
    ... def f(x,y,z):
    ...    return x - y + 2 * z
    
    >>> f(1,2,3)
    5
    >>> g = f(1)
    >>> g(2,3)
    5
    >>> f(1)(2,3)
    5
    >>> f(1)(2)(3)
    5
    """
    def __init__(self, function, N=None):
        base.__init__(self, function)
        
        try:
            if _sys.version_info[0] == 2:
                spec = _inspect.getargspec(self.function)
            else:
                spec = _inspect.getfullargspec(self.function)
        except TypeError:
            spec = None
        
        if spec:
            if _sys.version_info[0] == 2:
                assert spec.keywords is None
            else:
                assert spec.kwonlyargs == [] and spec.kwonlydefaults is None
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
    """ Beware, Does not work as expected for function that (may) take tuples !
    
    >>> @partiallymulti
    ... def f(x,y,z):
    ...     return x - y + 2 * z
    
    >>> f(1,2,3)
    5
    >>> g = f[1,2]
    >>> g(3)
    5
    >>> f[1,2](3)
    5
    >>> f[1,2,3]()
    5
    """
    def __getitem__(self, item):
        if isinstance(item, tuple):
            return partiallymulti(_partial(self.function, *item))
        return partiallymulti(_partial(self.function, item))


import functools

@infix
def compose(*functions):
    """
    compose(hex, ord)(x) == hex(ord(x))
    compose(hex, lambda x:1+x, ord)(x) = hex(1+ord(x))
    """
    return functools.reduce(lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)), functions, lambda x: x)

circle = compose  # (hex *circle* ord)(x) == hex(ord(x))

def elipartial(function, *args, **kwargs):
    """
    >>> tenexp = elipartial(pow, 10)  # = pow(10, something)
    >>> tenexp(2)
    100
    >>> square = elipartial(pow, ..., 2)  # = pow(something, 2)
    >>> square(5)
    25
    >>> elipartial(pow, ..., 2)(5)  # 5 ** 2
    25
    >>> elipartial(pow, 2, ...)(5)  # 2 ** 5
    32
    >>> elipartial('{}/{}/{}'.format, ..., 2, ...)(1,3)
    '1/2/3'
    >>> from __future__ import print_function
    >>> show = elipartial(print, 1, ..., 3, sep='/')
    >>> try: show()
    ... except TypeError:
    ...     print('Error')
    ... 
    Error
    >>> show(2)
    1/2/3
    """
    
    def newfunc(*fargs, **fwargs):
        itfargs = iter(fargs)
        
        def get_next():
            try:
                return next(itfargs)
            except StopIteration:
                raise TypeError('Not enough arguments, Ellipsis still in elipartial call.')
        
        # beware, generators can't raise StopIteration, so, don't do "newargsbase = tuple(arg if arg is not Ellipsis else next(itfargs) for arg in args)"
        
        newargsbase = tuple(arg if arg is not Ellipsis else get_next() for arg in args)
        remaining = tuple(itfargs)
        
        newargs = newargsbase + remaining
        
        newkeywords = kwargs.copy()
        newkeywords.update(fwargs)
        
        return function(*newargs, **newkeywords)
    
    # @functools.wraps(function) is not exactly what we want
    # so we manually call update_wrapper job
    WRAPPER_ASSIGNMENTS = ('__module__', '__qualname__' '__name__', '__doc__', '__annotations__') # no and 
    WRAPPER_UPDATES = ('__dict__',)
    functools.update_wrapper(newfunc, function, assigned = WRAPPER_ASSIGNMENTS, updated = WRAPPER_UPDATES)
    
    # TODO: update __annotations__ and/or __doc__ to show "x bounded to 5"
    
    return newfunc

class bracket(base):
    """
    >>> @bracket
    ... def f(x,y,z):
    ...     return x - y + 2 * z
    
    >>> f(1,2,3)
    5
    >>> g = f[1]
    >>> g(2,3)
    5
    >>> f[1](2,3)
    5
    >>> g = f[1, ..., 3]
    >>> g(2)
    5
    >>> g = f.partial(1, ..., 3)
    >>> g(2)
    5
    >>> g = f.partial(1, ..., z=3)
    >>> g(2)
    5
    >>> g = f.partial(1, z=3)
    >>> g(2)
    5
    """
    def key(self, **kwargs):
        return bracket(elipartial(self, **kwargs))
    
    def val(self, *vals):
        return bracket(elipartial(self, *vals))
    
    def partial(self, *args, **kwargs):
        return bracket(elipartial(self, *args, **kwargs))
    
    def partial(self, *args, **kwargs):
        return elipartial(self, *args, **kwargs)
    
    part = assuming = given = where = partial
    
    def __getitem__(self, item):
        if isinstance(item, tuple):
            return bracket(elipartial(self.function, *item))
        return bracket(elipartial(self.function, item))

elipartiallymulti = bracket

@infix
def elicurryargs(function, args):
    """
    >>> point = '{}/{}/{}'.format |elicurryargs| (..., 2, ...)
    >>> point(1,3)
    '1/2/3'
    """
    return elipartial(function, *args)

def simplecurry(*args, **kwargs):
    r"""
    >>> from __future__ import print_function
    >>> show = print |simplecurry(1, 2, sep='/')  # show is print with arguments 1, 2 and keyword argument sep='.'
    >>> show(3)
    1/2/3
    """
    return postfix(lambda function: _partial(function, *args, **kwargs))

def elicurry(*args, **kwargs):
    r"""
    >>> from __future__ import print_function
    >>> show = print |elicurry(1, ..., 3, sep='/')        # show is print with arguments 1, something, 3 and keyword argument sep='.'
    >>> show = print |with_arguments(1, ..., 3, sep='/')  # alias 
    >>> show = print |deferredcall(1, ..., 3, sep='/')    # alias
    >>> show(2)
    1/2/3
    >>> show(2, 4)
    1/2/3/4
    >>> show(2, 4, end=';\n')
    1/2/3/4;
    >>> try:
    ...     show()
    ... except TypeError as e:
    ...     print('Error')  # Ellipsis still in elipartial call
    Error
    >>> show = print |with_arguments(1,2, sep='/') |with_arguments(end=';\n')
    >>> show(3)
    1/2/3;
    >>> show()
    1/2;
    """
    return postfix(lambda function: elipartial(function, *args, **kwargs))

@infix
def infixcall(f, x):
    """WARNING: Renamed from "call" to "infixcall" in Version 1.0
    >>> print(5 + 2 * 10)
    25
    >>> print |infixcall| 5 + 2 * 10
    25
    >>> print(','.join('abcdef'))
    a,b,c,d,e,f
    >>> (print *compose* ','.join) |infixcall| 'abcdef'
    a,b,c,d,e,f
    >>> (print *compose* ','.join) |infixcall| 'abcdef' + 3 * 'x'
    a,b,c,d,e,f,x,x,x
    >>> compose(print, ','.join) |infixcall| 'abcdef'
    a,b,c,d,e,f
    """
    return f(x)

def call(*args, **kwargs):
    """WARNING: Renamed from "simplecall" to "call" in Version 1.0
    >>> ord |call('a')
    97
    >>> print *compose* ','.join |call('abcdef')
    a,b,c,d,e,f
    """
    @postfix
    def new(f):
        return f(*args, **kwargs)
    return new

@infix
def callargs(f, args):
    """
    >>> print |callargs| ('a', 5)
    a 5
    """
    return f(*args)

provide_left = curryleft
provide_right = curryright
add_args = elicurryargs
with_arguments = elicurry
latercall = deferredcall = elicurry

# utils

def mapwith(function):
    """
    >>> [1, 2, 7, 2] |mapwith(str) |to(list)
    ['1', '2', '7', '2']
    """
    return postfix(lambda *iterables: map(function, *iterables))

def filterwith(function):
    """
    >>> [1, 2, 7, 2] |filterwith(lambda x:x < 5) |to(list)
    [1, 2, 2]
    """
    return postfix(lambda iterable: filter(function, iterable))

if __name__ == '__main__':
    import sys
    if sys.argv[1:] in ([], ['-v']):
        import doctest
        doctest.testmod()
        unittest.main()
    elif sys.argv[1:] in (['-V'], ['--version']):
        print('funcoperators version', __version__)
