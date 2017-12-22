import csv
import sys
from pprint import pprint # for debugging

assert sys.version_info[0] >= 3, "Python 3 please"

FILENAME = 'generateurAMC_B.csv' 

POLICIES = {'EmptyColumnMeansZero'} # set() # {'NoSignMeansPlus'}

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

class EmptyColumn(Exception):
    pass

class MultipleTicksInColumn(Exception):
    pass

def parseQF(csvLine:list, name:'QF1b', *, policies=POLICIES):
    def parsePart(part:'digits|exp', expectedNumbers:3, *, base=10, hasSign=True, direction:'plus|minus'='plus'):
        """
        Parse a signed number.
        if hasSign, the first two boxes contains the sign (first = +, second = -).
        Then we have base=10 expectedNumbers boxes representing numbers. For example expectedNumbers = 3, digits = [6,0,9].
        If direction == "plus" Then Digits represents 609
        If direction == "minus" Then Digits represents 6.09
        """
        assert part in ('digits', 'exp') and direction in ('plus', 'minus')
    
        field = 'TICKED:{}{}'.format(name, part)
        Ticks = list(map(int, csvLine[field.format(name)].split(';')))
        
        # Example: Ticks = [0,1, 0,0,0,1,0,0,0,0,0,0, 0,1,0,0,0,0,0,0,0,0]
        
        assert len(Ticks) == (2 if hasSign else 0) + expectedNumbers * base
        
        if hasSign:
            Sign = Ticks[0:2]
            Digits = [Ticks[2+n : 2+n+base] for n in range(0, base * expectedNumbers, base)]
        else:
            Sign = [1,0] # Positive
            Digits = [Ticks[n : n+base] for n in range(0, base * expectedNumbers, base)]
        
        if Sign == [0,0] and 'NoSignMeansPlus' in policies:
            Sign = [1,0]
        
        # Example if hasSign == True and base == 10: Sign = [0,1]; Digits = [[0,0,0,1,0,0,0,0,0,0], [0,1,0,0,0,0,0,0,0,0]]
        
        for col in [Sign] + Digits:
            if sum(col) == 0:
                if 'EmptyColumnMeansZero' in policies:
                    col[0] = 1
                else:
                    raise EmptyColumn("User ticked zero columns in a column (for {})".format(part))
            if sum(col) > 1:
                raise MultipleTicksInColumn("User ticked two columns in a column (for {})".format(part))
        
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
