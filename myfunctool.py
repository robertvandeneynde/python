import itertools

# http://stackoverflow.com/questions/11173660/can-one-partially-apply-the-second-argument-of-a-function-that-takes-no-keyword
def _partial(func, *args, **keywords):
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

class partial:                                     
     def __init__(self, f, *args, **kwargs):
        if args or kwargs:
            self.func = _partial(f, *args, **kwargs) if args or kwargs else f
        
            self.leftmost_args = self.func.leftmost_args
            self.rightmost_args = self.func.rightmost_args
            self.keywords = self.func.keywords
        
        else:
            self.func = f
            self.leftmost_args = ()
            self.rightmost_args = ()
            self.keywords = kwargs
        
     def bind(self, *args, **kwargs):
         return partial(self.func, *args, **kwargs)
     
     def __getitem__(self, args):
         return self.bind(*args) if isinstance(args, tuple) else self.__getitem__((args,))
     
     def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
     def __str__(self):
         return "PartialObject<func={}, leftmost_args={}, rightmost_args={}, keywords={}>".format(self.func, self.leftmost_args, self.rightmost_args, self.keywords)
     
     @staticmethod
     def fix(*args, **kwargs):
         return partial(partial, ..., *args, **kwargs)
     
class auto_partial(partial):
    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except TypeError:
            return self.bind(*args, **kwargs)
    
    @staticmethod
    def fix(*args, **kwargs):
        return partial(auto_partial, ..., *args, **kwargs)

if __name__ == '__main__':
    # Normal function
    f0 = partial(pow)
    
    print(f0(2,3))
    
    # Operator [] or .bind to apply positional arguments partiallity
    # Or constructor
    f1 = partial(pow)[2]
    f1 = partial(pow).bind(2)
    f1 = partial(pow, 2)
    
    print(f1(3))
    
    # auto_partial "guess" within a call if is it a final call or some arguments are missing
    f2 = auto_partial(pow)(2)
    f2 = auto_partial(pow, 2)
    
    print(f2(3))
    
    # Ellipsis can be used as position place holder
    f3 = partial(pow)[..., 3]
    f3 = partial(pow, ..., 3)
    
    print( f3(2) )
    
    # Multiple arguments are easy
    f4 = partial(print)["Hello", ..., 5]
    f4 = partial(print, "Hello", ..., 5)
    
    f4("Bob")
    
    # For keywords arguments, constructor or .bind is required
    f5 = partial(print, "Hello", ..., 5, sep=' ++ ')
    f5 = partial(print, "Hello", ..., 5).bind(sep=' ++ ')
    f5 = partial(print).bind("Hello", ..., 5, sep=' ++ ')
    
    f5("Bob")
        
    # Can be used as a decorator to enhance simple functions
    @partial
    def f(x,y):
        print("{} + {} = {}".format(x, y, x + y))
    
    f[1](2)
    
    # .fix can fix an argument, here y will always be 5. But this is confusing
    
    @partial.fix(..., 5)
    def f(x,y,z):
        print("x", x, "y", y, "z", z)
    
    
    f[1](2)
