#!/usr/bin/env python3
import argparse
p = argparse.ArgumentParser()
p.add_argument('files', nargs='*', help='files to rename, default to all files in current dir')
# p.add_argument('-f', '-y', '--force', action='store_true', help='do not prompt, say yes to all questions')
g = p.add_mutually_exclusive_group()
g.add_argument('--iso', action="store_true", help='use yyyy-mm-dd date format')
g.add_argument('--iso-minutes', '--iso-time', action="store_true", help='use yyyy-mm-dd_HH-MM date format')
g.add_argument('--iso-seconds', action="store_true", help='use yyyy-mm-dd_HH-MM-SS date format')
args = p.parse_args()

import os
args.file = args.files or list(filter(os.path.exists, os.listdir()))
assert all(map(os.path.exists, args.files))  # all(map(os.path.isfile OR os.path.directory, args.files))

date_format = ('%Y-%m-%d' if args.iso else
               '%Y-%m-%d_%H-%M' if args.iso_minutes else
               '%Y-%m-%d_%H-%M-%S' if args.iso_seconds else 
               '%a-%d-%b-%Y_%H:%M_%S')

datetime_format = ('%Y-%m-%d_%H-%M-%S' if args.iso else 
                   '%Y-%m-%d_%H-%M' if args.iso_minutes else 
                   '%Y-%m-%d_%H-%M-%S' if args.iso_seconds else 
                   '%a-%d-%b-%Y')

try:
    from file_renaming import Renamer
except ImportError:
    class Renamer:
        def __init__(self):
            self.trycount = 0
        def rename(self, a, b):
            import os
            if a == b:
                return
            if self.trycount >= 5 or input('Rename {!r} -> {!r}? [Y/n]'.format(a,b)).lower() not in ('n', 'no', 'non'):
                os.rename(a, b)
            else:
                self.trycount += 1

from datetime import datetime, timedelta
from itertools import chain

N = datetime.now()
f = lambda n: (N + timedelta(days=n)).strftime(date_format).lower()
g = lambda: N.strftime(datetime_format).lower()

renamer = Renamer()
for old in chain(
        filter(os.path.isfile, args.file),
        filter(os.path.isdir, args.file)):  # dir after for weird file nesting like rename_today today/ today/today.txt
    new = (old.replace('now', g())
              .replace('today', f(0))
              .replace('yesterday', f(-1))
              .replace('tomorrow', f(1)))
    renamer.rename(old, new)
