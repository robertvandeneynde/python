from __future__ import print_function
import sys
import os

import math
from math import *

import builtins
pow = builtins.pow

if sys.version_info < (3,6):
    tau = 2 * pi

## degrees cos, sin, tan
cosd = lambda x: cos(radians(x)) if not(x % 90 == 0) else [1, 0, -1, 0][(x // 90) % 4]
sind = lambda x: sin(radians(x)) if not(x % 90 == 0) else [0, 1, 0, -1][(x // 90) % 4]
tand = lambda x: sind(x) / cosd(x)
atand = lambda x: degrees(atan(x))
atan2d = lambda y, x: degrees(atan(y, x))
acosd = lambda x: degrees(acos(x)) if not(x in (-1,0,1)) else [180, 90, 0][int(x)+1]
asind = lambda x: degrees(asin(x)) if not(x in (-1,0,1)) else [-90, 0, 90][int(x)+1]

## french
racine = sqrt

## log, ln, log10
ln = math.log

def log(x, base=None):
    if base is None:
        raise ValueError('Log without a base is ambiguous, use log10 or ln')
    return math.log(x, base)

## import *
import itertools
from itertools import *

import functools
from functools import *

from operator import *
from collections import *

## import module
if sys.version_info[0] >= 3:
    import html

import random
from random import randint, randrange, shuffle, choice

import string
from string import ascii_letters, ascii_lowercase, ascii_uppercase

import argparse
import unicodedata
import re
import json
import csv
import sqlite3
import subprocess
import subprocess as sub

from pprint import pprint
from glob import glob

from fractions import Fraction
frac = Fraction  # from fractions import Fraction as F

## funcoperators
try:
    from funcoperators import infix, postfix, unary
except ImportError:
    infix = postfix = unary = lambda x:x

## datetime
from datetime import date, time, datetime, timedelta

class CallableTimedelta(timedelta):
    def __call__(self, x):
        return self * x
    
seconds, milliseconds, microseconds, days, hours, minutes, weeks = (CallableTimedelta(**{x:1}) for x in ('seconds', 'milliseconds', 'microseconds', 'days', 'hours', 'minutes', 'weeks'))
years = 365.25 * days  # Julian year https://en.wikipedia.org/wiki/Julian_year_(astronomy)
combine = infix(datetime.combine)
now = datetime.now
today = datetime.today

## datetime utils
@postfix
def french_date(date):
    return date.strftime("%d/%m/%Y %Hh%M")

@postfix
def french_date_only(date):
    return date.strftime("%d/%m/%Y")

datefrench = datefr = date_french = frenchdate = french_date
datefrenchonly = dateonlyfr = date_only_french = frenchdateonly = french_date_only

## operator
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

## re
Re = re.compile

## numpy
try:
    import numpy
    import numpy as np
    from numpy import array, matrix
    from numpy import cross, dot
    from numpy.linalg import norm
    vec = lambda *args, **kwargs: numpy.array(args, **kwargs)
except:
    pass

if sys.version_info[0] >= 3:
    from importlib import reload

## related to current projects
try:
    pass
    #from mydjangoapp.views import *
    #from mydjangoapp.models import *
except:
    pass

## map, filter
if sys.version_info[0] < 3:
    lmap = map
    lfilter = filter
else:
    def lmap(*a, **b):
        """ return list(map(*a, **b)) """
        return list(map(*a, **b))

    def lfilter(*a, **b):
        """ return list(filter(*a, **b)) """
        return list(filter(*a, **b))

def mapwith(function):
    """
    >>> sum(map(int, '1 2 7 2'.split()))
    12
    >>> toints = mapwith(int)
    >>> sum(toints('1 2 7 2'.split()))
    12
    >>> '1 2 7 2'.split() |mapwith(int) |postfix(sum)
    12
    """
    return postfix(lambda *iterables: map(function, *iterables))
    
def filterwith(function):
    return postfix(lambda *iterables: filter(function, *iterables))

def lmapwith(function):
    """ @see mapwith """
    return postfix(lambda *iterables: lmap(function, *iterables))
    
def lfilterwith(function):
    """ @see filterwith """
    return postfix(lambda *iterables: lfilter(function, *iterables))

def whichall(iterable_of_x_condition):
    """
    >>> all(x % 2 == 0 for x in range(10))
    False
    >>> # annoying, I want to know which ones !
    >>> whichall((x, x % 2 == 0) for x in range(10))
    [0, 2, 4, 6, 8]
    >>> # the standard solution is annoying because it has to MOVE the condition to the end
    >>> [x for x in range(10) if x % 2 == 0]
    [0, 2, 4, 6, 8]
    """
    return [x for x,condition in iterable_of_x_condition if condition]

makemap, makefilter, makelmap, makelfilter = mapwith, filterwith, lmapwith, lfilterwith
Map, Filter = mapwith, filterwith

## unicode stuff
try:
    import uniutils
    from uniutils import *  # uniname, hexord, uord, uordname, uniline, unicontext, unilinecat, unibasecat
except:
    pass

## 3D, gl shaders like
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

## 3D + funcoperators, inline |dot| |cross| product
try:
    import funcoperators 
    from funcoperators import infix, prefix, postfix
except ImportError:
    pass
else:
    tostr, tolist, totuple, toset, tochr, toord, tojoin = map(postfix, (str, list, tuple, set, chr, ord, ''.join))
    
    from fractions import Fraction
    div = frac = funcoperators.infix(Fraction)
    
    try:
        import numpy
    except ImportError:
        pass
    else:
        dot = infix(numpy.dot)
        cross = infix(numpy.cross)

## Statistical stuffs
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
    return namedtuple('Stats', fields)(*(getattr(s,f) for f in fields))

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

## urllib
def urlparsetotal(url, *, multiple=False, fragment_is_qs=False):
    from urllib.parse import urlparse, parse_qs
    
    result = urlparse(url)._asdict()

    result['pqs'] = parse_qs(result.pop('query'))
    
    if not multiple:
        def single(a_dict):
            for k,v in a_dict.items():
                if not len(v) == 1:
                    raise ValueError("Doesn't have only one value {!r}: {}".format(k, v))
            return {k:v[0] for k,v in a_dict.items()}
        result['pqs'] = single(result['pqs'])

    if fragment_is_qs:
        result['fqs'] = parse_qs(result.pop('fragment'))

        if not multiple:
            result['fqs'] = single(result['fqs'])

    return dict(result)


## functional tools
try:
    from funcoperators import elipartial
except ImportError:
    pass

try:
    from funcoperators import compose, circle  # (hex |circle| ord)(x) == hex(ord(x))
    
    # french
    rond = circle
except ImportError:
    pass

## introspection
@postfix
def desc(x, *, underscore=False, callable=False, attrs=None):
    if isinstance(attrs, str):
        attrs = set(attrs.split())
    elif attrs is not None and not isinstance(attrs, (set, frozenset)):
        attrs = set(attrs)
    
    def keep1(n):
        return True if callable else not hasattr(getattr(x,n), '__call__')
    
    def keep2(n):
        return True if underscore else not n.startswith('_')
    
    def keep(n):
        return keep1(n) and keep2(n) and (attrs is None or n in attrs)
    
    return {n: getattr(x, n) for n in dir(x) if keep(n)}

@postfix
def dir_decorate(x, *, underscore=False, callable=True, attrs=None):
    if isinstance(attrs, str):
        attrs = set(attrs.split())
    elif attrs is not None and not isinstance(attrs, (set, frozenset)):
        attrs = set(attrs)
        
    def reduction(name):
        return 'function' if name == 'builtin_function_or_method' else name
    
    def decoration(obj):
        """ returns '(' if obj is callable, '!' if it's a class, else '' """
        return ('!' if type(obj) is type else 
                '(' if hasattr(obj, '__call__') else
                ':' + reduction(obj.__class__.__name__))
    
    def keep1(n):
        return True if callable else not hasattr(getattr(x,n), '__call__')
    
    def keep2(n):
        return True if underscore else not n.startswith('_')
    
    def keep(n):
        return keep1(n) and keep2(n) and (attrs is None or n in attrs)
    
    def filtered(x,n):
        return ((True if callable else not hasattr(getattr(x,n), '__call__')
            and (True if underscore else not n.startswith('_'))))
    
    def sorted_key(iterable_of_2tuple):
        return [b for a,b in sorted(iterable_of_2tuple)]
    
    return sorted_key((d, n + d) for n in dir(x) if keep(n) for d in [decoration(getattr(x,n))])
    # return [n + decoration(getattr(x, n)) for n in dir(x)]
    # return [n + d for n in dir(x) for d in [decoration(getattr(x,n))]]

desc_dir = descdir = dirdec = dirdecorate = dirdesc = dir_decorate

@postfix
def plddesc(*a, **b):
    print('\n'.join(ddesc(*a, **b)))

## ranges
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

## utils
def groupdict(iterable, *, key=None, reduce=None, join=None):
    """
    >>> groupdict((i%2, i) for i in range(10))
    {0: [0,2,4,6,8], 1: [1,3,5,7,9]}
    >>> def rest(x): return i % 2
    >>> groupdict(range(10), key=rest)
    {0: [0,2,4,6,8], 1: [1,3,5,7,9]}
    >>> groupdict(range(10), key=rest, reduce=sum)
    {0: 20, 1: 25}
    >>> groupdict('abc56', key=str.isdigit, join=''.join)
    {True: '56', False: 'abc'}
    """
    if key is not None:
        return groupdict(((key(x), x) for x in iterable), reduce=reduce, join=join)
    
    if join is not None and reduce is not None:
        raise ValueError("join and reduce are mutually exclusive")
    
    d = {}
    
    for x,y in iterable:
        if x not in d:
            d[x] = []
        d[x].append(y)
    
    if join is not None:
        return {x:join(map(str,y)) for x,y in d.items()}
    if reduce is not None:
        return {x:reduce(y) for x,y in d.items()}
    
    return d

def groupdictby(key, iterable, **kwargs):
    return groupdict(iterable, key=key, **kwargs)

groupings = groupdict
groupingsby = groupdictby

def setdiff(A, B):
    if not isinstance(A, (set, frozenset)):
        A = set(A)
    if not isinstance(B, (set, frozenset)):
        B = set(B)
    return (A - B, B - A)

def print_list_dict(dic, **kwargs):
    print('\n'.join('{}: {}'.format(x,y) for x,y in dic.items()), **kwargs)

def print_list(iterable, **kwargs):
    print('\n'.join(str(s) for s in iterable), **kwargs)

def dictuniq(it):
    d = {}
    for a,b in it:
        if a in d:
            raise ValueError
        d[a] = b
    return d

def mro(x):
    return x.__class__.__mro__

## modification of some standard functions

# implicit map
def all(*args):
    """ all(func, iterable) is all(map(func, iterable)) """
    import builtins
    return builtins.all(*args) if len(args) != 2 else builtins.all(map(args[0], args[1]))

# implicit map
def any(*args):
    """ any(func, iterable) is any(map(func, iterable)) """
    import builtins
    return builtins.any(*args) if len(args) != 2 else builtins.any(map(args[0], args[1]))

## custom short aliases
ul = uniline
pl, pld = print_list, print_list_dict
ddesc = dir_decorate
pfmt2 = print *circle* fmt2
to = postfix # same as tolist, tostr, etc. tolist = to(list)
c = compose  # vec
F = frac
nonascii = ''.join -c- filterwith(lambda x:ord(x) > 127) 
uln = ulnonascii = ul -c- nonascii
mapto = mapwith

def lentype(x):
    try: return len(x), type(x)
    except: return None, type(x)

## clipboard
import platform
if platform.system() == 'Linux':
	def pbpaste(*, selection:'primary|secondary|clipboard'='clipboard'):
		import subprocess
		return subprocess.check_output(['xclip', '-selection', selection, '-o']).decode('utf-8')

	@postfix
	def pbcopy(s, *, selection:'primary|secondary|clipboard'='clipboard'):
		import subprocess
		p = subprocess.Popen(['xclip', '-selection', selection], stdin=subprocess.PIPE)
		p.communicate(s.encode('utf-8'))
		# Warning: Use communicate() rather than .stdin.write, .stdout.read or .stderr.read to avoid deadlocks due to any of the other OS pipe buffers filling up and blocking the child process. 
		#p.stdin.write(s.encode('utf-8'))
		#p.stdin.close()
		
elif platform.system() == 'Windows':
    
    # TODO: use subprocess and 'clip' command (clip < stream and echo "hello" | clip)
    @postfix
    def pbcopy(x):
        from tkinter import Tk
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(x) 
        r.update() # now it stays on the clipboard after the window is closed
        r.destroy()
     
    def pbpaste():
        from tkinter import Tk
        r = Tk()
        r.withdraw()
        s = r.clipboard_get()
        r.update() # now it stays on the clipboard after the window is closed
        r.destroy()
        return s

cc, cv = pbcopy, pbpaste
ccm = partial(pbcopy, selection='primary')  # middle click
cvm = partial(pbpaste, selection='primary')  # middle click

## misc.

def dictuniq(it):
    d = {}
    for a,b in it:
        if a in d:
            raise ValueError
        d[a] = b
    return d

def formatwith(fmt):
    return postfix(partial(format, format_spec=fmt)) # postfix(lambda x:format(x, fmt))

def same_ast(a, b):
    import ast
    A, B = (ast.dump(ast.parse(x)) for x in (a, b))
    return A == B
    
def pprint_ast(x, *, show_offsets=True):
    import ast
    import astpretty
    astpretty.pprint(ast.parse(x), show_offsets=show_offsets)
    
#while True:
#  subprocess.call('kdialog --passivepopup'.split() +
#['h'.join(str(abs(now() - lever)).split(':')[:2])] + [str(10)]); sleep(60*3)
#from urllib.parse import urlunparse
import urllib
from pathlib import Path as path

def unquotecc(): 
    import urllib
    #cv() | to(urllib.parse.unquote) | cc
    cc(urllib.parse.unquote(cv()))
    
ccunquote = unquotecc
def strgroupn(x:str, n:int=8): 
   if not len(x) % 8 == 0:
       raise ValueError(f"{x:!r} len must be divisible by {n}")
   return [x[i*n:i*n+n] for i in range(len(x)//n)]
   
from urllib.parse import unquote as urlunquote
urldecode = urlunquote
