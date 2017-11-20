#!coding: utf-8
from __future__ import print_function, division

import pygame
import random

# importer la bibliothèque OpenGL !
from OpenGL.GL import *
from OpenGL.GL import shaders

import ctypes
import pygame
from math import sin, cos, degrees, radians, tan, sqrt

import numpy
from numpy import array, linalg
from numpy.linalg import norm

from functools import reduce

vertex_shader = """
#version 330
in vec3 position;
in vec3 normal;
in vec3 color;

uniform mat4 pvMatrix;
uniform mat4 mMatrix;

out vec3 normalVtx;
out vec3 positionVtx;
out vec3 colorVtx;

void main()
{
    gl_Position = pvMatrix * mMatrix * vec4(0.75 * position, 1);
    normalVtx = normal;
    positionVtx = (mMatrix * vec4(position, 1)).xyz;
    colorVtx = color;
}
"""

fragment_shader = """
#version 330
in vec3 normalVtx;
in vec3 positionVtx;
in vec3 colorVtx;

uniform vec3 lightPos;

out vec4 pixel;

void main()
{
    vec3 c = 1.0 * colorVtx + 0 * colorVtx * dot(normalVtx, normalize(lightPos - positionVtx));
    pixel = vec4(c, 1);
}
"""

class Axe:
    pass

Axe.X = 0
Axe.Y = 1
Axe.Z = 2

def polar(*args):
    if len(args) == 2:
        r, t = args
        return r * polar(t)
    elif len(args) == 1:
        t, = args
        return vec2(cos(t), sin(t))
    else:
        raise TypeError('Accept 1 or 2 arguments')


def polard(*args):
    if len(args) == 2:
        r, t = args
        return r * polard(t)
    elif len(args) == 1:
        t, = args
        return polar(radians(t))
    else:
        raise TypeError('Accept 1 or 2 arguments')

def spherical(*args):
    if len(args) == 3:
        r, p, t = args
        return r * spherical(p, t)
    elif len(args) == 2:
        p, t = args
        return vec3(sin(p) * sin(t),
                    sin(p) * cos(t),
                    cos(p))
    else:
        raise TypeError("Accept 2 or 3 arguments")

def sphericald(*args):
    if len(args) == 3:
        r, p, t = args
        return r * sphericald(p, t)
    elif len(args) == 2:
        p, t = args
        return spherical(radians(p), radians(t))
    else:
        raise TypeError("Accept 2 or 3 arguments")

def vec2(*args):
    """
    returns a vector in 3 dimensions
    vec3(1,2,3)
    vec3((1,2),3)
    """
    x, y = args
    return array((x, y), dtype=numpy.float32)

def vec3(*args):
    """
    returns a vector in 3 dimensions
    vec3(1,2,3)
    vec3((1,2),3)
    """
    if len(args) == 3:
        x, y, z = args
    elif len(args) == 2:
        (x, y), z = args
    else:
        raise TypeError('Accept 2 or 3 arguments')

    return array((x, y, z), dtype=numpy.float32)


def normalized(v):
    return v / linalg.norm(v)


def PerspectiveMatrix(fovy, aspect, zNear, zFar):
    f = 1.0 / tan(radians(fovy) / 2.0)
    return array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, 1. * (zFar + zNear) / (zNear - zFar), 2.0 * zFar * zNear / (zNear - zFar)],
        [0, 0, -1, 0]
    ], dtype=numpy.float32)


def TranslationMatrix(*args):
    """
    returns the TranslationMatrix
    TranslationMatrix(2,1,0)
    TranslationMatrix(2,1)
    TranslationMatrix((2,1,0))
    """
    if len(args) == 3:
        tx, ty, tz = args
    elif len(args) == 2:
        (tx, ty), tz = args, 0
    elif len(args) == 1:
        tx, ty, tz = args[0]
    else:
        raise TypeError("Accept 1, 2 or 3 arguments")

    return array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ], dtype=numpy.float32)


def LookAtMatrix(*args):
    """
    returns the LookAt matrix
    LookAtMatrix(1,2,3, 4,5,6, 7,8,9)
    LookAtMatrix((1,2,3), (4,5,6), (7,8,9))
    """
    if len(args) == 3:
        e, c, up = args
    elif len(args) == 9:
        e, c, up = args[:3], args[3:6], args[6:]
    else:
        raise TypeError("Accept 3 or 9 arguments")
    c = array(c)

    f = normalized(c - e)
    s = normalized(numpy.cross(f, up))
    u = numpy.cross(s, f)

    return array([
        [s[0], s[1], s[2], -s(e)],
        [u[0], u[1], u[2], -u(e)],
        [-f[0], -f[1], -f[2], f(e)],
        [0, 0, 0, 1],
    ], dtype=numpy.float32)
    
    # corresponds to M @ Translate(-e)


def SimpleRotationMatrix(angle, axe=Axe.Z):
    """
    returns the rotation matrix for angle in degree around X Y or Z
    """
    if angle % 90 == 0:
        a = angle % 360
        c = 1 if a == 0 else -1 if a == 180 else 0
        s = 1 if a == 90 else -1 if a == 270 else 0
    else:
        t = radians(angle)
        c = cos(t)
        s = sin(t)

    return array([
         [c, -s, 0, 0],
         [s, c, 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, 1]
     ] if axe == 2 else [
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ] if axe == 1 else [
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ], dtype=numpy.float32)


def RotationMatrix(angle, axe):
    """
    returns the rotation matrix for angle in degree around any axe
    """
    x, y, z = normalized(axe)

    if angle % 90 == 0:
        a = angle % 360
        c = 1 if a == 0 else -1 if a == 180 else 0
        s = 1 if a == 90 else -1 if a == 270 else 0
    else:
        t = radians(angle)
        c = cos(t)
        s = sin(t)

    k = 1 - c

    # Rodriguez rotation formula
    return array([
        [x * x * k + c, x * y * k - z * s, x * z * k + y * s, 0],
        [y * x * k + z * s, y * y * k + c, y * z * k - x * s, 0],
        [x * z * k - y * s, y * z * k + x * s, z * z * k + c, 0],
        [0, 0, 0, 1]
    ], dtype=numpy.float32)


def ScaleMatrix(kx, ky=None, kz=None):
    if ky is None:
        ky = kx
    if kz is None:
        kz = kx
    return array([
        [kx, 0, 0, 0],
        [0, ky, 0, 0],
        [0, 0, kz, 0],
        [0, 0, 0, 1]
    ], dtype=numpy.float32)

def IdentityMatrix():
    return array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=numpy.float32)

def couleur01(r,g,b):
    return [r/255, g/255, b/255]

ROUGE = couleur01(255, 0, 0)
VERT = couleur01(0, 255, 0)
BLEU = couleur01(0, 0, 255)
JAUNE = couleur01(255, 255, 0x44)
BLANC = couleur01(255, 255, 255)
NOIR = couleur01(0, 0, 0)
ORANGE = couleur01(255, 153, 0)
BLEU_CLAIR = couleur01(135, 206, 250)
GRIS = [0.2, 0.2, 0.2]

