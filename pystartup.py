from __future__ import print_function
import sys
import os

import math
from math import *
if sys.version_info < (3,6):
    tau = 2 * pi

# degrees cos, sin, tan
cosd = lambda x: cos(radians(x)) if not(x % 90 == 0) else [1, 0, -1, 0][(x // 90) % 4]
sind = lambda x: sin(radians(x)) if not(x % 90 == 0) else [0, 1, 0, -1][(x // 90) % 4]
tand = lambda x: sind(x)/cosd(x)
atand = lambda x: degrees(atan(x))
atan2d = lambda y, x: degrees(atan(y, x))
acosd = lambda x: degrees(acos(x)) if not(x in (-1,0,1)) else [180, 90, 0][int(x)+1]
asind = lambda x: degrees(asin(x)) if not(x in (-1,0,1)) else [-90, 0, 90][int(x)+1]

# french
racine = sqrt

# log, ln, log10
ln = math.log

def log(x, base=None):
    if base is None:
        raise ValueError('Log without a base is ambiguous, use log10 or ln')
    return math.log(x, base)

# import *
import itertools
from itertools import *

import functools
from functools import *

from operator import *
from collections import *

# import module
if sys.version_info[0] >= 3:
    import html

import random
from random import randint, randrange, shuffle, choice

import argparse
import unicodedata
import re
import json
import csv
import sqlite3

from pprint import pprint

from fractions import Fraction
frac = F = Fraction # from fractions import Fraction as F

# datetime
from datetime import date, time, datetime, timedelta

class CallableTimedelta(timedelta):
    def __call__(self, x):
        return self * x
    
seconds, milliseconds, microseconds, days, hours, minutes, weeks = (CallableTimedelta(**{x:1}) for x in ('seconds', 'milliseconds', 'microseconds', 'days', 'hours', 'minutes', 'weeks'))
combine = datetime.combine
now = datetime.now
today = datetime.today

# funcoperators
try:
    from funcoperators import infix, postfix, unary
except ImportError:
    infix = postfix = unary = lambda x:x

# datetime utils
@postfix
def french_date(date):
    return date.strftime("%d/%m/%Y %Hh%M")

@postfix
def french_date_only(date):
    return date.strftime("%d/%m/%Y")

datefrench = datefr = date_french = frenchdate = french_date
datefrenchonly = dateonlyfr = date_only_french = frenchdateonly = french_date_only

# operator
import operator
ops = operators = {
    '+': operator.add,
    '-': operator.sub,
    '/': operator.truediv,
    '//': operator.floordiv,
    '*': operator.mul,
    '%': operator.mod,
    '@': getattr(operator, 'matmul', operator.mul),
    '&': operator.and_,
    '^': operator.xor,
    '~': operator.invert,
    '|': operator.or_,
    '**': operator.pow,
    '<<': operator.lshift,
    '>>': operator.rshift,
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '>': operator.gt,
    'not': operator.not_,
    'is': operator.is_,
    'is not': operator.is_not,
    'and': operator.and_,
    'or': operator.or_,
}

# re
Re = re.compile

# numpy
try:
    import numpy
    import numpy as np
    from numpy import array, matrix
    from numpy import cross, dot
    from numpy.linalg import norm
    c = vec = lambda *args, **kwargs: numpy.array(args, **kwargs)
except:
    pass

if sys.version_info[0] >= 3:
    from importlib import reload

# related to current projects
try:
    pass # from mydjangoapp.views import *
    pass # from mydjangoapp.models import *
except:
    pass

# map, filter
    lmap = map
    lfilter = filter
else:
    def lmap(*a, **b):
        """ return list(map(*a, **b)) """
        return list(map(*a, **b))

    def lfilter(*a, **b):
        """ return list(filter(*a, **b)) """
        return list(filter(*a, **b))

# unicode stuff
try:
    import uniutils
    from uniutils import * # uniname, hexord, uord, uordname, uniline, unicontext, unilinecat, unibasecat
except:
    pass

# 3D, gl shaders like
def vec3(x=None, y=None, z=None):
    '''
    vec3(1) == array((1,1,1))
    vec3((1,2,3)) == 
    vec3((1,2), 3) == 
    vec3(1,(2, 3)) == 
    vec3(1,2,3) == array((1,2,3))
    '''
    return (array((0,0,0))         if x is None else
            array(x)               if y is None and z is None and hasattr(x, '__len__') and len(x) == 3 else
            array((x,x,x))         if y is None and z is None else
            array((x[0], x[1], y)) if z is None and hasattr(x, '__len__') and len(x) >= 2 else
            array((x, y[0], y[1])) if z is None and hasattr(y, '__len__') and len(y) >= 2 else
            array((x,y,z)))
            
@postfix
def normalized(x):
    return x / norm(x)

@postfix
def fmt2(x):
    return format(x, '.2f')
fmt = fmt2

# 3D + funcoperators, inline |dot| |cross| product
try:
    import funcoperators 
    from funcoperators import infix, prefix, postfix
except ImportError:
    pass
else:
    tostr, tolist, totuple, toset, tochr, toord = map(postfix, (str, list, tuple, set, chr, ord))
    
    from fractions import Fraction
    F = div = frac = funcoperators.infix(Fraction)
    
    try:
        import numpy
    except ImportError:
        pass
    else:
        dot = infix(numpy.dot)
        cross = infix(numpy.cross)

# Statistical stuffs
def mean(it):
    s = 0
    i = 0
    for x in it:
        s += x
        i += 1
    return 1.0 * s / i

def variance(it):
    s = s2 = i = 0
    for x in it:
        s += x
        s2 += x * x
        i += 1
    return (1.0 * s2 / i) - (1.0 * s / i) ** 2

def StatsWithData(it):
    from collections import namedtuple
    m1 = m2 = n = 0
    data = []
    for x in it:
        m1 += x
        m2 += x ** 2
        n += 1
        data.append(x)
    m1 /= 1. * n or 1.
    m2 /= 1. * n or 1.
    mean = m1
    variance = max(0, m2 - mean ** 2)
    
    data.sort()
    Min, Max = (None, ) * 2 if n == 0 else (data[0], data[-1])
    q1, q2, q3 = (None, ) * 3 if n == 0 else (data[len(data)*i//4] for i in (1,2,3))
    
    return namedtuple('StatsWithData', 'mean stdev n variance min max data q0 q1 q2 q3 q4')(mean, variance ** .5, n, variance, Min, Max, data, Min, q1, q2, q3, Max)

def Stats(it):
    s = StatsWithData(it)
    fields = tuple(f for f in s._fields if f != 'data')
    return namedtuple('Stats', fields)(*tuple(getattr(s,f) for f in fields))

def stdev(it):
    return sqrt(variance(it))

def print_matrix(M):
    M = [[format(x) for x in row] for row in M]
    ncolumns = max(len(row) for row in M)
    for row in M:
        row.extend([''] * (ncolumns - len(row)))
    widths = [max(len(M[i][j]) for i in range(len(M))) for j in range(ncolumns)]
    for row in M:
        for i in range(len(row)):
            row[i] += ' ' * (widths[i] - len(row[i]))
    print('\n'.join(' '.join(row) for row in M))

# functional tools
# TODO: elipartial(print, ..., '+', ...)(1,2) should print('1 + 2')
def elipartial(func, *args, **keywords):
    """ elipartial(pow, ..., 2) == lambda x: x**2 """
    import itertools
    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*(newfunc.leftmost_args + fargs + newfunc.rightmost_args), **newkeywords)
    newfunc.func = func
    args = iter(args)
    newfunc.leftmost_args = tuple(itertools.takewhile(lambda v: v != Ellipsis, args))
    newfunc.rightmost_args = tuple(args)
    newfunc.keywords = keywords
    return newfunc

try:
    from funcoperators import compose, circle # (hex |circle| ord)(x) == hex(ord(x))
    
    # french
    rond = circle
except ImportError:
    pass

@postfix
def desc(x):
    return {n:getattr(x, n) for n in dir(x) if not hasattr(getattr(x,n), '__call__')}

@infix
def irange(*args):
    """
    @returns range
    list(irange(5)) == [1,2,3,4,5]
    list(irange(1,5)) == [1,2,3,4,5]
    list(irange(2,5)) == [2,3,4,5]
    list(irange(2,10,2)) == [2,4,6,8,10]
    list(irange(5,2,-1)) == [5,4,3,2]
    """
    if len(args) == 1:
        return range(1, 1+args[0])
    r = range(*args)
    if r.step < 0:
        return range(r.start, r.stop-1, r.step)
    return range(r.start, 1+r.stop, r.step)

try:
    import funcoperators
except ImportError:
    exclusive = range
else:
    exclusive = infix(range)

inclusive = irange
