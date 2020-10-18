#!/usr/bin/env python3
#! coding: utf-8
from __future__ import print_function

import argparse
import xml.dom.minidom
import re

from generate_utils import OutFileGreen as OutFile

p = argparse.ArgumentParser(description='''
    In a svg file x.svg, look for every layer and creates x.state-{i}.svg
    for all detected states.
    
    The layers names must have set-pattern like
    {1} (include me in state 1)
    or {1,4,5} (in states 1 4 and 5)
    or {7,8,a} (in states 7 8 and a)
    or {1-5} (in states 1,2,3,4,5)
    or {hello-x, world} (in states "hello-w" and "world")
    
''')

'''
Idea: 
or {*} include in all slides
or {a*} include in all slides beginning with a
or {*a} include in all slides ending with a
or {a, b, c, 1-5, d*} in slides a, b, c from 1 to 5 and beginning with d

elif '*' in I:
    L = I.split('*')
    M = re.compile('.*'.join(map(re.escape, L)))
    that regex will be used as an alternative way for the layer to be inserted in the slide, based on the slide name

but when done that way, each slide must be declared in some layer because the regex represent an infinite number of slide

Idea: {a1-5} to have {a1,a2,a3,a4,a5}
'''

p.add_argument('svg_file', nargs='+')

g = p.add_mutually_exclusive_group()
g.add_argument('--state-in-filename', action='store_true', help='Filenames will be x.state-{i}.svg and not x.{i}.svg (@deprecated)')
g.add_argument('--remove-state-in-filename', action='store_true', help='Forces --state-in-filename to be False (@deprecated)')

g = p.add_mutually_exclusive_group()
g.add_argument('--numeric-layers', action='store_true', help='''
    Overrides the default behaviour and create one svg per layer, each svg is numeric 1 2 3 ...''')
g.add_argument('--layer-name', action='store_true', help='''
    Overrides the default behaviour and create one svg per layer, each svg has the name of the layer''')

a = args = p.parse_args()

if args.remove_state_in_filename:
    args.state_in_filename = False 

# for x in range(150): print(x, '\033[' + str(x) + 'm', 'Hel', '\033[0m')
def print_warning(*args): # orange
    print('\033[33m' + 'Warning:', *(args + ('\033[0m',)))
    
def print_info(*args): # green
    print('\033[32m' + 'Info:', *(args + ('\033[0m',)))
    
def print_error(*args): # error
    print('\033[31m' + 'Error:', *(args + ('\033[0m',)))
    
for svg_file in args.svg_file:
    if not svg_file.endswith('.svg'):
        print_error('filename is not .svg', svg_file)
        continue
    
    svg_filename = svg_file[:-4]
    with open(svg_file) as f:
        doc = xml.dom.minidom.parse(f)
        root = doc.documentElement

    def set_union(iterable):
        """ set_union( [ {1,2}, {3,4}, {1,7} ] ) == {1,2,3,4,7} """
        it = iter(iterable)
        S1 = next(it, set())
        return set.union(S1, *it)

    INK = 'http://www.inkscape.org/namespaces/inkscape'

    layers = [x for x in root.childNodes
            if getattr(x, 'tagName', None) == 'g'
            if x.getAttributeNS(INK, 'groupmode') == 'layer']

    R = re.compile('''
        \{(
        \d+ (- \d+)?
        ((\s+|\s*,\s*) \d+ (- \d+)?)*
        (\s+|\s*,\s*)?
        )\}''', re.X)

    all_infos = []
    nexts = {}
    for i,layer in enumerate(layers):
        nexts[layer] = layer.nextSibling
        
        if args.numeric_layers:
            all_infos.append((layer, {str(i+1)}))
            continue
        
        l = layer.getAttributeNS(INK, 'label').strip()
        
        if args.layer_name:
            all_infos.append((layer, {l}))
            continue
        
        m = re.search('\{([^{}]*)\}', l)
        if not m:
            print_info('Layer on every slide :', l)
            continue
        
        S = set_where_layer_is_in = set()
        for I in (s.strip() for s in m.group(1).split(',')):
            if re.match('\d+\s*-\s*\d+', I):
                a,b = tuple(map(int, I.split('-')))
                S |= set(map(str, range(a,b+1)))
            else:
                S.add(I)
                
        all_infos.append((layer, S))
        
    # all_infos : {
    #  DOM Element g[groupmode=layer]: {'1', '5', '6', '7', 'a'},
    #  DOM Element g[groupmode=layer]: {'a'},
    # }
    # first g will be include in slides 1 5 6 7 a
    # 
    # other slides non having S(...) infos will always be included

    if not all_infos:
        print_warning('In', svg_file, 'Nothing to do, add {tags} on your layers')
        continue

    slides = set_union(info for layer, info in all_infos)

    Format = ("{}.state-{}.svg" if args.state_in_filename else 
              "{}.{}.svg" )
    
    for slide in slides:
        new = OutFile(Format.format(svg_filename, slide))
        with new as f:
            for layer, info in all_infos:
                if slide not in info:
                    root.removeChild(layer)
            f.write(root.toxml())
            for layer, info in reversed(all_infos):
                if slide not in info:
                    root.insertBefore(layer, nexts[layer])
