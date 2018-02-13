import sqlite3
import csv
import re
import xml.etree.ElementTree as ET

Re = re.compile

def irange(*args):
    """ inclusiverange: irange(1,5) == range(1,6) """
    r = range(*args)
    return range(r.start, r.stop + 1, r.step)

def dict_int_key(it):
    return {int(a):b for a,b in it}

def warning(*args):
    print('[Warning]', *args)
    
def info(*args):
    print('[Info]', *args)

def error(*args):
    print('[Error]', *args)

from collections import defaultdict

def reverse_dict(D, check_uniq=False):
    R = {y:x for x,y in D.items()}
    if check_uniq and not(len(R) == len(D)):
        raise ValueError('Not a bijection')
    return R

class DictCollection:
    """
    Data = DictCollection()
    Data['Matricule', 'to', 'AmcStudentId'] = {'12345' + str(i): i+1 for i in range(5)}

    Data['Matricule', 'to', 'AmcStudentId'] # {'123450':1, '123451':2, '123452':3, '123453':4, '123454':5}
    Data['Matricule', 'from', 'AmcStudentId'] # {1:'123450', 2:'123451', 3:'123452', 4:'123453', 5:'123454'}

    Data('Matricule', '123450').to('AmcStudentId') # 1
    Data('AmcStudentId', 1).to('Matricule') # '132450'

    Matricule = Data('Matricule') # type ColumnId
    student = Matricule('123450').to('AmcStudentId') # 1

    AmcStudentId = Data('AmcStudentId')
    student = Matricule('123450').to(AmcStudentId) # 1
    
    Data['Name', 'from', 'Matricule'] = {'123450': 'Jean', '123450': 'Marie'}
    Data['AmcStudentId', 'to', 'Name'] # TODO, BEWARE: modification
    """
    
    def __init__(self, update_no_duplicates=False):
        self.dicts = {}
        self.update_no_duplicates = update_no_duplicates
    
    @staticmethod
    def _read_tup(tup:('a', 'action:from|to', 'b')):
        a, action, b = tup
        if isinstance(a, DictCollection.ColumnId):
            a = a.name
        if isinstance(b, DictCollection.ColumnId):
            b = b.name
        
        action = action.lower()
        assert action in ('from', 'to')
        
        if action == 'to':
            a,b = b,a
        
        return a,b
    
    def __setitem__(self, tup:('a', 'action:from|to', 'b'), D:dict):
        a,b = self._read_tup(tup)
        
        self.dicts[a,b] = D
        if (b,a) in self.dicts:
            del self.dicts[b,a] # modification
    
    def __contains__(self, tup):
        a,b = self._read_tup(tup)
        return (a,b) in self.dicts or (b,a) in self.dicts
        
    def set_or_update(self, tup:('a', 'action:from|to', 'b'), D:dict):
        if tup not in self:
            self[tup] = D
        else:
            if self.update_no_duplicates and bool(self[tup].keys() & D.keys()):
                raise ValueError('updating duplicates !')
            self[tup].update(D)
            
            a, b = self._read_tup(tup)
            if (b,a) in self.dicts:
                del self.dicts[b,a] # modification
    
    def __getitem__(self, tup:('a', 'action:from|to', 'b')) -> dict:
        """
        Dict['Matricule', 'to', 'AmcStudentId']
        Dict['AmcStudentId', 'from', 'Matricule']
        """
        a, b = self._read_tup(tup)
        
        if (a,b) in self.dicts:
            return self.dicts[a,b]
        if (b,a) in self.dicts:
            self.dicts[a,b] = reverse_dict(self.dicts[b,a])
            return self.dicts[a,b]
        raise KeyError(' '.join(tup))
    
    class ColumnId:
        def __init__(self, name, dictcls=None, value=None):
            self.name = name
            self.dictcls = dictcls
            self.value = value

        def to(self, other):
            if self.value is None:
                raise ValueError('value must be given and not None')
            return self.dictcls[self.name, 'to', other][self.value]
        
        def __call__(self, value):
            return DictCollection.ColumnId(self.name, self.dictcls, value)
        
        def __repr__(self):
            if self.value is None:
                return 'ColumnId({})'.format(self.name)
            else:
                return 'ColumnId({}, {!r})'.format(self.name, self.value)
    
    def __call__(self, name, value=None):
        return DictCollection.ColumnId(name, self, value)
    
    def keylist(self, *args):
        return [self(a) for a in args]
    
    def populateDictWithKeys(self, D, *args):
        for n in args:
            D[n] = self(n)

