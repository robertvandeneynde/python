#!/usr/bin/env python3
import getpass
import sqlite3

import os, sys, re
assert sys.version_info >= (3, 6)
from re import compile as Re

import csv
from pprint import pprint
import itertools
from itertools import groupby
from collections import namedtuple, Counter
from functools import lru_cache

import django
from django.conf import settings
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
import xml.etree.ElementTree as ET
import smtplib

HEADER        = 'PHYSH101 Examen Physique Juin 2017-2018'

NUM_PAGES     = 6 - 1 # Pages expected from the amc project
NUM_PAGES_CONSECUTIVE = False # If True, page numbers must be from 1 to NUM_PAGES
NUM_PAGES_INCLUDE_STATIC = [5] # Include the static pages called "subject-{serie}-page-{numpage}.jpg"

SEND_MAIL     = False # If False, no mail will be sent
PRINT_MAIL    = False # If True, mail will be printed, not sent.
TEST_COMMENTS = False # if True, 1 mail will be sent will all the contents of comments.xml
TO_ONE_PERSON = False # 'yuluuu@ulb.ac.be' # if present, all mails go to here
ALSO_TO       = False # 'yolooo@ulb.ac.be' # if present, send also to here
SEND_FROM     = 'yuluuu@ulb.ac.be' # must be a ulb address
COMPUTE_MARK  = False
MAKE_PDF      = True # if true, images are merged in one pdf, otherwise, each image is sent attached to the mail
MAKE_STATS    = 'stats.csv' # if not empty, path of .csv (or .xlsx) to store stats for each <question> in xml with number of times sent
STATS_INCLUDE_COMMENT = True # if True, include <comment> from xml and not just the <comment[name]>
STATS_GENERATE_TXT = True # if True, include a txt version (stats.txt) (when MAKE_STATS = stats.csv)

# WARNING: Tex support very basic (you'll probably have to edit generated file)
STATS_GENERATE_TEX = False # if True, include a tex version (stats.tex) (when MAKE_STATS = stats.csv)
STATS_TEX_TEMPLATE = 'faq-base.tex' # if not empty, template tex file, \content and \header will be replaced

STATS_GENERATE_HTML = True # if True, include stats.csv (when MAKE_STATS = stats.csv)
STATS_HTML_TEMPLATE = False # 'faq-base.html' # if not empty, template html file, {{ content }} and {{ header }} will be replaced

# Flow control
MAX_EMAIL        = None # None means no limit, 1 for example can be used for testing (send only 1 mail).
SKIP_LIMIT       = None # None or 0 means begin at first student, otherwise, skip SKIP_LIMIT students.
FILTER_MATRICULE = None # Default : None, can also be a int, or a list of int; or a function taking a int
FILTER_NETID     = None # Default : None, can also be a netid, or a list of netid, or a regex, or a function taking a str

# XML OPTIONS
CONFIG_XML = 'comments.xml'

# CSV OPTIONS
# All CSV must have first line as Header
# They must be English style "," separated, '"' if needed
# If there are decimal points, English style too "1.5" not "1,5".
# Ie. They can be read with python DictReader(file)
STUDENT_FILE_CSV = '../201718_PHYS-H-101_SES1_36418.csv' # '201718_PHYS-S-1001_SES1_ecursus.csv' # Must have MATRICULE and NETID columns, can have PRENOM and NOM.
QUESTIONS_TICKED_FILE_CSV = '' # 'ExamenJanvier2018Brut_numerical_values_refilled.csv' # Must have COPIE, A:MATRICULE, TICKED ";" amc option, "," separated. Pair QO1/QO1COMMENTS

# Directories OPTIONS
SERIES = ('a', 'b') # if empty or None, implies only one project
PDF_DIR = '.' # deprecated
AMC_PROJECT = "generateurAMC_{serie}" # if series are used: {serie} will be replaced by for example "a" (see SERIES)
ANNOTATE_CSV_PATH = "q{qid}-tags.csv"
# TODO: decide if paths should go in XML

if SERIES:
    assert all(Re('^[^\W\d_](.*[^\W\d_])?$').match(serie) for serie in SERIES), "Series must begin and end with letters"
    assert len(set(SERIES)) == len(SERIES), "No duplicates allowed in series"

settings.configure(
    EMAIL_USE_TLS = True,
    EMAIL_HOST = 'smtp.ulb.ac.be',
    EMAIL_PORT = 587,
    EMAIL_HOST_USER = SEND_FROM,
    EMAIL_HOST_PASSWORD = getpass.getpass() if SEND_MAIL else '',
)

assert SEND_MAIL + PRINT_MAIL <= 1, "maximum one of SEND_MAIL, PRINT_MAIL"

if MAKE_PDF:
    import img2pdf # https://gitlab.mister-muffin.de/josch/img2pdf

ZONE_BOX = 4

def warning(*args): # orange
    print('\033[33m' + 'Warning:', *args, '\033[0m')
    
def info(*args): # green
    print('\033[32m' + 'Info:', *args, '\033[0m')

def error(*args): # error
    print('\033[31m' + 'Error:', *args, '\033[0m')

def is_regex(obj):
    return isinstance(obj, re.compile('').__class__)

def irange(*args):
    """ inclusive_range: irange(1,5) == range(1,6) """
    r = range(*args)
    return range(r.start, r.stop + 1, r.step)

def dict_int_key(it):
    return {int(a):b for a,b in it}

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

class SerieSwitch:
    """
    SerieSwitch([
        "Hello {m}, I am {R}".format(m='m', R='R'),
        "Hello {m}, I am {R}".format(m='M', R='L'),
    ]) -> mapping = {'a': 'Hello m, I am R', 'b': 'Hello M, I am L'}
    
    SerieSwitch.from_dict_to_list(txt, {
        'h': ['h', 'L'],
        'alpha': ['α', 'θ'],
    })
    
    SerieSwitch.from_kwargs_to_list(txt,
        C2H6 = ['C₂H₆', 'C₄H₁₀'],
        ethane = ['éthane', 'buthane'],
        buthane = ['buthane', 'éthane'],
        six = [6, 8],
    )
    """
    
    def __init__(self, L):
        assert len(L) == len(SERIES)
        self.mapping = dict(zip(SERIES, L))
    
    def text_for_serie(self, serie):
        return self.mapping[serie]
    
    @staticmethod
    def from_dict_to_list(txt, d):
        """ SerieSwitch.from_dict_to_list('hello {m}', {'m': ['m', 'M'], 'R': ['R', 'L']}) """
        return SerieSwitch([
            txt.format(**{k:L[i] for k,L in d.items()})
            for i in range(len(SerieSwitch._fields))
        ])
    
    @staticmethod
    def from_kwargs_to_list(txt, *args, **kwargs): # beware: 'txt' not in kwargs
        """ SerieSwitch.from_dict_to_list('hello {m}', m=['m', 'M'], R=['R', 'L']}) """
        if args:
            raise ValueError('No args')
        return SerieSwitch.from_dict_to_list(txt, kwargs)

