
data = '''
Class_6/Class_7 Class_6/Class_2 Class_6/Class_8 Class_6/Class_3 Class_6/Class_5 Class_6/Class_9 Class_6/Class_4 Class_6/Class_1 Class_7/Class_2 
     2.67018628      3.85939323      3.54895040      3.70627688      2.38572059      2.95627386      2.64514805      2.86693719      0.88844380 
Class_7/Class_8 Class_7/Class_3 Class_7/Class_5 Class_7/Class_9 Class_7/Class_4 Class_7/Class_1 Class_2/Class_8 Class_2/Class_3 Class_2/Class_5 
     0.32408862      1.15008197      0.89306986     -0.15721356      0.07583285      0.17653904     -1.14708716      1.04907376      0.88945691 
Class_2/Class_9 Class_2/Class_4 Class_2/Class_1 Class_8/Class_3 Class_8/Class_5 Class_8/Class_9 Class_8/Class_4 Class_8/Class_1 Class_3/Class_5 
    -1.45457855     -1.41524663     -1.36483633      1.32636911      1.11414595     -0.74990466      0.05257464      0.10948572      0.66286561 
Class_3/Class_9 Class_3/Class_4 Class_3/Class_1 Class_5/Class_9 Class_5/Class_4 Class_5/Class_1 Class_9/Class_4 Class_9/Class_1 Class_4/Class_1 
    -1.56014856     -1.88280052     -1.47496370     -1.57218731     -1.06451453     -1.46181281      0.39569564      0.20119714     -0.16430385
'''.strip()
data = '''
Class_6/Class_7 Class_6/Class_2 Class_6/Class_8 Class_6/Class_3 Class_6/Class_5 Class_6/Class_9 Class_6/Class_4 Class_6/Class_1 Class_7/Class_2 
   4.127330e-01   -1.576825e-01   -5.606871e-01    2.021966e-01    7.127359e-01    3.117207e-01    6.196786e-01   -1.146571e-01   -5.471782e-01 
Class_7/Class_8 Class_7/Class_3 Class_7/Class_5 Class_7/Class_9 Class_7/Class_4 Class_7/Class_1 Class_2/Class_8 Class_2/Class_3 Class_2/Class_5 
  -8.676759e-01   -1.588642e-01    7.115747e-01    4.798882e-02    4.919920e-01   -3.870684e-01   -2.376562e-01    1.056907e+00    7.447847e-01 
Class_2/Class_9 Class_2/Class_4 Class_2/Class_1 Class_8/Class_3 Class_8/Class_5 Class_8/Class_9 Class_8/Class_4 Class_8/Class_1 Class_3/Class_5 
   4.293579e-01    9.942105e-01    1.186823e-01    6.101743e-01    9.607564e-01    7.934963e-01    8.980752e-01    4.729189e-01    5.083349e-01 
Class_3/Class_9 Class_3/Class_4 Class_3/Class_1 Class_5/Class_9 Class_5/Class_4 Class_5/Class_1 Class_9/Class_4 Class_9/Class_1 Class_4/Class_1 
  -9.952567e-05    9.696188e-01   -2.098734e-01   -6.541823e-01   -3.483338e-01   -7.520886e-01    1.724717e-01   -1.883524e-01   -5.623264e-01
'''.strip()

bags = {}
for i, line in enumerate(data.split("\n")):
    if i % 2 == 0:
        headers = [c.split("/") for c in line.strip().split()]
    else:
        datas = map(float, line.strip().split())
        for (h1, h2), d in zip(headers, datas):
            bags[h1] = bags.get(h1, 0) + d
            bags[h2] = bags.get(h2, 0) + d
print(max(bags.items(), key=lambda it:it[1]))