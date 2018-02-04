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

if __name__ != '__main__':
    import sys
    sys.exit(0)

QO = Re('QO(\d+)')
QO_FORMAT = 'QO{}'.format

QOANN = Re('QANN(\d+)')
QOANN_FORMAT = 'QANN{}'.format

ZONE_BOX = 4

SERIES = ('A', 'B')
PROJ_NAME_FROM_SERIE = lambda x: 'generateurAMC_{}'.format(x.upper())

qo_info = {
    'QO2': ReadFromMatriculeMarkCsv('q2-marks.csv', 'QO2'), # ReadFromAnnotate(''),
}

for serie in SERIES:
    proj = PROJ_NAME_FROM_SERIE(serie)
    # student_csv = f'.csv'

    dbs = defaultdict(lambda name: sqlite3.connect(f'{proj}/data/{name}.sqlite'))

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
        if not QO.match(latexname):
            continue # TODO QF (see compute_digits)
        for exam, matricule in Dict[AmcStudentId, 'to', Matricule].items():
            if latexname in qo_info and isinstance(qo_info[latexname], ReadFromMatriculeMarkCsv):
                mark = qo_info[latexname].Matricule(matricule).to(qo_info[latexname].Mark)
                annotations = [] # TODO
            else: # FromScannedAnnotationsAndMark
                try:
                    info = QOInfo(Dict, dbs, seuil, exam, latexname)
                    mark = info.correctionValue()
                    annotations = info.correctionCommentsList()
                except (QOInfo.CorrectorMultiTick, QOInfo.CorrectorNoTick) as e:
                    error("{}{}".format(serie, exam), matricule, latexname, e.__class__.__name__, e.__class__.__name__)
                    continue
            print("{}{}".format(serie, exam), matricule, latexname, mark, ''.join(chr(ord('A') + i) for i in annotations))