class TagSource:
    pass

class TagSourceAmcAnnotatedCopy(TagSource):
    pass

class TagSourceCsvImageAnnotate(TagSource):
    
    @lru_cache(None)
    def data_for_qid(self, qid):
        with open(ANNOTATE_CSV_PATH.format(qid=qid)) as f:
            L = list(csv.reader(f))
        
        assert all(len(x) == 2 for x in L)
        
        return {
            a: tuple(b.split())
            for a,b in L
        }

from collections import OrderedDict, defaultdict
class FaqInfo:
    """
    info: OrderedDict(question -> OrderedDict(comment -> text to send over mail))
    the text to send over mail can be a SerieSwitch that will select text based on serie (not used in EXAM_IRCI_2017_2018_JANVIER)
    
    example:
    info = OrderedDict{ "1": OrderedDict{"accel": "L'accélération c'est cool."},
                        "2": OrderedDict{ "vf=0": "Pour que bille reste en contact.",
                                          "nrj": "Attention" } }
    info = OrderedDict{ "1": OrderedDict{ "vf=0": SerieSwitch("Hello A", "Hello B") } }
    """
    def __init__(self):
        self.info = OrderedDict()
        self.tags_sources = {}
        self.matchers = {}
        
    def tag_source_for_qid(self, qid):
        return self.tags_sources[qid]
    
    def matcher_for_qid(self, qid):
        return self.matchers[qid]
        
def make_faq_info_from_file(filename:str) -> FaqInfo:
    from xml.dom.minidom import parse
    with open(filename) as f: # 'rb' ?
        return make_faq_info_from_string(f.read())
        # return make_faq_info_from_xml(parse(f))

def make_faq_info_from_string(string:str) -> FaqInfo:
    import re
    string = re.sub(r'<(\s|\d|=)', r'&lt;\1', string) # string.replace('< ', '&lt; ')
    string = re.sub(r'&(\s|\d)', r'&amp;\1', string) # string.replace('& ', '&amp; ')
    from xml.dom.minidom import parseString
    return make_faq_info_from_xml(parseString(string))

def make_faq_info_from_xml(xml_doc) -> FaqInfo:
    """
    xml_doc: "Formal" syntax:
        questions: question+
        question[id, matcher=simple, source=amc-comment]: has comment+, has serie-switch?
        comment[name, syntax=rawmd]: has one text field
        serie-switch: has tag+
        tag[name, value-*]: empty
        
    question[matcher] and question[source] may also be on parent nodes to group
    comment[syntax] can also be on parent nodes to group.
    
    Examples:
    
    <questions>
        <question id="1"> <!-- default matcher="simple" -->
            <!-- order of <comment> are important -->
            <comment name="a"> <!-- markdown/latex/html convention by default: paragraph on blank line. (syntax="rawmd") -->
                La vitesse finale n'est pas de zéro.
                En effet, on a de l'énergie.
                
                Ce qui nous amène à une conclusion.
            </comment>
            <comment name="B"> <!-- case is not important, B upper case = b lower case -->
                Attention à la perte d'énergie.
            </comment>
        </question>
        <question id="2">
            <comment name="A">
                L'accélération n'est pas une force.
            </comment>
        </question>
    </questions>
    
    -> 
    
    OrderedDict{
        "1": OrderedDict{
            "a": "La vitesse finale n'est pas zéro. En effet, on a de l'énergie.\nCe qui nous amène à une conclusion.",
            "b": "Attention à la perte d'énergie.",
        }, 
        "2": OrderedDict{
            "a": "L'accélération n'est pas une force",
        }, 
    }
    
    <questions>
        <question id="1">
            <comment name="vf=0">
                Une masse {m} et rayon {R}.
                Attention !
            </comment>
            <serie-switch> <!-- optional, if not present, comment will be sent exactly -->
                <tag name="m"
                     for-a="m"
                     for-b="M" />
                <tag name="R"
                     for-a="R"
                     for-b="L" />
            </serie-switch>
        </question>
    </questions>
    
    -> 
    
    OrderedDict{
        "1": OrderedDict{
            "vf=0": SerieSwitch(
                a = "Une masse m et rayon R",
                b = "Une masse M et rayon L",
            ),
        }
    }
    """
    
    # Maybe the parsing is easier with xml.etree
    
    def warning(*args):
        print('Warning:', *args)
    
    faq = FaqInfo()
    info = faq.info
    root = next(c for c in xml_doc.childNodes if c.nodeType == c.ELEMENT_NODE)
    RA = dict(root.attributes.items())
    # assert all(c.nodeName == 'question' for c in root.childNodes if c.nodeType == c.ELEMENT_NODE), 'in root: all ELEMENT_NODE are question '
    # assert all(c.nodeValue.strip() for c in root.childNodes if c.nodeType == c.TEXT_NODE), "all TEXT_NODE are empty (.strip()) in root"
    for question in root.getElementsByTagName('question'):
        QA = dict(question.attributes.items())
        qid = QA['id'] # getAttribute('id')
        assert qid not in info, f'Duplicate id="{qid}"'
        info[qid] = OrderedDict()
        
        # assert all ELEMENT_NODE are <comment> or <serie-switch> in question, warning otherwise
        # assert all TEXT_NODE are empty in question
        assert question.getElementsByTagName('serie-switch').length <= 1

        for comment in question.getElementsByTagName('comment'):
            CA = dict(comment.attributes.items())
            name = CA['name'].lower()
            syntax = CA.get('syntax', QA.get('syntax', RA.get('syntax', 'rawmd')))
            
            SYNTAX_SUPPORTED = ('rawmd', 'raw', 'oneline')
            assert syntax in SYNTAX_SUPPORTED, f'syntax=\"{syntax}\" not supported. Supported {SYNTAX_SUPPORTED} only. Future implementations will include whatsapp, md, html, tex...'
            
            assert name not in info[qid], f"Duplicates comment for <question id=\"{qid}\">: {name}"
            assert 0 == sum(c.nodeType == c.ELEMENT_NODE for c in comment.childNodes), "comment must have exactly 0 ELEMENT_NODE"
            
            EMPTY = re.compile('^\s*$')
            is_empty = lambda x: bool(EMPTY.match(x))
            
            txt = ''.join(c.nodeValue for c in comment.childNodes if c.nodeType == c.TEXT_NODE)
            
            if is_empty(txt):
                warning(f'<comment name="{name}"> in <question id="{qid}"> have some non empty text')
            
            from textwrap import dedent
            lines = dedent(txt).split('\n')
            
            # remove empty lines at begin and end
            while lines and is_empty(lines[0]):
                del lines[0]
            while lines and is_empty(lines[-1]):
                del lines[-1]
            
            if syntax == 'rawmd':
                # merge consecutive non empty lines and remove empty lines
                lines = [
                    ' '.join(li)
                    for empty,li in groupby(lines, is_empty)
                    if not empty
                ]
                
            info[qid][name] = (' '.join(lines) if syntax == 'oneline' else
                               '\n'.join(lines))
        
        source = QA.get('source', RA.get('source', 'amc-comments'))
        source_cls = {
            'amc-comments': TagSourceAmcAnnotatedCopy,
            'annotate-src': TagSourceCsvImageAnnotate,
        }
        
        try:
            faq.tags_sources[qid] = source_cls[source]()
        except KeyError:
            raise
        
        matcher = QA.get('matcher', RA.get('matcher', 'simple'))
        matcher_cls = {
            'simple': CommentMatcherSimple,
            'multiple': CommentMatcherMultiple,
            'proposition': CommentMatcherBooleanProposition,
            'boolean-list': CommentMatcherMultipleOrAnd,
            'boolean': CommentMatcherFullBoolean,
        }
        
        try:
            faq.matchers[qid] = matcher_cls[matcher]()
        except KeyError:
            raise
        
        if matcher == "proposition":
            if False: # this warning is not useful anymore
                if (any(name.startswith('!') for name in info[qid])
                    and not all(name.startswith('!') for name in info[qid])):
                    warning('Mixing not* and regular comment[name]. Check list <question id="{}"> is {}'.format(qid, tuple(info[qid].keys())))
        
        if matcher == 'boolean':
            matcher_more_characters = QA.get('matcher-more-characters', RA.get('matcher-more-characters'))
            if matcher_more_characters:
                faq.matchers[qid].set_more_characters(matcher_more_characters)
                
        if question.getElementsByTagName('serie-switch'):
            serie_switch, = question.getElementsByTagName('serie-switch')
            # assert all ELEMENT_NODE are tag in serie_switch
            # assert all TEXT_NODE are empty in serie_switch
            VALUE = re.compile('for-(.*)')
            serie_switch_info = {}
            for tag in serie_switch.getElementsByTagName('tag'):
                assert 0 == tag.childNodes.length, "<tag> must be empty"
                A = dict(tag.attributes.items()) # don't care for doublons
                name = A['name']
                values = {}
                for k in A:
                    if k == 'name':
                        pass
                    elif VALUE.match(k):
                        serie = VALUE.match(k).group(1).lower()
                        assert serie in ('a', 'b')
                        values[serie] = A[k]
                    else:
                        raise ValueError('Unknow attribute for <tag> : {}'.format(k))
                serie_switch_info[name] = [values['a'], values['b']]
            
            for q in info[qid]:
                info[qid][q] = SerieSwitch.from_dict_to_list(info[qid][q], serie_switch_info)
                    
    return faq

