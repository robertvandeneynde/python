#!/usr/bin/env python3
import argparse
from textwrap import dedent

p = parser = argparse.ArgumentParser(description=dedent('''
        Create an image for whatsapp
    ''').strip('\n'))

p.add_argument("files", nargs='+')
p.add_argument("--out", "-o", nargs='+')
p.add_argument("-b", '--background', default=None)
p.add_argument("-v", "--verbose", action='store_true')

args = parser.parse_args()

def parse_color(string):
    """
    >>> parse_color('#ffcc99') == (0xff, 0xcc, 0x99)
    True
    """
    assert string.startswith('#')
    assert len(string) in (6+1, 8+1)
    return tuple(int(string[1+i:1+i+2], base=16)
                 for i in range(len(string) // 2))

def new_name(x):
    import os
    from itertools import count, filterfalse
    splitext = os.path.splitext
    a,b = splitext(x)

    def first_not_exists(x):
        return next(filterfalse(os.path.exists, x))

    return first_not_exists('{}__{}{}'.format(a, i, b)
                            for i in count(1))

if args.out:
    assert len(args.files) == len(args.out)
else:
    args.out = list(map(new_name, args.files))


from PIL import Image
for filename, out_filename in zip(args.files, args.out):
    im = Image.open(filename)
    bcolor = im.getpixel((0,0)) if not args.background else parse_color(args.background)
    real_background_color = bcolor[:len(im.mode)]
    out = Image.new(im.mode, (max(im.size), max(im.size)), real_background_color)
    position = ((im.size[0] // 2, 0) if im.size[0] < im.size[1] else 
                (0, im.size[1] // 2))
    out.paste(im, position)
    out.save(out_filename)

    if args.verbose:
        print('Created', out_filename)

