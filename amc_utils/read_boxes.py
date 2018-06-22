#!/usr/bin/env python3
import sqlite3
import csv
import re
from re import compile as Re
import xml.etree.ElementTree as XmlElement
import os
from os.path import splitext

ZONE_BOX = 4

def irange(*args):
    """ inclusive_range: irange(1,5) == range(1,6) """
    r = range(*args)
    return range(r.start, r.stop + 1, r.step)

def dict_int_key(it):
    return {int(a):b for a,b in it}

def warning(*args): # orange
    print('\033[33m' + 'Warning:', *args, '\033[0m')
    
def info(*args): # green
    print('\033[32m' + 'Info:', *args, '\033[0m')

def error(*args): # error
    print('\033[31m' + 'Error:', *args, '\033[0m')

from collections import defaultdict

# Shared Class between amc_utils module
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
    
    Matricule('1111111').set('AmcStudentId', '666') # Matricule('111111').to('AmcStudentId') == '666'
    """
    
    def __init__(self, update_no_duplicates=False):
        self.dicts = {}
        self.update_no_duplicates = update_no_duplicates
    
    @staticmethod
    def reverse_dict(D, check_uniq=False):
        R = {y:x for x,y in D.items()}
        if check_uniq and not(len(R) == len(D)):
            raise ValueError('Not a bijection')
        return R
    
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
            self.dicts[a,b] = self.reverse_dict(self.dicts[b,a])
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
        
        def exists(self, other):
            if self.value is None:
                raise ValueError('value must be given and not None')
            return self.value in self.dictcls[self.name, 'to', other]
        
        def set(self, other, value):
            if self.value is None:
                raise ValueError('value must be given and not None')
            self.dictcls[self.name, 'to', other][self.value] = value
            
            # delete reverse
            a, b = self.dictcls._read_tup((self.name, 'to', other))
            if (b,a) in self.dictcls.dicts:
                del self.dictcls.dicts[b,a] # modification
                # TODO: maybe just update self.dicts[b,a][self.value], but what if this introduces non bijection ?
        
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

def set_testsubset(A,B):
    assert A <= B
    return A

class QFInfo:
    POLICIES = set_testsubset({'EmptyColumnMeansFirstTicked', 'NoMantissaMeansError'}, {'NoMantissaMeansError', 'EmptyColumnMeansFirstTicked', 'NoSignMeansPlus', 'MultipleTickMeansNoTick'}) # set(args.policies)
    
    class Error(Exception):
        pass
    
    class EmptyColumn(Error):
        pass

    class MultipleTicksInColumn(Error):
        pass
    
    class NoMantissa(Error):
        pass
    
    def __init__(self, Dict:DictCollection, dbs:{'name':sqlite3}, seuil:float, exam:int, name:'QO1'):
        assert StandardNames.QF_SERIE.fullmatch(name)
        self.Dict = Dict
        self.dbs = dbs
        self.seuil = seuil
        self.exam = exam
        self.name = name

    def parseQF(self, *, base=10, policies=POLICIES) -> {'value':float, 'mantissa':float, 'exp':float, 'sign':int}:
        
        AmcQuestionId, LatexQuestionName = self.Dict.keylist('AmcQuestionId', 'LatexQuestionName')
        
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
            
            CaseToRatio = {
                digit: ratio if manual == -1 else manual
                for digit, ratio, manual in self.dbs['capture'].execute(f'''
                    select id_b, 1.0*black/total, manual from capture_zone
                    where student=?
                    and type={ZONE_BOX}
                    and id_a=?
                    ''',
                    (self.exam, LatexQuestionName(self.name + part).to(AmcQuestionId)))
            }
            assert all(0 <= v <= 1 for v in CaseToRatio.values())
            assert CaseToRatio.keys() == set(irange(1,expectedBoxes))
            
            Ticks = [int(v >= self.seuil) for k,v in CaseToRatio.items()]
            # Example: Ticks = [0,1, 0,0,0,1,0,0,0,0,0,0, 0,1,0,0,0,0,0,0,0,0]
            
            if hasSign:
                Sign = Ticks[0:2]
                Digits = [Ticks[2+n : 2+n+base] for n in range(0, base * expectedNumbers, base)]
                # Example: Sign = [0,1]
                # Example: Digits = [[0,0,0,1,0,0,0,0,0,0], [0,1,0,0,0,0,0,0,0,0]]
            else:
                Sign = [1,0] # Positive
                Digits = [Ticks[n : n+base] for n in range(0, base * expectedNumbers, base)]
                # Example: Digits = [[0,0,0,1,0,0,0,0,0,0], [0,1,0,0,0,0,0,0,0,0]]
            
            if 'NoMantissaMeansError' in policies:
                if part == 'digits':
                    if all(sum(col) == 0 for col in Digits):
                        raise self.NoMantissa("User ticked no mantissa")
                
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
                        raise self.EmptyColumn("User ticked zero columns in a column (for {})".format(part))
                if sum(col) > 1:
                    raise self.MultipleTicksInColumn("User ticked two columns in a column (for {})".format(part))
            
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
    class Error(Exception):
        pass
    
    class CorrectorNoTick(Error):
        pass
    
    class CorrectorMultiTick(Error):
        pass

    def __init__(self, Dict:DictCollection, dbs:{'name':sqlite3}, seuil:float, exam:int, name:'QO1'):
        assert StandardNames.QO.fullmatch(name)
        self.Dict = Dict
        self.dbs = dbs
        self.seuil = seuil
        self.exam = exam
        self.name = name
        self.qnum = int(StandardNames.QO.fullmatch(name).group(1))
    
    def correctionValue(self) -> 4:
        if hasattr(self, '_correctionValue'):
            return self._correctionValue
        
        AmcQuestionId, LatexQuestionName = self.Dict.keylist('AmcQuestionId', 'LatexQuestionName')
        
        CaseToRatio = {
            digit: ratio if manual == -1 else manual
            for digit, ratio, manual in self.dbs['capture'].execute(f'''
                select id_b, 1.0*black/total, manual from capture_zone
                where student=?
                and type={ZONE_BOX}
                and id_a=?
                ''',
                (self.exam,
                LatexQuestionName(self.name).to(AmcQuestionId)))
        }
        assert all(0 <= v <= 1 for v in CaseToRatio.values())
        
        assert CaseToRatio.keys() == set(irange(1,11))
        
        points = [int(k)-1 for k,v in CaseToRatio.items() if v >= self.seuil]
        if len(points) == 0:
            raise self.CorrectorNoTick("no points ticked")
        
        if len(points) > 1:
            raise self.CorrectorMultiTick("too much points ticked")
        
        self._correctionValue = points[0]
        return self._correctionValue
    
    def correctionCommentsList(self) -> [0, 2, 3]:
        if hasattr(self, '_correctionCommentsList'):
            return self._correctionCommentsList
        
        LatexQuestionName, AmcQuestionId = self.Dict.keylist('LatexQuestionName', 'AmcQuestionId')
        
        AnswerAnnotate_to_Ratio = {
            digit: ratio if manual == -1 else manual
            for digit, ratio, manual in self.dbs['capture'].execute(f'''
                select id_b, 1.0*black/total, manual from capture_zone
                where student=?
                and type={ZONE_BOX}
                and id_a=?
                ''',
                (self.exam,
                LatexQuestionName(StandardNames.QOANN_FORMAT(self.qnum)).to(AmcQuestionId)))
        }
        assert AnswerAnnotate_to_Ratio.keys() == set(irange(1,7)) # 7 annotations possible
        annotations = [int(k)-1 for k,v in AnswerAnnotate_to_Ratio.items() if v >= self.seuil]
        
        self._correctionCommentsList = annotations
        return self._correctionCommentsList
    
class QMatriculeInfo:
    class Error(Exception):
        pass
    
    class StudentNoTick(Error):
        pass
    
    class StudentMultiTick(Error):
        pass

    def __init__(self, Dict:DictCollection, dbs:{'name':sqlite3}, seuil:float, exam:int):
        self.Dict = Dict
        self.dbs = dbs
        self.seuil = seuil
        self.exam = exam
    
    def matriculeValue(self) -> str:
        if hasattr(self, '_matriculeValue'):
            return self._matriculeValue
        
        AmcQuestionId, LatexQuestionName = self.Dict.keylist('AmcQuestionId', 'LatexQuestionName')
        
        matricule_list = []
        for nmatr in reversed(irange(1,6)):
            CaseToRatio = {
                digit: ratio if manual == -1 else manual
                for digit, ratio, manual in self.dbs['capture'].execute(f'''
                    select id_b, 1.0*black/total, manual from capture_zone
                    where student=?
                    and type={ZONE_BOX}
                    and id_a=?
                    ''',
                    (self.exam,
                    LatexQuestionName(StandardNames.QMAT_FORMAT(nmatr)).to(AmcQuestionId)))
            }
                    
            assert all(0 <= v <= 1 for v in CaseToRatio.values())

            assert CaseToRatio.keys() == set(irange(1,10)), 'When reading digit zmatr[{nmatr}], with student {self.exam}, found {} keys: {}'.format(
                len(CaseToRatio.keys()), list(CaseToRatio.keys()), nmatr=nmatr, self=self)
            
            points = [int(k)-1 for k,v in CaseToRatio.items() if v >= self.seuil]
            
            if len(points) == 0:
                raise self.StudentNoTick("no points ticked")
            
            if len(points) > 1:
                raise self.StudentMultiTick("too much points ticked")
            
            matricule_list.append(points[0])
        
        assert len(matricule_list) == 6, "matricule must have exactly 6 digits"
        
        self._matriculeValue = ''.join(map(str, matricule_list))
        return self._matriculeValue

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
    def __init__(self, filename, *, print_created=False):
        import os
        if os.path.splitext(filename)[1] == '':
            filename += '.xlsx'
        assert filename.endswith('.xlsx')
        import openpyxl
        self.filename = filename
        self.wb = openpyxl.Workbook()
        self.print_created = print_created
        
    def writerow(self, row):
        self.wb.active.append(row)
    
    def close(self):
        self.wb.save(self.filename)
        if self.print_created:
            info('Created', self.filename)
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()

class CSVWriter:
    def __init__(self, filename, *, print_created=False):
        import os
        if os.path.splitext(filename)[1] == '':
            filename += '.csv'
        assert filename.endswith('.csv')
        self.filename = filename
        self.f = open(filename, 'w', newline='')
        self.writer = csv.writer(self.f)
        self.print_created = print_created
        
    def writerow(self, row):
        self.writer.writerow(row)
    
    def close(self):
        self.f.close()
        if self.print_created:
            info('Created', self.filename)
    
    def __enter__(self):
        self.f.__enter__()
        return self
    
    def __exit__(self, type, value, traceback):
        self.f.__exit__(type, value, traceback)
        if self.print_created:
            info('Created', self.filename)

class CSVAndXLWriter:
    def __init__(self, filename, *, print_created=False):
        import os
        if os.path.splitext(filename)[1] == '':
            filename += '.csv'
        assert filename.endswith('.csv')
        self.csv = CSVWriter(filename, print_created=print_created)
        self.xl = XLWriter(filename[:-4] + '.xlsx', print_created=print_created)
        
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
    
class StandardNames:
    QO = Re('^QO(\d+)$')
    QO_FORMAT = 'QO{}'.format
    
    QF_SERIE = Re('^QF(?P<num>\d+)(?P<serie>\w)$')
    QF_SERIE_FORMAT = 'QF{num}{serie}'.format
    QF_DIGITS = Re('^QF(?P<num>\d+)(?P<serie>\w)(?P<part>digits|exp)$')
    QF_DIGITS_FORMAT = 'QF{num}{serie}{part}'.format
    
    QOANN = Re('^QANN(\d+)$')
    QOANN_FORMAT = 'QANN{}'.format
    
    QMAT = Re('^zmatr[\d+]$')
    QMAT_FORMAT = 'zmatr[{}]'.format

def DoAssociationAuto(SERIES=('A', 'B'), PROJECT_NAME:'string that may contain {serie} tag'='generateurAMC_{serie}'):
    assert len(set(map(str.lower, SERIES))) == len(SERIES), "no duplicates in series !"

    to_commit = []
    for serie in SERIES:
        proj = PROJECT_NAME.format(serie=serie)
        dbs = {name:sqlite3.connect(f'{proj}/data/{name}.sqlite') for name in ('layout', 'association', 'capture')}
        
        xmldoc = XmlElement.parse(f'{proj}/options.xml')
        try:
            seuil = float(xmldoc.find('seuil').text)
        except:
            seuil = 0.35
            warning(f'serie {serie}: seuil not found in xml, default seuil of {seuil} used')
        
        Dict = DictCollection()
        
        AmcQuestionId, LatexQuestionName = Dict.keylist('AmcQuestionId', 'LatexQuestionName')
        AmcStudentId, Matricule = Dict.keylist('AmcStudentId', 'Matricule')
        
        Dict[AmcQuestionId, 'to', LatexQuestionName] = dict_int_key(
            dbs['layout'].execute('''select question, name from layout_question'''))
        
        Mapping = []
        
        for student, in dbs['capture'].execute('select distinct student from capture_zone'):
            info = QMatriculeInfo(Dict, dbs, seuil, student)
            try:
                Mapping.append((student, info.matriculeValue()))
            except QMatriculeInfo.Error as e:
                warning(serie, student, e.__class__.__name__)
        
        assert set(x for x, in dbs['capture'].execute('select distinct copy from capture_page').fetchall()) <= {0}, f'In {proj}: Multiple copies are not allowed'
        
        current_records = int(dbs['association'].execute('select count(*) from association_association').fetchone()[0])
        assert current_records == 0, f'In {proj}: association_association must be empty but {current_records} records found'
        
        dbs['association'].executemany('''
            insert into association_association(student,copy,manual,auto)
            values (?,0,NULL,?)''', Mapping)
        to_commit.append(dbs['association'])
    
    for db in to_commit:
        db.commit()

def GenerateAnswers(*, SERIES=('A', 'B'), PROJECT_NAME:'string that may contain {serie} tag'='generateurAMC_{serie}'):
    assert len(set(map(str.lower, SERIES))) == len(SERIES), f"no duplicates in series, got {SERIES}"
    
    try:
        import openpyxl
        Writer = XLWriter
    except ImportError:
        warning('openpyxl not installed, no xlsx generated.')
        Writer = CSVWriter
        
    with Writer('all_closed_answers') as writer, Writer('frequencies') as other_writer:
      for serie in SERIES:
        proj = PROJECT_NAME.format(serie=serie)
        dbs = {name:sqlite3.connect(f'{proj}/data/{name}.sqlite') for name in ('layout', 'association', 'capture')}
        
        xmldoc = XmlElement.parse(f'{proj}/options.xml')
        try:
            seuil = float(xmldoc.find('seuil').text)
        except:
            seuil = 0.35
            warning(f'serie {serie}: seuil not found in xml, default seuil of {seuil} used')
        
        Dict = DictCollection()
        
        AmcQuestionId, LatexQuestionName = Dict.keylist('AmcQuestionId', 'LatexQuestionName')
        AmcStudentId, Matricule = Dict.keylist('AmcStudentId', 'Matricule')
        
        Dict[AmcQuestionId, 'to', LatexQuestionName] = dict_int_key(
            dbs['layout'].execute('''select question, name from layout_question'''))
        
        A = Dict[AmcStudentId, 'to', Matricule] = {
            int(student): int(auto or manual)
            for student, auto, manual in dbs['association'].execute('select student, auto, manual from association_association')
        }
        
        firstrow = ['examfull', 'matricule']
        
        qf_names = []
        for latexname in Dict[AmcQuestionId, 'to', LatexQuestionName].values():
            qf_match = StandardNames.QF_DIGITS.fullmatch(latexname)
            if qf_match and qf_match.group('part') == 'digits':
                m = qf_match.groupdict()
                basename = StandardNames.QF_DIGITS_FORMAT(part='', num=m['num'], serie=m['serie'])
                qf_names.append(basename)
        qf_names.sort()
        
        for basename in qf_names:
            firstrow.extend([basename + '_' + x for x in ('value', 'mantissa', 'exp', 'sign')])
        
        writer.writerow(firstrow)
        
        from collections import defaultdict, Counter
        aggreg = defaultdict(Counter)
        
        for exam, matricule in Dict[AmcStudentId, 'to', Matricule].items():
            examfull = "{}{}".format(serie, exam)
            row = [examfull, matricule]
            for basename in qf_names:
                info = QFInfo(Dict, dbs, seuil, exam, basename)
                
                try:
                    values = info.parseQF()
                    value = values['value'] # values['mantissa'], values['exp'], values['sign']
                    row.extend((values['value'], values['mantissa'], values['exp'], values['sign']))
                    
                    aggreg[basename][value] += 1
                
                except QFInfo.NoMantissa:
                    aggreg[basename][''] += 1
                    row.extend(('', ) * 4)
                
                except QFInfo.MultipleTicksInColumn:
                    warning(examfull, matricule, basename, 'MultipleTicksInColumn')
                    row.extend(('MultipleTicksInColumn', ) * 4)
            
            writer.writerow(row)
        
        # other_writer
        # from pprint import pprint
        from functools import partial
        for key, agg in aggreg.items():
            other_writer.writerow([key])
            revsorted = partial(sorted, reverse=True)
            for row in revsorted((y,x) for x,y in agg.items()):
                other_writer.writerow(row)
    
    globals()['info']('Created', other_writer.filename)
    globals()['info']('Created', writer.filename)

ANSWERS_PHYSS1001_JANVIER_2017_2018 = { # list of [value, min, max, -points minus]
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
    
ANSWERS_PHYSS1001_JUIN_2017_2018 = { 
    'QF7a': [
        [0, 0, 0, 0],
    ],
    'QF8a': [
        [6.53e6, 6.43e6, 6.63e6, 0],
    ],
    'QF9a': [
        [2.72e7, 2.62e7, 2.72e7, 0],
    ],
    'QF10a': [
        [2.83e-7, 2.73e-7, 2.93e-7, 0],
    ],
}

# from list to dict with optional keys
ANSWERS_PHYSS1001_JUINRATTR_2017_2018 = { # list of [value, min, max, -points minus]
    'QF7a': [
        [0, 0, 0, 0],
    ],
    'QF8a': [
        [6.53e6, 6.43e6, 6.63e6, 0],
    ],
    'QF9a': [
        [2.72e7, 2.62e7, 2.72e7, 0],
    ],
    'QF10a': [
        [2.83e-7, 2.73e-7, 2.93e-7, 0],
    ],
}
    
def ComputeMarks(*, OUT_FILE='all_marks', qf_answers, SERIES=('A', 'B'), PROJECT_NAME:'path to project, may contain {serie}'='generateurAMC_{serie}'):
    assert splitext(OUT_FILE)[1] == '', "please do not provide any extension"
    assert len(set(map(str.lower, SERIES))) == len(SERIES), f"no duplicates in series, got {SERIES}"
    
    assert all(len(L) > 0 for L in qf_answers.values())
    assert all(len(X) == 4 for L in qf_answers.values() for X in L)
    assert all(minus == 0 for L in qf_answers.values() for i,(value, m, M, minus) in enumerate(L) if i == 0)
    assert all(minus <= 0 for L in qf_answers.values() for value, m, M, minus in L)

    # TODO: assert no overlap : assert all(map(no_overlap, qf_answers.values()))

    question_formats = {
        # 'QO2': ReadFromMatriculeMarkCsv('q2-marks.csv', 'QO2'), # ReadFromAnnotate(''),
    }

    # should move in qf_answers
    qf_special_treatment = {
        'QF5a': {},
        'QF6a': {}, # {'SignMinus1'},
        'QF7a': {},
        'QF8a': {},
        'QF9a': {},
        'QF9a': {},
        'QF10a': {},
        'QF5b': {},
        'QF6b': {}, # {'SignMinus1'},
        'QF7b': {},
        'QF8b': {},
    }
    
    for k in qf_special_treatment:
        if not isinstance(qf_special_treatment[k], set):
            qf_special_treatment[k] = set(qf_special_treatment[k])

    assert all(X <= {'SignMinus1'} for X in qf_special_treatment.values())
    
    data_marks = []
    
    with CSVAndXLWriter(OUT_FILE, print_created=True) as writer:
        writer.writerow(('COPIE','MATRICULE','QUESTION','MARK','ANNOTATION','COMMENTS'))
        for serie in SERIES:
            proj = PROJECT_NAME.format(serie=serie)

            dbs = {name:sqlite3.connect(f'{proj}/data/{name}.sqlite') for name in ('layout', 'association', 'capture')}
            
            xmldoc = XmlElement.parse(f'{proj}/options.xml')

            try:
                seuil = float(xmldoc.find('seuil').text)
            except:
                seuil = 0.35
                warning(f'serie {serie}: seuil not found in xml, default seuil {seuil} used')
            
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
                    qf_match = StandardNames.QF_DIGITS.fullmatch(latexname) 
                    if qf_match and qf_match.group('part') == 'digits': # latexname = QF5digits
                        m = qf_match.groupdict()
                        basename = StandardNames.QF_DIGITS_FORMAT(part='', num=m['num'], serie=m['serie']) # basename = QF5a
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
                                if 'SignMinus1' in qf_special_treatment[basename] and values['sign'] != answer_sign:
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
                        
                        except QFInfo.NoMantissa:
                            mark = 0
                        
                        except QFInfo.MultipleTicksInColumn:
                            warning(examfull, matricule, basename, 'MultipleTicksInColumn')
                            mark = 0
                                
                    elif StandardNames.QO.fullmatch(latexname):
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
                            except QOInfo.Error as e:
                                error(examfull, matricule, basename, e.__class__.__name__)
                                continue
                    else:
                        continue
                    writer.writerow((examfull, matricule, basename, mark, ''.join(chr(ord('A') + i) for i in annotations), str(comments)))
                    data_marks.append((examfull, matricule, basename, mark))
    
    # generate pretty xl
    # TODO: make it work for series
    
    all_questions = set() # not mandatory
    student_info = {}
    for examfull, matricule, basename, mark in data_marks:
        if matricule not in student_info:
            student_info[matricule] = {
                'exam': examfull,
                'questions': {},
            }
        else:
            assert student_info[matricule]['exam'] == examfull, f"Student {matricule} has mutiple exams {student_info[matricule]['exam']}, {examfull}!"
            
        student_info[matricule]['questions'][basename] = mark
        all_questions.add(basename) # not mandatory
    
    assert all(student_info[matricule]['questions'].keys() == all_questions for matricule in student_info) # not mandatory
    
    def sort_key(basename):
        first = (2 if basename.startswith('QF') else 
                 1 if basename.startswith('QO') else
                 3)
        digits = Re('\d+').findall(basename)
        second = int(digits[0]) if digits else 1000
        return first, second
    
    all_questions = sorted(all_questions, key=sort_key)
    
    with CSVAndXLWriter(OUT_FILE + '_pretty', print_created=True) as writer:
        firstrow = ['MATRICULE', 'EXAM'] + list(all_questions)
        writer.writerow(firstrow)
        for matricule in sorted(map(int, student_info)):
            row = [matricule, student_info[matricule]['exam']]
            for question in all_questions:
                row.append( student_info[matricule]['questions'][question] )
            writer.writerow(row)
