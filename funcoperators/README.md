Always wanted to add custom operators to your functions ?

```python
a = 2 + (1,2,3) /dot/ (4,5,6)                 # a = 2 + dot((1,2,3), (4,5,6))
Y = [1,2,7,0,2,0] |no_zero |plus(1) |to(set)  # Y == {2,3,8}
square = elipartial(pow, ..., 2)              # square = lambda x: pow(x, 2)
display = hex *compose* ord                   # display = lambda x: hex(ord(x))
```

This example shows how infix operators can be created,
the library also introduces bash like _pipes_ and
shortcuts to create partial functions or function
composition inspired by functional languages.

# Using infix

Infix operators can be created using the `infix` class.

It works for existing functions, like `numpy.dot`:

```python
import numpy
dot = infix(numpy.dot)
a = (1,2,3) /dot/ (4,5,6)  # use as an infix
```

If you already have `dot` in your namespace, don't worry, it still works as a function:

```python
a = dot((1,2,3), (4,5,6))  # still works as a function
```

Or for custom functions as a decorator:

```python
@infix
def crunch(x,y):
    """
    Do a super crunchy operation between two numbers.
    """
    return x + 2 * y

a = 1 |crunch| 2  # a = crunch(1, 2)
a = crunch(1, 2)  # still works
help(crunch.function)  # to get help about the initial function
```

Any binary operator can be used, `1 |f| 2` can be written `1 *f* 2`, `1 %f% 2` or `1 << f << 2` but `/` or `|` should be clean for all use cases.
Beware if you use `**`, the operator is right to left:
    
```python
b = 1 **f** 2  # a = f(2, 1)
```

# Useful for dot and cross product

Dot and cross products are used heavily in mathematics and physics as an infix operator `·` or `×`.

```python
import numpy
dot = infix(numpy.dot)

a = (1,2,3) /dot/ (4,5,6)
a = (1,2,3) |dot| (4,5,6)  # same 
r = 2 + (1,2,3) /dot/ (4,5,6)  # here "/" has priority over "+" like in normal python
r = 2 + (1,2,3) *dot* (4,5,6)  # for a dot PRODUCT, "*" seems logical
r = 2 + dot((1,2,3), (4,5,6))  # still works as a function

cross = infix(numpy.cross)
tau = (1,2) /cross/ (3,4)
Z = (1,2,3) /cross/ (4,5,6)
```

# Using `|` for low priority

In some use cases, one want to mix classic operators with function operators,
the `|` operator may be used as a low priority operator.

```python
Y = A + B |dot| C  # is parsed as Y = (A + B) |dot| C
Y = A + B /dot/ C  # is parsed as Y = A + (B /dot/ C)
```

# Useful for fractions

When using the `fractions` module, often you want to transition from `float` to `Fraction`.
Your current code uses `/` for division and you can just replace the slashes with `/frac/`, the expression stays natural to read.

```python
from fractions import Fraction
frac = infix(Fraction)
a = 1 + 1 / 3  # 1.3333...
a = 1 + 1 /frac/ 3  # Fraction(4, 3)
b = 2 * Fraction(a + 3, a + 1)  # very different from '(a + 3) / (a + 1)'
b = 2 * (a + 3) /frac/ (a + 1)  # almost identical to '(a + 3) / (a + 1)'
```

# Useful for ranges, do you like `2..5` in ruby?

In many languages, iterating over a range has a notational shortcut, like `2..5` in ruby.
Now you can even write `for i in 1 /inclusive/ 5` in python.

```python
@infix
def inclusive(a,b):
    return range(a, b+1)

for i in 2 /inclusive/ 5:
    print(i)  # 2 3 4 5

for i in inclusive(2, 5):
    print(i)  # 2 3 4 5
```

However, redefining `range = infix(range)` is a bad idea because it would break code like `isinstance(x, range)`.
In that particuliar example, I would choose `exclusive = infix(range)`.

# Useful for isinstance, do you like `instanceof` in Java and Js?

In Java and Javascript, testing the class of an object is done via `x instanceof Class`,
the python builtin `isinstance` could be enhanced with infix notation or be renamed to `instanceof`.