def nouvel_ecran(W, H):
    e = pygame.display.set_mode([W,H], pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
    
    glViewport(0, 0, W, H)
    glEnable(GL_DEPTH_TEST)

    return e

class Point:
    pos = None
    
    def __init__(self, other=None):
        if other is not None:
            self.pos = other.pos
    
    def copy(self):
        return Point(self)
    
class Quad:
    color = None
    colorid = None
    normal = None
    
    def __init__(self, other=None):
        self.points = [Point() for p in range(4)]
        
        if other is not None:
            for p1,p2 in zip(self.points, other.points):
                p1.pos = p2.pos
            self.color = other.color
            self.colorid = other.colorid
            self.normal = other.normal
    
    def __str__(self):
        return str(dict(
            points = [p.pos for p in self.points],
            color = self.color,
        ))
    
    def __repr__(self):
        return str(self)
    
    def copy(self):
        return Quad(self)
    
class Cub:
    span = None
    
    def  __init__(self, pos_or_other):
        if isinstance(pos_or_other, Cub):
            other = pos_or_other
            self.matrix = other.matrix
            self.pos = other.pos
            self.quads = [Quad(q) for q in other.quads]
            self.span = other.span
            
        else:
            pos = pos_or_other
            self.matrix = TranslationMatrix(pos)
            self.pos = pos
            self.quads = [Quad() for i in range(6)]
    
    def __str__(self):
        return str(dict(
            matrix = self.matrix,
            pos = self.pos,
            span = [self.span.start, self.span.stop],
        ))
    
    def __repr__(self):
        return str(self)
    
    def copy(self):
        return Cub(self)
    
    @property
    def rotmatrix(self):
        return array([self.matrix[i][:3] for i in range(3)])
    
    @property
    def transvec(self):
        return array([self.matrix[i][3] for i in range(3)])
    
    def colorAt(self, normal):
        inner = self.rotmatrix
        return next(quad.color for quad in self.quads if (inner @ quad.normal == normal).all())
    
    def colorIdAt(self, normal):
        inner = self.rotmatrix
        return next(quad.colorid for quad in self.quads if (inner @ quad.normal == normal).all())

class Rubik:
    def __init__(self, other=None):
        import itertools
        
        if other is not None:
            self.width = other.width
            self.dimensions = other.dimensions
            self.maxValue = other.maxValue
            self.cubes = [Cub(cub) for cub in other.cubes]
        else:
            self.width = 3
            self.dimensions = 3
            self.maxValue = self.width / 2.0
            pos1D = [self.maxValue - 0.5 - i for i in range(self.width)] # [1, 0, -1]
            self.cubes = [Cub(pos) for pos in itertools.product(pos1D, repeat=self.dimensions)] # 3 ** 3
            
            rubik = self
        
            def make(dim, rev):
                V = [-0.5 if rev else 0.5] * 3
                d1 = (dim + 1) % 3
                d2 = (dim + 2) % 3
                for i in range(4):
                    yield list(V)
                    V[d1], V[d2] = V[d2], -V[d1]
            
            quad_defs = [
                list(make(i, False)) for i in range(3)
            ] + [
                list(reversed(list(make(i, True)))) for i in range(3)
            ] # 6 quads of 4 points of 3 reals
            
            for cub in rubik.cubes:
                for quad, quad_def in zip(cub.quads, quad_defs):
                    for point, pos in zip(quad.points, quad_def):
                        point.pos = pos
            
            for cube in rubik.cubes:
                for i, quad in enumerate(cube.quads):
                    quad.normal = [0,0,0]
                    if i < 3:
                        quad.normal[i] = 1
                    else:
                        quad.normal[i-3] = -1
            
            colors = [
                ROUGE, JAUNE, BLEU, # x, y, z
                ORANGE, BLANC, VERT # -x, -y, -z
            ]
            
            maxValue = rubik.maxValue # 1.5 for 3×3×3
            for cube in rubik.cubes:
                for quad in cube.quads:
                    quad.color = NOIR
                    quad.colorid = -1
                    for dim in range(rubik.dimensions):
                        if all((array(cube.pos) + point.pos)[dim] == maxValue for point in quad.points):
                            quad.colorid = dim
                            quad.color = colors[dim]
                        elif all((array(cube.pos) + point.pos)[dim] == -maxValue for point in quad.points):
                            quad.colorid = dim + 3
                            quad.color = colors[dim + 3]
            
            i = 0
            for cub in rubik.cubes:
                beg = i
                i += 6 * 4
                cub.span = range(beg, i)
    
    def copy(self):
        return Rubik(self)
    
    def __add__(self, other):
        S = Rubik(self)
        S.radd(other)
        return S
    
    def __radd__(self, other):
        for cub in self.cubes:
            cub.matrix = cub.matrix @ other
            for d in range(3):
                cub.matrix[d][3] /= 2
        return S
    
    def __eq__(self, other):
        return all(
            (a.matrix == b.matrix).all()
            for a,b in zip(self.cubes, other.cubes))
    
    def solved(self):
        D = {}
        for cub in self.cubes:
            sub_matrix = cub.rotmatrix
            for quad in cub.quads:
                if quad.color != NOIR:
                    d = tuple(sub_matrix @ quad.normal)
                    if d not in D:
                        D[d] = tuple(quad.color)
                    elif D[d] != tuple(quad.color):
                        return False
        return True
    
    def cubAt(self, pos):
        return next(cub for cub in self.cubes
                    if (cub.transvec == pos).all())
    
    def identify(self):
        cross = 0
        for i in range(4):
            Moves["y"](self)
            if (self.cubAt((0,-1,1)).colorIdAt((0,0,1)) == self.cubAt((0,0,1)).colorIdAt((0,0,1)) and
                self.cubAt((0,-1,1)).colorIdAt((0,-1,0)) == self.cubAt((0,-1,0)).colorIdAt((0,-1,0))):
                cross += 1
        if cross < 4:
            return 'Cross', cross
        
        corner = 0
        f2l = 0
        for i in range(4):
            Moves["y"](self)
            if (self.cubAt((1,-1,1)).colorIdAt((0,0,1)) == self.cubAt((0,0,1)).colorIdAt((0,0,1)) and
                self.cubAt((1,-1,1)).colorIdAt((1,0,0)) == self.cubAt((1,0,0)).colorIdAt((1,0,0))):
                corner += 1
                if (self.cubAt((1,0,1)).colorIdAt((0,0,1)) == self.cubAt((0,0,1)).colorIdAt((0,0,1)) and
                    self.cubAt((1,0,1)).colorIdAt((1,0,0)) == self.cubAt((1,0,0)).colorIdAt((1,0,0))):
                    f2l += 1
        
        if f2l == 4:
            return self.identifyOLL()
        
        if corner == 4:
            return 'F2L', f2l
        
        return 'Corner', corner, 'F2L', f2l
    
    def identifyOLL(self):
        OLL = True
        import itertools
        center_color = self.cubAt((0,1,0)).colorIdAt((0,1,0))
        
        TOP = [
            center_color == self.cubAt((x,1,z)).colorIdAt((0,1,0))
            for z,x in itertools.product((-1,0,1), repeat=2)
        ]
        
        ## TOP ##
        # 0 1 2 #
        # 3 4 5 #
        # 6 7 8 #
        #########
        
        LTOP = [TOP[i] for i in (2,1,0, 5,4,3, 8,7,6)]
        ## LTOP ##
        # 2 1 0 #
        # 5 4 3 #
        # 8 7 6 #
        #########
        
        n = sum(TOP) - 1
        nOCLL = sum(TOP[i] for i in (1, 3, 5, 7))
        OCLL = nOCLL == 4
        answer = None
        
        def try_answer(x, y, symmetry=None):
            nonlocal answer
            if False:
                if answer is not None:
                    if answer[0] == x:
                        if symmetry is not None and (answer[1] - symmetry) % 4 == y:
                            pass # OK
                        else:
                            print('DOUBLE', answer, 'VS', x, y)
                    else:
                        print('DOUBLE', answer, 'VS', x, y)
            answer = (x, y)
        
        if OCLL:
            TOP_LEFT, TOP_RIGHT = (-1,1,-1), (1,1,-1)
            BOT_LEFT, BOT_RIGHT = (-1,1,1), (1,1,1)
            UP, RIGHT, LEFT, FACING, BACKING = (0,1,0), (1,0,0), (-1,0,0), (0,0,1), (0,0,-1)
            C = lambda POS, DIR: self.cubAt(POS).colorIdAt(DIR)
            
            r = n - 4
            for i in (3,2,1,0):
                Moves["U'"](self)
                
                if r == 1:
                    if center_color == C(BOT_LEFT, UP) == C(BOT_RIGHT, FACING):
                        try_answer('Sune', i)
                    if center_color == C(BOT_RIGHT, UP) == C(BOT_LEFT, FACING):
                        try_answer('Antisune', i)
                elif r == 0:
                    if center_color == C(TOP_LEFT, LEFT) == C(TOP_RIGHT, BACKING):
                        try_answer('Pi', i)
                    if center_color == C(TOP_LEFT, LEFT) == C(BOT_RIGHT, RIGHT):
                        try_answer('Flip', i, symmetry=2)
                elif r == 2:
                    if center_color == C(TOP_LEFT, BACKING) == C(TOP_RIGHT, BACKING):
                        try_answer('Headlights', i)
                    if center_color == C(TOP_LEFT, BACKING) == C(BOT_LEFT, FACING):
                        try_answer('Chameleon', i)
                    if center_color == C(TOP_RIGHT, BACKING) == C(BOT_LEFT, LEFT):
                        try_answer('Bowtie', i)
                elif r == 4:
                    try_answer('Solved', i, symmetry=1)
        else: # not OCLL
            for i in (3,2,1,0):
                Moves["U'"](self)
                
                TOP = [
                    center_color == self.cubAt((x,1,z)).colorIdAt((0,1,0))
                    for z,x in itertools.product((-1,0,1), repeat=2)
                ]
                
                LTOP = [TOP[i] for i in (2,1,0, 5,4,3, 8,7,6)]
                
                right = [center_color == self.cubAt((x,1,z)).colorIdAt((+1,0,0)) for x,z in ((+1,+1), (+1,0), (+1,-1))]
                left  = [center_color == self.cubAt((x,1,z)).colorIdAt((-1,0,0)) for x,z in ((-1,+1), (-1,0), (-1,-1))]
                top   = [center_color == self.cubAt((x,1,z)).colorIdAt((0,0,-1)) for x,z in ((-1,-1), (0,-1), (+1,-1))]
                bot   = [center_color == self.cubAt((x,1,z)).colorIdAt((0,0,+1)) for x,z in ((-1,+1), (0,+1), (+1,+1))]
                
                cpattern = [TOP[i] for i in (0, 2, 8, 6)]
                pattern = [TOP[i] for i in (1, 5, 7, 3)]
                
                clpattern = [LTOP[i] for i in (0, 2, 8, 6)]
                lpattern = [LTOP[i] for i in (1, 5, 7, 3)]
                
                if n == 0:
                    if all(right) and all(left):
                        try_answer('Blank', i, symmetry=2)
                    elif not all(right) and all(left):
                        try_answer('Zamboni', i)
                elif n == 1:
                    # No-Edge
                    if TOP[2] and sum(right) == 2:
                        try_answer('Nazi', i)
                    elif TOP[2] and sum(top) == 2:
                        try_answer('Anti-Nazi', i)
                elif n == 2:
                    if nOCLL == 0:
                        # No-Edge
                        if cpattern == [1,0,1,0] and sum(right) == 1:
                            try_answer('Slash', i)
                        elif cpattern == [0,1,1,0] and all(left):
                            try_answer('Crown', i)
                        elif cpattern == [1,1,0,0] and not all(bot):
                            try_answer('Bunny', i)
                    else: # nOCLL == 2
                        # L-Shapes
                        for A, p, T, hand in zip(('', 'Anti-'), (pattern, lpattern), (TOP, LTOP), (right, left)):
                            if p == [1,0,0,1] and sum(hand) == 1 and sum(bot) == 2:
                                try_answer(A + 'Breakneck', i)
                            elif p == [1,0,0,1] and sum(hand) == 3 and sum(bot) == 1:
                                try_answer(A + 'Frying Pan', i)
                            elif p == [0,0,1,1] and sum(hand) == 3 and sum(top) == 2:
                                if A == '':
                                    try_answer('Right back squeezy', i)
                                else:
                                    try_answer('Right front squeezy', i)
                        
                        # I-Shapes 
                        if pattern == [1,0,1,0] and all(left) and all(right):
                            try_answer('Highway', i, symmetry=2)
                        elif pattern == [0,1,0,1] and sum(right) == 2 and sum(left) == 2:
                            try_answer('Streetlights', i, symmetry=2)
                        elif pattern == [0,1,0,1] and sum(right) == 2 and sum(left) == 0:
                            try_answer('Ant', i)
                        elif pattern == [1,0,1,0] and not all(left) and all(right):
                            try_answer('Rice Cooker', i)
                        
                elif n == 3:
                    for A, p, T, hand in zip(('', 'Anti-'), (pattern, lpattern), (TOP, LTOP), (right, left)):
                        
                        # Square shape
                        if p == [0,1,1,0] and T[8] and sum(hand) == 1:
                            if A == '':
                                try_answer('Lefty Square', i)
                            else:
                                try_answer('Righty Square', i)
                            
                        # Small lightning bolt shapes
                        if p == [1,0,0,1] and T[6] and sum(hand) == 2 and sum(bot) == 2:
                            try_answer(A + 'Lightning', i) # Wide Sune, Left Wide Sune
                        elif p == [0,0,1,1] and T[0] and sum(hand) == 2 and sum(bot) == 1 and sum(top) == 1:
                            if A == '':
                                try_answer('Downstairs', i)
                            else:
                                try_answer('Upstairs', i)
                        
                        # Fish shape
                        if p == [1,1,0,0] and T[6] and sum(hand) == 1 and sum(bot) == 1:
                            try_answer(A + 'Kite', i)
                        # Knight move shapes
                        if p == [0,1,0,1] and T[6] and sum(bot) == 2:
                            try_answer(A + 'Gun', i)
                        if p == [0,1,0,1] and T[8] and sum(bot) == 1:
                            try_answer(A + 'Squeegee', i)
                        
                elif n == 4:
                    for A, p, T, L, R in zip(('', 'Anti-'), (pattern, lpattern), (TOP, LTOP), (left, right), (right, left)):
                        # P-Shapes
                        if p == [0,0,1,1] and not all(R) and T[0] and T[6]:
                            try_answer(A + 'Couch', i)
                        if p == [0,1,1,0] and all(L) and T[2] and T[8]:
                            try_answer(A + 'P', i)
                        
                        # Big lightning bolt shapes
                        if p == [0,1,0,1] and sum(R) == 1 and T[2] and T[6]:
                            try_answer(A + 'Fung', i)
                        
                        # Awkward 
                        if p == [0,0,1,1] and sum(R) == 2 and T[0] and T[2]:
                            try_answer(A + 'Spotted Chameleon', i)
                        if p == [0,1,1,0] and sum(L) == 1 and T[0] and T[2]:
                            try_answer(A + 'Awkward Fish', i)
                        
                        # W Shapes 
                        if p == [0,1,1,0] and sum(L) == 2 and T[2] and T[6]:
                            try_answer(A + 'Moustache', i)
                    
                    # Fish Shape
                    if pattern == [0,1,1,0] and sum(left) == 1 and TOP[0] and TOP[8]:
                        try_answer('Fish Salad', i)
                    if pattern == [0,0,1,1] and sum(right) == 2 and TOP[2] and TOP[6]:
                        try_answer('Untying', i)
                    
                    # C-Shapes
                    if pattern == [0,1,0,1] and not all(top) and TOP[6] and TOP[8]:
                        try_answer('City', i)
                    
                    if pattern == [1,0,1,0] and all(right) and TOP[0] and TOP[6]:
                        try_answer('Seeing Headlights', i)
                    
                    # T-Shapes 
                    if pattern == [0,1,0,1] and TOP[2] and TOP[8]:
                        if sum(bot) == 2:
                            try_answer('Tying', i)
                        elif sum(bot) == 1:
                            try_answer('Suit Up', i)
                    
                    # AllCorners 
                    if pattern == [0,0,0,0]:
                        try_answer('Checkers', i, symmetry=1)
                    
                elif n == 6:
                    # AllCorners 
                    if pattern == [1,0,0,1]:
                        try_answer('Arrow', i)
                    elif pattern == [0,1,0,1]:
                        try_answer('Mummy', i, symmetry=2)
                    
        return ('OCLL' if OCLL else 'OLL'), answer[0], answer[1]
    
    def identifyPLL(self):
        
        def inv(a,b):
            return (a + 3) % 6 == b
        
        """
        data = [
            ("H",  "GBGROR"),
            ("Ua", "GOGRRR"),
            ("Ub", "GBRRR"), 
            ("Z",  "GRGRGR"),
            ("Aa", "RGBORR"),
            ("Ab", "BGOGRG"),
            ("E",  "OGRBRG"),
            ("F",  "OBGRRR"),
            ("Ga", "GGRBOB"),
            ("Gb", "GGBOBG"),
            ("Gc", "BROGOG"),
            ("Gd", "RORBGO"),
            ("Ja", "GGGRBB"),
            ("Jb", "RROGGR"),
            ("Na", "BBGRRO"),
            ("Nb", "GBBORR"),
            ("Ra", "GORBRG"),
            ("Rb", "ORGRGR"),
            ("T",  "RBOGRR"),
            ("V",  "GOBORR"),
            ("Y",  "GGBORR"),
        ]
        data_map = dict((y,x) for x,y in data)
        
        """
        C = lambda POS, DIR: self.cubAt(POS).colorIdAt(DIR)
        
        OX, OY, OZ = (1,0,0), (0,1,0), (0,0,1)
        mOX, mOY, mOZ = (-1,0,0), (0,-1,0), (0,0,-1)
        
        """
        colors_map = {
            C(OZ, OZ): "R", C(mOZ, mOZ): "O",
            C(OX, OX): "G", C(mOX, mOX): "B",
            C(OY, OY): "Y", C(mOY, mOY): "W",
        }
        """
        
        answer = None
        def try_answer(x, y, symmetry=None):
            nonlocal answer
            if False:
                if answer is not None:
                    if answer[0] == x:
                        if symmetry is not None and (answer[1] - symmetry) % 4 == y:
                            pass # OK
                        else:
                            print('DOUBLE', answer, 'VS', x, y)
                    else:
                        print('DOUBLE', answer, 'VS', x, y)
            answer = x, y
            
        for i in (3,2,1,0):
            self.apply("U'")
            a,b,c,d,e,f = (
                self.cubAt((x,1,z)).colorIdAt(DIR)
                for (x,z), DIR in zip(
                    ((1,-1), (1,0), (1,1), (1,1), (0,1), (-1,1)),
                    (OX, OX, OX, OZ, OZ, OZ)
                )
            )
            
            if a == c and d == e == f and inv(b,d):
                try_answer('Ua', i)
            if a == c and d == e == f and inv(a,b):
                try_answer('Ub', i)
            if a == c == e and b == d == f:
                try_answer('Z', i)
            if a == e == f and inv(a,d) and inv(b,c):
                try_answer('Aa', i)
            if b == d == f and inv(a,b) and inv(c,e):
                try_answer('Ab', i)
            if b == f and c == e and inv(a,c) and inv(b,d):
                try_answer('E', i)
            if d == e == f and inv(a,d) and inv(b,c):
                try_answer('F', i)
            if a == b and d == f and inv(a,d) and inv(c,e):
                try_answer('Ga', i)
            if a == b == f and c == e and inv(a,c):
                try_answer('Gb', i)
            if c == e and d == f and inv(a,d) and inv(b,c):
                try_answer('Gc', i)
            if a == c and b == f and inv(a,b) and inv(d, e):
                try_answer('Gd', i)
            if a == b == c and e == f and inv(a,f):
                try_answer('Ja', i)
            if a == b == f and d == e and inv(b,c):
                try_answer('Jb', i)
            if a == b and d == e and inv(b,c) and inv(e,f):
                try_answer('Na', i)
            if b == c and e == f and inv(a,b) and inv(d, e):
                try_answer('Nb', i)
            if a == f and c == e and inv(a,d) and inv(b,c):
                try_answer('Ra', i)
            if b == d == f and c == e and inv(a,b):
                try_answer('Rb', i)
            if a == e == f and inv(a,c) and inv(b,d):
                try_answer('T', i)
            if b == d and e == f and inv(a,c) and inv(d,e):
                try_answer('V', i)
            if a == b and e == f and inv(b,c) and inv(d,e):
                try_answer('Y', i)
            if a == b == c and d == e == f:
                try_answer('I', i, symmetry=1)
            
        return answer
    
    def apply(self, alg):
        Alg(alg)(self)
        
def test_PLL():
    # do rotation test
    pass

def find_PLL():
    OLLS, sy = readOLLS()
    
    r = Rubik()
    for alg_base in [
        " F R U R' U' F' ",
        " f R U R' U' f' ",
        " F (R U R' U')2 F' ",
        " f (R U R' U')2 f' ",
        " R U R' U' R' F R F' ",
        " R U2 R' U' R U' R' ", 
        " r U2 R' U' R U' r' ", 
        " R U R' U R U2 R' ", 
        " r U R' U R U2 r' ", 
        " R2 D' R U' R' D R U R ",
    ]:
        r.apply(alg_base) 
        
        _, t, n = r.identify()
        r.apply("U" * n)
        
        for algo in OLLS[t]:
            r.apply(algo)
            I = r.identify()
            if I[1] == 'Solved':
                pllT, pllN = r.identifyPLL()
                if pllT != 'I':
                    print(pllT, alg_base, ('' if n == 0 else "U" if n == 1 else "U2" if n == 2 else "U'"), algo, sep='\t')
            # show(r)
            r.apply(alg.inv(algo))
        
        r.apply("U'" * n)
        r.apply(alg.inv(alg_base))
    
def creer_vao_rubiks(shader, rubik):
    all_colors = [quad.color for cub in rubik.cubes for quad in cub.quads for point in quad.points]
    all_colors = array(all_colors, dtype=numpy.float32).flatten()
    all_positions = [point.pos for cub in rubik.cubes for quad in cub.quads for point in quad.points]
    all_positions = array(all_positions, dtype=numpy.float32).flatten()
    all_normals = [quad.normal for cub in rubik.cubes for quad in cub.quads for point in quad.points]
    all_normals = array(all_normals, dtype=numpy.float32).flatten()
    
    alls = {
        'color': (all_colors, 3, GL_FLOAT),
        'position': (all_positions, 3, GL_FLOAT),
        'normal': (all_normals, 3, GL_FLOAT),
    }
    
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    
    for name, (value, number, typ) in alls.items():
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(value), value, GL_STATIC_DRAW)
        loc = glGetAttribLocation(shader, name)
        
        if loc != -1:
            glEnableVertexAttribArray(loc)
            glVertexAttribPointer(loc, number, typ, False, 0, ctypes.c_void_p())
        else:
            print('inactive attribute "{}"'.format(name))
    
    glBindVertexArray(0)
    
    return vao