def clean_ws(x):
    from textwrap import dedent
    return dedent(x.strip('\n'))

# TODO: add a way to send a mail to one student for one question, for example 'if qid=1 and feuille=b128: send "Hello"'

def add_lf_if_nempty(x):
    return x + '\n' if x else x

class SerieInfo:
    def __init__(self, serie_name:'a'):
        self.serie_name = serie_name
        
        self.Dict = DictCollection()
        self.Matricule, self.CopyNumber, self.SrcPage = self.Dict.keylist('Matricule', 'CopyNumber', 'SrcPage')
        
        with sqlite3.connect(os.path.join(AMC_PROJECT.format(serie=serie_name), "data", "association.sqlite")) as db:
            self.Dict[self.Matricule, 'to', self.CopyNumber] = self.MatriculeToCopyNumber = {
                str(auto or manual): int(student)
                for student, auto, manual in db.execute('select student, auto, manual from association_association')
            }
        
        CopyNumberToSrcPage = defaultdict(list)
        with sqlite3.connect(os.path.join(AMC_PROJECT.format(serie=serie_name), "data", "capture.sqlite")) as db2:
            for student, src, page in db2.execute('select student, src, page from capture_page where src is not NULL'):
                CopyNumberToSrcPage[int(student)].append( (int(page), str(src)) )
        
        self.Dict[self.CopyNumber, 'to', self.SrcPage] = dict(CopyNumberToSrcPage)

def simplify_key(key):
    key = key.upper() # uppercase
    
    import unicodedata # to remove accents
    key = ''.join(c for c in unicodedata.normalize('NFD', key) if ord(c) <= 127)
    
    return key

class StudentInfo:
    def __init__(self):
        with open(STUDENT_FILE_CSV) as f:
            self.Students = [{simplify_key(k):v for k,v in student.items()} for student in csv.DictReader(f)]
            for s in self.Students:
                s['MATRICULE'] = str(int(s['MATRICULE'])) # remove zero at beginning
        self.Matricule_to_Netid = {s['MATRICULE']: s['NETID'] for s in self.Students}

def printret(x, *args, **kwargs):
    from pprint import pprint
    pprint(x) if not args and not kwargs else pprint([x] + list(args) + list(map('{}='.format, kwargs)) + list(kwargs.values()))
    return x

def throw(e):
    raise e

class Mark:
    class Error(Exception):
        pass
    class TooManyTicks(Error):
        pass
    class NoTicks(Error):
        pass
    
    @staticmethod
    def calculate_mark(tick_list):
        ticked = {i for i,v in enumerate(tick_list) if v}

        if len(ticked) == 0:
            raise Mark.NoTicks("corrector did not tick any")
        if len(ticked) > 1:
            raise Mark.TooManyTicks("corrector ticked too much")
        
        return ticked.pop()

class Reader:
    class Error(Exception):
        pass
    class EmptyValue(Error):
        pass
    
    @staticmethod
    def read_ticked(line, base_name):
        try:
            return list(map(int, line['TICKED:' + base_name].split(';')))
        except:
            raise Reader.EmptyValue(f'Box TICKED:{base_name} is empty.')

