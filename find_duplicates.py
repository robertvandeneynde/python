#!/usr/bin/env python3

"""
Simple O(n²) algorithm to find duplicates file
"""

import re, sys, os, argparse

parser = argparse.ArgumentParser()
parser.add_argument('files', nargs='+')
parser.add_argument('--shallow', action='store_true')
parser.add_argument('-v', '--different', '--inverted', help='print files that differ instead of files that are equal', action='store_true')

a = args = parser.parse_args()

import filecmp

files = args.files
flip = args.different  # = True if args.different else False

N = len(files)
for i in range(N):
    for j in range(i+1, N):
        if filecmp.cmp(files[i], files[j], shallow=args.shallow) ^ flip:
            print(repr(files[i]), '=' if not flip else '!=', repr(files[j]))
