class Vec(tuple):
    
    def __repr__(self):
        return "Vec({})".format(tuple(self))
    
    def __add__(self, other):
        return Vec(a + b for a,b in zip(self,other))
    
    def __radd__(self, other):
        return Vec(b + a for a,b in zip(self,other))

    def __sub__(self, other):
        return Vec(a - b for a,b in zip(self,other))
    
    def __rsub__(self, other):
        return Vec(b - a for a,b in zip(self,other))
    
    def __mul__(self, scalar):
        return Vec(a * scalar for a in self)
    
    def __rmul__(self, scalar):
        return Vec(scalar * a for a in self)
    
    def __div__(self, scalar):
        return Vec(a / scalar for a in self)
    
    def __truediv__(self, scalar):
        return Vec(a / s for a in self)
    
    def __floordiv__(self, scalar):
        return Vec(a // scalar for a in self)
    
    def __neg__(self):
        return Vec(-a for a in self)

    def __pos__(self):
        return Vec(+a for a in self)
    
    def __getattribute__(self, name):
        """ To support vec.x, vec.y, vec.z"""
        return self[ord(name) - ord('x')]
    
    def dot(self, other):
        return sum(a*b for a,b in zip(self,other))
    
    def __abs__(self):
        from math import sqrt
        return sqrt(Vec.dot(self,self))
    
    def length():
        return abs(self)
    
    def length_squared(self):
        return self.dot(other)