class CommentMatcher:
    def compile_name(self, name):
        return name
    
    def compile_tags(self, tags):
        return tags
    
    def get_compiled(self, name, tags):
        # cache name but not tags
        if name not in self._name_cache:
            self._name_cache[name] = self.compile_name(name)
        return self._name_cache[name], self.compile_tags(tags)
    
    def match(self, name, tags):
        raise ValueError('not implemented')
    
    def __init__(self):
        self._name_cache = {}
    
class CommentMatcherSetLowercase(CommentMatcher):
    def compile_tags(self, tags):
        return set(map(str.lower, tags))

class CommentMatcherSimple(CommentMatcherSetLowercase):
    def match(self, name, tags):
        """ name="a" tags=['a', 'c'] -> True """
        return name.lower() in tags
    
class CommentMatcherMultiple(CommentMatcherSetLowercase):
    def compile_name(self, name):
        return set(map(str.lower, name.split()))
    
    def match(self, name, tags):
        """ name="a c", tags=['a', 'c', 'd'] -> True """
        S, tags = self.get_compiled(name, tags)
        return bool(S & tags)
    
class CommentMatcherMultipleOrAnd(CommentMatcherSetLowercase):
    def compile_name(self, name):
        """ a | b & c | d -> [{'a'}, {'b', 'c'}, {'d'}]"""
        S = [s.strip().lower() for s in name.split('|')]
        assert all(S)
        
        S = [set(x.strip().lower() for x in s.split('&')) for s in S]
        assert all(all(x) for x in S)
        
        return S
    
    def match(self, name, tags):
        """ name="a | c | d & a | d & e", tags=['d', 'a'] -> True """
        or_exprs, tags = self.get_compiled(name, tags)
        
        # or_exprs = [{'a'}, {'c'}, {'d', 'a'}, {'d', 'e'}]
        return any(and_expr <= tags for and_expr in or_exprs)

def CommentMatcherBooleanProposition(CommentMatcherSetLowercase):
    """ can have 'a' or '!a' """
    R = Re('([a-z])$|(![a-z])$', re.I)
    
    def compile_name(self, name):
        try:
            return tuple(map(str.lower, R.fullmatch(name).groups()))
        except:
            raise ValueError('when matching via "A" and "!A", can only have "Letter" or "!Letter"')
    
    def match(self, name, tags):
        """ name='!a', tags=['a', 'c'] -> True """
        name, tags = self.get_compiled(name, tags)
        
        def index_of_letter(l):
            return ord(l) - ord('a')
        
        true_val, false_val = name
        
        if true_val:
            return index_of_letter(true_val) in tags
        else:
            return index_of_letter(false_val) not in tags

class CommentMatcherFullBoolean(CommentMatcherSetLowercase):
    """
    Can have 'a | b & c' or (a | b) & c
    Beware: in xml, "&" is a special character, so replace it with "&amp;" or "& " with a space after.
    """
    
    def __init__(self):
        super().__init__()
        self.more_characters = set()
    
    def set_more_characters(self, more_characters):
        self.more_characters = set(more_characters)
        assert not set('&|!()') & self.more_characters, "cannot allow those charcters"
    
    @staticmethod
    def test():
        m = CommentMatcherFullBoolean()
        
        Tags = list(map(list, ['abc', 'ab', 'ac', 'bc', 'a', 'b', 'c', '']))
        
        def show(expr):
            return [''.join(tags) for tags in Tags if m.match(expr, tags)]
        
        assert show('a & b') == ['abc', 'ab']
        assert show('a | b') == ['abc', 'ab', 'ac', 'bc', 'a', 'b']
        assert show('a & !b') == ['ac', 'a']
        assert show('a | b & c') == ['abc', 'ab', 'ac', 'bc', 'a']
        assert show('(a | b) & c') == ['abc', 'ac', 'bc']
        
        assert show('a & !b') == show('a & ! b')
        assert show('a | b & c') == show('a|b&c')
        assert show('a | b & c') == show('a | b & c')
        assert show('a | b & c') == show('a | (b & c)')
        assert show('(a | b) & c') == show('(a & c) | (b & c)')
        assert show('(a | b) & c') == show('a & c | b & c')
        
        def assertRaise(expr):
            try:
                m.compile_name(expr)
                ok = False
            except:
                ok = True
            assert ok, f"expr {expr!r} should raise Exception"
        
        assertRaise('| b')
        assertRaise('a || b')
        assertRaise('!')
        assertRaise('a | (b & c')
    
    class Node:
        def __init__(self, op, *params):
            self.op = op
            self.params = params
    
    def compile_name(self, name):
        """
        expr: or_expr | ('|' or_expr)*
        or_expr: and_expr | ('&' and_expr)*
        and_expr: identifier | "(" expr ")"
        identifier: [a-ZA-Z0-9_]* | self.more_characters
        """
        
        # eg. name = a | hello & world | d & (e | f)
        import unicodedata
        
        def lexer_cat(c):
            cat = unicodedata.category(c)
            return (
                'I' if cat[0] == 'L' or c in '_' or cat == 'Nd' else
                'P' if c in ('(', ')', '&', '|', '!') else
                'I' if c in self.more_characters else
                'S' if c == ' ' else throw(ValueError(f'Invalid character: {c}')))
        
        bits = []
        Token = namedtuple('type', 'val')
        for a,b in groupby(name, lexer_cat):
            if a == 'S':
                pass
            elif a == 'P':
                bits.extend(b)
            else:
                bits.append(''.join(b))
        
        # eg. bits = ['a', '|', 'hello', '&', 'world', '|', 'd', '&', '(', 'e', '|', 'f', ')']
        
        bits += ['$']
        
        try:
            lexer_cat('$')
            ok = False
        except:
            ok = True
        assert ok, '$ should not be an allowed character'
        
        assert all(bits)
        
        i = 0

        binary = unary = Leaf = lambda x:x
        Node = CommentMatcherFullBoolean.Node

        def consume():
            nonlocal i
            i += 1
            
        def expect(tok):
            nonlocal i
            if bits[i] == tok:
                i += 1
            else:
                raise ValueError
            
        def Eparser():
            t = E()
            expect("$")
            return t

        def E():
            t = T()
            while bits[i] == "|":
                op = binary(bits[i])
                consume()
                t1 = T()
                t = Node(op, t, t1)
            return t
        
        def T():
            t = F()
            while bits[i] == '&':
                op = binary(bits[i])
                consume()
                t1 = F()
                t = Node(op, t, t1)
            return t
        
        def F():
            if lexer_cat(bits[i][0]) == 'I':
                t = Leaf(bits[i])
                consume()
                return t
            elif bits[i] == "(":
                consume()
                t = E()
                expect(")")
                return t
            elif bits[i] == "!":
                consume()
                t = F()
                return Node(unary("!"), t)
            else:
                raise ValueError
        
        return Eparser()
                
    def match(self, name, tags):
        """ name="a | c & d", tags=['c', 'd'] -> True """
        tree, tags = self.get_compiled(name, tags)
        
        def parse(node):
            if not isinstance(node, CommentMatcherFullBoolean.Node):
                return node in tags
            else:
                if node.op == '|':
                    return any(parse(p) for p in node.params)
                elif node.op == '&':
                    return all(parse(p) for p in node.params)
                elif node.op == '!':
                    return not parse(node.params[0])
                else:
                    raise ValueError
        
        return parse(tree)
        
