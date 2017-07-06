import ast
import re

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    
def pretty(string, *args, **kwargs):
    s = ast.dump(ast.parse(string), *args, **kwargs)
    i = 0
    # it = itertools.count(1)
    for x in re.findall('([^()\[\]]+|.)', s): # (''.join(b) for a,b in groupby(s, lambda x: next(it) if x in '([])' else 0)):
        if x in '([':
            i += 1
        elif x in '])':
            i -= 1
        else:
            print(i * ' ', x.lstrip(',').lstrip())
 
if __name__ == '__main__':
    with open(parser.filename) as f:
        pretty(f.read(), filename=parser.filename)