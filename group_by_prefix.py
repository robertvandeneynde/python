#!/usr/bin/env python
from __future__ import print_function

import sys

if sys.version_info[0] <= 2:
    input = raw_input

import os, argparse, re

p = argparse.ArgumentParser(description='Given a prefix, creates a directory, move all files in current dir beginning with that prefix in that directory, and rename them removing the prefix')

p.add_argument('prefix', help='prefix to use or special value :longuest to use the longest prefix of all files (or dirs if --only-directories)')
p.add_argument('--only-directories', action='store_true', help='do not include simple files, only dirs')
p.add_argument('--dir', '--directory', default='.', help='use this directory instead of current directory')
p.add_argument('-v', '--verbose', action='store_true', help='')

g = p.add_mutually_exclusive_group()
g.add_argument('--no-rename', action='store_true', help='do not do the rename part, only moving')
g.add_argument('--rename', action='store_true', help='(default) rename the files, removing the prefix')
g.add_argument('--no-special-chars', action='store_true', help='(default: prompt) do not do the rename part, only moving')
g.add_argument('--special-chars', action='store_true', help='(default: prompt) do not do the rename part, only moving')

def modify_args(args):
    a = args

    if a.prefix == ':longuest':
        a.prefix = longuest_prefix(os.listdir(a.dir))

    a.special_chars_is_set = a.special_chars or a.no_special_chars
    a.special_chars ^= not a.no_special_chars
    
    return args

def longuest_prefix(iterable):
    lines = iter(iterable)
    prefix = next(lines, None)
    for l in lines:
        i = len(prefix)
        while prefix[:i] != l[:i]:
            i -= 1
        prefix = prefix[:i]
        if prefix == '':
            break
    return prefix

args = modify_args(p.parse_args())
prefix = args.prefix

if not os.path.isdir(prefix):
    os.mkdir(prefix)

L = []
Renames = []
for l in os.listdir(args.dir):
    dir = True if not args.only_directories else os.path.isdir(l)
    if dir and l != prefix and l.startswith(args.prefix):
        L.append(l)
        nl_base = l[len(args.prefix):] if not args.no_rename else l
        nl_base_new = re.sub('^([.*-]|\s)+', '', nl_base)
        if nl_base != nl_base_new:
            Renames.append((nl_base, nl_base_new, prefix))
        os.rename(l, os.path.join(prefix, nl_base))

if not args.no_special_chars and Renames:
    if args.verbose or not args.special_chars_is_set:
        print('There are', len(Renames), 'files that starts with weird characters like . <space> * or -')
        print('\n'.join('- ' + repr(a) for a,b,d in Renames))
    if args.special_chars if args.special_chars_is_set else input('Rename ? (Y/n) ').lower() != 'n':
        for a,b,d in Renames:
            os.rename(os.path.join(d,a), os.path.join(d,b))
            if args.verbose:
                print('`' + os.path.join(d,a) + '`', '->', '`' + os.path.join(d,b) + '`')
                
if args.verbose and L:
    print('\n'.join(L))
print(len(L), 'files')