class CopyInfo:
    """
    Provides Matricule to Feuille mapping (Feuille = "124" if not SERIES else "a124")
    """
    def __init__(self):
        self.Dict = DictCollection()
        self.Matricule, self.Feuille = self.Dict.keylist('Matricule', 'Feuille')
        
        self.AnnotationInfo = namedtuple('Info', 'mark ticked')
    
    def make_tags(self, faq, matricule, qid) -> list:
        """
        returns all comment[name] that match for a student for that qid
        matricule="123456", qid="2" -> ["a", "!b", "!d"]
        given <comment name="A"> <comment name="!A"> <comment name="!B"> <comment name="!C"> <comment name="!D">
        and 'a' and 'c' were ticked on the copy
        """
        raise ValueError('Abstract Method')
    
class DbCopyInfo(CopyInfo):
    def __init__(self):
        super().__init__()
        
        # self.CopyNumber = self.Dict.keylist('CopyNumber') # beware, Matricule -> CopyNumber may not be a bijection !
        
        self.projects_by_serie = OrderedDict(
            (serie, AmcProject(AMC_PROJECT.format(serie=serie)))
            for serie in (SERIES or [''])
        )
        
        self.Dict[self.Matricule, 'to', self.Feuille] = {
            mat: "{}{}".format(serie, sid) if serie else "{}".format(sid)
            for serie, proj in self.projects_by_serie.items()
            for mat, sid in proj.Dict[proj.Matricule, 'to', proj.AmcStudentId].items()
        }
        
        if SERIES:
            duplicates_mat = set()
            mats = set()
            for serie, proj in self.projects_by_serie.items():
                for mat, sid in proj.Dict[proj.Matricule, 'to', proj.AmcStudentId].items():
                    if mat in mats:
                        duplicates_mat.add(mat)
                    else:
                        mats.add(mat)
            assert not duplicates_mat, "students in multiple amc projects: {}".format(duplicates_mat)
    
    def img_filenames(self, matricule):
        """
        '132456' -> [(1, 'path1.jpg'), (2, 'path2.jpg'), (3, 'path3.jpg')]
        """
        proj, sid = next((proj, proj.Matricule(matricule).to('AmcStudentId'))
                         for proj in self.projects_by_serie.values()
                         if proj.Matricule(matricule).exists('AmcStudentId'))
        return [
            (int(num), filename.replace('%PROJET', proj.path))
            for num, filename in proj.dbs['capture'].execute('select page, src from capture_page where student=? order by page', [sid])
        ]
    
    def make_tags(self, faq, matricule, qid) -> list:
        """
        returns all xml comment[name] that match for a student for that qid
        matricule="123456", qid="2" -> ["a", "notb", "notd"]
        given <comment name="A"> <comment name="notA"> <comment name="notB"> <comment name="notC"> <comment name="notD">
        and 'a' and 'c' were ticked on the copy
        """
        
        # for that matricule, find out which comments are ticked (eg. A, C)
        
        proj, sid = next((proj, proj.Matricule(matricule).to('AmcStudentId'))
                          for proj in self.projects_by_serie.values()
                          if proj.Matricule(matricule).exists('AmcStudentId'))
        
        AmcQuestionId, LatexQuestionName, AmcStudentId = proj.Dict.keylist('AmcQuestionId', 'LatexQuestionName', 'AmcStudentId')
        
        source = faq.tag_source_for_qid(qid)
        
        # TODO: tags = source.tags_for_matricule(matricule)
        
        if isinstance(source, TagSourceAmcAnnotatedCopy):
            # go in the db
            QO_BASE = re.compile('^QO(\d+)$')
            QO_BASE_FORMAT = 'QO{}'.format
            QO_COMMENTS = re.compile('^QANN(\d+)$')
            QO_COMMENTS_FORMAT = 'QANN{}'.format
            
            CaseToRatio = {
                digit: ratio if manual == -1 else manual
                for digit, ratio, manual in proj.dbs['capture'].execute(f'''
                    select id_b, 1.0*black/total, manual from capture_zone
                    where student=?
                    and type={ZONE_BOX}
                    and id_a=?
                    ''',
                    (proj.Matricule(matricule).to(AmcStudentId),
                     LatexQuestionName(QO_COMMENTS_FORMAT(qid)).to(AmcQuestionId)))
            }
            # assert CaseToRatio.keys() == set(irange(1,11)) # here, corresponds to 7 (ABCDEFG) but we don't check that
            
            indices = [int(k)-1 for k,v in CaseToRatio.items() if v >= proj.seuil]
            # len(indices) can be any length, no Exception possible
            
            # eg. indices = [0, 2] meaning "a" and "c" ticked
            
            def letter_of_index(i):
                """ 'a' -> 0 """
                if not 0 <= i < 26:
                    raise ValueError
                return chr(ord('a') + i)
            
            tags = [letter_of_index(i) for i in indices]
        
        elif isinstance(source, TagSourceCsvImageAnnotate):
            # TODO: move this code in class CsvImageAnnotateSource(TagSource)
            
            data = source.data_for_qid(qid)
            
            def basename(path):
                return path.split('/')[-1]
            
            # for all known scan of student sid for that project, check if there are tags in csv
            possibles_tags = [
                data[img]
                for img in (basename(path) for path, in proj.dbs['capture'].execute('select src from capture_page where student=?', (sid,)))
                if img in data 
            ]
            
            assert len(possibles_tags) == 1
            
            tags = possibles_tags[0]
            
        else:
            raise ValueError('Unknown type: {}'.format(type(source)))
        
        matcher = faq.matcher_for_qid(qid)
        
        return [
            comment_name
            for comment_name in faq.info[qid] # comment_name in ['a', 'not a', 'c']
            if matcher.match(comment_name, tags)
        ]
    