class QFInfo:
    POLICIES = {'EmptyColumnMeansFirstTicked'} & {'EmptyColumnMeansFirstTicked', 'NoSignMeansPlus', 'MultipleTickMeansNoTick'} # set(args.policies)
    
    class EmptyColumn(Exception):
        pass

    class MultipleTicksInColumn(Exception):
        pass
    
    def __init__(self, Dict:DictCollection, dbs:{'name':sqlite3}, seuil:float, exam:int, name:'QO1'):
        assert QFSerie.match(name)
        self.Dict = Dict
        self.dbs = dbs
        self.seuil = seuil
        self.exam = exam
        self.name = name

    def parseQF(self, *, base=10, policies=POLICIES) -> {'value':float, 'mantissa':float, 'exp':float, 'sign':int}:
        
        def parsePart(part:'digits|exp', expectedNumbers:3, *, base=base, hasSign=True, direction:'plus|minus'='plus'):
            """
            Parse a signed number.
            if hasSign, the first two boxes contains the sign (first = +, second = -).
            Then we have base=10 expectedNumbers boxes representing numbers. For example expectedNumbers = 3, digits = [6,0,9].
            If direction == "plus" Then Digits represents 609
            If direction == "minus" Then Digits represents 6.09
            """
            assert part in ('digits', 'exp') and direction in ('plus', 'minus')
            expectedBoxes = (2 if hasSign else 0) + expectedNumbers * base
            
            CaseToRatio = dict(self.dbs['capture'].execute(f'''
                select id_b, 1.0*black/total from capture_zone
                where student=?
                and type={ZONE_BOX}
                and id_a=?
                ''',
                (self.exam,
                self.Dict('LatexQuestionName', self.name + part).to('AmcQuestionId'))
            ))
            assert CaseToRatio.keys() == set(irange(1,expectedBoxes))
            
            Ticks = [int(v >= self.seuil) for k,v in CaseToRatio.items()]
            # Example: Ticks = [0,1, 0,0,0,1,0,0,0,0,0,0, 0,1,0,0,0,0,0,0,0,0]
            
            if hasSign:
                Sign = Ticks[0:2]
                Digits = [Ticks[2+n : 2+n+base] for n in range(0, base * expectedNumbers, base)]
            else:
                Sign = [1,0] # Positive
                Digits = [Ticks[n : n+base] for n in range(0, base * expectedNumbers, base)]
            
            if Sign == [0,0] and 'NoSignMeansPlus' in policies:
                Sign = [1,0]
            
            # Example if hasSign == True and base == 10: Sign = [0,1]; Digits = [[0,0,0,1,0,0,0,0,0,0], [0,1,0,0,0,0,0,0,0,0]]
            
            if 'MultipleTickMeansNoTick' in policies:
                for col in [Sign] + Digits:
                    if sum(col) > 1:
                        for i in range(len(col)):
                            col[i] = 0
            
            for col in [Sign] + Digits:
                if sum(col) == 0:
                    if 'EmptyColumnMeansFirstTicked' in policies:
                        col[0] = 1
                    else:
                        raise QFInfo.EmptyColumn("User ticked zero columns in a column (for {})".format(part))
                if sum(col) > 1:
                    raise QFInfo.MultipleTicksInColumn("User ticked two columns in a column (for {})".format(part))
            
            sign = +1 if Sign[0] else -1
            digits = [D.index(1) for D in Digits]
            
            # Example: sign = -1; digits = [3, 1]
            
            number = (sign * sum(n * base ** (-i) for i,n in enumerate(digits)) if direction == 'minus' else
                      sign * sum(n * base ** i for i,n in enumerate(reversed(digits))) if direction == 'plus' else None)
        
            # Example if direction == 'minus': number = -3.1
            # Example if direction == 'plus':  number = -31
            
            return number
        
        number = parsePart('digits', 3, hasSign=True, direction='minus')
        numberExp = parsePart('exp', 1, hasSign=True, direction='plus')
        numberFinal = number * base ** numberExp
        
        return {'value': numberFinal, 'mantissa':number, 'exp':numberExp, 'sign': 0 if numberFinal == 0 else -1 if numberFinal < 0 else 1}

