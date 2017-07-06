#!/usr/bin/env python
import argparse

p = argparse.ArgumentParser(description='Prints each line of a file without their commmon prefix')

p.add_argument('file')
p.add_argument('--prefix', action='store_true', help='print prefix')
p.add_argument('--prefix-length', action='store_true', help='print prefix length')
p.add_argument('--all-stripped-lines', action='store_true', help='(default) print all striped lines')

a = args = p.parse_args()

if not (a.prefix or a.prefix_length or a.all_stripped_lines):
    a.all_stripped_lines = True

lines = iter(l.strip('\n') for l in open(args.file))
l = next(lines)
prefix = l

for l in lines:
   i = len(prefix)
   while prefix[:i] != l[:i]:
       i = i - 1
   prefix = prefix[:i]

if args.prefix:
    print(prefix)
if args.prefix_length:
    print(len(prefix))

if args.all_stripped_lines:
    for l in open(args.file):
        print(l[len(prefix):])
