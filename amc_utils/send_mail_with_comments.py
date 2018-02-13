#!/usr/bin/env python3
import getpass
import sqlite3

import os, sys, re
assert sys.version_info >= (3, 6)

import csv
from pprint import pprint
import itertools
from itertools import groupby

import django
from django.conf import settings
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

HEADER        = 'PHYSH100 Examen Physique Janvier 2017-2018'
SEND_MAIL     = False # If False, no mail will be sent
PRINT_MAIL    = False # If True, mail will be printed, not sent.
TEST_COMMENTS = False # if True, 1 mail will be sent will all the contents of comments.xml
TO_ONE_PERSON = '' # 'rovdeynd@ulb.ac.be' # if present, all mails go to here
ALSO_TO       = '' # 'Guillaume.Tillema@ulb.ac.be' # if present, send also to here
SEND_FROM     = 'rovdeynd@ulb.ac.be'
COMPUTE_MARK  = False

# Flow control
MAX_EMAIL        = None # None means no limit, 1 for example can be used for testing (send only 1 mail).
SKIP_LIMIT       = None # None or 0 means begin at first student, otherwise, skip SKIP_LIMIT students.
FILTER_MATRICULE = None # Default : None, can also be a int, or a list of int; or a function taking a int
FILTER_NETID     = None # Default : None, can also be a netid, or a list of netid, or a regex, or a function taking a str

# XML OPTIONS
CONFIG_XML = 'comments.xml'
USE_SERIE = False # if not False nor None, a number which is the number of series, multiple AMC projects exist, one for each "serie" # TODO: decide if this should go to the XML

# CSV OPTIONS
# All CSV must have first line as Header
# They must be English style "," separated, '"' if needed
# If there are decimal points, English style too "1.5" not "1,5".
# Ie. They can be read with python DictReader(file)
STUDENT_FILE_CSV = 'ExamenJanvier2018_student_file_from_ecursus.csv' # Must have MATRICULE and NETID columns, can have PRENOM and NOM.
QUESTIONS_TICKED_FILE_CSV = 'ExamenJanvier2018Brut_numerical_values_refilled.csv' # Must have COPIE, A:MATRICULE, TICKED ";" amc option, "," separated. Pair QO1/QO1COMMENTS

# Directories OPTIONS
PDF_DIR = '.'
AMC_PROJECT = "" # if series are used: {serie} will be replaced by for example "a".

settings.configure(
    EMAIL_USE_TLS = True,
    EMAIL_HOST = 'smtp.ulb.ac.be',
    EMAIL_PORT = 587,
    EMAIL_HOST_USER = SEND_FROM,
    EMAIL_HOST_PASSWORD = getpass.getpass() if SEND_MAIL else '',
)

assert SEND_MAIL + PRINT_MAIL <= 1, "maximum one of SEND_MAIL, PRINT_MAIL"
assert USE_SERIE in (False, None) or USE_SERIE == 2, "Currently, only 2 series can be used"

def warning(*args):
    print('[Warning]', *args)

def info(*args):
    print('[Info]', *args)

def is_regex(obj):
    return isinstance(obj, re.compile('').__class__)