class Modifier:
    
    R, L = array((1,0,0)), array((-1,0,0))
    U, D = array((0,1,0)), array((0,-1,0))
    F, B = array((0,0,1)), array((0,0,-1))
    
    @staticmethod
    def turn(raxe, theta, rubik):
        for cub in Modifier.cub_of_axe(raxe, rubik):
            cub.matrix = RotationMatrix(theta, raxe) @ cub.matrix
    
    @staticmethod
    def cub_of_general_movement(raxe, subset:'Subset[range(3)]', rubik):
        """
        # {} -> no move
        # {0} -> R
        # {1} -> M
        # {2} -> L'
        # {0,1} -> r
        # {1,2} -> l'
        # {1,3} -> R L'
        # {0,1,2} -> x
        """
        d = next(i for i in range(rubik.dimensions) if raxe[i] != 0)
        for cub in rubik.cubes:
            if abs(cub.matrix[d][3] - raxe[d]) in subset:
                yield cub
    
    @staticmethod
    def cub_of_axe(raxe, rubik):
        d = next(i for i in range(rubik.dimensions) if raxe[i] != 0)
        L = raxe[d]
        for cub in rubik.cubes:
            if cub.matrix[d][3] == L:
                yield cub
                
    @staticmethod
    def cub_of_rotation(raxe, rubik):
        yield from rubik.cubes
        
    @staticmethod
    def cub_of_wide(raxe, rubik):
        d = next(i for i in range(rubik.dimensions) if raxe[i] != 0)
        for cub in rubik.cubes:
            if abs(cub.matrix[d][3] - raxe[d]) <= 1:
                yield cub
                
    @staticmethod
    def cub_of_general_close(raxe, interval, rubik):
        d = next(i for i in range(rubik.dimensions) if raxe[i] != 0)
        i,j = interval
        for cub in rubik.cubes:
            if i <= abs(cub.matrix[d][3] - raxe[d]) <= j:
                yield cub

