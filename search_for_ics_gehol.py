#!/usr/bin/env python3
from pprint import pprint
import re
from re import compile as Re
from datetime import datetime

_ics_cache = {}

def naive_to_utc(naive):
    import pytz
    return pytz.timezone('Europe/Brussels').localize(naive, is_dst=None).astimezone(pytz.utc)

def assertret(x, f, msg=''): assert f(x), msg; return x
def printret(x): print(x); return x
def pprintret(x): pprint(x); return x
def throw(e): raise e

is_not_none = lambda x: x is not None

def find_matching_location(event:dict, filename):
    if filename not in _ics_cache:
        _ics_cache[filename] = list(parse_ics_vevent(filename))
    event_list = _ics_cache[filename]
    
    a = event
    gt, ga = Re('(InGe|IrBi|IrCi|IrAr)(\d*)', re.I).search(a['SUMMARY']).groups()
    
    LT = [
        b for b in event_list
        for _ in [ b['DTSTART;TZID=Europe/Brussels'] ]
        for _ in [ datetime.strptime(_, '%Y%m%dT%H%M%S') ]
        for _ in [ naive_to_utc(_) ]
        for _ in [ _.strftime('%Y%m%dT%H%M%S') ]
        if _ == a['DTSTART'][:-1]
    ]
    
    L = [
        b for b in LT
        for ddict in [ event_desc_dict(b) ]
        for m in [ Re('(INGE|IRBI|IRAR|IRCI) - (?:groupe |gr.)(\d+)', re.I).search(b['DESCRIPTION']) ]
        if m
        for ogt, oga in [ m.groups() ]
        if int(ga) == int(oga) and gt.lower() == ogt.lower()
    ] if gt.lower() != 'irar' else [
        b for b in LT
        for ddict in [ event_desc_dict(b) ]
        if Re('irar', re.I).search(b['DESCRIPTION'])
        and not Re('Théorie', re.I).search(b['DESCRIPTION'])
    ]
    # TODO: use event_groups(b) :  "B1-IRBI - gr.5" "B1-INGE - groupe 04" "B1-IRAR"
    # TODO: use event_acti(b)
    
    if len(L) == 1:
        return L[0]['LOCATION']
    elif len(L) > 1:
        return 'Gehol Too Much {}'.format(' '.join(l['LOCATION'] for l in L))
    elif len(L) == 0:
        return 'Gehol Not Found'

def ReGroups(N, match):
    return match.groups() if match else (None,) * N

def GetDict(d, *keys):
    return [d[k] for k in keys]

def parse_ics_vevent(filename):
    """
    yields dict like
    {'DESCRIPTION': 'stuff', 'DTSTART':20120101T010101'}
    or {'DESCRIPTION': 'stuff', 'DTSTART;TZID=Europe/Brussels':20120101T010101'}
    """
    class EOF(Exception):
        pass
    
    def nextline():
        l = f.readline()
        if not l:
            raise EOF
        return l.strip()
    
    with open(filename) as f:
        try:
            while True:
                l = nextline()
                if l == 'BEGIN:VEVENT':
                    d = {}
                    while True:
                        l = nextline()
                        if l == 'END:VEVENT':
                            break
                        a,b = l.split(':', 1)
                        d[a] = b
                    yield d     
        except EOF:
            return

def group_id_from_descdict(dic):
    m = Re('groupe (\d+)').search(dic['Groupes'])
    return 0 if not m else int(m.group(1))

def event_groups(event):
    ddict = event_desc_dict(event)
    return list(map(str.strip, ddict['Groupes'].split('\\,')))

def event_acti(event) -> ('Travaux Pratiques', 'Théorie', 'Exercices'):
    ddict = event_desc_dict(event)
    return ddict['Activité']

def event_desc_dict(event):
    return {
        a.strip(): b.strip()
        for bit in event['DESCRIPTION'].split('\\n')
        for a,b in [ bit.split(':', 1) ]
    }
        
