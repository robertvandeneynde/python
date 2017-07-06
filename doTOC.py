#!/usr/bin/python3
import os
import sys
import re
import itertools

names = [n for n in sys.argv[1:] if not n.startswith('-')]
params = [n for n in sys.argv[1:] if n.startswith('-')]

if not names or any(h in params for h in ('-h', '--help')):
    print("Usage : pdf1 pdf2 pdf3 [--html] ...")
    exit()

pages = [
    int(re.search(
        'NumberOfPages: ([0-9]+)',
        os.popen('pdftk "{}" dump_data output'.format(name)).read()
    ).group(1))
    for name in names
]
sums = list(itertools.accumulate(pages))
percents = [s*100//sums[-1] for s in sums]

if '--html' not in params:
    M1,M2 = max(map(len,names)), max(map(len,map(str,pages)))
    for name, page, percent in zip(names, pages, percents):
        print(("{:<%d} {:0>%d} {:>3}%% |{:<10}|" % (M1,M2)).format(name, page, percent, '*' * ((percent + 5) // 10)))
else:
    print("<html><head><style>table { border-collapse: collapse } td, th { border: 1px solid #ccc; } </style></head><body>")
    print('<table>')
    
    print('<tr> <th>Chapter name</th> <th>Pages</th> <th colspan="2">Progress</th> </tr>')
    for name, page, percent in zip(names, pages, percents):
        print('<tr> <td>{}</td> <td style="text-align:center">{}</td> <td style="text-align:right">{}%</td> <td><progress value="{}" max="100"/></td> </tr>'.format(name, page, percent, percent))
    print('</table>')
    print('</body></html>')