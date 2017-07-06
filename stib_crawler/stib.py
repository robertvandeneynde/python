import sys

if sys.version_info[0] != 3:
    print('Python version != 3')
    sys.exit(1)
    

from dom_functions import getElementsBySelector as queryAll

import urllib
import urllib.request
import urllib.parse

import re

import xml
import xml.dom
import xml.dom.minidom

from pprint import pprint as pp

def index_if(sequence, predicate):
    for i,elem in enumerate(sequence):
        if predicate(elem):
            return i
    return -1

url_base = "http://www.stib.be/horaires-dienstregeling2.html?"
url = url_base + urllib.parse.urlencode(dict(
    l='fr',
    fmodule='l',
    results='r',
    moduscode='B',
    linecode='71',
    arretcode='3556',
    codesens='V',
    horairedate='20131215',
))

print(url)

reponse = urllib.request.urlopen(
    url
).read().decode('cp1252')

lignes = reponse.split('\n')

begin_index = index_if(lignes, lambda l: """<div id="horaireLines">""" in l)
end_index = -1 + index_if(lignes, lambda l: """<div id="horaireInfo">""" in l)
# le -1 est un petit hack pour virer le </div> en trop

if begin_index >= 0 and end_index >= 0:
    my_xml = '\n'.join(lignes[begin_index:end_index]).replace('&nbsp;', ' ')
    root = xml.dom.minidom.parseString(my_xml).documentElement
    
    def get_direct(tagName, element):
        return [
            elem for elem in element.childNodes
            if elem.nodeType == elem.ELEMENT_NODE
            and elem.tagName == tagName
        ]
    
    def convert(string):
        match = re.search('[0-9]+', string)
        if match:
            match2 = re.search('[A-Za-z]+', string)
            if match2:
                return int(match.group(0)), match2.group(0)
            else:
                return int(match.group(0)), ''
        else:
            return None
        
    horaire = [
        [
            convert(span.firstChild.data)
            for span in get_direct('span', div)
        ]
        for div in get_direct('div', root)
    ]
    
    def get_notes_mapper():
        begin_notes = index_if(lignes, lambda l: """<div id="horaireInfoNotes">""" in l)
        end_notes = -2 + index_if(lignes, lambda l: """<!-- HORAIRE END -->""" in l)
        
        if begin_notes >= 0 and end_notes >= 0:
            notes_xml = '\n'.join(lignes[begin_notes:end_notes]).replace('&nbsp;', ' ')
            root = xml.dom.minidom.parseString(notes_xml).documentElement
            
            def convert_note(string):
                liste = string.split()
                return liste[0], ' '.join(liste[1:])
            
            return dict(
                convert_note(div.firstChild.data)
                for div in get_direct('div', root)
                if div.getAttribute('class') == 'note'
            )
        else:
            return dict()
    
    notes_mapper = get_notes_mapper()
    liste = []
    for i in range(len(horaire)):
        for j in range(len(horaire[i])):
            if horaire[i][j] is not None:
                heures = j + 4
                minutes, terminus = horaire[i][j]
                
                liste.append( (
                    heures,
                    minutes,
                    terminus if terminus in notes_mapper else ''
                ) )
                        
    print('\n'.join(str(l) for l in horaire))
    pp(notes_mapper)
    pp(sorted(liste))
    
        
else:
    raise Exception('sentinel lines not found')