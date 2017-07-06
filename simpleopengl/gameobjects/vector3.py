from math import *
from util import format_number



class Vector3(object):
    
    __slots__ = ('_v')    
    
       
    def __init__(self, *args):
        """Creates a Vector3 from 3 numeric values or a list-like object
        containing at least 3 values. No arguments result in a null vector.
                
        """
        if len(args) == 3:
            self._v = map(float, args[:3])            
            return
        
        if not args:
            self._v = [0., 0., 0.]
        elif len(args) == 1:
            self._v = map(float, args[0][:3])                        
        else:
            raise ValueError("Vector3.__init__ takes 0, 1 or 3 parameters")

    def _get_0(self):   
        return self._v[0]
    
    def _get_1(self):
        return self._v[1]
    
    def _get_2(self):
        return self._v[2]
    
    def _set_0(self, value):
        self._v[0] = value
        
    def _set_1(self, value):
        self._v[1] = value
        
    def _set_2(self, value):
        self._v[2] = value
        
    _getters = (_get_0, _get_1, _get_2)
    _setters = (_set_0, _set_1, _set_2)
       
    @classmethod
    def from_points(cls, p1, p2):
        
        v = cls.__new__(cls, object)
        ax, ay, az = p1
        bx, by, bz = p2        
        v._v = [bx-ax, by-ay, bz-az]
        
        return v        
       
    @classmethod
    def from_floats(cls, *args):
        """Creates a Vector3 from individual float values.
        Warning: There is no checking for efficiency here: x, y, z _must_ be
        floats.
        
        """
        v = cls.__new__(cls, object)
        v._v = list(args)
        return v
    

    @classmethod
    def from_iter(cls, iterable):
        """Creates a Vector3 from an iterable containing at least 3 values."""
        it = iter(iterable)
        v = cls.__new__(cls, object)
        v._v = [ float(it.next()), float(it.next()), float(it.next()) ]        
        return v
    
    def copy():
        """Returns a copy of this vector."""
                
        v = cls.__new__(sel.__class__, object)
        v._v = self._v[:]
        return v
        #return self.from_floats(self._v[0], self._v[1], self._v[2])
    
    __copy__ = copy

    def _get_x(self):
        return self._v[0]
    def _set_x(self, x):
        assert isinstance(x, float), "Must be a float"
        self._v[0] = x
    x = property(_get_x, _set_x, None, "x component.")
    
    def _get_y(self):
        return self._v[1]
    def _set_y(self, y):
        assert isinstance(y, float), "Must be a float"
        self._v[1] = y
    y = property(_get_y, _set_y, None, "y component.")
    
    def _get_z(self):
        return self._v[2]
    def _set_z(self, z):
        assert isinstance(z, float), "Must be a float"
        self._v[2] = z
    z = property(_get_z, _set_z, None, "z component.")
        
    def _get_length(self):
        x, y, z = self._v
        return sqrt(x*x + y*y +z*z)
        
    def _set_length(self, length):        
        v = self._v
        try:
            x, y, z = v
            l = length / sqrt(x*x + y*y +z*z)
        except ZeroDivisionError:
            v[0] = 0.
            v[1] = 0.
            v[2] = 0.        
            return self
        
        v[0] = x*l
        v[1] = y*l
        v[2] = z*l        
        
    length = property(_get_length, _set_length, None, "Length of the vector")
    
    def unit(self):
        """Returns a unit vector."""
        x, y, z = self._v
        l = sqrt(x*x + y*y + z*z)
        return self.from_floats(x/l, y/l, z/l)            
                
        
    def set(self, x, y, z):
        """Sets the components of this vector.
        x -- x component
        y -- y component
        z -- z component
        
        """
        assert ( isinstance(x, float) and 
                 isinstance(y, float) and
                 isinstance(z, float) ), "x, y, z must be floats"
        v = self._v
        v[0] = x
        v[1] = y
        v[2] = z
        return self
        
            
    def __str__(self):
        
        return "(%s, %s, %s)" % (format_number(self._v[0]), format_number(self._v[1]), format_number(self._v[2]))
        
        
    def __repr__(self):
        
        return "Vector3(%s, %s, %s)" % (self._v[0], self._v[1], self._v[2])        
        
        
    def __len__(self):
        
        return 3
    
    def __iter__(self):
                
        return iter(self._v)
        
    def __getitem__(self, index):
       
        try:
            return self._v[index]
        except IndexError:
            raise IndexError, "There are 3 values in this object, index should be 0, 1 or 2!"                        
        
    def __setitem__(self, index, value):
        
        try:
            assert isinstance(value, float), "Must be a float"
            self._v[index] = value
        except IndexError:
            raise IndexError, "There are 3 values in this object, index should be 0, 1 or 2!"


    def __add__(self, rhs):
        """Returns the result of adding a vector (or collection of 3 numbers) from this vector."""
        
        x, y, z = self._v
        ox, oy, oz = rhs        
        return self.from_floats(x+ox, y+oy, z+oz)
        
        
    def __iadd__(self, rhs):
        """Adds another vector (or a collection of 3 numbers) to this vector."""
        x, y, z = self._v
        ox, oy, oz = rhs
        v = self._v
        v[0] = x+ox
        v[1] = y+oy
        v[2] = z+oz        
        return self
        
        
    def __radd__(self, lhs):
        
        x, y, z = self._v
        ox, oy, oz = lhs[:3]        
        return self.from_floats(x+ox, y+oy, z+oz)
    
    
        
    def __sub__(self, rhs):
        """Returns the result of subtracting a vector (or collection of 3 numbers) from this vector."""
        
        x, y, z = self._v
        ox, oy, oz = rhs[:3]
        return self.from_floats(x-ox, y-oy, z-oz)
        
        
    def _isub__(self, rhs):
        """Subtracts another vector (or a collection of 3 numbers) from this vector."""
        
        x, y, z = self._v
        ox, oy, oz = rhs
        v = self._v
        v[0] = x-ox
        v[1] = y-oy
        v[2] = z-oz
        return self
        
    def __rsub__(self, lhs):
        
        x, y, z = self._v
        ox, oy, oz = lhs[:3]
        return self.from_floats(x-ox, y-oy, z-oz)
        
        
    def __mul__(self, rhs):
        """Return the result of multiplying this vector by another vector, or a scalar (single number)."""
        
        x, y, z = self._v
        try:
            return self.from_floats(x*rhs, y*rhs, z*rhs)
        except TypeError:
            ox, oy, oz = rhs
            return self.from_floats(x*ox, y*oy, z*oz)            
            
        
    def __imul__(self, rhs):
        """Multiply this vector by another vector, or a scalar (single number).""" 
            
        v = self._v    
        try:
            x, y, z = v
            v[0] = x * rhs
            v[1] = y * rhs
            v[2] = z * rhs
            #self._v = [x*rhs, y*rhs, z*rhs]
        except TypeError:
            ox, oy, oz = rhs            
            v[0] = x * ox
            v[1] = y * oy
            v[2] = z * oz
                    
        return self
        
        
    def __div__(self, rhs):        
        """Return the result of dividing this vector by another vector, or a scalar (single number)."""
        
        x, y, z = self._v
        try:            
            return self.from_floats(x/rhs, y/rhs, z/rhs)
        except TypeError:
            ox, oy, oz = rhs._v
            return self.from_floats(x/ox, y/oy, z/oz)
                    
            
    def __idiv__(self, rhs):
        """Divide this vector by another vector, or a scalar (single number)."""
        
        v = self._v
        try:
            x, y, z = v
            v[0] = x/rhs
            v[1] = y/rhs
            v[2] = z/rhs            
        except TypeError:
            ox, oy, oz = rhs
            v[0] = x/ox
            v[1] = y/oy
            v[2] = z/oz            
                    
        return self
            
            
    def __neg__(self):
        """Returns the negation of this vector (a vector pointing in the opposite direction.
        eg v1 = Vector(1,2,3)
        print -v1
        >>> (-1,-2,-3)
        
        """
        x, y, z = self._v
        return self.from_floats(-x, -y, -z)
    
    def __pos__(self):
        
        return self
    
    
    def __nonzero__(self):
        
        x, y, z = self._v
        return x and y and z
    
    
    def __call__(self, keys):
        """Returns a tuple of the values in a vector
        
        keys -- An iterable containing the keys (x, y or z)
        eg v = Vector3(1.0, 2.0, 3.0)
        v('zyx') -> (3.0, 2.0, 1.0)
        
        """
        ord_x = ord('x')
        _v = self._v
        return tuple( _v[ord(c)-ord_x] for c in keys )        
             
             
    def as_tuple(self):
        """Returns a tuple of the x, y, z components. A little quicker than
        iter(vector)."""
        
        return tuple(self._v)
        
        
    def scale(self, scale):
        """Scales the vector by onther vector or a scalar. Same as the
        *= operator.
        
        scale -- Value to scale the vector by
        
        """
        v = self._v
        try:
            x, y, z = v
            v[0] = x*rhs
            v[1] = y*rhs
            v[2] = z*rhs            
        except TypeError:
            ox, oy, oz = rhs
            v[0] = x*ox
            v[1] = y*oy
            v[2] = z*oz
                    
        return self
        
        
    def get_length(self):
        """Calculates the length of the vector."""
        
        x, y, z = self._v
        return sqrt(x*x + y*y +z*z)
    get_magnitude = get_length
        
    def set_length(self, new_length):
        """Sets the length of the vector. (Normalises it then scales it)
        
        new_length -- The new length of the vector.
        
        """        
        try:
            x, y, z = self._v
            l = length / sqrt(x*x + y*y + z*z)
        except ZeroDivisionError:
            self.v[:] = [0., 0., 0.]
            return self
            
        v = self._v
        v[0] = x*l
        v[1] = y*l
        v[2] = z*l        
                
        return self
        
        
    def get_distance_to(self, p):
        """Returns the distance of this vector to a point.
        
        p -- A position as a vector, or collection of 3 values.
        
        """
        ax, ay, az = self._v
        bx, by, bz = p
        
        return sqrt( (ax-bx)**2 + (bx-by)**2 + (cx-cy)**2 )    
        
        
    def get_distance_squared(self, p):
        """Returns the squared distance of this vector to a point.
        
        p -- A position as a vector, or collection of 3 values.
        
        """
        ax, ay, az = self._v
        bx, by, bz = p
        
        return ( (ax-bx)**2 + (bx-by)**2 + (cx-cy)**2 )    
        
        
    def normalise(self):
        """Scales the vector to be length 1."""
        x, y, z = self._v        
        l = sqrt(x*x + y*y + z*z)
        v = self._v
        v[0] = x/l
        v[1] = y/l
        v[2] = z/l
        return self        
    normalize = normalise
        
    def get_normalised(self):
        
        x, y, z = self._v        
        l = sqrt(x*x + y*y + z*z)
        return self.from_floats(x/l, y/l, z/l)
    get_normalized = get_normalised
    
    
    def in_sphere(self, sphere):
        """Returns true if this vector (treated as a position) is contained in
        the given sphere.
        
        """
        
        return distance3d(sphere.position, self) <= sphere.radius
     
    def dot(self, other):
        
        """Returns the dot product of this vector with another.
        
        other -- A vector or tuple
        
        """
        x, y, z = self._v
        ox, oy, oz = other
        return x*ox + y*oy + z*oz
    
    def cross(self, other):
        
        """Returns the cross product of this vector with another.
        
        other -- A vector or tuple
        
        """
                
        x, y, z = self._v
        bx, by, bz = other
        return self.from_floats( y*bz - by*z,
                                 z*bx - bz*x,
                                 x*by - bx*y )

    