from collections import namedtuple
class SerieSwitch(namedtuple('SerieSwitch', ['a', 'b'])):
    """
    SerieSwitch(
        txt.format(m='m', R='R'),
        txt.format(m='M', R='L'),
    )
    
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
    
    @staticmethod
    def from_dict_to_list(txt, d):
        """ SerieSwitch.from_dict_to_list('hello {m}', {'m': ['m', 'M'], 'R': ['R', 'L']}) """
        return SerieSwitch(*[
            txt.format(**{k:L[i] for k,L in d.items()})
            for i in range(len(SerieSwitch._fields))
        ])
    
    @staticmethod
    def from_kwargs_to_list(txt, *args, **kwargs): # beware: 'txt' not in kwargs
        """ SerieSwitch.from_dict_to_list('hello {m}', m=['m', 'M'], R=['R', 'L']}) """
        if args: raise ValueError('No args')
        return SerieSwitch.from_dict_to_list(txt, kwargs)

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
    def __init__(self, info):
        self.info = info
        
def make_faq_info_from_file(filename:str) -> FaqInfo:
    from xml.dom.minidom import parse
    with open(filename) as f: # 'rb' ?
        return make_faq_info_from_string(f.read())
        # return make_faq_info_from_xml(parse(f))

def make_faq_info_from_string(string:str) -> FaqInfo:
    import re
    string = re.sub(r'<(\s|\d)', r'&lt;\1', string) # string.replace('< ', '&lt; ')
    string = re.sub(r'&(\s|\d)', r'&amp;\1', string) # string.replace('& ', '&amp; ')
    from xml.dom.minidom import parseString
    return make_faq_info_from_xml(parseString(string))

def make_faq_info_from_xml(xml_doc) -> FaqInfo:
    """
    xml_doc: "Formal" syntax:
        questions: question+
        question[id]: has comment+, has serie-switch?
        comment[name]: has one text field
        serie-switch: has tag+
        tag[name, value-*]: empty
        
    Examples:
    
    <questions>
        <question id="1">
            <!-- order of comments are important -->
            <comment name="a"> <!-- markdown/latex/html convention: paragraph on blank line -->
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
    
    def warning(*args):
        print('Warning:', *args)
    
    info = OrderedDict()
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
        
        if (any(name.startswith('not') for name in info[qid])
            and not all(name.startswith('not') for name in info[qid])):
            warning('Mixing not* and regular comment[name]. Check list <question id="{}"> is {}'.format(qid, tuple(info[qid].keys())))
        
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
                    
    return FaqInfo(info=info)

faq = make_faq_info_from_file(CONFIG_XML)

def clean_ws(x):
    from textwrap import dedent
    return dedent(x.strip('\n'))

# BEGIN not used in EXAM_IRCI_2017_2018_JANVIER

# TODO: read messages_info from xml as <message-info>, has same formatting options as <comment> (syntax=)
messages_info = {
    "1": {
        'b128': clean_ws("""
            Some text for b128 for question 1
            Another line for b128
        """)
    },
    "2": {
        'b208':clean_ws("""
            Some text for b208 for question 2
        """),
    },
    "3": {},
    "4": {},
    "5": {},
    "6": {},
}

#assert (
    #set(feuille for question, D in messages_info.items() for feuille in D)
    #<= set(feuille for feuille, in db_conn.execute('select feuille from student where feuille is not NULL'))
#), str(
    #set(feuille for question, D in messages_info.items() for feuille in D)
    #- set(feuille for feuille, in db_conn.execute('select feuille from student where feuille is not NULL'))
#)

# END not used in EXAM_IRCI_2017_2018_JANVIER

def add_lf_if_nempty(x):
    return x + '\n' if x else x

class SerieInfo:
    def __init__(self, serie_name):
        self.serie_name = serie_name
        
        with sqlite3.connect(os.path.join(serie_name, "data", "association.sqlite")) as db:
            self.MatriculeToCopyNumber = {
                str(auto or manual): int(student)
                for student, auto, manual in db.execute('select student, auto, manual from association_association')
            }
        
        self.CopyNumberToSrcPage = defaultdict(list)
        with sqlite3.connect(os.path.join(serie_name, "data", "capture.sqlite")) as db2:
            for student, src, page in db2.execute('select student, src, page from capture_page where src is not NULL'):
                self.CopyNumberToSrcPage[int(student)].append( (int(page), str(src)) )

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
    class TooManyTicks(Exception):
        pass
    class NoTicks(Exception):
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
    class EmptyValue(Exception):
        pass
    
    @staticmethod
    def read_ticked(line, base_name):
        try:
            return list(map(int, line['TICKED:' + base_name].split(';')))
        except:
            raise Reader.EmptyValue(f'Box TICKED:{base_name} is empty.')

