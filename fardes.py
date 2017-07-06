from collections import namedtuple
from decimal import Decimal

Cours = namedtuple('Cours', ('nom','css','poids','poids_syllabus'))

(bio, musique, techno, geo,
latin, math, fr, eps, ndls, 
paras, morale, hist, phys) = les_cours = [
    Cours("Bio"         , "bio"         , 2, 0),
    Cours("Musique"     , "musique"     , 1, 0),
    Cours("Techno"      , "techno"      , 0, 0),
    Cours("Géo"         , "geo"         , 1, 0),
    Cours("Latin"       , "latin"       , 3, 1),
    Cours("Math"        , "math"        , 2, Decimal('0.5')),
    Cours("Français"    , "francais"    , 2, 1),
    Cours("EPS"         , "eps"         , 4, 0),
    Cours("Ndls"        , "ndls"        , 2, Decimal('1.5')),
    Cours("Parascolaire", "parascolaire", 0, 0),
    Cours("Morale"      , "morale"      , 1, 0),
    Cours("Histoire"    , "histoire"    , 2, 0),
    Cours("Physique"    , "physique"    , 1, 0)
]

dispo = {bio, latin, fr, ndls, hist, phys}

les_cours = set(les_cours)

horaire = [
	[musique,techno,bio,geo,latin,math,math],
	[fr,latin,eps,phys,fr,ndls,paras,paras],
	[morale,morale,latin,fr,math],
	[geo,bio,math,hist,latin,fr,ndls],
	[eps,eps,math,ndls,ndls,fr,hist]
]

ModeleFarde = namedtuple('ModeleFarde', ['capacite', 'poids','nom'])

modeleM, modeleL, modeleXL = modeles_fardes = [
    ModeleFarde(4, 2, 'M'),
    ModeleFarde(8, 4, 'L'),
    ModeleFarde(16, 8, 'XL')
]

NOMS_JOUR = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']

