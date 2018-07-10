Always wanted to add custom operators ?

    a = 2 + (1,2,3) /dot/ (4,5,6)  # a = 2 + dot((1,2,3), (4,5,6))
    Y = [1,2,7,0,2,0] |no_zero |plus_one  # Y == [2,3,8,3]
    square = elipartial(pow, ..., 2)  # square = lambda x: pow(x, 2)
    display = hex /compose/ ord  # display = lambda x: hex(ord(x))

This example shows how infix operators can be created,
the library also introduces bash like _pipes_ and
shortcuts to create partial functions or function
composition inspired by functional languages.
    
# infix

Infix operators can be created using the `infix` class.

It works for existing functions, like `numpy.dot`:

    import numpy
    dot = infix(numpy.dot)
    a = (1,2,3) /dot/ (4,5,6)  # use as an infix

If you already have `dot` in your namespace, don't worry, it still works as a function:

    a = dot((1,2,3), (4,5,6))  # still works as a function

Or for custom functions as a decorator:

    @infix
    def crunch(x,y):
        """
        Do a super crunchy operation between two numbers.
        """
        return x + 2 * y

    a = 1 |crunch| 2  # a = crunch(1, 2)
    a = crunch(1, 2)  # still works
    help(crunch.function)  # to get help about the initial function

Any binary operator can be used like `1 *f* 2`, `1 %f% 2` or `1 << f << 2` but `/` or `|` should be clean for all use cases.
Beware if you use `**`, the operator is right to left:
    
    b = 1 **f** 2  # a = f(2, 1)

# dot and cross product

Dot and cross products are used heavily in mathematics and physics as an infix operator `·` or `×`.

    a = (1,2,3) /dot/ (4,5,6)
    a = (1,2,3) |dot| (4,5,6)  # same 
    r = 2 + (1,2,3) /dot/ (4,5,6)  # here "/" has priority over + like in normal python
    r = 2 + (1,2,3) *dot* (4,5,6)  # for a dot PRODUCT, '*' seems logical
    r = 2 + dot((1,2,3), (4,5,6))  # still works as a function

# using '|' for low priority

In some use cases, one want to mix classic operators with function operators,
the `|` operator may be used as a low priority operator.

    Y = A + B |dot| C  # is parsed as Y = (A + B) |dot| C
    Y = A + B /dot/ C  # is parsed as Y = A + (B /dot/ C)

# fractions

When using the `fractions` module, often you want to transition from `floats` to `Fraction`.
Your current code uses `/` for division and you can just replace the slashes with `/frac/`, the mathematical stays natural to read!

    from fractions import Fraction
    frac = infix(Fraction)
    a = 1 + 1 / 3  # 1.3333...
    a = 1 + 1 /frac/ 3  # Fraction(4, 3)
    b = 2 * (a + 3) /frac/ (a + 1)  # nicer complex expressions

# ranges, 2..5 in ruby ?

In many languages, iterating over a range has a notational shortcut, like `2..5` in ruby.
Now you can even write `for i in 1 /inclusive/ 5` in python.

    @infix
    def inclusive(a,b):
        return range(a, b+1)

    for i in 2 /inclusive/ 5:
        print(i)  # 2 3 4 5

    for i in inclusive(2, 5):
        print(i)  # 2 3 4 5

However, redefining range = infix(range) is a bad idea because it would break code like `isinstance(x, range)`.
In that particuliar example, I would choose `exclusive = infix(range)`.

# isinstance (Java and Js instanceof)

In Java and Javascript, testing the class of an object is done via `x instanceof Class`,
the python builtin `isinstance` could be enhanced with infix notation or renamed to `instanceof`.

    isinstance = infix(isinstance)
    assert 1 /isinstance/ int
    assert [] /isinstance/ (list, tuple)
    assert 1 / 2 |isinstance| float

# pipes : postfix

In bash, a functionality called _pipes_ is useful to reuse an expression and change the behavior by just adding code _at the end_.
The library can be used for that.

    @postfix
    def no_zero(L):
        return [x for x in L if x != 0]

    @postfix
    def plus_one(L):
        return [x+1 for x in L]

    Y = [1,2,7,0,2,0] |no_zero |plus_one  # Y == [2,3,8,3]
    Y = plus_one(no_zero([1,2,7,0,2,0]))  # Y == [2,3,8,3]

# pipe factory

Sometimes, pipes want extra information, for example in our last example, `no_zero` is a special case of a pipe that filters out a value,
use the `pipe factory` recipe like so:

    def filter_out(x):
        @postfix
        def f(L):
            return [y for y in L if y != x]
        return f

    L = [1,2,7,0,2,0] | filter_out(0)  # Y == [2,3,8,3]

# function compose (alias circle)

In mathematics and functional programming languages, [function composition](https://en.wikipedia.org/wiki/Function_composition) is naturally used using a `circle` operator to write things like `h = f ∘ g`.

    s = hex(ord('A'))  # s = '0x41'

    from funcoperators import compose
    display = hex /compose/ ord
    s = display('A')  # s = '0x41'

    display = hex *circle* ord 

# partial syntax

The library adds sugar to functools, called `curry`, the names comes from other languages.

    def f(x,y):
        return x + y
    
    from funcoperators import curry
    g = f /curry/ 5
    y = f(2)  # y = 7

    from funcoperators import partially
    @partially
    def f(x,y,z):
        return x + y + z

    r = f(1,2,3)
    r = f[1](2,3)
    r = f[1][2][3]()
    # NOT: f[1,2] which will give one argument: a tuple

# partiallyauto

In functional languages, function composition is sometimes not dissociable from function call,
`partiallyauto` only works for methods with N fixed positional arguments.

    @partiallyauto
    def f(x,y,z):
        return x + y + z

    r = f(1,2,3)    # r = 6
    r = f(1)(2)(3)  # r = 6
    r = f(1)(2,3)   # r = 6
    g = f(1)    # g = a function with two arguments 
    r = g(2,3)  # r = 6
    k = g(2)    # k = a function with one argument

# elipartial, elicurry (alias `with_arguments` and `deferredcall`)
    
Python's `functools.partial` only works for arguments that will be provided later, one must use keywords arguments.
However, not all functions do keywords arguments.

    square = curryright(pow, 2)  # square(x) = x ** 2

The library also proposes to use Python's `...` (`Ellipsis`) as a natural placeholder for arguments.
    
    tenexp = elipartial(pow, 10)  # = pow(10, something)
    y = tenexp(2)  # 10 ** 2
    square = elipartial(pow, ..., 2)  # = pow(something, 2)
    y = square(5)  # 5 ** 2
    
Here as a more complex example, we define `show` to be the `print` function with arguments `1`, _something_, `3` and keyword argument `sep='.'`.

    show = print | elicurry(1, ..., 3, sep='/')
    show(2)  # prints 1/2/3
    
# see more examples in the test cases in [source code](https://github.com/robertvandeneynde/python/blob/master/funcoperators.py)
