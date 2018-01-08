from OpenGL.GL import *
from OpenGL.GL import shaders
import ctypes
import pygame
from math import sin,cos,degrees,radians,tan

import numpy
from numpy import array, matrix, linalg

def farray(*args):
    return numpy.array(*args, dtype=numpy.float32)

class Axis:
    pass

Axis.X = 0
Axis.Y = 1
Axis.Z = 2

def polar(*args):
    if len(args) == 2: r,t = args
    elif len(args) == 1: r,t = 1,args[0]
    else: raise TypeError('Accept 1 or 2 arguments')
    
    return r * vec2(cos(t), sin(t))

def polard(*args):
    if len(args) == 2: r,t = args
    elif len(args) == 1: r,t = 1,args[0]
    else: raise TypeError('Accept 1 or 2 arguments')
    
    return r * polar(radians(t))

def vec2(x,y):
    return array((x,y), dtype=numpy.float32)

NAME_TO_INT = {
    'x': 0,
    'y': 1,
    'z': 2,
}

def vec3(*args, **kwargs):
    '''
    Returns numpy.array depending on arguments:
    vec3() -> (0,0,0)
    vec3(1,2,3) -> (1,2,3)
    vec3((1,2,3)) -> (1,2,3)
    vec3((1,2),3) -> (1,2,3)
    vec3(1,(2,3)) -> (1,2,3)
    vec3(x=1,y=2,z=3) -> (1,2,3)
    vec3(xy=(1,2),z=3) -> (1,2,3)
    vec3(x=1,yz=(2,3)) -> (1,2,3)
    vec3(y=2,xz=(1,3)) -> (1,2,3)
    vec3(xyz=(1,2,3)) -> (1,2,3)
    '''
    if args and kwargs:
        raise TypeError('vec3 accept either args or kwargs, not both')
    
    elif kwargs:
        V = array((0,0,0), dtype=numpy.float32)
        
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
            x,y,z = args
        elif len(args) == 0:
            x,y,z = 0,0,0
        else:
            raise TypeError('Accept 1 2 or 3 arguments')
    
        return array((x,y,z), dtype=numpy.float32)

def normalized(v):
    return v / linalg.norm(v)

def PerpectiveMatrix(fovy, aspect, zNear, zFar):
    f = 1.0/tan(radians(fovy)/2.0)
    return matrix([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, 1. * (zFar + zNear) / (zNear - zFar), 2.0 * zFar * zNear / (zNear - zFar)],
            [0,0,-1,0]
        ], dtype=numpy.float32)

def TranslationMatrix(*args):
    if len(args) == 3: tx,ty,tz = args
    elif len(args) == 2: (tx,ty),tz = args, 0
    elif len(args) == 1: tx,ty,tz = args[0]
    else: raise TypeError("Accept 1, 2 or 3 arguments")
        
    return matrix([
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1]
        ], dtype=numpy.float32)

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
    
    return matrix([
        [ s[0],  s[1],  s[2], 0],
        [ u[0],  u[1],  u[2], 0],
        [-f[0], -f[1], -f[2], 0],
        [    0,     0,     0, 1],
    ], dtype=numpy.float32).dot(
        TranslationMatrix(-e)
    )

def AxeRotationMatrix(angle, axe=Axis.Z):
    if angle % 90 == 0:
        x = angle % 360
        c = 1 if x == 0 else -1 if x == 180 else 0
        s = 1 if x == 90 else -1 if x == 270 else 0
    else:
        t = radians(angle)
        c = cos(t)
        s = sin(t)
    
    return matrix([
            [c, s, 0, 0],
            [-s, c, 0, 0],
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

def create_object(shader):
    vertex_array_object = glGenVertexArrays(1)
    glBindVertexArray( vertex_array_object )
    
    vertex_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    
    position = glGetAttribLocation(shader, 'position')
    glEnableVertexAttribArray(position)
    
    glVertexAttribPointer(position, 4, GL_FLOAT, False, 0, ctypes.c_void_p(0))
    
    glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vertices), vertices, GL_STATIC_DRAW)
    
    glBindVertexArray(0)
    
    glDisableVertexAttribArray(position)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    return vertex_array_object
    
def display(shader, vertex_array_object, t):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(shader)
    
    # build projection matrix
    p = PerpectiveMatrix(45, 1.0 * 512/512, 0.1, 100)
    
    # build view matrix (lookAt)
    v = LookAtMatrix(vec3(xy = 7 * polar(0.5 * t), z = 5), (0, 0, 0), (0, 0, 1))
    pv = p.dot(v)
    
    # build model matrix of triangles (boucy animation)
    m = TranslationMatrix(0, 0, abs(sin(3*t)))
    pvm = pv.dot(m)
    
    # use our only vao
    glBindVertexArray(vertex_array_object)
    
    # set matrix
    loc_matrix = glGetUniformLocation(shader, 'pvmMatrix')
    glUniformMatrix4fv(loc_matrix, 1, False, pvm.T)
    
    # draw
    glPointSize(5)
    glDrawArrays(GL_TRIANGLES, 0, 18)
    glBindVertexArray(0)
    
    glUseProgram(0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((512, 512), pygame.OPENGL|pygame.DOUBLEBUF)
    glClearColor(0.5, 0.5, 0.5, 1.0)
    glViewport(0, 0, 512, 512)
    glEnable(GL_DEPTH_TEST)

    shader = shaders.compileProgram(
        shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    )
    
    vertex_array_object = create_object(shader)
    
    clock = pygame.time.Clock()
    
    t = 0
    done = False
    while not done:     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        
        t += 1
        display(shader, vertex_array_object, t/60.)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()