class Move:
    def __init__(self, selector, axe, direction:[-1,1], **kwargs):
        self.selector = selector
        self.axe = axe
        self.direction = direction
        self.kwargs = kwargs
        self.matrix = RotationMatrix(self.direction * 90, self.axe)
    
    def select(self, rubik):
        yield from self.selector(self.axe, rubik=rubik, **self.kwargs)
    
    def __call__(self, rubik):
        for cub in self.select(rubik):
            cub.matrix = self.matrix @ cub.matrix
    apply = __call__
    
    def inv(self):
        return Move(self.selector, self.axe, -self.direction, **self.kwargs)

Unit = [array((1,0,0)), array((0,1,0)), array((0,0,1))]
Moves = {}
for i, (a, b) in enumerate(("RL", "UD", "FB")):
    Moves[a] = Move(Modifier.cub_of_axe, Unit[i], -1)
    Moves[b] = Move(Modifier.cub_of_axe, -Unit[i], -1)
Moves["O"] = Move(Modifier.cub_of_general_movement, Unit[0], -1, subset=())

for k,move in list(Moves.items()):
    Moves[k.lower()] = Move(Modifier.cub_of_wide, move.axe, move.direction)
    Moves[k + "w"] = Move(Modifier.cub_of_wide, move.axe, move.direction)
    