def distance3d_squared(p1, p2):
    
    return (p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2


def distance3d(p1, p2):
    
    return sqrt( (p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2 )

def centre_point3d(points):
    
    return sum( Vector3(p) for p in points ) / len(points)


if __name__ == "__main__":
    
    v1 = Vector3(2.2323, 3.43242, 1.)
    
    print (1, 2, 3)+v1
    print v1('xxxyyyzzz')
    print v1[2]
    print v1.z
    v1[2]=5.
    print v1    
    v2= Vector3(1.2, 5, 10)
    print v2
    v1 += v2
    print v1.get_length()
    print repr(v1)
    print v1[1]
    
    p1 = Vector3(1,2,3)
    print p1
    print repr(p1)    
    
    for v in p1:
        print v
        
    #print p1[6]
    
    ptest = Vector3( [1,2,3] )
    print ptest
    
    z = Vector3()
    print z
        
    file("test.txt", "w").write( "\n".join(str(float(n)) for n in range(20)) )
    f = file("test.txt")
    v1 = Vector3.from_iter( f )
    v2 = Vector3.from_iter( f )
    v3 = Vector3.from_iter( f ) 
    print v1, v2, v3
    
    print "--"
    print v1
    print v1 + (10,20,30)
    
    print v1('xz')
    
    print -v1

    #print tuple(ptest)
    #p1.set( (4, 5, 6) )
    #print p1
    
    print Vector3(10,10,30)+v1
    