```python
isinstance = infix(isinstance)
assert 1 /isinstance/ int
assert [] /isinstance/ (list, tuple)
assert 1 / 2 |isinstance| float
```

# Useful for pipes: postfix (alias to)

In bash, a functionality called _pipes_ is useful to reuse an expression and change the behavior by just adding code _at the end_.
The library can be used for that.

```python
@postfix
def no_zero(L):
    return [x for x in L if x != 0]

@postfix
def plus_one(L):
    return [x+1 for x in L]

Y = [1,2,7,0,2,0] |no_zero |plus_one  # Y == [2,3,8,3]
Y = plus_one(no_zero([1,2,7,0,2,0]))  # Y == [2,3,8,3]
```

Using `to = postfix` makes it quite readable in a pipe.

```python
>>> from funcoperators import postfix as to  # funcoperators version 0.x
>>> from funcoperators import to             # funcoperators version 1.x
>>> 'hello' |to(str.upper) |to(lambda x:x + '!') |to('I said "{}"'.format) |to(print)
I said "HELLO!"
>>> print('I said "{}"'.format('hello'.upper() + '!'))
I said "HELLO!"
```

# Pipes with arguments: pipe factory

Sometimes, pipes want extra information, for example in our last example, `no_zero` is a special case of a pipe that filters out a value,
use the _pipe factory_ recipe like so:

```python
def filter_out(x):
    @postfix
    def f(L):
        return [y for y in L if y != x]
    return f

# shorter with a lambda
def filter_out(x):
    return postfix(lambda L:[y for y in L if y != x])

L = [1,2,7,0,2,0] | filter_out(0)  # L == [2,3,8,3]

from funcoperators import mapwith
s = '1 2 7 2'.split() | mapwith(int) | to(sum)  # s = 12 = sum(map(int, '1 2 7 2'.split()))

from funcoperators import mapwith as Map
from funcoperators import filterwith as Filter
S = '1 2 7 2'.split() | Map(int) | Filter(lambda x:x < 5) | to(set)
```

# Useful for format and join

```python
>>> 42 | format /curryright/ 'x'
'2a'
>>> formatwith = lambda fmt: postfix(lambda value: format(value, fmt))
>>> 52 |formatwith('x')
'2a'
>>> from funcoperators import to
>>> 3.1415 |to('{:.02}'.format)
'3.1'
>>> [1, 2, 7, 2] |mapwith(str) |to('/'.join) |to(print)
1/2/7/2
```

# Function composition (compose, alias circle)