for i, letter in enumerate("xyz"):
    Moves[letter] = Move(Modifier.cub_of_rotation, Unit[i], -1)

for i, a in enumerate("MES"):
    Moves[a] = Move(Modifier.cub_of_general_movement, Unit[i], +1 if a != 'S' else -1, subset={1})

for k,move in list(Moves.items()):
    Moves[k + "2"] = Move(move.selector, move.axe, move.direction * 2, **move.kwargs)
    
for k,move in list(Moves.items()):
    new = Moves[k + "'"] = Move(move.selector, move.axe, -move.direction, **move.kwargs)
    new.opp = move
    move.opp = new

def allstatic(Class):
    for x in dir(Class):
        if not x.startswith('__'):
            setattr(Class, x, staticmethod(getattr(Class, x)))
    return Class

@allstatic
class alg:
    
    def parse(string):
        import re
        toks = re.findall("[ORLFBUDMSExyzrlfbud]w?2?'?|\(|\)\d*", string)
        """
        toks = []
        for c in string:
            if c.strip() == '':
                pass
            elif c in 'ORLFBUDMSExyzrlfbud' or c in '()':
                state = 'move'
            elif not toks:
                raise ValueError("Modifier must apply to somehting: " + c)
            elif c in "'w":
                if toks[-1][0] in '()':
                    raise ValueError("Modifier cannot be applied to parenthesis: " + c)
                toks[-1] += c
            elif "0" <= c <= "9":
                if toks[-1][0] in '(':
                    raise ValueError("Modifier cannot be applied to open parenthesis: " + c)
                toks[-1] += c
        """
        
        stack = [[]]
        for t in toks:
            if t == '(':
                stack.append([])
            elif t.startswith(')'):
                n = int(t[1:] or 1)
                stack[-2].extend(stack.pop() * n)
            else:
                stack[-1].append(t)
        
        if len(stack) != 1:
            raise ValueError("Parenthesis not closed !")
        
        return stack[-1]
    
    def simplify(string):
        L = alg.parse(string)
        i = 0
        R = re.compile("([ORLFBUD]w?|[MSExyzrlfbud])(2?'?)")
        
        def T(x):
            l,n = R.match(x).groups()
            n = (1 if not n else
                 2 if "2" in n else
                 -1)
            if l.endswith('w'):
                l = l[0].lower()
            return l,n
        
        while i < len(L) - 1:
            (l1,n1),(l2,n2) = T(L[i]), T(L[i+1])
            if l1 == l2:
                n = (n1 + n2) % 4
                if n == 0:
                    del L[i:i+2]
                    i = max(0, i-1)
                else:
                    L[i] = l1 + ('' if n == 1 else '2' if n == 2 else "'")
                    del L[i+1]
            else:
                i += 1
                
        return L
    
    def inv(string):
        return (' '.join if isinstance(string, str) else list)(
            next(k for k,v in Moves.items() if v == Moves[m].opp)
            for m in reversed(alg.parse(string) if isinstance(string, str) else string))
    
    def close(A,B):
        """ [A: B] """
        return A + B + alg.inv(A)
    
    def commute(A,B):
        """ [A,B] """
        return A + B + alg.inv(A) + alg.inv(B)
    
    def anti(string):
        SUB = {
            "R": "L'",
            "L": "R'",
            "F": "F'",
            "B": "B'",
            "U": "U'",
            "D": "D'",
        }
        for k, v in list(SUB.items()):
            SUB[v] = k
            
        return ' '.join(SUB[x] for x in alg.parse(string))

