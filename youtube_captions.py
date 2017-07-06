#!/usr/bin/env python3
from __future__ import division
from __future__ import print_function

import argparse

p = argparse.ArgumentParser()
p.add_argument('action', choices='sbv2txt txt2sbv po po2sbv merge split fillgap'.split())
p.add_argument('-i', '--input', default='captions.sbv', help='the sbv file')
p.add_argument('-o', '--output', default='')

# po
p.add_argument('--left', default='captions.txt')
p.add_argument('--right', default='translated.txt')
p.add_argument('--lang', default='en')

# txt
p.add_argument('--txt', default='translated.txt')

# po
p.add_argument('--po', default='trans.po')

# sbv2txt txt2sbv po po2sbv
g = p.add_mutually_exclusive_group()
g.add_argument('--lower', action='store_true')
g.add_argument('--no-lower', action='store_true')

g = p.add_mutually_exclusive_group()
g.add_argument('--forget-new-line', action='store_true')
g.add_argument('--no-forget-new-line', action='store_true')

# po 
p.add_argument('--po-empty', action='store_true')

# fillgap 
p.add_argument('--ms', type=int, default=400, help='gaps lengthy of less than --ms millisecond will be filled')
p.add_argument('--filler', default='next', choices='next prev middle'.split(), help='next sub will be sooner, or prev text will be sooner, or middle, both will move')

args = p.parse_args()
action = args.action

def input_bool(msg):
    return input(msg + ' [Y/n] ') not in ('n', 'no')

def ask_lower_and_new_line():
    if args.no_lower:
        args.lower = False
    elif not args.lower:
        args.lower = input_bool('Lowering all begin of lines?')
    del args.no_lower
    
    if args.no_forget_new_line:
        args.forget_new_line = False
    elif not args.forget_new_line:
        args.forget_new_line = input_bool('Forget new line?')
    del args.no_forget_new_line

import re

def lowerlize(s):
    return '' if not s else s[0].lower() + s[1:]

def change_ext(filename, ext):
    import os
    return os.path.splitext(filename)[0] + '.' + ext

def to_timedelta(a,b,c):
    from datetime import timedelta 
    assert c.count('.') <= 1
    return timedelta(hours=int(a),
                     minutes=int(b),
                     seconds=int(c.split('.')[0]),
                     milliseconds=int(c.split('.')[1] if len(c.split('.')) >= 1 else 0))