class QOInfo:
    class CorrectorNoTick(Exception):
        pass
    
    class CorrectorMultiTick(Exception):
        pass

    def __init__(self, Dict:DictCollection, dbs:{'name':sqlite3}, seuil:float, exam:int, name:'QO1'):
        assert QO.match(name)
        self.Dict = Dict
        self.dbs = dbs
        self.seuil = seuil
        self.exam = exam
        self.name = name
        self.qnum = int(QO.match(name).group(1))
    
    def correctionValue(self) -> 4:
        if hasattr(self, '_correctionValue'):
            return self._correctionValue
        
        D = DictCollection()
        CaseToRatio = D['AnswerPoints', 'to', 'Ratio'] = dict(self.dbs['capture'].execute(f'''
            select id_b, 1.0*black/total from capture_zone
            where student=?
            and type={ZONE_BOX}
            and id_a=?
            ''',
            (self.exam,
             self.Dict('LatexQuestionName', self.name).to('AmcQuestionId'))
        ))
        assert CaseToRatio.keys() == set(irange(1,11))
        points = [int(k)-1 for k,v in CaseToRatio.items() if v >= self.seuil]
        if len(points) == 0:
            raise QOInfo.CorrectorNoTick("no points ticked")
        
        if len(points) > 1:
            raise QOInfo.CorrectorMultiTick("too much points ticked")
        
        self._correctionValue = points[0]
        return self._correctionValue
    
    def correctionCommentsList(self) -> [0, 2, 3]:
        if hasattr(self, '_correctionCommentsList'):
            return self._correctionCommentsList
        
        AnswerAnnotate_to_Ratio = dict(self.dbs['capture'].execute(f'''
            select id_b, 1.0*black/total from capture_zone
            where student=?
            and type={ZONE_BOX}
            and id_a=?
            ''',
            (self.exam,
             self.Dict('LatexQuestionName', QOANN_FORMAT(self.qnum)).to('AmcQuestionId'))
        ))
        assert AnswerAnnotate_to_Ratio.keys() == set(irange(1,7)) # 7 annotations possible
        annotations = [int(k)-1 for k,v in AnswerAnnotate_to_Ratio.items() if v >= self.seuil]
        
        self._correctionCommentsList = annotations
        return self._correctionCommentsList

class ReadFromAnnotate:
    def __init__(self, annotate_csv_file):
        self.annotate_csv_file = annotate_csv_file
        assert annotate_csv_file.endswith('.csv')

class ReadFromMatriculeMarkCsv:
    def __init__(self, csv_file, column_name:'QO2'):
        self.column_name = column_name
        assert csv_file.endswith('.csv')
        
        self.Dict = DictCollection()
        self.Matricule = self.Dict('Matricule')
        self.Mark = self.Dict('Mark')
        
        with open(csv_file) as f:
            self.Dict['Matricule', 'to', 'Mark'] = {int(s['MATRICULE']): int(s[column_name]) for s in csv.DictReader(f)}

class XLWriter:
    def __init__(self, filename):
        import openpyxl
        self.filename = filename
        self.wb = openpyxl.Workbook()
        
    def writerow(self, row):
        self.wb.active.append(row)
    
    def close(self):
        self.wb.save(self.filename)
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()

class CSVWriter:
    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename, 'w')
        self.writer = csv.writer(self.f)
        
    def writerow(self, row):
        self.writer.writerow(row)
    
    def close(self):
        self.f.close()
    
    def __enter__(self):
        self.f.__enter__()
        return self
    
    def __exit__(self, type, value, traceback):
        self.f.__exit__(type, value, traceback)