# will be Deprecated in favor of xml source="ticked-csv"
# Easier to go directly in db operation from amc, however, export csv may be much smaller in size
# TODO: should look at the source as in DbCopyInfo
class CsvCopyInfo(CopyInfo):
    def __init__(self):
        super().__init__()
        
        with open(QUESTIONS_TICKED_FILE_CSV) as f:
            self.Copies = [{simplify_key(k):v for k,v in line.items()} for line in csv.DictReader(f)]
        
        self.CopyNumber = self.Feuille
        
        self.Dict[self.Matricule, 'to', self.CopyNumber] = {
            c['A:MATRICULE']: c['COPIE'] for c in self.Copies
        }
        
        QO_BASE = re.compile('^QO(\d+)$')
        
        _bla = defaultdict(dict)
        for student in self.Copies:
            matricule, copy = student['A:MATRICULE'], student['COPIE']
            for column in filter(QO_BASE.match, student):
                id = QO_BASE.match(column).group(1)
                
                try:
                    _bla[matricule][id] = self.AnnotationInfo(
                        mark = None if not COMPUTE_MARK else Mark.calculate_mark(Reader.read_ticked(student, column)),
                        ticked = {i for i,v in enumerate(Reader.read_ticked(student, column + 'COMMENTS'))
                                if v})
                except (Mark.Error, Reader.Error) as e:
                    warning(e.__class__.__name__, f'Copy {copy}, matricule {matricule}, column {column}') # str(e))
                    # raise e
        
        self.AnnotationsInfos = dict(_bla) # self.AnnotationsInfos[matricule]['1'].mark and .ticked
        
        Matricule_to_PdfPath = {}
        import os
        RE = re.compile('(\d+).*\.pdf$')
        for name in os.listdir(PDF_DIR or '.'):
            if RE.match(name):
                number = int(RE.match(name).group(1))
                matricule = self.CopyNumber(str(number)).to(self.Matricule)
                path = name if PDF_DIR in ('.', '') else os.path.join(PDF_DIR, name)
                Matricule_to_PdfPath[matricule] = path
        
        self.PdfPath = self.Dict('PdfPath')
        self.Dict[self.Matricule, 'to', self.PdfPath] = Matricule_to_PdfPath
    
    def FindPdfForMatricule(self, matricule:(str,int)):
        return self.Matricule(str(matricule)).to(self.PdfPath)
    
    def make_tags(self, faq, matricule, qid) -> list:
        """
        returns all comment[name] that match for a student for that qid
        matricule="123456", qid="2" -> ["a", "!b", "!d"]
        given <comment name="A"> <comment name="notA"> <comment name="notB"> <comment name="notC"> <comment name="notD">
        and 'a' and 'c' were ticked on the copy
        """
        indices = self.AnnotationsInfos[matricule][qid].ticked # eg. {0, 2}
        
        assert all(0 <= i < 26 for i in indices)
        
        tags = [chr(ord('a') + i) for i in indices]
        
        source = faq.tag_source_for_qid(qid)
        matcher = faq.matcher_for_qid(qid)
        
        return [
            comment_name
            for comment_name in faq.info[qid] # comment_name in ['a', '!a', 'c']
            if matcher.match(comment_name, tags)
        ]
    
class AmcProject:
    def __init__(self, path):
        self.path = path
        self.dbs = {name:sqlite3.connect(f'{path}/data/{name}.sqlite') for name in ('layout', 'association', 'capture')}
        
        self.xmldoc = ET.parse(f'{path}/options.xml')
        try:
            self.seuil = float(self.xmldoc.find('seuil').text)
        except:
            warning(f'project {path}: seuil not found in xml, default seuil used')
            self.seuil = 0.35
        
        self.Dict = DictCollection()
        self.AmcStudentId, self.Matricule = self.Dict.keylist('AmcStudentId', 'Matricule')
        self.AmcQuestionId, self.LatexQuestionName = self.Dict.keylist('AmcQuestionId', 'LatexQuestionName')
    
        self.Dict[self.AmcQuestionId, 'to', self.LatexQuestionName] = dict_int_key(
            self.dbs['layout'].execute('''select question, name from layout_question'''))
    
        self.Dict[self.AmcStudentId, 'to', self.Matricule] = {
            int(student): int(auto or manual)
            for student, auto, manual in self.dbs['association'].execute('select student, auto, manual from association_association')
        }

class QOInfo:
    
    QO = Re('^QO(\d+)$')
    QO_FORMAT = 'QO{}'.format
    
    QOANN = Re('^QANN(\d+)$')
    QOANN_FORMAT = 'QANN{}'.format
    
    class Error(Exception):
        pass
    
    class CorrectorNoTick(Error):
        pass
    
    class CorrectorMultiTick(Error):
        pass

    def __init__(self, project:AmcProject, exam:int, name:'QO1'):
        assert self.QO.match(name)
        self.project = project
        self.exam = exam
        self.name = name
        self.qnum = int(self.QO.match(name).group(1))
    
    def correctionValue(self) -> 4:
        if hasattr(self, '_correctionValue'):
            return self._correctionValue
        
        D = DictCollection()
        CaseToRatio = D['AnswerPoints', 'to', 'Ratio'] = dict(self.project.dbs['capture'].execute(f'''
            select id_b, 1.0*black/total from capture_zone
            where student=?
            and type={ZONE_BOX}
            and id_a=?
            ''',
            (self.exam,
             self.project.LatexQuestionName(self.name).to(self.project.AmcQuestionId))
        ))
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
        
        AnswerAnnotate_to_Ratio = dict(self.project.dbs['capture'].execute(f'''
            select id_b, 1.0*black/total from capture_zone
            where student=?
            and type={ZONE_BOX}
            and id_a=?
            ''',
            (self.exam,
             self.project.LatexQuestionName(self.QOANN_FORMAT(self.qnum)).to(self.project.AmcQuestionId))
        ))
        assert AnswerAnnotate_to_Ratio.keys() == set(irange(1,7)) # 7 annotations possible
        annotations = [int(k)-1 for k,v in AnswerAnnotate_to_Ratio.items() if v >= self.seuil]
        
        self._correctionCommentsList = annotations
        return self._correctionCommentsList
    
