"""Python AST pretty-printer.

This module exports a function that can be used to print a human-readable
version of the AST.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import sys
import ast
# from ast import Node
import re

__all__ = ('printAst',)

def printAst(ast, indent='  ', stream=sys.stdout, initlevel=0):
    "Pretty-print an AST to the given output stream."
    rec_node(ast, initlevel, indent, stream.write)
    stream.write('\n')

def rec_node(node, level, indent, write):
    "Recurse through a node, pretty-printing it."
    pfx = indent * level
    if isinstance(node, Node):
        write(pfx)
        write(node.__class__.__name__)
        write('(')

        if any(isinstance(child, Node) for child in node.getChildren()):
            for i, child in enumerate(node.getChildren()):
                if i != 0:
                    write(',')
                write('\n')
                rec_node(child, level+1, indent, write)
            write('\n')
            write(pfx)
        else:
            # None of the children as nodes, simply join their repr on a single
            # line.
            write(', '.join(repr(child) for child in node.getChildren()))

        write(')')

    else:
        write(pfx)
        write(repr(node))


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()

    import traceback
    for fn in args.files:
        print('\n\n%s:\n' % fn)
        try:
            printAst(compiler.parseFile(fn), initlevel=1)
        except SyntaxError:
            traceback.print_exc()

    
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

def main2(): 
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    with open(args.filename) as f:
        pretty(f.read(), filename=args.filename)

if __name__ == '__main__':
    main2()