class CopyInfo:
    def __init__(self):
        with open(QUESTIONS_TICKED_FILE_CSV) as f:
            self.Copies = [{simplify_key(k):v for k,v in line.items()} for line in csv.DictReader(f)]
        self.Matricule_to_CopyNumber = {c['A:MATRICULE']: c['COPIE'] for c in self.Copies}
        self.CopyNumber_to_Matricule = {c['COPIE']: c['A:MATRICULE'] for c in self.Copies}
        
        QO_BASE = re.compile('^QO(\d+)$')
        
        self.bla = defaultdict(dict)
        Info = namedtuple('Info', 'mark ticked')
        for student in self.Copies:
            matricule, copy = student['A:MATRICULE'], student['COPIE']
            for column in filter(QO_BASE.match, student):
                id = QO_BASE.match(column).group(1)
                
                try:
                    self.bla[matricule][id] = Info(
                        mark = None if not COMPUTE_MARK else Mark.calculate_mark(Reader.read_ticked(student, column)),
                        ticked = {i for i,v in enumerate(Reader.read_ticked(student, column + 'COMMENTS'))
                                if v})
                except (Mark.TooManyTicks, Mark.NoTicks, Reader.EmptyValue) as e:
                    warning(e.__class__.__name__, f'Copy {copy}, matricule {matricule}, column {column}') # str(e))
                    # raise e
            
        self.Matricule_to_PdfPath = {}
        import os
        RE = re.compile('(\d+).*\.pdf$')
        for name in os.listdir(PDF_DIR or '.'):
            if RE.match(name):
                number = int(RE.match(name).group(1))
                matricule = self.CopyNumber_to_Matricule[str(number)]
                path = name if PDF_DIR in ('.', '') else os.path.join(PDF_DIR, name)
                self.Matricule_to_PdfPath[matricule] = path
                
    def FindPdfForMatricule(self, matricule:(str,int)):
        return self.Matricule_to_PdfPath[str(matricule)]
    
    def make_tags_for_matricule_and_question(self, faq, matricule, qid) -> list:
        """
        returns all comment[name] that match for a student for that qid
        matricule="123456", qid="2" -> ["a", "notb", "notd"]
        given <comment name="A"> <comment name="notA"> <comment name="notB"> <comment name="notC"> <comment name="notD">
        and 'a' and 'c' were ticked on the copy
        """
        indices = self.bla[matricule][qid].ticked # eg. {0, 2}
        
        def index_of_letter(l):
            """ 'a' -> 0 """
            if not 'a' <= l <= 'z' or len(l) != 1:
                raise ValueError('when matching via A and notA, can only have letters or notLetters.')
            return ord(l) - ord('a')
        
        return [
            comment_name
            for comment_name in faq.info[qid] # eg. a, nota, notb, notc, notd
            if not comment_name.startswith('not') and index_of_letter(comment_name) in indices
            or comment_name.startswith('not') and index_of_letter(comment_name[3:]) not in indices
        ]

skipLimit = itertools.count()
countLimit = itertools.count()

if False:
    series_info = {serie_name: SerieInfo(serie_name) for serie_name in ('a','b')}
student_info = StudentInfo()
copy_info = CopyInfo()

warning('Matricule without copy: ' + ' '.join(
    student['MATRICULE']
    for student in student_info.Students
    if student['MATRICULE'] not in copy_info.Matricule_to_CopyNumber
))