class StatsQuestionComments:
    def __init__(self, path, faq):
        assert path.endswith('.csv')
        self.path = path
        self.faq = faq
        
        self.D = defaultdict(Counter)
        self.N = 0
    
    def close(self):
        
        def convert_comment(comment):
            if isinstance(comment, SerieSwitch):
                return comment.text_for_serie(SERIES[0])
            else:
                return comment
        
        assert self.N % len(self.faq.info) == 0
        total = self.N // len(self.faq.info)
        
        print(total)
        
        latexbits = []
        htmlbits = []
        
        try:
            f = open(self.path, 'w')
            if STATS_GENERATE_TXT:
                f2 = open(self.path[:-4] + '.txt', 'w')
            
            W = csv.writer(f)
            W.writerow(['QID', 'TAG', 'COUNT'] + ['CONTENT'] * bool(STATS_INCLUDE_COMMENT))
            
            for qid in self.faq.info:
                if STATS_GENERATE_TXT:
                    title = f'Question {qid}'
                    f2.write(title + '\n' + '=' * len(title) + '\n\n')
                
                if STATS_GENERATE_TEX:
                    latexbits.append(r'\section*{Question %s}' % qid)
                
                if STATS_GENERATE_HTML:
                    htmlbits.append(r'<h3>Question %s</h3>' % qid)
                
                bycount = lambda tag: self.D[qid][tag]
                for tag in sorted(faq.info[qid], key=bycount, reverse=True):
                    data = [qid, tag, self.D[qid][tag], convert_comment(self.faq.info[qid][tag])]
                    
                    W.writerow(data if STATS_INCLUDE_COMMENT else data[:3])
                    
                    if STATS_GENERATE_TXT:
                        f2.write('[[ {2}: {1} ]]\n{3}\n\n'.format(*data))
                    
                    if STATS_GENERATE_TEX:
                        latexbits.append('\\paragraph*{{ {1} ({2}) }}'.format(*data))
                        latexbits.append(data[3].replace('\n', '\n\n') + '\n')
                    
                    if STATS_GENERATE_HTML:
                        htmlbits.append('<h4>{1} ({2})</h4>'.format(*data))
                        htmlbits.append('<p>{}</p>'.format(data[3].replace('\n', '\n\n')) + '\n')
            
            if STATS_GENERATE_TXT:
                f2.close()
            
            if STATS_GENERATE_TEX:
                if STATS_TEX_TEMPLATE:
                    if not STATS_TEX_TEMPLATE.endswith('.tex'):
                        warning(f'not a tex file: {STATS_TEX_TEMPLATE}')
                    with open(STATS_TEX_TEMPLATE) as temp:
                        template = temp.read()
                else:
                    template = '\\header\n\n\\content'
                
                with open(self.path[:-4] + '.tex', 'w') as file:
                    file.write(template
                        .replace(r'\header', HEADER)
                        .replace(r'\content', '\n'.join(latexbits)))
            
            if STATS_GENERATE_HTML:
                if STATS_HTML_TEMPLATE:
                    if not STATS_HTML_TEMPLATE.endswith('.html'):
                        warning(f'not a html file: {STATS_HTML_TEMPLATE}')
                    with open(STATS_HTML_TEMPLATE) as temp:
                        template = temp.read()
                else:
                    template = '<html><head><meta charset="utf-8"/></head><body><h2>{{ header }}</h2>\n\n{{ content }}</body></html>'
                
                with open(self.path[:-4] + '.html', 'w') as file:
                    file.write(template
                        .replace('{{ header }}', HEADER)
                        .replace('{{ content }}', '\n'.join(htmlbits)))
        finally:
            f.close()
            print('Written', self.path)
            
            if STATS_GENERATE_TXT:
                print('Written', self.path[:-4] + '.txt')
            
            if STATS_GENERATE_TEX:
                print('Written', self.path[:-4] + '.tex')
                
            if STATS_GENERATE_HTML:
                print('Written', self.path[:-4] + '.html')
        
    def update(self, qid, tags):
        """
        Will be called once per mail per qid, containing the tags for that mail for that qid
        """
        for tag in tags:
            self.D[qid][tag] += 1
        self.N += 1

skipLimit = itertools.count()
countLimit = itertools.count()

faq = make_faq_info_from_file(CONFIG_XML)
if SERIES:
    series_info = {serie_name: SerieInfo(serie_name) for serie_name in SERIES}
student_info = StudentInfo()
copy_info = DbCopyInfo()

if MAKE_STATS:
    stats = StatsQuestionComments(MAKE_STATS, faq)


def format_long_list(L, N=10):
    return '({}): {}{}'.format(len(L), ' '.join(map(str, L[:N])), '...' * (len(L) > N))

if any(not copy_info.Matricule(int(student['MATRICULE'])).exists('Feuille') for student in student_info.Students):
    L = [int(student['MATRICULE']) for student in student_info.Students if not copy_info.Matricule(int(student['MATRICULE'])).exists(copy_info.Feuille)]
    warning('Matricule without copy {}'.format(format_long_list(L)))

NoEmailList = [
    matricule
    for matricule in copy_info.Dict[copy_info.Matricule, 'to', copy_info.Feuille].keys()
    if str(matricule) not in student_info.Matricule_to_Netid
]

if NoEmailList:
    warning('Copy without email in student list {}'.format(format_long_list(NoEmailList)))

if SEND_MAIL:
    django.core.mail.get_connection().open()
    
