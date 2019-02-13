#!/usr/bin/env python3
import argparse
from textwrap import dedent

p = parser = aragparse.ArgumentParser(help=dedent('''
        stuff
        __ convention
    ''').strip('\n'))

p.add_argument("files", nargs='+')
p.add_argument("--out", "-o", nargs='+')

args = parser.parse_args()

def new_name(x):
    import os
    from itertools import count, filterfalse
    splitext = os.path.splitext
    a,b = splitext(x)

    def first_not_exists(x):
        return next(filterfalse(os.path.exists, x))

    return first_not_exists('{}__{}{}'.format(a, i, b)
                            for i in count(1))

if args.out:
    assert len(args.files) == len(args.out)
else:
    args.out = list(map(new_name, args.files))

