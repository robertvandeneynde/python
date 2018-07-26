f = lambda x: x/2 + 7
g = lambda x: (x - 7) * 2
c = lambda a,b: f(a) <= b <= g(a)

for i in range(50):
    for j in range(50):
        if c(i,j) and not c(j,i):
            print("{},{}".format(i,j))