for feuille, matricule, netid, prenom, nom in (
    [[SERIES[0] + '0' if SERIES else '0', '123456', 'test', 'John', 'Doe']] if TEST_COMMENTS else (
        (copy_info.Matricule(int(student['MATRICULE'])).to('Feuille'),
            int(student['MATRICULE']),
            student['NETID'],
            student.get('PRENOM', ''),
            student['NOM'])
        for student in student_info.Students
        if copy_info.Matricule(int(student['MATRICULE'])).exists('Feuille')
    )): # aaq for 4 # aq for 8 # ad for 14
    # and (netid < 'aaq') -- (feuille in "a201", "b250", "a244", "b284")) -- "a21", "a279", "b208", "a87", "a295"))
    
    if FILTER_MATRICULE:
        if isinstance(FILTER_MATRICULE, (int,str)) and not(int(matricule) == int(FILTER_MATRICULE)):
            continue
        elif isinstance(FILTER_MATRICULE, (tuple,list,set)) and not(int(matricule) in FILTER_MATRICULE):
            continue
        elif is_regex(FILTER_MATRICULE) and not FILTER_MATRICULE.match(str(matricule)):
            continue
        elif hasattr(FILTER_MATRICULE, '__call__') and not FILTER_MATRICULE(int(matricule)):
            continue
    
    if netid is not None and FILTER_NETID:
        if isinstance(FILTER_NETID, str) and not (netid == FILTER_NETID):
            continue
        elif isinstance(FILTER_NETID, (tuple,list,set)) and not (netid in FILTER_NETID):
            continue
        elif is_regex(FILTER_NETID) and not FILTER_NETID.match(netid):
            continue
        elif hasattr(FILTER_NETID, '__call__') and not FILTER_NETID(matricule):
            continue
    
    if SKIP_LIMIT is not None and next(skipLimit) < SKIP_LIMIT:
        continue
    
    currentCount = next(countLimit)
    if MAX_EMAIL is not None and currentCount >= MAX_EMAIL:
        break
    
    if netid is None:
        warning(feuille, 'has no netid')
        continue
    
    info('{: 4}'.format(currentCount + (SKIP_LIMIT or 0)), 'Creating', feuille, 'for', netid, matricule)
    
    if SERIES:
        assert feuille
        serie = feuille[0] # current hack to get serie
        assert serie in SERIES
    
    if TEST_COMMENTS:
        my_tags = {qid: list(faq.info[qid]) for qid in faq.info}
    else:
        my_tags = {qid: copy_info.make_tags(faq, matricule, qid) for qid in faq.info}
    
    if MAKE_STATS:
        for qid in faq.info:
            stats.update(qid, my_tags[qid])
    
    if SEND_MAIL + PRINT_MAIL == 0:
        continue
    
    def convert_comment(comment):
        if isinstance(comment, SerieSwitch):
            return comment.text_for_serie(serie)
        else:
            return comment
    
    mail = EmailMessage(
        HEADER,
        'Bonjour {prenom} {nom} (matricule {matricule}, netid {netid}, copie d\'examen numéro {feuille}), voici en attaché votre examen ({header}), la correction de l\'examen se trouve sur l\'UV.'.format(
            matricule=matricule,
            prenom=prenom,
            nom=nom,
            netid=netid,
            header=HEADER,
            feuille=feuille,
        ) + '\n\n' + '\n\n'.join(
            'Le·la correcteur·trice de la question {qid} a laissé ces commentaires supplémentaires:\n{coms}'.format(
                qid = qid,
                coms = '\n'.join(
                    "- {}".format(convert_comment(faq.info[qid][tag]).replace('\n', '\n  '))
                    for tag in my_tags[qid]
                    if convert_comment(faq.info[qid][tag])
                )
            )
            for qid in faq.info
            if my_tags[qid]
        ) + '\n\n' + '\n'.join([
            "Plus d'infos sur la FAQ de l'examen sur l'UV.",
            "L'équipe des assistants",
        ]),
        SEND_FROM,
        (
            ([TO_ONE_PERSON] if TO_ONE_PERSON else [netid + '@ulb.ac.be'])
            + [ALSO_TO] * bool(ALSO_TO)
        )
    )
    
    pdf_filename_from_infos = '{header} {long_name} ({matricule}) (Number {feuille}).pdf'.format(
        header=HEADER,
        long_name=nom.upper() + ' ' + prenom,
        matricule=int(matricule),
        feuille=feuille)
    
    if False:
        if TEST_COMMENTS:
            filenames = ['test.pdf']
        else:
            try:
                filenames = {
                    pdf_filename_from_infos: copy_info.FindPdfForMatricule(matricule)
                }
            except KeyError as e:
                warning("Can't find pdf", e.__class__.__name__, e)
                continue
    else:
        if TEST_COMMENTS:
            filenames = {i:'test.jpg' for i in irange(1, NUM_PAGES)}
        else:
            num_filename = copy_info.img_filenames(matricule)
            assert len(num_filename) == NUM_PAGES, num_filename
            
            if NUM_PAGES_INCLUDE_STATIC:
                assert set(NUM_PAGES_INCLUDE_STATIC) & set(num for num, filename in num_filename) == set()
                
                for numpage in NUM_PAGES_INCLUDE_STATIC:
                    filename = (f"subject-{serie}-page-{numpage}.jpg" if SERIES else 
                                f"subject-page-{numpage}.jpg")
                    
                    num_filename.append( (numpage, filename) ) # will be sorted after anyway
            
            filenames = OrderedDict(
                (f'page-{num}.jpg', filename)
                for num, filename in sorted(num_filename))
            
            if NUM_PAGES_CONSECUTIVE:
                assert set(num for num, filename in num_filename) == set(irange(1, NUM_PAGES))
            if NUM_PAGES_INCLUDE_STATIC:
                assert set(num for num, filename in num_filename) == set(irange(1, NUM_PAGES + len(NUM_PAGES_INCLUDE_STATIC)))
            assert set(filename.lower().endswith('.jpg') for num, filename in num_filename)
    
    if isinstance(filenames, dict):
        if MAKE_PDF:
            if not all(map(os.path.exists, filenames.values())):
                raise FileNotFoundError(next(f for f in filenames.values() if not os.path.exists(f)))
            mail.attach(pdf_filename_from_infos, img2pdf.convert(list(filenames.values())))
        else:
            files = OrderedDict()
            for new_name, orig_name in filenames.items():
                try:
                    with open(orig_name, 'rb') as f:
                        files[new_name] = f.read()
                except FileNotFoundError as e:
                    raise e
        
            for name, content in files.items():
                mail.attach(name, content)
            
    else:
        if MAKE_PDF:
            if not all(map(os.path.exists, filenames)):
                raise FileNotFoundError(next(f for f in filenames if not os.path.exists(f)))
            mail.attach(pdf_filename_from_infos, img2pdf.convert(filenames))
        else:
            for name in filenames:
                mail.attach_file(name)
    
    assert SEND_MAIL + PRINT_MAIL == 1
    
    if PRINT_MAIL:
        print('-- MAIL --\n', mail.message().as_string())
        n_send = 1
    elif SEND_MAIL:
        try:
            n_send = mail.send()
        except smtplib.SMTPServerDisconnected:
            print('Retrying')
            django.core.mail.get_connection().close()
            django.core.mail.get_connection().open()
            n_send = mail.send()
    else:
        raise AssertionError
    
    if n_send != 1:
        warning('Not sent', feuille, 'for', netid, prenom, nom.upper())

if MAKE_STATS:
    stats.close()
