def convert(string):
    lines = string.split('\n')
    i = 0
    for l in lines:
        if l.strip() == '' or l == 'Ami(e)Amis':
            pass
        else:
            if i % 2 == 0:
                yield l
            i += 1

data1 = set(convert('''Martin Delobbe
39 ami(e)s en commun
Ami(e)Amis
Hamza Hammoumi
13 ami(e)s en commun
Ami(e)Amis
Samy Weimb
57 ami(e)s en commun
Sidney Golstein
42 ami(e)s en commun
Lobar Da
29 ami(e)s en commun
Cédric Hannotier
16 ami(e)s en commun'''))

data2 = set(convert('''Ami(e)Amis
Mohamed Khlifi
33 ami(e)s en commun
Ami(e)Amis
Raphael Hannaert
38 ami(e)s en commun
Ami(e)Amis
Erica Berghman
58 ami(e)s en commun
Sophia Azzagnuni
23 ami(e)s en commun
'''))

data3= set(convert('''
Ami(e)Amis
Rémi Crépin
75 ami(e)s en commun
Ami(e)Amis
Maxime de Changy
20 ami(e)s en commun
Ami(e)Amis
Benoît Vernier
20 ami(e)s en commun
Ami(e)Amis
Raphael Hannaert
38 ami(e)s en commun
Ami(e)Amis
Martin Delobbe
39 ami(e)s en commun
Ami(e)Amis
Maxime Wautrin
63 ami(e)s en commun
Ami(e)Amis
Alicia De Groote
58 ami(e)s en commun
Ami(e)Amis
Pierre-Alexandre Petitjean
19 ami(e)s en commun
Ami(e)Amis
Samy Weimb
57 ami(e)s en commun
Ami(e)Amis
Enes Ulusoy
29 ami(e)s en commun
Ami(e)Amis
Bastien Ryckaert
57 ami(e)s en commun
Ami(e)Amis
Mariame Sacko
13 ami(e)s en commun
Ami(e)Amis
Antonin Halut
61 ami(e)s en commun
Ami(e)Amis
Hamza Hammoumi
13 ami(e)s en commun
Nicolas Hautekeet
23 ami(e)s en commun
Cédric Hannotier
16 ami(e)s en commun
Anthony Vanden Eede
18 ami(e)s en commun
Lobar Da
29 ami(e)s en commun
Sam Sadraee
31 ami(e)s en commun
Sidney Golstein
42 ami(e)s en commun
Tom Vandenbroucke
33 ami(e)s en commun
Lucas Lefevre
4 ami(e)s en commun
Mathieu Petitjean
19 ami(e)s en commun
Elisabeth Gruwé
28 ami(e)s en commun
Mahdi Moghaddamfar
13 ami(e)s en commun
Raphaël Zacchello
42 ami(e)s en commun
Aurélie Vermeulen
37 ami(e)s en commun
Sophia Azzagnuni
'''))

def printsets(*sets):
    for s in sets:
        print(len(s), s)
printsets(data1, data2, data3, data1 - data3, data2 - data3, data3 - data2 - data1)