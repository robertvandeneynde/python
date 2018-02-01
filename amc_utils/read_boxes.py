import sqlite3

serie = 'A'
proj = f'generateurAMC_{serie}'

db_layout = sqlite3.connect(f'{proj}/data/layout.sqlite')
db_capture = sqlite3.connect(f'{proj}/data/capture.sqlite')

def dict_int_key(it):
    return {int(a):b for a,b in it}

def reverse_dict(D, check_uniq=False):
    R = {y:x for x,y in D.items()}
    if check_uniq and not(len(R) == len(D)):
        raise ValueError('Not a bijection')
    return R

def dict_pair(D):
    return D, reverse_dict(D)

AmcQuestionId_to_LatexQuestionName, \
AmcQuestionId_to_LatexQuestionName = dict_pair(
    dict_int_key(
        db_layout.execute('''
            select question, name from layout_question'''))

ZONE_BOX = 4

class QOInfo:
    def __init__(exam:int, name:'QO1'):
        
        assert name.startswith('QO')
        
        CaseToRatio = dict(db_capture.execute(f'''
            select id_b, 1.0*black/total from capture_zone
            where student=?
            and type={ZONE_BOX}
            and id_a=?
            order by id_b
            ''',
            (
                exam,
                LatexQuestionName_from_AmcQuestionId[name],
            )
        ))
            
        assert CaseToRatio.keys() == {0,1,2,3,4,5,6,7,8,9,10}
        
        seuil = 0.35 # <seuil>0.35</seuil>
        
        points = [k for k,v in CaseToRatio.items() if v >= seuil]
        
        assert len(points) > 0, "not enough"
        assert len(points) < 2, "too much"
    
    def correctionValue(self) -> 4:
        pass # TODO
    
    def correctionCommentsList(self) -> [0, 2, 3]:
        pass # TODO
    