class Alg:
    def __init__(self, arg):
        if isinstance(arg, str):
            arg = alg.parse(arg)
        self.list = arg
        self.moves = [Moves[k] for k in arg]
    
    def __call__(self, rubik):
        for m in self.moves:
            m(rubik)
    apply = __call__
    
    def on(self, rubik):
        copy = Rubik(rubik)
        self(copy)
        return copy
    
    def inv(self, r=None):
        return Alg(alg.inv(self.list)) if r is None else self.inv()(r)

def readOLLS():
    from collections import OrderedDict
    OLLS = OrderedDict({})
    oll = None
    state = 1
    
    synonyms = {}
    with open('oll.csv') as f:
        for l in f:
            if l.strip().startswith('#'):
                continue
            T = l.strip().split('\t')
            if not l.strip():
                state = 1
            elif state == 1:
                name = T[0].split(',')[0].strip()
                synonyms[name] = {s.strip() for s in T[0].split(',')}
                OLLS[name] = oll = []
                state = 2
            elif state == 2:
                rubik_state = T[0].strip()
                assert rubik_state == 'OLL'
                
                algo = T[1]
                try:
                    alg.parse(algo)
                    oll.append(algo)
                except:
                    print('Unparsable', algo)
    
    for k, L in list(synonyms.items()):
        for l in L:
            synonyms[l] = synonyms[k]
    
    return OLLS, synonyms

def test_OLLS():
    OLLS, synonyms = readOLLS()
    cub = Rubik()
    for name, list_of_alg in OLLS.items():
        for algo in list_of_alg:
            try:
                Alg(alg.inv(algo))(cub)
            except:
                print("Cannot apply", alg.inv(algo))
                cub = Rubik()
                continue
            
            Is = []
            for i in range(4):
                try:
                    a,b,c = cub.identify()
                    assert name in synonyms[b]
                    Is.append(c)
                except Exception as e:
                    try:
                        identification = cub.identify()
                    except:
                        identification = ('?', )
                    print(name, identification, algo, alg.inv(algo), sep='\n', end='\n\n') # type(e), e, 
                    Is.append(None)
                Alg('U')(cub)
            if all(x is not None for x in Is):
                if not any(
                    all((Is[i]-1)%P == Is[(i+1)%P] for i in range(4))
                    for P in (1,2,4)
                ):
                    print('ERROR', Is)
                
            Alg(algo)(cub)
            
def test_OLLS_rot():
    """
    # 3 → y, 2 → y2, 1 → y'
    3 Sune (U L U' R') (U L' U' R)
    2 Antisune (R' U L U') (R U L')
    3 Antisune y' L' U R U' L U R'
    1 Flip L' U2 M' (y) R U2 R U2 R' U2 (y') l
    1 Pi (R' U L U' R U L') U2 (R' U L U' R U L')
    2 Headlights F (R U R' U') (R' F R F2) (L' U2 L)
    2 Headlights R2' B2 R F2' R' B2 R F2' R
    2 Bowtie y F' L F R' F' L' F R
    1 Bowtie y' x U R' U' L U R U' r'
    1 Bowtie y R' U' (R U R' F') (R U R' U') (R' F R2)
    2 Bowtie x' R' D R U' R' D' R U x
    2 Bowtie x R' U R D' R' U' R D x'
    3 Bowtie y2 x L U' L' D L U L' D' x'
    1 Bowtie U R U2 R' L' U' L U' R U' R' L' U2 L
    2 Bowtie x U R' U' r x' U R U' r'
    3 Nazi l L2 U' L U' l' U2 l U' M'
    2 Slash F R' F' l R L' U R U' R' U' M'
    1 Crown l' U' r' U2 L U2 L' U2 r U l
    2 Crown (y) (F R' F' R) U2 (F R' F' R)(U' R U' R')
    2 Crown (y) x (U R' U' R) B2 (U R' U' R)(B' R B' R') x'
    2 Anti-Couch (y) M' U R U R' F' U' F R U' r'
    2 Frying Pan (y') r U2 R' U' R U' r' R U2 R' U' R U' R'
    1 Highway L F' L' U' L F' L' U L F L' U' M' U M
    1 Highway (L F' L' U' L F' L' U L F L' U' L)(R' F R) L'
    2 Arrow (y) r' U' R U' R' U2 r R' U2 R U R' U R
    2 Arrow r' U2 R U R' U r R' U' R U' R' U2 R
    """
    OLLS, sy = readOLLS()
    cub = Rubik()
    for name, list_of_alg in OLLS.items():
        for algo in list_of_alg:
            try:
                Alg(algo).inv(cub)
            except:
                print("Cannot apply", alg.inv(algo))
                cub = Rubik()
                continue
            
            id = cub.identify()
            assert id[1] == name, "{} != {}".format(id[1], name)
            if not id[2] == 0:
                print(id[2], name, algo)
            
            Alg(algo)(cub)

