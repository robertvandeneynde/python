#!/usr/bin/env python3
# coding: utf-8

import re
from re import compile as Re
import pytz
from datetime import datetime, date, time, timedelta
from itertools import filterfalse
from collections import defaultdict

IN_FILE = 'cfs-v1.txt'
GEHOL_FILE = 'calendar(18).ics'  # gehol-q2.ics'
ASSISTANTS = '''
    watchi decrol mahrou tillema gernier
    dierick arnhem jvc vanden friob vanwelde
    chimie casier imatouchan jvc
'''.split()
PREFIX_PER_ASSISTANT = {}
DEFAULT_PREFIX = "TP"
ALL_DURATION = '2h'
SEANCES = 'num'  # empty meaning not present, 'num' meaning numbers, 'letters' meaning letters, 'mixed' meaning numbers and text
GROUPS_PREFIXES = ('IrBi', 'IrCi', 'InGe', 'IrAr')  # groups begin with a prefix, then possibly a number
ALL_ASSISTANTS = 'all-assistants-2.ics'  # if not empty, name of ics file where all the assistants are merged

if ALL_ASSISTANTS:
    if ALL_ASSISTANTS.endswith('.ics'):
        ALL_ASSISTANTS = ALL_ASSISTANTS[:-4]

if SEANCES:
    SEANCES = {'letter': 'letters'}.get(SEANCES, SEANCES)
    assert SEANCES in ('num', 'letters', 'mixed')

GROUPS = GROUPS_PREFIXES

DAYS = 'lun|mar|mer|jeu|ven|sam|dim'.split('|')
DAY = Re('|'.join(DAYS))

HOUR = Re('(\d+)[h:](\d*)')
HOUR_FROM = Re('(de|from)(\d+)[h:](\d*)')
HOUR_TO = Re('(à|to)(\d+)[h:](\d*)')
DATE = Re('(\d+)/(\d+)')
WEEK_SHIFT = Re('([+-]\d*)w')

GROUP = Re('(' + '|'.join(map(re.escape, map(str, GROUPS))) + ')(\d*)', re.I)
SEANCE = Re('S({})'.format({'num': '\d+', 'letters':'\w+', 'mixed':'[\d\w]+'}[SEANCES]), re.I) if SEANCES else Re('')
ASSISTANT = Re('|'.join(map(re.escape, ASSISTANTS)), re.I)

DURATION_RE = Re('(\d+)h(\d\d)?(min)?|(\d+)min')
assert DURATION_RE.fullmatch(ALL_DURATION), '"{ALL_DURATION}" is not like "6h" or "6h30" or "5min"'

def convert_duration(string):
    hour, minute, _, single_minute = DURATION_RE.fullmatch(string).groups()
    if single_minute:
        return timedelta(minutes=int(single_minute))
    else:
        return timedelta(hours=int(hour), minutes=int(minute or 0))

DURATION = convert_duration(ALL_DURATION)

try:
    import search_for_ics_gehol
except ImportError:
    print('[Warning] no module search_for_ics_gehol, locations will be empty')
    search_for_ics_gehol = None

RE_LIST = (
    [DAY, HOUR, HOUR_FROM, HOUR_TO, DATE, WEEK_SHIFT]
    + [ASSISTANT] * bool(ASSISTANT)
    + [GROUP] * bool(GROUPS)
    + [SEANCE] * bool(SEANCES)
)

is_none = lambda x: x is None
is_not_none = lambda x: x is not None

# [convert(L[0][i]) for i in range(len(L[0]))]

def naive_to_utc(naive):
    return pytz.timezone('Europe/Brussels').localize(naive, is_dst=None).astimezone(pytz.utc)

def printret(x): print(x); return x

class Memorizer:
    def __init__(self):
        self.cache = {}
        
    def ask(self, name):
        if name in self.cache:
            return self.cache[name]
        self.cache[name] = input(str(('Is assistant ?', name, '[Y/n]'))) not in ('n', )
        return self.cache[name]

memorizer = Memorizer()

def convert(bit):
    M = [(r, r.fullmatch(bit)) for r in RE_LIST]
    F = [(r,m) for r,m in M if m]
    if len(F) == 0 and memorizer.ask(bit):
        return ('assistant', bit)
    assert len(F) == 1, f"in {bit}: exactly one must match, but {len(F)} matched"
    return F[0]

text_bits_per_assistant = defaultdict(list)

with open(IN_FILE) as f:
    lines = [l.strip('\n').strip() for l in f]

