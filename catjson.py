#!/usr/bin/env python3
from __future__ import print_function
import sys, json

import argparse
p = argparse.ArgumentParser()
p.add_argument('files', nargs='+')
p.add_argument('--names', action='store_true')
a = p.parse_args()

for n in a.files:
    if a.names:
        print("==> {} <==".format(n))
    with open(n) as f:
        print(json.dumps(json.load(f), indent=2))
