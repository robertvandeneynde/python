#! /usr/bin/python3

def get_moyenne(ensemble):
    return sum(ensemble) / len(ensemble)

def get_ecart_type(ensemble, moyenne=None):
    if moyenne is None:
        moyenne = get_moyenne(ensemble)
    variance = sum((n - moyenne) ** 2 for n in ensemble) / len(ensemble)
    from math import sqrt
    return sqrt(variance)

def affiche(ensemble, nom):
    moyenne = get_moyenne(ensemble)
    ecart = get_ecart_type(ensemble,moyenne)
    print("{} ({}) : µ = {:.2f}, σ = {:.2f}".format(nom, len(ensemble), moyenne, ecart))

notes_tot = [int(n) for n in open("notesanacomp.txt") if int(n) <= 20]
notes = [n for n in notes_tot if n != 0]

affiche(notes_tot, "Notes avec zéros")
affiche(notes, "Notes sans zéros")
