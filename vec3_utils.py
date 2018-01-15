from __future__ import division

from math import sin, cos, degrees, radians, tan

import numpy
from numpy import array, matrix, linalg

def farray(*args):
    return numpy.array(*args, dtype=numpy.float32)

def sind(x):
    return sin(radians(x))

def cosd(x):
    return cos(radians(x))

def tand(x):
    return tan(radians(x))

def polar(*args):
    """
    polar(pi/6) -> (cosd(pi/6), sind(pi/6)) = vec2(0.86602539, 0.5)
    polar(5, pi/6) -> (5 * cosd(pi/6), 5 * sind(pi/6)) = vec2(4.33012676, 2.5)
    """
    if len(args) == 2:
        r,t = args
    elif len(args) == 1:
        r,t = 1, args[0]
    else:
        raise TypeError('Accept 1 or 2 arguments')
    
    return r * vec2(cos(t), sin(t))

def polard(*args):
    """
    polard(30) -> (cosd(30), sind(30)) = vec2(0.86602539, 0.5)
    polard(5, 30) -> (5 * cosd(30), 5 * sind(30)) = vec2(4.33012676, 2.5)
    """
    if len(args) == 2:
        r,t = args
    elif len(args) == 1:
        r,t = 1, args[0]
    else:
        raise TypeError('Accept 1 or 2 arguments')
    
    return r * polar(radians(t))

def vec2(x,y=None):
    """
    vec2(1,2) -> farray((1.0, 2.0))
    vec2(5) -> farray((5.0, 5.0))
    vec2(y=6, x=1) -> farray((1.0, 6.0))
    """
    if y is None:
        try:
            x,y = x
        except TypeError:
            x,y = x,x
    return farray((x,y))

NAME_TO_INT = {
    'x': 0,
    'y': 1,
    'z': 2,
    'w': 3,
    'r': 0,
    'g': 1,
    'b': 2,
    'a': 3,
}

def readvec(V, names):
    """
    Returns numpy.array from values of vector V depending on arguments:
    readvec((1,2,3), 'xy') -> farray((1,2))
    readvec((1,2,3), 'rg') -> farray((1,2))
    readvec((1,2,3), 'zx') -> farray((3,1))
    readvec((1,2,3), 'zz') -> farray((3,3))
    
    If the funcoperators lib is installed, I'd suggest defining functions like xy
    (1,2,3)|xy -> farray((1,2))
    
    Given:
    xy = postfix(lambda vec: readvec(vec, 'xy'))
    """
    return farray([
        V[NAME_TO_INT[x]]
        for i,x in enumerate(names)])

def vec3(*args, **kwargs):
    '''
    Returns numpy.array depending on arguments:
    vec3() -> (0,0,0)
    vec3(5) -> (5,5,5)
    vec3(1,2,3) -> (1,2,3)
    vec3((1,2,3)) -> (1,2,3)
    vec3((1,2),3) -> (1,2,3)
    vec3(1,(2,3)) -> (1,2,3)
    vec3(x=1,y=2,z=3) -> (1,2,3)
    vec3(r=1,g=2,b=3) -> (1,2,3)
    vec3(xy=(1,2),z=3) -> (1,2,3)
    vec3(x=1,yz=(2,3)) -> (1,2,3)
    vec3(y=2,xz=(1,3)) -> (1,2,3)
    vec3(xyz=(1,2,3)) -> (1,2,3)
    '''
    if args and kwargs:
        raise TypeError('vec3 accept either args or kwargs, not both')
    
    elif kwargs:
        V = farray((0,0,0))
        
        for x,v in kwargs.items():
            if len(x) == 1:
                V[NAME_TO_INT[x]] = v
            else:
                it = iter(v)
                for c in x:
                    V[NAME_TO_INT[c]] = next(it)
                
        return V
    else:
        if len(args) == 3:
            x,y,z = args
        elif len(args) == 2:
            try:
                (x,y),z = args
            except TypeError:
                x,(y,z) = args
        elif len(args) == 1:
            try:
                x,y,z = args[0]
            except TypeError:
                x,y,z = args[0], args[0], args[0]
        elif len(args) == 0:
            x,y,z = 0,0,0
        else:
            raise TypeError('Accept 0, 1, 2 or 3 arguments')
    
        return farray((x,y,z))

def normalized(v):
    return v / linalg.norm(v)

def PerspectiveMatrix(fovy, aspect, zNear, zFar):
    f = 1.0 / tan(radians(fovy) / 2.0)
    return farray([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, 1.0 * (zFar + zNear) / (zNear - zFar), 2.0 * zFar * zNear / (zNear - zFar)],
            [0,0,-1,0]
        ])

def TranslationMatrix(*args):
    if len(args) == 3:
        tx,ty,tz = args
    elif len(args) == 2:
        (tx,ty),tz = args, 0
    elif len(args) == 1:
        tx,ty,tz = args[0]
    else:
        raise TypeError("Accept 1, 2 or 3 arguments")
        
    return farray([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ])

def LookAtMatrix(*args):
    if len(args) == 3:
        e,c,ur = args
    elif len(args) == 9:
        e,c,ur = args[:3], args[3:6], args[6:]
    else:
        raise TypeError("Accept 3 or 9 arguments")
    e,c,ur = array(e), array(c), array(ur)
    
    U = normalized(ur)
    f = normalized(c - e)
    s = numpy.cross(f, U)
    u = numpy.cross(normalized(s), f)
    
    return farray([
        [ s[0],  s[1],  s[2], 0],
        [ u[0],  u[1],  u[2], 0],
        [-f[0], -f[1], -f[2], 0],
        [    0,     0,     0, 1],
    ]).dot(
        TranslationMatrix(-e)
    )

class Axis:
    X = 0
    Y = 1
    Z = 2

def AxeRotationMatrix(angle, axis=Axis.Z):
    if angle % 90 == 0:
        x = angle % 360
        c = 1 if x == 0 else -1 if x == 180 else 0
        s = 1 if x == 90 else -1 if x == 270 else 0
    else:
        t = radians(angle)
        c = cos(t)
        s = sin(t)
    
    return farray([
            [c, s, 0, 0],
            [-s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ] if axis == 2 else [
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ] if axis == 1 else [
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])
