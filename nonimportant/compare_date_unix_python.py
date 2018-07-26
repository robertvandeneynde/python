import subprocess, os
from datetime import datetime

env = os.environ.copy()
env['LANG'] = 'en'

Data = [
    (x,
     subprocess.Popen(['date', '+%' + x], env=env, stdout=subprocess.PIPE).communicate()[0],
     datetime.today().strftime('%' + x) + '\n')
    for a in sorted('azertyuiopqsdfghjklmwxcvbn')
    for x in (a.lower(), a.upper())
]
    
from pprint import pprint
pprint(sorted(
    ('Same' if a == b else 'Diff', x) + (a != b) * ('Unix:'+a, 'Pyth:'+b)
    for x,a,b in Data
))