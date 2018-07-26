functions = [
    (lambda x: x),
    (lambda x: int(x)),
    (lambda x: int(x+0.5)),
    # (lambda x: int(x+0.25)),
    # (lambda x: int(x+0.75)),
    # (lambda x: int(x-0.5)),
    # (lambda x: int(x-0.25)),
    # (lambda x: int(x-0.75))
]

means = [
    lambda x,y: (x + y) / 2,
    lambda x,y: (x * y) ** 0.5
]

x = 0
while x < 20:
   x += 0.25
   for i,f in enumerate(functions):
     for j,g in enumerate(functions):
       for k,m in enumerate(means):
         if f(m(g(11.25), x)) == 13 and f(m(g(16.75), x)) == 17:
           print(i, j, k, x)