for line in filterfalse(Re('\s*#').match, filter(bool, lines)):
    
    year = 2018
    delta = timedelta(0)
    month, day, weekday, hour, minute, hour_end, minute_end, *nones = [None] * 100

    assistants = []
    groups = []
    seances = []
    
    for r, m in map(convert, line.split()):
        if r is DAY:
            DAYS.index(m.group(0))
        elif r is HOUR:
            hour, minute = int(m.group(1)), int(m.group(2) or 0)
        elif r is HOUR_FROM:
            hour, minute = int(m.group(2)), int(m.group(3) or 0)
        elif r is HOUR_TO:
            hour_end, minute_end = int(m.group(2)), int(m.group(3) or 0)
        elif r is DATE:
            day, month = int(m.group(1)), int(m.group(2))
        elif r is GROUP:
            groups.append((m.group(1), m.group(2)))
        elif r is SEANCE:
            seances.append(int(m.group(1)))
        elif r is ASSISTANT:
            assistants.append(m.group(0).lower())
        elif r == 'assistant':
            assistants.append(m.lower())
        elif r is WEEK_SHIFT:
            delta = timedelta(weeks=int(m.group(1)))
        else:
            raise AssertionError
    
    if not ASSISTANTS:
        assert not assistants
        assistants = ['default']
    
    assert len(assistants) > 0, f"on line {line}: at least one assistant"
    
    if GROUPS:
        assert len(assistants) == len(groups), f"on line {line}: length differs, assistants:{len(assistants)}, groups:{len(groups)}, seances:{len(seances)}"
    assert len(assistants) == len(seances), f"on line {line}: length differs, assistants:{len(assistants)}, groups:{len(groups)}, seances:{len(seances)}"
    assert all(map(is_not_none, (month, day, hour, minute))), f"on line {line}: missing required parts in {line}: month {month}, day {day}, hour {hour}, minute {minute}"

    base_time = datetime(year, month, day, hour, minute) + delta
    
    if hour_end is not None:
        assert DURATION == datetime.combine(base_time, time(hour_end, minute_end)) - base_time, f"Duration must be {ALL_DURATION}"
    
    if weekday is not None:
        assert base_time.weekday() == weekday
        
    utc = naive_to_utc(base_time)
    
    beg = utc
    end = utc + DURATION
    
    for i in range(len(assistants)):
        assistant = assistants[i]
        seance = seances[i]
        
        prefix = PREFIX_PER_ASSISTANT.get(assistant, DEFAULT_PREFIX)
        
        if ALL_ASSISTANTS:
            prefix = (prefix + ' ' + assistant).strip()
        
        if GROUPS:
            grouptype, groupnum = groups[i]
            summary = f'{prefix} {grouptype}{groupnum} S{seance}'
        else:
            summary = f'{prefix} S{seance}'
        
        if search_for_ics_gehol and GEHOL_FILE:
            Devent = {
                'DTSTART': f'{beg:%Y%m%dT%H%M%S}Z',
                'DTEND': f'{end:%Y%m%dT%H%M%S}Z',
                'SUMMARY': summary,
            }
            location = search_for_ics_gehol.find_matching_location(Devent, GEHOL_FILE)
        else:
            location = 'Gehol'
        
        text_bits_per_assistant[assistant].append(f"""
            BEGIN:VEVENT
            DTSTART:{beg:%Y%m%dT%H%M%S}Z
            DTEND:{end:%Y%m%dT%H%M%S}Z
            LOCATION:{location}
            SUMMARY:{summary}
            END:VEVENT
        """)

if ALL_ASSISTANTS:
    text_bits_per_assistant = {
        ALL_ASSISTANTS: [text_bit for text_bits in text_bits_per_assistant.values()
                                  for text_bit in text_bits]
    }

for assistant, text_bits in text_bits_per_assistant.items():
  with open(printret(f'{assistant}.ics'), 'w') as outfile:
    text_bits.insert(0, '''
        BEGIN:VCALENDAR
        PRODID:-//Google Inc//Google Calendar 70.9054//EN
        VERSION:2.0
        CALSCALE:GREGORIAN
        METHOD:PUBLISH
    ''') # X-WR-CALNAME:TP Robert
    
    text_bits.append('''
        END:VCALENDAR
    ''')
    
    outfile.write('\n'.join(
        line_string.strip()
        for line_string in '\n'.join(text_bits).split('\n')
        if line_string.strip()
    ) + '\n')