def format_datetime(td):
    from datetime import timedelta 
    return '{}.{:03}'.format(
        timedelta(days=td.days, seconds=td.seconds),
        td.microseconds // 1000)

TimeReg = re.compile('{0},{0}'.format('(\d+):(\d+):([0-9.]+)'))

def to_interval(line):
    a,b,c,A,B,C = TimeReg.match(line).groups()
    return [to_timedelta(a,b,c), to_timedelta(A,B,C)]

def format_interval(td1,td2):
    return format_datetime(td1) + ',' + format_datetime(td2)

def cleanspace(string):
    return re.sub(' +', ' ', string.strip())

# input
if args.input == '-':
    import os
    Orig = os.stdin.readlines()
else:
    with open(args.input) as f:
        Orig = f.readlines()
    
R = TimeReg
L = Orig

assert R.match(L[0]), "first line must be a time span"

cuts = []
for i in range(len(L)):
    if R.match(L[i]) and (i == 0 or L[i-1] == '\n'):
        cuts.append(i)
        
print('cuts:', len(cuts))

def GetBlocks():
    B = ''.join(l for i,l in enumerate(Orig) if i not in cuts).split('\n\n')
    if B[-1].strip() == '':
        del B[-1]
    return B

def splitNN(string):
    T = string.split('\n\n')
    if T and T[-1].strip() == '':
        del T[-1]
    return T

def GetTimeIntervals():
    return [to_interval(Orig[i]) for i in cuts]

if action == 'sbv2txt':
    ask_lower_and_new_line()
    flo = args.output or change_ext(args.input, 'txt')
    assert flo.endswith('.txt')
    with open(flo, 'w') as f:
        mf = lambda x:x if not args.lower else lowerlize
        if not args.forget_new_line:
            for i,l in enumerate(L):
                if i not in cuts:
                    f.write(mf(l))
        else:
            f.write('\n\n'.join(mf(b.replace('\n', ' ')) for b in GetBlocks()))
    print('Saved as <', flo, '>, use google translate, edit translation but beware to keep lines then save in new file translated.txt')

elif action == 'txt2sbv':
    ask_lower_and_new_line()
    
    # input('reading: translated.txt... ')
    fl = args.txt
    assert fl.endswith('.txt')
    
    with open(fl) as f:
        T = f.readlines()
    
    assert len(T) + len(cuts) == len(L)
    
    for i in cuts:
        T.insert(i, Orig[i])
        
    if args.lower:
        T = map(lowerlize, T) # only iterated once
    if args.forget_new_line:
        T = map(lambda x:x.replace('\n', ' '))
        
    flo = args.output or change_ext(fl, 'sbv')
    assert flo.endswith('.sbv')
    with open(flo, 'w') as f:
        for t in T:
            f.write(t)
    print('saved:', flo)

elif action == 'po':
    ask_lower_and_new_line()
    
    Times = [Orig[i].strip() for i in cuts]
    
    fl1 = args.left
    assert fl1.endswith('.txt')
    with open(fl1) as f:
        A = splitNN(f.read())
        
    if args.po_empty:
        B = [''] * len(A)
    else:
        fl2 = args.right
        assert fl2.endswith('.txt')
        with open(fl2) as f:
            B = splitNN(f.read())
    assert len(A) == len(B), "{} vs {} blocks".format(len(A), len(B))
    assert len(A) == len(cuts), "{} blocks vs {} cuts".format(len(A), len(cuts))
    
    flo = args.output or 'trans.po'
    assert flo.endswith('.po')
    with open(flo, 'w') as f:
        f.write('msgid ""\n'
                'msgstr ""\n'
                '"Content-Type: text/plain; charset=UTF-8\\n"\n'
                + '"Language: {}\\n"\n'.format(args.lang)
                + '\n')
        
        for n,(a,b) in enumerate(zip(A,B)):
            f.write('msgctxt "' + str(Times[n]) + '"\n')
            for x,s in ((a,'msgid'),(b,'msgstr')):
                for i,l in enumerate(x.split('\n')):
                    if i == 0:
                        f.write(s)
                        f.write(' ')
                    f.write('"')
                    if i > 0:
                        f.write('\\n')
                    t = l.replace('"', '\\"')
                    f.write(lowerlize(t) if args.lower and s == 'msgstr' else t)
                    f.write('"\n')
            f.write('\n')
    print('saved:', flo)
elif action == 'po2sbv':
    ask_lower_and_new_line()
    
    Times = [Orig[i].strip() for i in cuts]
    Header = re.compile('(msg[a-z]*) +"(.*)" *$')
    Empty = re.compile(' *"(.*)" *$')
    Comment = re.compile(' *#.*$')
    fl = args.po
    assert fl.endswith('.po')
    # input('reading:', fl)
    with open(fl) as f:
        L = []
        last = None
        D = {}
        for line in map(str.strip, f):
            if line == '' or Comment.match(line):
                if last is not None:
                    L.append(D)
                last = None
                D = {}
            elif Header.match(line):
                h,m = Header.match(line).groups()
                last = h
                assert last not in D, "duplicate key: {}".format(last)
                D[last] = m.replace('\\n', '\n').replace('\\"', '"')
            elif Empty.match(line):
                m, = Empty.match(line).groups()
                assert last is not None
                D[last] += m.replace('\\n', '\n').replace('\\"', '"')
            else:
                raise ValueError('Syntax in po file, line: ' + repr(line)) 
        if last is not None:
            L.append(D)
        
        assert all('msgid' in d and 'msgstr' in d for d in L)
        assert len(L) > 0
        assert L[0]['msgid'] == ''
        assert all('msgctxt' in d for d in L[1:])
        assert len(Times) == len(L) - 1
        assert all(Times[i] == L[i+1]['msgctxt'] for i in range(len(Times)))
        
        if args.forget_new_line:
            for d in L[1:]:
                d['msgstr'] = d['msgstr'].replace('\n', ' ')
        
        if args.lower:
            for d in L[1:]:
                d['msgstr'] = lowerlize(d['msgstr'])
            
        flo = args.output or 'translated.sbv'
        assert flo.endswith('.sbv')
        with open(flo, 'w') as f:
            for t, d in zip(Times, L[1:]):
                f.write(t + '\n')
                f.write(d['msgstr'] + '\n')
                f.write('\n')
        print('saved:', flo)
elif action == 'merge':
    # input
    Times = [Orig[i].split(',') for i in cuts]
    Blocks = GetBlocks()
    assert len(Times) == len(Blocks)
    # action
    i = 0
    while i < len(Times):
        if Blocks[i].startswith('<<') and i > 0:
            Blocks[i-1] = cleanspace(Blocks[i-1] + ' ' + Blocks[i][2:]) + '\n'
            Times[i-1][1] = Times[i][1]
            del Times[i]
            del Blocks[i]
        else:
            if Blocks[i].endswith('>>') and i+1 < len(Times):
                Blocks[i] = cleanspace(Blocks[i][:-2] + ' ' + Blocks[i+1]) + '\n'
                Times[i][1] = Times[i+1][1]
                del Times[i+1]
                del Blocks[i+1]
            i += 1
    # output
    flo = args.output or 'merged.sbv'
    assert flo.endswith('.sbv')
    with open(flo, 'w') as f:
        sep = ''
        for t,b in zip(Times, Blocks):
            f.write(sep)
            f.write(','.join(t))
            f.write(b)
            sep = '\n\n'
elif action == 'split':
    # input
    Times = GetTimeIntervals()
    Blocks = GetBlocks()
    assert len(Times) == len(Blocks)
    # action
    i = 0
    while i < len(Times):
        S = Blocks[i].strip().split('//')
        if len(S) > 1:
            beg, end = Times[i]
            Ts = [beg + (end - beg) * float(i+1)/len(S)
                for i in range(len(S)-1)] + [end]
            
            Times[i][1] = Ts[0]
            Blocks[i] = cleanspace(S[0])
            for j in range(len(S)-1):
                Times.insert(i+j+1, [Ts[j], Ts[j+1]])
                Blocks.insert(i+j+1, cleanspace(S[j+1]))
        i += len(S)
    # output
    flo = args.output or 'split.sbv'
    assert flo.endswith('.sbv')
    with open(flo, 'w') as f:
        sep = ''
        for a,b in zip(Times, Blocks):
            f.write(sep)
            f.write(','.join(map(format_datetime, a)))
            f.write('\n')
            f.write(b)
            sep = '\n\n'
elif action == 'fillgap':
    # input
    Times = GetTimeIntervals()
    Blocks = GetBlocks()
    assert len(Times) == len(Blocks)
    # action
    assert args.filler in 'prev middle next'.split(), args.filler
    for i in range(len(Times) - 1):
        a,b = Times[i][1], Times[i+1][0]
        if (b - a).total_seconds() * 1000 <= args.ms:
            Times[i+1][0] = Times[i][1] = (
                a if args.filler == 'prev' else
                b if args.filler == 'next' else
                (a + b) / 2 if args.filler == 'middle' else None)
    # output
    flo = args.output or 'fillgap.sbv'
    assert flo.endswith('.sbv')
    with open(flo, 'w') as f:
        sep = ''
        for a,b in zip(Times, Blocks):
            f.write(sep)
            f.write(','.join(map(format_datetime, a)))
            f.write('\n')
            f.write(b)
            sep = '\n\n'