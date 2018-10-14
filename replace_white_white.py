#!/usr/bin/env python3

import argparse, sys

p = argparse.ArgumentParser()
p.add_argument('file')
p.add_argument('--color', default='#aaaaaa')
args = p.parse_args()

import re
if re.compile('[A-Z0-9]{3}', re.I).fullmatch(args.color):
    args.color = ''.join(c * 2 for c in args.color) 
if re.compile('[A-Z0-9]{6}', re.I).fullmatch(args.color):
    args.color = '#' + args.color.lower()
assert re.fullmatch('#[a-f0-9]{6}|[A-Za-z]+', args.color), f"Wrong color argument: {args.color}"

with open(args.file) as f:
    r = f.read()
sys.stdout.write(r.replace('color:#ffffff;background-color:#ffffff', 'color:{};background-color:#ffffff'.format(args.color)))
