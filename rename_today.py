#!/usr/bin/env python3
import argparse
p = argparse.ArgumentParser()
p.add_argument('files', nargs='+')
args = p.parse_args()

import os
assert all(map(os.path.isfile, args.files))

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

N = datetime.now()
def f(n):
    return (N + timedelta(days=n)).strftime('%a-%d-%b-%Y').lower()
def g():
    return N.strftime('%a-%d-%b-%Y_%H:%M_%S').lower()

renamer = Renamer()
for old in args.files:
    new = (old.replace('now', g())
              .replace('today', f(0))
              .replace('yesterday', f(-1))
              .replace('tomorrow', f(1)))
    renamer.rename(old, new)
