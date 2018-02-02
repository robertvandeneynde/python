import sqlite3
import csv
import re

Re = re.compile

serie = 'A'
proj = f'generateurAMC_{serie}'
# student_csv = f'.csv'

db_layout = sqlite3.connect(f'{proj}/data/layout.sqlite')
db_capture = sqlite3.connect(f'{proj}/data/capture.sqlite')
db_association = sqlite3.connect(f'{proj}/data/association.sqlite')

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
    
    def __init__(self):
        self.dicts = {}
    
    def __setitem__(self, tup:('a', 'action:from|to', 'b'), D:dict):
        a, action, b = tup
        if isinstance(a, DictCollection.ColumnId):
            a = a.name
        if isinstance(b, DictCollection.ColumnId):
            b = b.name
        
        action = action.lower()
        assert action in ('from', 'to')
        
        if action == 'to':
            a,b = b,a
        
        self.dicts[a,b] = D
        if (b,a) in self.dicts:
            del self.dicts[b,a] # modification
    
    def __getitem__(self, tup:('a', 'action:from|to', 'b')) -> dict:
        """
        Dict['Matricule', 'to', 'AmcStudentId']
        Dict['AmcStudentId', 'from', 'Matricule']
        """
        a, action, b = tup
        if isinstance(a, DictCollection.ColumnId):
            a = a.name
        if isinstance(b, DictCollection.ColumnId):
            b = b.name
        
        action = action.lower()
        assert action in ('from', 'to')
        
        if action == 'to':
            a,b = b,a
        
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
    
    def populateDictWithKeys(self, n, *args):
        for n in args:
            D[n] = self(n)
class QOInfo:
    class CorrectorNoTick(Exception):
        pass
    
    class CorrectorMultiTick(Exception):
        pass

    def __init__(self, exam:int, name:'QO1'):
        
        assert QO.match(name)
        qnum = int(QO.match(name).group(1))
        
        D = DictCollection()
        
        CaseToRatio = D['AnswerPoints', 'to', 'Ratio'] = dict(db_capture.execute(f'''
            select id_b, 1.0*black/total from capture_zone
            where student=?
            and type={ZONE_BOX}
            and id_a=?
            ''',
            (exam,
             LatexQuestionName(name).to(AmcQuestionId))
        ))
            
        CaseToRatioAnnotate = D['AnswerAnnotate', 'to', 'Ratio'] = dict(db_capture.execute(f'''
            select id_b, 1.0*black/total from capture_zone
            where student=?
            and type={ZONE_BOX}
            and id_a=?
            ''',
            (exam,
             LatexQuestionName(QOANN_FORMAT(qnum)).to(AmcQuestionId))
        ))
        
        assert CaseToRatio.keys() == set(irange(1,11))
        assert CaseToRatioAnnotate.keys() == set(irange(1,7)) # 7 annotations possible
        
        points = [int(k)-1 for k,v in CaseToRatio.items() if v >= seuil]
        annotations = [int(k)-1 for k,v in CaseToRatioAnnotate.items() if v >= seuil]
        
        if len(points) == 0:
            raise QOInfo.CorrectorNoTick("no points ticked")
        
        if len(points) > 1:
            raise QOInfo.CorrectorMultiTick("too much points ticked")
        
        self._correctionValue = points[0]
        self._correctionCommentsList = annotations
    
    def correctionValue(self) -> 4:
        return self._correctionValue
    
    def correctionCommentsList(self) -> [0, 2, 3]:
        return self._correctionCommentsList

import xml.etree.ElementTree as ET
xmldoc = ET.parse(f'{proj}/options.xml')

try:
    seuil = float(xmldoc.find('seuil').text)
except:
    warning('seuil not found in xml, default seuil used')
    seuil = 0.35
    
ZONE_BOX = 4

Dict = DictCollection()
AmcStudentId, Matricule = Dict.keylist('AmcStudentId', 'Matricule')
AmcQuestionId, LatexQuestionName = Dict.keylist('AmcQuestionId', 'LatexQuestionName')

Dict[AmcQuestionId, 'to', LatexQuestionName] = dict_int_key(
    db_layout.execute('''select question, name from layout_question'''))

Dict[AmcStudentId, 'to', Matricule] = {
    int(student): int(auto or manual)
    for student, auto, manual in db_association.execute('select student, auto, manual from association_association')
}

QO = Re('QO(\d+)')
QO_FORMAT = 'QO{}'.format

QOANN = Re('QANN(\d+)')
QOANN_FORMAT = 'QANN{}'.format

for qid, latexname in Dict[AmcQuestionId, 'to', LatexQuestionName].items():
    if QO.match(latexname):
        for exam, matricule in Dict[AmcStudentId, 'to', Matricule].items():
            try:
                info = QOInfo(exam, latexname)
                value, annotations = info.correctionValue(), info.correctionCommentsList()
                print(exam, matricule, latexname, value, ''.join(chr(ord('A') + i) for i in annotations))
            except (QOInfo.CorrectorMultiTick, QOInfo.CorrectorNoTick) as e:
                error(e.__class__.__name__, exam, matricule, latexname)