import itertools
def genere_fardes(ensemble, N):
    """ ensemble doit être un iterable """
    if N == 1:
        yield (tuple(ensemble),)
        return
    ensemble_s = set(ensemble)
    for i in range(1,len(ensemble)//2+1):
        for gauche in itertools.combinations(ensemble, i):
            comp = ensemble_s - set(gauche)
            for droite in genere_fardes(comp, N-1):
                yield (gauche,) + droite

def plural(N, carac='s'):
    return '' if N == 1 else carac

def poids_cours(cours):
    return cours.poids

def poids_syllabus(cours):
    return cours.poids_syllabus

def poids_cours_et_syllabus(cours):
    return poids_cours(cours) + poids_syllabus(cours)

def cours_farde(cours):
    return cours in dispo

def cours_cahier(cours):
    return cours not in dispo

def poids_interieur_farde(farde):
    return sum(map(poids_cours, farde))

def get_modele(farde):
    if set(farde) == {bio, hist, phys}:
        return modeleM
    somme = poids_interieur_farde(farde)
    for modele in sorted(modeles_fardes, key=lambda modele:modele.capacite):
        if modele.capacite >= somme:
            return modele
    return modele # De plus grande capacité


def poids_farde_seule(farde):
    return get_modele(farde).poids

def poids_farde(farde):
    return poids_farde_seule(farde) + poids_interieur_farde(farde)

def nombre_heure(cours):
    return sum(sum(1 for c in aujourdhui if c == cours) for aujourdhui in horaire)        

def farde_prise(aujourdhui):
    def f(farde):
        for cours in farde:
            if cours in aujourdhui:
                return True
        return False
    return f


def description_choix(fardes):
    les_cours_inutiles = [list(cours_inutiles(fardes, aujourdhui)) for aujourdhui in horaire]
    les_fardes_prises = [list(fardes_prises(fardes, aujourdhui)) for aujourdhui in horaire]
        
    return '<table>{}{}{}</table>'.format(
        '<tr><th>Jour</th> {}</tr>'.format(
            '\n'.join(
                '<th>{}</th>'.format(fonction.nom)
                for fonction in les_evaluations_jour
            )
        ),
        '\n'.join(
            '''<tr>
                    <th class="jour">{}</th>
                    <td class="fardes">{}</td>
                    <td class="cours">{}</td>
                    {}
            </tr>'''.format(
                nom_jour,
                ' '.join(
                    '#{}|{}'.format(
                        1 + fardes.index(farde),
                        get_modele(farde).nom,
                    )
                    for farde in fardes_prises_aujourdhui
                ),
                '({}){}'.format(
                    len(cours_inutiles_aujourdhui),
                    ''.join( map(html_cours, cours_inutiles_aujourdhui) )
                ),
                '\n'.join(
                    '<td class="nombre{1}">{0}</td>'.format(
                        fonction(fardes, aujourdhui),
                        ' maximum' if fonction(fardes, aujourdhui) ==
                        max(fonction(fardes, jour) for jour in horaire)
                        else ''
                    )
                    for fonction in les_evaluations_jour[2:]
                )
            )
            for nom_jour, aujourdhui, cours_inutiles_aujourdhui, fardes_prises_aujourdhui
            in zip(NOMS_JOUR, horaire, les_cours_inutiles, les_fardes_prises)
        ),
        '<tr><th class="total">Totaux:</th>{}</tr>'.format(
            '\n'.join(
                '<th class="total">{}</th>'.format( fonction.somme(fardes) )
                for fonction in les_evaluations_jour
            )
        )
    )

def fardes_prises(fardes, aujourdhui):
    yield from filter(farde_prise(aujourdhui), fardes)

def cours_inutiles(fardes, aujourdhui):
    for farde in fardes_prises(fardes, aujourdhui):
        for cours in farde:
            if cours not in aujourdhui:
                yield cours
                
def nombre_fardes_prises(fardes, aujourdhui):
    return sum(1 for farde in fardes_prises(fardes, aujourdhui))

def nombre_cours_inutiles(fardes, aujourdhui):
    return sum(1 for cours in cours_inutiles(fardes,aujourdhui))

def heures_inutiles(fardes, aujourdhui):
    return sum(map(nombre_heure, cours_inutiles(fardes,aujourdhui)))

def poids_fardes_prises(fardes, aujourdhui):
    return sum(map(poids_farde_seule, fardes_prises(fardes, aujourdhui)))

def poids_cours_a_fardes(fardes, aujourdhui):
    return sum(map(poids_farde, filter(farde_prise(aujourdhui), fardes)))
    
def poids_cours_a_cahier(fardes, aujourdhui):
    return sum(map(poids_cours, filter(cours_cahier, set(aujourdhui))))

def poids_inutile(fardes, aujourdhui):
    return sum(map(poids_cours, cours_inutiles(fardes, aujourdhui)))

def poids_des_syllabus(fardes, aujourdhui):
    return sum(map(poids_syllabus, set(aujourdhui)))
    
def poids_total_minimum(fardes, aujourdhui):
    return sum(map(poids_cours_et_syllabus, set(aujourdhui)))

def poids_total(fardes,aujourdhui):
    return (
        poids_cours_a_fardes(fardes, aujourdhui) +
        poids_cours_a_cahier(fardes, aujourdhui) +
        poids_des_syllabus(fardes, aujourdhui)
    )
    
def evaluer_depuis_somme_jour(fonction_jour):
    return lambda fardes: sum(fonction_jour(fardes,aujourdhui) for aujourdhui in horaire)

infos_evaluations_jour = [
    (nombre_fardes_prises, "Fardes prises", True),
    (nombre_cours_inutiles, "Cours inutiles", True),
    (heures_inutiles, "Heures inutiles", True),
    (poids_inutile, "Poids inutile", True),
    (poids_fardes_prises, "Poids fardes seules", True),
    (poids_cours_a_fardes, "Poids fardes remplies", True),
    (poids_cours_a_cahier, "Poids cahiers", False),
    (poids_des_syllabus, "Poids syllabus", False),
    (poids_total, "Poids total", True),
    ( poids_total_minimum, "Poids minimum", False)
]

def nombre_fardes_prises(fardes, aujourdhui):
    return sum(1 for farde in fardes_prises(fardes, aujourdhui))

def max_nombre_farde(fardes):
    le_max = max(
        nombre_fardes_prises(fardes, aujourdhui)
        for aujourdhui in horaire
    )
    return le_max,sum(1 for aujourdhui in horaire
                      if nombre_fardes_prises(fardes,aujourdhui) == le_max)
max_nombre_farde.nom = "(Nombres fardes, Jours)"

def max_poids_total(fardes):
    return max(poids_total(fardes,aujourdhui) for aujourdhui in horaire)
max_poids_total.nom = "Max poids total"

les_evaluations_jour = []
evaluations = [
    max_nombre_farde,
    max_poids_total,
]

for fonction,nom,facteur_tri in infos_evaluations_jour:
    fonction.nom = nom
    les_evaluations_jour.append(fonction)
    fonction.somme = evaluer_depuis_somme_jour(fonction)
    fonction.somme.nom = "Somme {}".format(nom)
    if facteur_tri:
        evaluations.append(fonction.somme)

def filtre_total(fonction_farde):
    def f(fardes):
        for farde in fardes:
            if fonction_farde(farde):
                return False
        return True
    return f

infos_filtres_simple = [
    ((lambda f: len(f) == 1), 'Enlever les fardes avec 1 seul cours'),
    ((lambda f: get_modele(f) == modeleXL), 'Enlever les XL')
]

filtres = []
for fonction,nom in infos_filtres_simple:
    filtre = filtre_total(fonction)
    filtre.nom = nom
    filtres.append(filtre)

def html_cours(cours):
    return '<span class="cours {}">{}</span>'.format(cours.css,cours.nom)

def get_classe(real, ecart, debut=0):
    from math import floor
    return debut + ecart * floor( (real - debut) / ecart ) 
    
def in_classe_real(fonction_real, ecart, debut=0):
    return lambda fardes: get_classe(fonction_real(fardes), ecart, debut)

def essayer(infos_evaluer, les_filtres=()):
    infos_evaluer = [
        (tup, evaluations[tup]) if type(tup) is int
        else tup
        for tup in infos_evaluer
    ]

    colonnes_highlight, les_evaluer = zip(*infos_evaluer)
    
    evaluer_scalaire = lambda fardes: tuple(ev(fardes) for ev in les_evaluer)
    def filtre(fardes):
        for f in les_filtres:
            if not f(fardes):
                return False
        return True
    
    html = open('fardes.html', 'w', encoding='utf-8')
    html.write("""
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8"/>
    <style>
        table{ text-align:center; margin: 10px; border-collapse:collapse;}
        th { background-color:#ccf; }
        td,th { border: 2px solid black; }
        .choisi0 { background-color: #77f; }
        .choisi1 { background-color: #99f; }
        .choisi2 { background-color: #bbf; }
        .resultats td.farde{ width: 150px; text-align:left; }
        .horaire td{ width: 100px; border: 2px solid black; border-radius: 5px; }
        .horaire{ border-collapse: separate; border-spacing: 5px 5px; }
        .description{ text-align: left; }
        td.description { background-color: #ddf; }
        td.description .nombre { width: 50px; }
        td.description .nombre.maximum { font-weight: bold; text-decoration: underline; }
        td.description .fardes { width: 75px; }
        td.description .cours { width: 300px; } 
        .cache .description { display: none; }
        .cache tr:hover .description { display: table-cell; }
        .montre .description th:not(.jour):not(.total) { display: none; }
        .montre tr:hover .description th:not(.jour):not(.total) { display: table-cell; }
        .cours { margin: 3px; font-weight: bold; }

        .a_farde .type { background-color: #fc6; }
        .cahier .type { background-color: #999; }
        
        .latin { color: #909; }
        .francais { color: #c60; }
        .bio { color: #f06; }
        .ndls { color: #060; }
        .histoire { color: #930; }
        .physique { color: #00f; }
        .morale { color: #333; }
        .geo { color: #0aa; }
        .eps { color: #333; }
        .math { color: #c00; }
        .musique { color: #393; }
        .techno { color: #6c6; }
        .parascolaire { color: #999; }

        %s
    </style>
    </head>
    <body class='cache'>
    """ % (
        '\n'.join(
            '.hide_filtre{0} .filtre{0} {{ display: none; }}'.format(i)
            for i in range(len(filtres))
        )
    ))

    ancre = 1
    def ecrire_resultats(liste, titre, possibilites):
        nonlocal ancre
        html.write('<table id="{}" class="resultats">'.format(ancre))
        ancre += 1
        html.write(
            """<tr>
                <th width=30>Num</th>
                {}
                <th colspan=100>{} : {} Possibilité{}</th>
            </tr>""".format(
                '\n'.join(
                    '<th class="scalaire{}">{}</th>'.format(
                        '' if i not in colonnes_highlight else
                        ' choisi{}'.format(colonnes_highlight.index(i)),
                        f.nom
                    )
                    for i,f in enumerate(evaluations)
                ),
                titre,
                possibilites,
                plural(possibilites)
            )
        )
        for i,fardes in enumerate(liste):
            html.write(
                """<tr class='{}'>
                     <th><a href="#">#{}</a></th>
                     {}
                     {}
                     <td class='description'>{}</th>
                </tr>""".format(
                    ' '.join(
                        'filtre{}'.format(j)
                        for j,filtre in enumerate(filtres)
                        if not filtre(fardes)
                    ),
                    i+1,
                    '\n'.join(
                        '<th width=50 class="scalaire{}">{}</th>'.format(
                            '' if i not in colonnes_highlight else
                            ' choisi{}'.format(colonnes_highlight.index(i)),
                            f(fardes) if i not in colonnes_highlight else
                            f(fardes) if f == les_evaluer[ colonnes_highlight.index(i) ] else
                            '{}&nbsp;|{}|'.format(
                                f(fardes),
                                les_evaluer[ colonnes_highlight.index(i) ](fardes),
                            )
                        )
                        for i,f in enumerate(evaluations)
                    ),
                    ''.join(
                        '<td class="farde">{}({}/{}){}({})</td>'.format(
                            get_modele(farde).nom,
                            poids_interieur_farde(farde),
                            get_modele(farde).capacite,
                            ''.join( map(html_cours,farde) ),
                            len(farde)
                        )
                        for farde in fardes
                    ),
                    description_choix(fardes)
                )
            )
        html.write('</table>')

    html.write('<div style="display:inline-block;">')
    html.write('<h1>Horaire</h1>')
    html.write('<table class="horaire">')
    html.write('<tr><th width=50>Heure</th>{}</tr>'.format(
        ''.join(
            '<th>{}</th>'.format(n)
            for n in NOMS_JOUR
        )
    ))

    fusionner = False
    def rowspan(i,j):
        if not fusionner:
            return 1
        if i >= len(horaire[j]):
            return 1
        if i-1 >= 0:
            if horaire[j][i-1] == horaire[j][i]:
                return None
        somme = 0
        for k in range(i,len(horaire[j])):
            if horaire[j][i] == horaire[j][k]:
                somme += 1
            else:
                return somme
    for i in range(max(map(len,horaire))):
        html.write("""
            <tr>
                <th>{}</th>
                {}
            </tr>""".format(
                i+1,
                ''.join(
                    '<td rowspan={}>{}</td>'.format(
                        rowspan(i,j),
                        html_cours(horaire[j][i]) if i < len(horaire[j]) else '',
                    )
                    for j in range(len(horaire))
                    if rowspan(i,j) is not None
                )
            )
        )
    html.write('</table>')
    html.write('</div>')

    html.write('<div style="display:inline-block; vertical-align:top;">')
    html.write('<h1>Cours</h1>')
    html.write('<table>{}{}</table>'.format(
        '''<tr>
              <th>Type</th>
              <th>Nom</th>
              <th>Heures</th>
              <th>Cours</th>
              <th>Syll</th>
        </tr>''',
        '\n'.join(
            '''<tr class="{}">
                <td class="type">{}</td>
                <td class="nom">{}</td>
                <td class="heures">{}</td>
                <td class="poids">{}</td>
                <td class="poids_syllabus">{}</td>
            </tr>'''.format(
                    'a_farde' if cours_farde(cours) else 'cahier',
                    'Farde' if cours_farde(cours) else 'Cahier',
                    html_cours(cours),
                    nombre_heure(cours),
                    poids_cours(cours),
                    poids_syllabus(cours) or ''
            )
            for cours in sorted(les_cours, key=lambda cours:
                (cours_farde(cours), cours.nom)
            )
        )
    ))
    html.write('</div>')

    html.write('<div style="display:inline-block; vertical-align:top;">')
    html.write('<h1>Fardes</h1>')
    html.write('<table>{}{}</table>'.format(
        '''<tr>
               <th>Nom</th>
               <th>Capacité</th>
               <th>Poids</th>
        </tr>''',
        '\n'.join(
            '''<tr>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
            </tr>'''.format(
                modele.nom,
                modele.capacite,
                modele.poids
            )
            for modele in modeles_fardes
        )
    ))
    html.write('</div>')
    
    html.write('<h1>Fin du calcul</h1>')

    html.write('<ul>{}</ul>'.format(
        ''.join(
            '''<li>
                     <input
                       class="checkbox_filtre"
                       onchange="calculer_class_body()"
                       type="checkbox" />{}
                </li>'''.format(
                filtre.nom
            )
            for i,filtre in enumerate(filtres)
        )
    ))
    
    html.write('<p>{}</p>'.format(
        ''.join(
            '<a href="#{0}">#{0} </a>'.format(i)
            for i in range(1,len(dispo)+2)
        )
    ))


    html.write('<p>{}</p>'.format(
        """<input
              id='afficher_description'
              onchange="calculer_class_body()"
              type="checkbox" />Afficher les descriptions
        """
    ))

    def tri_farde(farde):
        return (len(farde),) + farde
    
    MAXI = 100
    total = []
    for sep in range(1,len(dispo)+1):
        A = tuple(genere_fardes(dispo, sep))
        S = frozenset(
                tuple(sorted(
                    (tuple(sorted(farde)) for farde in fardes),
                    key=tri_farde,
                    reverse=True
                )) for fardes in A
            )
        
        print(sep, "Ma generation", len(A), " vrai set :", len(S))
        L = sorted(filter(filtre,S), key=evaluer_scalaire)
        ecrire_resultats(L[:MAXI], '{} Farde{}'.format(sep, '' if sep == 1 else 's'), len(L))
        total += L
    ecrire_resultats(sorted(total,key=evaluer_scalaire)[:MAXI*3], 'Toutes les combinaisons', len(total))

    html.write('''<script>
    var afficher_description = document.getElementById('afficher_description')
    var checkbox_filtres = document.querySelectorAll('.checkbox_filtre')
    var body = document.querySelector('body')
    function calculer_class_body(){
        var classes = []
        if(afficher_description.checked)
            classes.push('montre')
        else
            classes.push('cache')

        for(var i = 0; i < checkbox_filtres.length; i++)
            if(checkbox_filtres[i].checked)
                classes.push('hide_filtre' + i)
        
        body.setAttribute('class', classes.join(' '))
    }
    afficher_description.onclick = calculer_class_body
    
    
</script>''')
    html.write('</body></html>')
    html.close()

# essayer( [(1, in_classe_real(evaluations[1], 4, 21)), 8] ) #MaxPoidsTotal, PoidsTotal, PoidsInutile
essayer( [0, 8, 5] ) #(Nb,Jour), PoidsTotal, PoidsInutile