class CSVAndXLWriter:
    def __init__(self, filename):
        assert filename.endswith('.csv')
        self.csv = CSVWriter(filename)
        self.xl = XLWriter(filename[:-4] + '.xlsx')
        
    def writerow(self, row):
        self.csv.writerow(row)
        self.xl.writerow(row)
    
    def close(self):
        self.csv.close()
        self.xl.close()
    
    def __enter__(self):
        self.csv.__enter__()
        self.xl.__enter__()
        return self
    
    def __exit__(self, type, value, traceback):
        self.csv.__exit__(type, value, traceback)
        self.xl.__exit__(type, value, traceback)
        
class PrintWriter:
    def __init__(self, filename):
        print('--', filename, '--')
        
    def writerow(self, row):
        print(*row)
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass

if __name__ != '__main__':
    import sys
    sys.exit(0)

OUT_FILE = 'lolilol.csv'
assert OUT_FILE.endswith('.csv')

QO = Re('^QO(\d+)$')
QO_FORMAT = 'QO{}'.format

QFSerie = Re('^QF(?P<num>\d+)(?P<serie>\w)$')
QFSerieFormat = 'QF{num}{serie}'.format
QFDigitsReg = Re('^QF(?P<num>\d+)(?P<serie>\w)(?P<part>digits|exp)$')
QFDigitsFormat = 'QF{num}{serie}{part}'.format

QOANN = Re('^QANN(\d+)$')
QOANN_FORMAT = 'QANN{}'.format

ZONE_BOX = 4

SERIES = ('A', 'B')
PROJ_NAME_FROM_SERIE = lambda x: 'generateurAMC_{}'.format(x.upper())

question_formats = {
    # 'QO2': ReadFromMatriculeMarkCsv('q2-marks.csv', 'QO2'), # ReadFromAnnotate(''),
}

qf_answers = { # list of [value, min, max, -points minus]
    'QF5a': [
        [7.81e-1, 7.71e-1, 7.81e-1, 0],
        [1.56, 1.54, 1.58, -1]
    ],
    'QF6a': [
        [-3.32e-9, 3.22e-9, 3.42e-9, 0],
        [-375, 371, 379, -1],
    ],
    'QF7a': [
        [1.33e-8, 1.23e-8, 1.43e-8, 0],
        [5.32e-8, 5.3e-8, 5.34e-8, -3],
        [2.66e-8, 2.64e-8, 2.68e-8, -3]
    ],
    'QF8a': [
        [2.5, 2.4, 2.6, 0],
    ],
    'QF5b': [
        [1.53, 1.43, 1.63, 0],
        [3.06, 3.04, 3.08, -1]
    ],
    'QF6b': [
        [-5.53e-9, 5.43e-9, 5.63e-9, 0],
        [625, 621, 629, -1]
    ],
    'QF7b': [
        [1.18e-8, 1.08e-8, 1.28e-8, 0],
        [2.36e-8, 2.34e-8, 2.38e-8, -3],
        [3.54e-8, 3.52e-8, 3.56e-8, -3],
        [1.77e-8, 1.75e-8, 1.79e-8, -3],
    ],
    'QF8b': [
        [1.41, 1.31, 1.51, 0],
    ],
}

assert all(len(L) > 0 for L in qf_answers.values())
assert all(len(X) == 4 for L in qf_answers.values() for X in L)
assert all(minus == 0 for L in qf_answers.values() for i,(value, m, M, minus) in enumerate(L) if i == 0)
assert all(minus <= 0 for L in qf_answers.values() for value, m, M, minus in L)

# TODO: assert no overlap : assert all(map(no_overlap, qf_answers.values()))

qf_policies = {
    'QF5a': set(),
    'QF6a': set(), # {'SignMinus1'},
    'QF7a': set(),
    'QF8a': set(),
    'QF5b': set(),
    'QF6b': set(), # {'SignMinus1'},
    'QF7b': set(),
    'QF8b': set(),
}

