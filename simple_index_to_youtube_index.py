#!/usr/bin/env python3
# coding: utf-8
import argparse
p = argparse.ArgumentParser()
p.add_argument('file', nargs='?', default=None)
args = p.parse_args()

if args.file:
    assert args.file.endswith('.txt'), "must be a txt file"

import sys
import re

try:
    from generate_utils import OutFileGreen as OutFile
except ImportError:
    OutFile = open

with (open(args.file) if args.file else sys.stdin) as f:
    L = [x.strip('\n') for x in f]
    
for i in range(len(L)):
    try:
        a,b,c = re.compile('(\d+) (\d+)(.*)').fullmatch(L[i]).groups()
    except AttributeError:
        print('Line {!r} did not match'.format(L[i]))
        continue
    L[i] = a.zfill(2) + ':' + b.zfill(2) + c

with (OutFile(args.file + '.index', 'w') if args.file else sys.stdout) as f:
    f.write('\n'.join(L))
    
    