for feuille, matricule, netid, prenom, nom in (
    [['a0', '123456', 'test', 'John', 'Doe']] if TEST_COMMENTS else
    (
        (copy_info.Matricule_to_CopyNumber[student['MATRICULE']],
            student['MATRICULE'],
            student['NETID'],
            student.get('PRENOM', ''),
            student['NOM'])
        for student in student_info.Students
        if student['MATRICULE'] in copy_info.Matricule_to_CopyNumber
    ) if True else [] # TODO: (some) DB
    ): # aaq for 4 # aq for 8 # ad for 14
    # and (netid < 'aaq') -- (feuille in "a201", "b250", "a244", "b284")) -- "a21", "a279", "b208", "a87", "a295"))
    
    if FILTER_MATRICULE:
        if isinstance(FILTER_MATRICULE, (int,str)) and not(int(matricule) == int(FILTER_MATRICULE)):
            continue
        elif isinstance(FILTER_MATRICULE, (tuple,list,set)) and not(int(matricule) in FILTER_MATRICULE):
            continue
        elif is_regex(FILTER_MATRICULE) and not FILTER_MATRICULE.match(matricule):
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
    
    if USE_SERIE:
        assert feuille.startswith('a') or feuille.startswith('b')
        serie = feuille[0]
    
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
            'Le·la correcteur·trice de la question {qid} a laissé ces commentaires supplémentaires:\n{coms_perso}{coms}'.format(
                qid = qid,
                coms_perso = (
                    '- ' + messages_info[qid][feuille].replace('\n', '\n  ') + '\n'
                    if feuille in messages_info[qid] else ''
                ),
                coms = '\n'.join(
                    "- {}".format(com.replace('\n', '\n  ')) # (com if '\n' not in com else com.replace('\n', '\n  ') + '\n')
                    for tag in tags 
                    for com in [
                        faq.info[qid][tag] if not isinstance(faq.info[qid][tag], SerieSwitch) else
                        getattr(faq.info[qid][tag], serie) # will raise Error if serie is not Defined
                    ]
                )
            )
            for qid in faq.info
            for tags in [
                list(faq.info[qid]) if TEST_COMMENTS else
                copy_info.make_tags_for_matricule_and_question(faq, matricule, qid)
            ]
            if (tags or feuille in messages_info[qid])
        ) + '\n\n' + '\n'.join([
            "Plus d'infos sur la FAQ de l'examen sur l'UV.",
            "Robert VANDEN EYNDE",
            "Assistant",
        ]),
        SEND_FROM,
        (
            ([TO_ONE_PERSON] if TO_ONE_PERSON else [netid + '@ulb.ac.be'])
            + [ALSO_TO] * bool(ALSO_TO)
        )
    )
    
    if True:
        if TEST_COMMENTS:
            filenames = ['test.pdf']
        else:
            try:
                base_name = HEADER.replace(' ', '-')
                filenames = {
                    '{} {} (Number {}).pdf'.format(
                        HEADER,
                        nom.upper() + ' ' + prenom,
                        feuille,
                    ): copy_info.FindPdfForMatricule(matricule)
                }
            except KeyError as e:
                warning("Can't find pdf", e.__class__.__name__, e)
                continue
    else:
        if TEST_COMMENTS:
            filenames = {i:'test.jpg' for i in (1,2,3,4,5)}
        else:
            num_filename = [
                (int(num),filename)
                for num, filename in db_conn.execute('select num, filename from capture where feuille=?', [feuille])
            ]
                            
            filenames = OrderedDict(
                (f'page-{num}.jpg', filename)
                for num, filename in sorted(num_filename)
            )
    
            assert set(num for num, filename in num_filename) == {1,2,3,4,5}
            assert set(filename.lower().endswith('.jpg') for num, filename in num_filename)
    
    if isinstance(filenames, dict):
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
        for name in filenames:
            mail.attach_file(name)
    
    if PRINT_MAIL:
        print('-- MAIL --\n', mail.message().as_string())
        n_send = 1
    elif SEND_MAIL:
        n_send = mail.send()
    else:
        n_send = 1
    
    if n_send != 1:
        warning('Not sent', feuille, 'for', netid, prenom, nom.upper())
