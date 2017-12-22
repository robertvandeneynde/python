import csv
import sys
from pprint import pprint # for debugging

assert sys.version_info[0] >= 3, "Python 3 please"

FILENAME = 'generateurAMC_B.csv' 

assert FILENAME.endswith('.csv')

with open(FILENAME) as f:
    csvMatrix = list(csv.DictReader(f))

if not csvMatrix:
    print('Empty csv')
    sys.exit(1)

MANDATORY_COLUMNS = {'Exam', 'A:Matricule', 'Name', 'Mark', 'zmatr'} | {'zmatr[{}]'.format(i) for i in (1,2,3,4,5,6)}
FIELDS = set(csvMatrix[0].keys()) # DictReader enforces that all(l.keys() == FIELDS for l in csvMatrix)
assert MANDATORY_COLUMNS <= FIELDS, "Missing columns: {}".format(MANDATORY_COLUMNS - FIELDS)
Questions = {f for f in FIELDS - MANDATORY_COLUMNS if not f.startswith('TICKED:')}

def parseQF(csvLine:list, name:'QF1b'):
    def parsePart(part:'digits|exp', expectedNumbers:3):
    
        field = 'TICKED:{}{}'.format(name, part)
        Mantiss = list(map(int, csvLine[field.format(name)].split(';')))
        
        assert len(Mantiss) == 2 + expectedNumbers * 10
        
        Sign = Mantiss[0:2]
        Digits = [Mantiss[2 + n : 2 + n + 10] for n in range(0, 10 * expectedNumbers, 10)]
        
        for col in [Sign] + Digits:
            assert sum(col) == 1, "User ticked two columns in a column (for {})".format(part)
        
        sign = (+1 if Sign[0] else -1)
        digits = [next(i for i in range(len(D)) if D[i]) for D in Digits]
        
        number = sign * sum(n * 10 ** (-i) for i,n in enumerate(digits))
    
        return number
    
    number = parsePart('digits', 3)
    numberExp = parsePart('exp', 1)
    numberFinal = number * 10 ** numberExp
    
    return numberFinal

ClosedQuestionsColumns = {q for q in Questions if q.startswith('QF')}

assert all(c.endswith('digits') or c.endswith('exp') for c in ClosedQuestionsColumns)
for a,b in (('digits', 'exp'), ('exp', 'digits')):
    assert all(c[:-len(a)] + b in ClosedQuestionsColumns
               for c in ClosedQuestionsColumns
               if c.endswith(a))

ClosedQuestions = {c[:-len('digits')] for c in ClosedQuestionsColumns if c.endswith('digits')}

print('ClosedQuestions', ClosedQuestions)
for student in csvMatrix[:2]:
    answers = {}
    
    for q in ClosedQuestions:
        try:
            answers[q] = parseQF(student, q)
        except Exception as e:
            answers[q] = e
    
    pprint([student['A:Matricule'], 'has', answers])