def main(rubik=None, use_move=None, period=None):
    pygame.init()
    
    tx, ty = taille = [800, 600]
    ecran = nouvel_ecran(tx, ty)

    clock = pygame.time.Clock()

    shader = shaders.compileProgram(
        shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    if rubik is None:
        rubik = Rubik()
    vao_rubiks = creer_vao_rubiks(shader, rubik)
    basic_rubik = Rubik()
    t = 0
    import itertools
    
    Sexy = "R U R' U'" # [R, U]
    Longerxy = "R U R' F"
    MyAntiSune = "R U2 R' U' R U' R'" # [R: [U: [U, R']]]
    MySune = "L' U2' L U L' U L"
    
    OLLS, synonyms = readOLLS()
    
    FrontNSexy = lambda i: "F" + Sexy * i + "F'"
    DoubleFrontNSexy = lambda i: "f" + Sexy * i + "f'"
    
    Simple = FrontNSexy(1)
    Double = DoubleFrontNSexy(1)
    
    chosen_move = alg.parse(use_move) if use_move is not None else alg.parse(
        # Sexy
        # MySune + 'O' + "U'" + MyAntiSune
        # ''.join(random.choice('RUFLDB') for i in range(10))
        " O ".join([
            "l U L U' L' U L U' L' U2' l' y",
            "y' l U2 L U L' U' L U L' U' l'",
            
            "l' U L U' L' U L U' L' U2' l y'",
            "y l' U2 L U L' U' L U L' U' l",
            
            "l' U l' L U L' U' L U L' U' l U' l'",
            "l U l' U L U' L' U L U' L' l U' l",
            
            "x U R' y U' R' y' U' R U x' R' U R y",
            "y' R' U' R x U' R' U y R U y' R U' x'",
            
            "L' U L' U' L U L' F' L F L' F' L F L' y",
            "y' L F' L' F L F' L' F L U' L' U L U' L",
            
            "F2' U M U' M' F2' U M U' M'",
            "M U M' U' F2 M U M' U' F2",
        ])
        
        #''.join(
            #alg.inv(''.join(OLLS[k][0])) + 'O' + ''.join(OLLS[k][0]) + 'O'
            #for k in list(OLLS)[20:]
        #)
        # "F" + "URU'R'" * 3 + "F'" + 'U O'
        # ''.join('F' + Sexy * i + "F' O" + alg.inv('F' + Sexy * i + "F'") + 'O' for i in range(6))
    )
    
    if use_move:
        move_cycle = iter(chosen_move)
        # move_cycle = itertools.cycle(chosen_move)
    else:
        move_cycle = iter(())
        
    fini = 0
    rcamx = rcamy = 0
    go = True
    period = period if period is not None else 50 # 2 # 20 # 50
    stopAtO = not True
    RANDOM = 0 # 'subset'
    move = None
    while fini == 0:
        # pour tous les événements qui se sont passsés depuis la dernière fois
        pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # si l'event est de type QUIT
                fini = 1 # on met fini à 1, ce qui va quitter la boucle à la fin de ce tick
            elif event.type == pygame.VIDEORESIZE:
                # on s'adapte à la nouvelle fenêtre
                ecran = nouvel_ecran(event.w, event.h) # re créer l'écran !
            elif event.type == pygame.MOUSEMOTION:
                if mouse_buttons[0]:
                    rcamx += 0.20 * event.rel[0]
                    rcamy += 0.20 * event.rel[1]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3: # right click
                    rcamx = rcamy = 0
            elif event.type == pygame.KEYDOWN:
                MOVE_KEY = {
                    pygame.K_u: "U",
                    pygame.K_d: "D",
                    pygame.K_l: "L",
                    pygame.K_f: "F",
                    pygame.K_b: "B",
                    pygame.K_r: "R",
                    pygame.K_m: "M",
                    pygame.K_e: "E",
                    pygame.K_s: "S",
                    pygame.K_x: "x",
                    pygame.K_y: "y",
                    pygame.K_z: "z",
                }
                
                if event.key == pygame.K_z:
                    rcamx = rcamy = 0
                elif event.key == pygame.K_SPACE:
                    go = not go
                elif event.key == pygame.K_i:
                    print(*rubik.identify())
                elif event.key in MOVE_KEY:
                    Shift = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
                    Control = bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
                    
                    key = (str.lower if Control else str.upper)(MOVE_KEY[event.key]) + Shift * "'"
                    key = next(key for key in (key, key.lower(), key.upper()) if key in Moves)
                    
                    #move = Moves[key]
                    #if not go:
                        #prev_matrix = {}
                        #for cub in move.select(rubik):
                            #prev_matrix[cub] = cub.matrix
                    
                    if not go:
                        go = True
                        t = 0
                        move_cycle = iter(alg.parse(key))
        
        if pressed[pygame.K_LEFT]:
            rcamx += 1
        if pressed[pygame.K_RIGHT]:
            rcamx -= 1
        if pressed[pygame.K_UP]:
            rcamy += 1
        if pressed[pygame.K_DOWN]:
            rcamy -= 1
        
        # logic
        from random import choice, randrange, randint
        from functools import partial
        randc = lambda *arguments: choice(arguments)
        
        if go:
            P = period
            if t % P == 0:
                def random_interval():
                    i = randint(0,2)
                    j = randint(i, 2)
                    return [i,j]
                
                try:
                    if RANDOM == 'close':
                        move = Move(Modifier.cub_of_general_close,
                            interval = random_interval(),
                            direction = randc(-1,1,2,-2),
                            axe = Unit[randc(0,1,2)])
                        
                    elif RANDOM == 'subset':
                        move = Move(Modifier.cub_of_general_movement,
                            subset = {i for i in range(3) if randc(0,1)},
                            direction = randc(-1,1,2,-2),
                            axe = Unit[randc(0,1,2)])
                    else:
                        move = Moves[next(move_cycle)]
                        if (move.selector == Modifier.cub_of_general_movement and 
                            len(move.kwargs['subset']) == 0): # Null move
                            print('{0: 5}'.format(t // P), 'Solved' if rubik.solved() else ' ' * len('Solved'), *rubik.identify())
                            if stopAtO:
                                go = False
                
                    prev_matrix = {}
                    for cub in move.select(rubik):
                        prev_matrix[cub] = cub.matrix
                except StopIteration:
                    go = False
                    
            elif move and 1 <= t % P < P-1:
                r = (t % P - 1) / (P-1 - 1)
                for cub in move.select(rubik):
                    cub.matrix = RotationMatrix(r * move.direction * 90, move.axe) @ prev_matrix[cub]
            
            elif move and t % P == P-1:
                for cub in move.select(rubik):
                    cub.matrix = RotationMatrix(move.direction * 90, move.axe) @ prev_matrix[cub]
                del prev_matrix
                move = None
            
            t += 1
        
        # dessin
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)
        
        P = PerspectiveMatrix(45, 1.0 * tx / ty, 0.01, 20) # fov 45°, ratio tx / ty, distance min : 100, distance max : 2000

        # position et orientation de la camera :
        x,z = norm((5,5)) * polard(45 + t * 1.0 * 0 + rcamx * 2.5)
        y = norm((5,5)) + rcamy * 0.30 # norm((5,5)) * cos(t * 0.02 * 0 + radians(rcamy))
        # x,y,z = 10 * sphericald(90 * cos(t * 0.005), 180 * cos(t * 0.006))
        x,y,z = normalized((x,y,z)) * 10
        V = LookAtMatrix(x,y,z, 0,0,0, 0,1,0)

        # position de la lampe :
        glUniform3f(glGetUniformLocation(shader, 'lightPos'), 5, 0, 0)

        PV = P @ V
        
        # dessin du cube
        glBindVertexArray(vao_rubiks)
        
        glUniformMatrix4fv(glGetUniformLocation(shader, 'pvMatrix'), 1, True, PV)
        
        for cub in rubik.cubes:
            glUniformMatrix4fv(glGetUniformLocation(shader, 'mMatrix'), 1, True, cub.matrix)
            glDrawArrays(GL_QUADS, cub.span.start, cub.span.stop - cub.span.start)

        glBindVertexArray(0)
        glUseProgram(0)
        
        # appliquer les dessins
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    
    return rubik

def show(cube, move='', **kwargs):
    return main(cube, move, **kwargs)

def make_graph_move(move, nodes):
    A = Alg(move)
    r = Rubik()
    OLLS, sy = readOLLS()
    S = set()
    if nodes.lower() == '__all__':
        nodes = list(OLLS)
    elif nodes.lower() == '__ocll__':
        nodes = ['Solved', 'Sune', 'Antisune', 'Chameleon', 'Headlights', 'Pi', 'Flip']
    for node in nodes:
        P = Alg(OLLS[node][0]) if not node == 'Solved' else Alg('')
        P.inv()(r)
        for j in range(4):
            I = r.identify()
            if I not in S:
                print(*I)
                A(r)
                while r.identify() != I:
                    print('>', *r.identify())
                    S.add(r.identify())
                    A(r)
                S.add(I)
            Alg("U")(r)
        P(r)
        assert r.identify()[0] in ('OCLL', 'Solved')

def find_simple_OLL():
    dirname = 'Simple-Olls'
    filename = 'Fast-Sune'
    include_images = False
    
    Bases = (
        ('Suit Up', 'P') if filename in ('WSune-Small', 'Sune-Small', 'Long-Small') else 
        ('Suit Up', 'P', 'Breakneck', 'Ant', 'Tying', 'Untying',) if filename == 'Fast-Simple' else
        ('Suit Up', 'P', 'Sune', 'Antisune', 'Lightning', 'Anti-Lightning', 'Lefty Square', 'Righty Square') if filename == 'Fast-Sune' else
        ()
    )
    
    Excludes = (()
        + ("Flip", "Chameleon") * (filename == 'Fast-Sune' or filename == 'Fast-Simple' and not include_images)
        + ("Headlights", "Gun", "Anti-Couch" , "Zamboni" , "Pi" , "Mummy",
         "Anti-Lightning", "Frying Pan", "Crown" , "Anti-Frying Pan" , "Kite",
         "Moustache", "Lefty Square", "Slash" , "Upstairs" , "Nazi" , "Downstairs",
         "Anti-Kite", "Anti-Nazi", "Spotted Chameleon" , "Lightning" , "Arrow",
         "Righty Square", "Streetlights", ) * (filename == 'Fast-Sune')
        + () * (filename in ('WSune-Small', 'Sune-Small', 'Long-Small'))
    )
    
    show_all = (
        (lambda k2: k2 in ('Lightning', 'Anti-Lightning', 'Lefty Square', 'Righty Square')) if filename == 'Fast-Sune' else
        (lambda k2: k2 in Bases) if (filename == 'Fast-Simple' and not include_images) else
        (lambda k2: False) # else lambda k2: i == 0
    )
    
    MAX_LEVEL = (
        0 if filename in ("WSune-Small", "Sune-Small", "Long-Small") else
        3 if filename in ("Fast-Simple", "Fast-Sune") else
        10
    )
    
    Moves = list(zip(
        ("WSune", "WAntisune", "WMySune", "WMyAntiSune") if filename == "WSune-Small" else
        ("Sune", "Antisune", "MySune", "MyAntiSune") if filename == "Sune-Small" else
        ("Breakneck", "Ant", "Tying", "Untying") if filename == "Long-Small" else
        ("Small", "Big") if filename in ("Fast-Simple", "Fast-Sune") else
        ()
        ,
        map(Alg,
            ("rUR'URU2r'", "l'U'LU'L'U2l", "rU2R'U'RU'r'", "l'U2LUL'Ul") if filename == 'WSune-Small' else
            ("RUR'URU2R'", "L'U'LU'L'U2L", "RU2R'U'RU'R'", "L'U2LUL'UL") if filename == 'Sune-Small' else
            ("F (RUR'U')2 F'", "f (RUR'U')2 f'", "RUR'U' R'FRF'", " F RU'R'U' RUR'F'") if filename == 'Long-Small' else
            ("F RUR'U' F'", "f RUR'U' f'") if filename in ('Fast-Simple', 'Fast-Sune') else
            ()
        ),
    ))
        
    Excludes += tuple(M[0] for M in Moves)
    
    OLLS, sy = readOLLS()
    from collections import defaultdict
    M = defaultdict(list)
    levels = {}
    M['Solved'] = []
    
    for b in Bases:
        M[b] = []
    r = Rubik()
    
    import re
    R = re.compile('OLL(\d+)')
    OLLNumbers = {
        k: next(R.match(m).group(1) for m in sy[k] if R.match(m))
        for k in sy
    }
    OLLNumbers['Solved'] = '0'
    
    import itertools
    for n in range(MAX_LEVEL+1):
        mod = False
        newM = defaultdict(list)
        for Aname, Aval in Moves:
            for node in OLLS:
                if node in M:
                    continue
                P = Alg(OLLS[node][0])
                P.inv()(r)
                for j in range(4):
                    Aval(r)
                    I = r.identify()
                    assert I[0] in ('OCLL', 'Solved', 'OLL')
                    if I[1] in M:
                        newM[node].append((j, Aname, I[1], I[2]))
                        levels[node] = n
                        mod = True
                    Aval.inv()(r)
                    r.apply('U')
                P(r)
        if not mod:
            break
        for k,l in newM.items():
            M[k].extend(l)
        # print(n, '\n' + '\n'.join(map(str,sorted(dict(M).items()))))
    
    def node_chain(v):
        for x in M[v]:
            yield x[1]
            yield from node_chain(x[1])
            break
    
    for L in M.values():
        pass # del L[1:]
    
    def label_img(node1, a,t,b, node2):
        if not include_images:
            return '"{}-{}-{}"'.format(a,t,b)
        knode1, knode2 = OLLNumbers[node1], OLLNumbers[node2]
        return '<<table border="0"><tr> <td>{}</td> <td><img src="images/O{}U{}.gif"/></td> <td>{}</td> <td><img src="images/O{}U{}.gif"/></td> <td>{}</td> </tr></table>>'.format(
            'U'+str(a), knode1, (4 - a) % 4, t, knode2, (4-b)%4, 'U'+str(b))
    
    from functools import partial
    import os
    realfilename = os.path.join(dirname, (filename if include_images else filename + '-noimage') + '.dot')
    with open(realfilename, 'w') as file:
        print('digraph {', file=file)
        print('rankdir=LR;', file=file)
        for k,L in sorted(M.items()):
            if k in Excludes:
                continue
            # if k not in levels:
            #     continue
            # if levels[k] > 0:
            #     continue
            for i,(n,f,k2,n2) in enumerate(L):
                if show_all(k2):
                    print('"{}" -> "{}" [label={}]'.format(k, k2, label_img(k, n,f,n2, k2)), file=file)
                else:
                    print('"{}" -> "{} ({})" [label={}]'.format(k, k2,k, label_img(k, n,f,n2, k2)), file=file)
                    print('"{0} ({1})" [label="{0}"]'.format(k2,k), file=file)
        
        for k,l in levels.items():
            if k in Excludes:
                continue
            print('"Level {}" -> "{}"'.format(l, k), file=file)
        print('}', file=file)
    print('Written ' + realfilename)

if __name__ == '__main__':
    find_simple_OLL() # main()
