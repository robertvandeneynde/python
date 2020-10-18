#!/usr/bin/env python3
import argparse
p = parser = argparse.ArgumentParser()
p.add_argument("fuzzy_time", help='''
    can be a string like 9h meaning "the next 09:00"
''')
a = args = parser.parse_args()

x = a.fuzzy_time

from datetime import date, time, datetime, timedelta
C = datetime.combine

N = datetime.now()

from re import compile as Re
R = Re('(\d+)[h:](\d*)')

match = R.fullmatch(x)
if not match:
    import sys
    print("Wrong match, must be", R.pattern, file=sys.stderr)
else:
    h, m = match.groups()
    h, m = int(h), int(m or '0')

    d = N.replace(hour=h, minute=m, second=0, microsecond=0)
    if d < N:
        d += timedelta(days=1)

    delta = d - N

    print(*str(delta).split(':')[:2], sep=':')

