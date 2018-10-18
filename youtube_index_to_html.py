#!/usr/bin/env python3
import argparse
p = argparse.ArgumentParser()
p.add_argument('baselink')
p.add_argument('txt_file')
p.add_argument('--no-time', action='store_true', help='do not display the times')
args = p.parse_args()
baselink, txt_file = args.baselink, args.txt_file
with_times = not args.no_time

assert txt_file.endswith('.txt')
new_name = txt_file + '.html'

import sys, html
from re import compile as Re
import generate_utils
try: from generate_utils import OutFileGreen as OutFile
except ImportError:
    OutFile = open

with open(txt_file) as file:
    string = file.read()

R = Re('\d?\d:\d+\d+')
A = R.split(string)
B = R.findall(string)

if not(A and A[0].strip() == ''):
    raise ValueError("Must begin with a time")

assert len(A) == 1 + len(B), "the programmer did not understand re.split and re.findall"

bits = []
for i in range(len(B)):
    b,a = A[i+1], B[i]
    x,y = a.split(':')
    x,y = int(x), int(y)
    time = x * 60 + y
    title = html.escape(b)
    if with_times:
        title = a + ' ' + title
    bits.append(f'<li><a href="{baselink}&amp;t={time}">{title}</a></li>')

with OutFile(new_name, 'w') as out:
    out.write('<ul>{}</ul>'.format('\n'.join(bits)))
