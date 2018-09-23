#!/usr/bin/env python3
import csv, re
from pprint import pprint

def warning(*args): # orange
    print('\033[33m' + 'Warning:', *args, '\033[0m')
    
def info(*args): # green
    print('\033[32m' + 'Info:', *args, '\033[0m')

def error(*args): # error
    print('\033[31m' + 'Error:', *args, '\033[0m')

SERIES = ('A', 'B')

import sqlite3
conns = {L:sqlite3.connect(f'generateurAMC_{L}/data/capture.sqlite') for L in SERIES}
assocs = {L:sqlite3.connect(f'generateurAMC_{L}/data/association.sqlite') for L in SERIES}
files = {L:[(x.replace('%PROJET', f'generateurAMC_{L}'), int(number), int(page)) for x,number,page in conns[L].execute('select src,student,page from capture_page')] for L in 'AB'}
infos = {L:[(int(number), matricule) for number,matricule  in assocs[L].execute('select student, case when manual is not null then manual else auto end from association_association')] for L in 'AB'}

with open('annotate-q2-marks-all-auditoire.csv') as f:
    annotations = list(csv.reader(f))

SRC = re.compile('^generateurAMC_(?P<serie>[A-Za-z]+)/scans/(?P<filename>.*)$')
SRC_FORMAT = 'generateurAMC_{serie}/scans/{filename}'

def compute_mark_list_q2(note, points_distrib:(3,1,2,2,1,1)):
    """
    if note == 'fx-vxx' yields 2,0,1,2,0,0
    if note == 'fx-v' yields 2,0,1,2,0,0
    if note == '123456' raises ValueError
    if note == 'vvvvvvv' raises ValueError
    """
    points = (3,1,2,2,1,1)
    assert sum(points_distrib) == 10
    n = len(points_distrib)
    assert len(note) <= n, note
    assert set(note) <= set('fvx-'), "Unrecognized characters: {}".format(set(note) - set('fvx-'))
    exp = note + (n - len(note)) * 'x'
    assert len(exp) == n
    
    for n,p in zip(exp, points_distrib):
        if n == 'v':
            yield p
        elif n == 'x':
            yield 0
        elif n == 'f':
            if not p > 2:
                raise ValueError(f'Cannot have "f" when line has {p} points')
            yield 2
        elif n == '-':
            if p == 1:
                warning(f'Should not have "-" when line has {p} points. On {note}')
            if p == 0:
                raise ValueError(f'Cannot have "-" when line has {p} points. On {note}')
            yield 1

PARSE_FILENAME = re.compile('(?P<auditoire>\w+)-(?P<serie>[A-B])-P(?P<page>\d+)-(?P<scan_number>\d+).jpg')

M = {}
for L in SERIES:
    D = {student_number:matricule for student_number, matricule in infos[L]}
    M.update({filename: D[student_number] for filename, student_number, page in files[L]})

assert len(M) == sum(len(files[L]) for L in SERIES)

ImgPath_to_Matricule = M
del M

QO2_GRID = (3,1,2,2,1,1)

with open('q2-marks.csv', 'w') as fw:
    writer = csv.writer(fw)
    writer.writerow(
        ['MATRICULE', 'FILENAME']
        + ['QO2_{}(/{})'.format(i+1,x) for i,x in enumerate(QO2_GRID)]
        + ['QO2'])
    
    for filename, annot in annotations:
        match = PARSE_FILENAME.match(filename)
        
        if not match:
            warning(filename, 'has a weird name')
            continue
        
        serie = match.group('serie').upper()
        assert int(match.group('page')) == 2
        
        path = SRC_FORMAT.format(serie=serie, filename=filename)
        
        # compute_mark
        mark_list = list(compute_mark_list_q2(annot, QO2_GRID))
        sum_question = sum(mark_list)
        
        try:
            matricule = ImgPath_to_Matricule[path]
            writer.writerow([matricule, filename] + mark_list + [sum_question])
        except KeyError:
            warning(filename, 'has no matricule')
            continue
print('Created', 'q2-marks.csv')