In mathematics and functional programming languages, [function composition](https://en.wikipedia.org/wiki/Function_composition) is naturally used using a `circle` operator to write things like `h = f ∘ g`.

```python
s = hex(ord('A'))  # s = '0x41'

from funcoperators import compose
display = hex /compose/ ord
s = display('A')  # s = '0x41'

display = hex *circle* ord

from funcoperators import compose as o
display = hex -o- ord  # looks like a dot
```

`compose` can have more than two functions.

```python
f = compose(str.upper, hex, lambda x:x+1, ord)  # simple function
f = str.upper /compose/ hex /compose/ (lambda x:x+1) /compose/ ord  # operator
```

## Using call for inline compose

```python
>>> print(5 + 2 * 10, 'B', sep='/')
25
>>> print |call(5 + 2 * 10, 'B', sep='/')
25/B
>>> print(','.join('abcdef' + 3 * 'x'))
a,b,c,d,e,f,x,x,x
>>> print *compose* ' '.join |call('abcdef' + 3 * 'x')
a,b,c,d,e,f,x,x,x
>>> compose(print, ','.join) |call('abcdef' + 3 * 'x')
a,b,c,d,e,f,x,x,x
```

```python
>>> len |infixcall| 'hallo' * 3
15
```

```python
>>> print |callargs| ('a', 5)
a 5
```

# More partial syntax

The library adds sugar to functools.partial, using functions called `curry` (and variants like `curryright`, `simplecurry`) and `partially`. The name `curry` comes from other languages.

```python
def f(x,y,z):
    return x + y + z

from funcoperators import curry
g = f /curry/ 5
y = f(2,1)  # y = 8

from funcoperators import curryright
square = pow /curryright/ 2  # square(x) = x ** 2
square = curryright(pow, 2)  # square(x) = x ** 2

from funcoperators import provide_right  # alias provide_right = curryright
square = provide_right(pow, 2)  # square(x) = x ** 2
square = pow /provide_right/ 2  # square(x) = x ** 2

from funcoperators import simplecurry
g = f |simplecurry(1, z=3)
y = g(2)
```

`partially` allows to _upgrade_ a function to provide methods like `f.partial` and provides `f[arg]` to curry.

```python
from funcoperators import partially
@partially
def f(x,y,z):
    return x - y + 2 * z

r = f(1,2,3)
g = f[1]  # g = a function with two arguments: y,z
r = g(2,3)
r = f[1](2,3)
r = f[1][2][3]()
# Notice that "f[1,2]" doesn't work because it gives only one argument: a tuple (@see partiallymulti)

g = f[1]  # gives positional arguments
g = f.val(1)  # gives positional arguments
g = f.key(z=3)  # gives keyword arguments
g = f.partial(1, z=3)  # gives positional and keyword arguments

# alias part = assuming = given = where = partial
g = f.part(1, z=3)
g = f.where(1, z=3)
g = f.given(1, z=3)
```

`partiallymulti` allows `f[arg1, arg2]`.
   
```python
from funcoperators import partiallymulti
@partiallymulti
def f(x,y,z):
    return x - y + 2 * z

r = f(1,2,3)
g = f[1,2]  # g = a function with one argument: z
r = g(3)
```

# Using partiallyauto

In functional languages, function composition is sometimes not dissociable from function call,
`partiallyauto` only works for methods with N fixed positional arguments.

```python
@partiallyauto
def f(x,y,z):
    return x - y + 2 * z

r = f(1,2,3)    # r = 6
r = f(1)(2)(3)  # r = 6
r = f(1)(2,3)   # r = 6
g = f(1)    # g = a function with two arguments 
r = g(2,3)  # r = 6
k = g(2)    # k = a function with one argument
```

# Using Ellipsis
    
Python's `functools.partial` only works for arguments that will be provided later, one must use keywords arguments.
However, not all functions accept keywords arguments, like the builtin `pow`, one can use `curryright` because pow only has two arguments.

```python
square = curryright(pow, 2)  # square(x) = x ** 2
```

The library also proposes to use Python's `...` (`Ellipsis`) as a natural placeholder for arguments.
The functions using this convention have a name beginning with `eli`.
   
```python
tenexp = elipartial(pow, 10)  # = pow(10, something)
y = tenexp(2)  # 10 ** 2
square = elipartial(pow, ..., 2)  # = pow(something, 2)
y = square(5)  # 5 ** 2
square = pow |elicurry(..., 2)  # = pow(something, 2)
y = square(5)  # 5 ** 2
```

If you like the `partially` and `partiallymulti` syntax, there is `bracket` that has all the concepts in one class.

```python
@bracket
def f(x,y,z):
    return x - y + 2 * z

r = f(1,2,3)
g = f[1, ..., 3]  # g = a function with one argument: y
r = g(2)
g = f.partial(1, ..., 3)  # as a method
g = f.partial(1, z=3)     # allowing keyword arguments
```

Here is a more complex example using `elicurry`, we define `show` to be the `print` function with arguments `1`, _something_, `3` and keyword argument `sep='/'`.

```python
show = print |elicurry(1, ..., 3, sep='/')
show(2)  # prints 1/2/3
```

Let's note that `elicurry` has many aliases:

```python
show = print |elicurry(1, ..., 3, sep='/')
show = print |with_arguments(1, ..., 3, sep='/')
show = print |deferredcall(1, ..., 3, sep='/')
show = print |latercall(1, ..., 3, sep='/')
```
    
# More examples

See more examples in the test cases in [source code](https://github.com/robertvandeneynde/python/blob/master/funcoperators.py).

# Release Notes
Version 1.0 created some non backward-compatible change (`call`) and included useful use cases (`to`, `mapwith`)