assert all(X <= {'SignMinus1'} for X in qf_policies.values())

with CSVAndXLWriter(OUT_FILE) as writer:
    writer.writerow(('COPIE','MATRICULE','QUESTION','MARK','ANNOTATION','COMMENTS'))
    for serie in SERIES:
        proj = PROJ_NAME_FROM_SERIE(serie)
        # student_csv = f'.csv'

        dbs = {name:sqlite3.connect(f'{proj}/data/{name}.sqlite') for name in ('layout', 'association', 'capture')}

        xmldoc = ET.parse(f'{proj}/options.xml')

        try:
            seuil = float(xmldoc.find('seuil').text)
        except:
            warning(f'serie {serie}: seuil not found in xml, default seuil used')
            seuil = 0.35
        
        Dict = DictCollection()
        
        AmcStudentId, Matricule = Dict.keylist('AmcStudentId', 'Matricule')
        AmcQuestionId, LatexQuestionName = Dict.keylist('AmcQuestionId', 'LatexQuestionName')
        
        Dict[AmcQuestionId, 'to', LatexQuestionName] = dict_int_key(
            dbs['layout'].execute('''select question, name from layout_question'''))

        Dict[AmcStudentId, 'to', Matricule] = {
            int(student): int(auto or manual)
            for student, auto, manual in dbs['association'].execute('select student, auto, manual from association_association')
        }

        for latexname in Dict[AmcQuestionId, 'to', LatexQuestionName].values():
            for exam, matricule in Dict[AmcStudentId, 'to', Matricule].items():
                examfull = "{}{}".format(serie, exam)
                comments = ''
                if QFDigitsReg.match(latexname) and QFDigitsReg.match(latexname).group('part') == 'digits': # latexname = QF5digits
                    m = QFDigitsReg.match(latexname).groupdict()
                    basename = QFDigitsFormat(part='', num=m['num'], serie=m['serie']) # basename = QF5a
                    info = QFInfo(Dict, dbs, seuil, exam, basename)
                    
                    try:
                        values = info.parseQF()
                        value = values['value'] # values['mantissa'], values['exp'], values['sign']
                        
                        mark = 0
                        for answer, themin, themax, minus in qf_answers[basename]:
                            answer_sign = (0 if answer == 0 else 1 if answer > 0 else -1)
                            
                            if themin <= abs(value) <= themax:
                                m = 5
                            elif any(themin * 10 ** i <= abs(value) <= themax * 10 ** i for i in irange(-20,20)):
                                m = 3
                            else:
                                m = 0
                            if 'SignMinus1' in qf_policies[basename] and values['sign'] != answer_sign:
                                m -= 1
                            if minus:
                                assert minus < 0
                                m += minus
                            if m < 0:
                                m = 0
                            mark = max(m, mark)
                            if mark:
                                break # TakeFirstAnswerGivingMarks
                            
                        comments = (values, qf_answers[basename])
                        annotations = [] # TODO ?
                    except QFInfo.MultipleTicksInColumn:
                        warning(examfull, matricule, basename, 'MultipleTicksInColumn')
                        mark = 0
                            
                elif QO.match(latexname):
                    basename = latexname
                    if latexname in question_formats:
                        fmt = question_formats[latexname]
                        if isinstance(fmt, ReadFromMatriculeMarkCsv):
                            mark = fmt.Matricule(matricule).to(fmt.Mark)
                            annotations = [] # TODO
                        else:
                            error("{}{}".format(serie, exam), matricule, latexname, 'UnknownQuestionFormat')
                            continue
                    else: # FromScannedAnnotationsAndMark
                        try:
                            info = QOInfo(Dict, dbs, seuil, exam, latexname)
                            mark = info.correctionValue()
                            annotations = info.correctionCommentsList()
                        except (QOInfo.CorrectorMultiTick, QOInfo.CorrectorNoTick) as e:
                            error(examfull, matricule, basename, e.__class__.__name__)
                            continue
                else:
                    continue
                writer.writerow((examfull, matricule, basename, mark, ''.join(chr(ord('A') + i) for i in annotations), str(comments)))
