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

def vec2(x, y):
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
        [s[0], s[1], s[2], -s.dot(e)],
        [u[0], u[1], u[2], -u.dot(e)],
        [-f[0], -f[1], -f[2], f.dot(e)],
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


def GenericRotationMatrix(angle, axe):
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
JAUNE = couleur01(255, 255, 0)
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
    
    def identifyOLL(self):
        import itertools
        TOP = [
            self.cubAt((x,1,z)).colorIdAt((0,1,0))
            for z,x in itertools.product((-1,0,1), repeat=2)
        ] # left-top, top, right-top,  second-row, third-row
        
        center_color = TOP[4]
        n = sum(center_color == v for v in TOP)
        COLL = center_color == TOP[1] == TOP[3] == TOP[4] == TOP[5] == TOP[7] # COLL
        answer = None
        if n == 5 + 1:
            for i in range(4):
                if (self.cubAt((-1,1,-1)).colorIdAt((0,1,0)) == center_color
                    == self.cubAt((-1,1,1)).colorIdAt((-1,0,0))):
                    answer = 'sune', i
                elif (self.cubAt((1,1,-1)).colorIdAt((0,1,0)) == center_color
                    == self.cubAt((1,1,1)).colorIdAt((1,0,0))):
                    answer = 'antisune', i
                Moves["U"](self)
        elif n == 5 + 0:
            for i in range(4):
                if (self.cubAt((-1,1,-1)).colorIdAt((-1,0,0)) == center_color
                    == self.cubAt((1,1,-1)).colorIdAt((0,0,-1))):
                    answer = 'pi', i
                if (self.cubAt((-1,1,-1)).colorIdAt((0,0,-1)) == center_color
                    == self.cubAt((1,1,-1)).colorIdAt((0,0,-1))):
                    answer = answer or ('flip', i)
                Moves["U"](self)
        elif n == 5 + 2:
            for i in range(4):
                if (self.cubAt((-1,1,-1)).colorIdAt((0,0,-1)) == center_color
                    == self.cubAt((1,1,-1)).colorIdAt((0,0,-1))):
                    answer = 'headlights', i
                if (self.cubAt((-1,1,-1)).colorIdAt((0,0,-1)) == center_color
                    == self.cubAt((-1,1,1)).colorIdAt((0,0,1))):
                    answer = 'cameleon', i
                if (self.cubAt((1,1,-1)).colorIdAt((0,0,-1)) == center_color
                    == self.cubAt((-1,1,1)).colorIdAt((-1,0,0))):
                    answer = 'bowtie', i
                Moves["U"](self)
        elif n == 5 + 4:
            answer = 'solved', 0
        return 'COLL' if COLL else '', n, answer
    
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
            cub.matrix = GenericRotationMatrix(theta, raxe) @ cub.matrix
    
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
        self.matrix = GenericRotationMatrix(self.direction * 90, self.axe)
    
    def select(self, rubik):
        yield from self.selector(self.axe, rubik=rubik, **self.kwargs)
    
    def __call__(self, rubik):
        for cub in self.select(rubik):
            cub.matrix = self.matrix @ cub.matrix
    
    def inv(self):
        return Move(self.selector, self.axe, -self.direction, **kwargs)
    
Unit = [array((1,0,0)), array((0,1,0)), array((0,0,1))]
Moves = {}
for i, (a, b) in enumerate(("RL", "UD", "FB")):
    Moves[a] = Move(Modifier.cub_of_axe, Unit[i], -1)
    Moves[b] = Move(Modifier.cub_of_axe, -Unit[i], -1)
Moves["O"] = Move(Modifier.cub_of_general_movement, Unit[0], -1, subset=())

for k,move in list(Moves.items()):
    Moves[k.lower()] = Moves[k + "w"] = Move(Modifier.cub_of_wide, move.axe, move.direction)
    
for i, letter in enumerate("xyz"):
    Moves[letter] = Move(Modifier.cub_of_rotation, Unit[i], -1)

for i, a in enumerate("MSE"):
    Moves[a] = Move(Modifier.cub_of_general_movement, Unit[i], -1, subset={1})

for k,move in list(Moves.items()):
    Moves[k + "2"] = Move(move.selector, move.axe, move.direction * 2)
    
for k,move in list(Moves.items()):
    new = Moves[k + "'"] = Move(move.selector, move.axe, -move.direction)
    new.opp = move
    move.opp = new

class alg:
    @staticmethod
    def parse(string):
        import re
        return re.findall("[ORLFBUDrlfbudxyz]w?2?'?", string)
    
    @staticmethod
    def inv(string):
        return ''.join(next(k for k,v in Moves.items() if v == Moves[m].opp)
                       for m in reversed(alg.parse(string)))
    @staticmethod
    def close(A,B):
        return A + B + alg.inv(A)
    
    @staticmethod
    def commute(A,B):
        return A + B + alg.inv(A) + alg.inv(B)

def main():
    pygame.init()
    
    tx, ty = taille = [800, 600]
    ecran = nouvel_ecran(tx, ty)

    clock = pygame.time.Clock()

    shader = shaders.compileProgram(
        shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    global rubik
    rubik = Rubik()
    vao_rubiks = creer_vao_rubiks(shader, rubik)
    basic_rubik = Rubik()
    t = 0
    import itertools
    
    Sexy = commute("R", "U") # R U R' U'
    Longerxy = "R U R' F"
    MyAntiSune = "R U2 R' U' R U' R'" # close(R, close(U, commute(U, R')))
    MySune = "L' U2' L U L' U L"
    
    FrontNSexy = lambda i: "F" + Sexy * i + "F'"
    
    chosen_move = alg.parse(
        MyAntiSune + "O"
    )
    
    move_cycle = iter(chosen_move)
    move_cycle = itertools.cycle(chosen_move)
        
    fini = 0
    rcamx = rcamy = 0
    go = True
    period = 2
    stopAtO = False
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
                if event.key == pygame.K_s:
                    rcamx = rcamy = 0
                elif event.key == pygame.K_SPACE:
                    go = not go
        
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
                    move = Moves[next(move_cycle)]
                    if (move.selector == Modifier.cub_of_general_movement and 
                        len(move.kwargs['subset']) == 0): # Null move
                        print('{0: 5}'.format(t // P), 'Solved' if rubik.solved() else ' ' * len('Solved'), rubik.identifyOLL())
                        if stopAtO:
                            go = False
                
                    # Move(Modifier.cub_of_general_close,
                    #     interval = random_interval(),
                    #     direction = randc(-1,1,2,-2),
                    #     axe = Unit[randc(0,1,2)])
                    
                    prev_matrix = {}
                    for cub in move.select(rubik):
                        prev_matrix[cub] = cub.matrix
                except StopIteration:
                    move = None
                    
            elif move and 1 <= t % P < P-1:
                r = (t % P - 1) / (P-1 - 1)
                for cub in move.select(rubik):
                    cub.matrix = GenericRotationMatrix(r * move.direction * 90, move.axe) @ prev_matrix[cub]
            
            elif move and t % P == P-1:
                for cub in move.select(rubik):
                    cub.matrix = GenericRotationMatrix(move.direction * 90, move.axe) @ prev_matrix[cub]
                del prev_matrix, move
            
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

if __name__ == '__main__':
    main()
