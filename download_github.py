#!/usr/bin/env python3
import argparse
p = parser = argparse.ArgumentParser()

p.add_argument("url")

m = p.add_mutually_exclusive_group()
m.add_argument('--log', default='warning')
m.add_argument('-v', default='warning')
m.add_argument('-vv', default='warning')

args = parser.parse_args()

assert f'NotSyntaxError', 'Python >= 3.6 needed'

def throw(e):
    raise e

def re_variable(x):
    r"""
    >>> v('{word}')
    '(?P<word>[a-zA-Z][a-zA-Z_0-9]*)'
    >>> v('{word:int}')
    '(?P<word>\\d+)'
    """
    R = Re('{([^:}]+)(:[^:}]+)?}', re.I)
    assert R.fullmatch(x), f'{x!r} does not match {R.pattern!r}'
    a,b = R.fullmatch(x).groups()
    r = ('[a-zA-Z][a-zA-Z_0-9]*' if not b or b.lstrip(':') == 'str' else 
         '\d+' if b.lstrip(':') == 'int' else 
         '[a-zA-Z/][a-zA-Z_0-9/]*' if b.lstrip(':') == 'url' else throw(Exception))
    return f'(?P<{a}>{r})'

def re_parts(*parts):
    return Re(''.join(parts))

def set_logging_from_args(args):
    import logging
    loglevel = args.log
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

import re 
from re import compile as Re
class Pattern1:
    """
    https://github.com/robertvandeneynde/python/blob/master/rename_today.py
    → https://raw.githubusercontent.com/robertvandeneynde/python/master/rename_today.py
    """
    
    def identify(x) -> 'match|None':
        return Re('(https?)://github.com/([^/]+)/([^/]+)/blob/(.*)').fullmatch(x)
    
        # STUB for next version, that's more precise
        from re import escape as l
        v = re_variable
        def rps(*parts, sep='/'):
            return Re(re.escape(sep).join(parts))
        
        return rps(l('https://github.com'),
                   v('{user}'),
                   v('{repo}'),
                   l('blob'),
                   v('{branch}'),
                   l('{filename:url}')).fullmatch(x)
    
    @classmethod
    def remap(cls, x):
        """
        >>> remap('https://github.com/robertvandeneynde/python/blob/master/rename_today.py')
        'https://raw.githubusercontent.com/robertvandeneynde/python/master/rename_today.py'
        """
        protocol, user, repo, rest = Re('(https?)://github.com/([^/]+)/([^/]+)/blob/(.*)').fullmatch(x).groups()
        return f'{protocol}://raw.githubusercontent.com/{user}/{repo}/{rest}'

if __name__ == '__main__':
    from logging import info
    set_logging_from_args(args)
    
    url = (Pattern1.remap(args.url) if Pattern1.identify(args.url)
           else throw(Exception(f'Unrecognized pattern {args.url}')))
    
    import subprocess
    subprocess.call(['wget', url])
