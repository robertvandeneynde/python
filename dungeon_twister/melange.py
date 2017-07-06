from random import *

noms_persos = [
    ["Voleuse", "Gobelin", "Guerrier", "Magicien", "Passe-Muraille", "Troll", "Clerc", "Méchanork"],
    ["Paladin", "Dragon rouge", "Maître d'armes", "Golem", "Pickpocket", "Illusioniste", "Éclaireur elfe", ],
    ["Élémentaire d'eau", "Élémentaire de feu", "Télékinésiste", "Prophète", "Magophage", "Acrobate", ],
    ["Dragon mort-vivant", "Ombre", "Ange de lumière", "Nécromancien", "Momie", ],
    ["Ange sombre", "Berserk", "Général", "Nain tueur de troll", "Arbalétrier", "Assasin", "Dragon doré", "Samouraï"],
    ["Araknis", "Pondeuse", "Archer elfe", "Élémentaire de pierre", "Bûcheron", "Druide", ],
    ["Maitre des bêtes", "Dragon de glace", "Élémentaire de glace", "Sorcière des glaces", "Yéti", "Élémentaire de foudre", "Mamouth", ]
]

noms_objets = [
    ["Corde", "Bâton de boule de feu", "Épée", "Armure", "Trésor", "Potion de vitesse"],
    ["Corde", "Clef", "Bouclier contrefeu", "Parchemin de charme", "Anneau de téléportation", ],
    ["Corde", "Clef", "Parchemin de confusion", "Parchememin de reconstruction", "Anneau de répulsion", ],
    ["Clef", "Croix sainte", "Parchemin d'inversion", "Boulet", "Anneau de faiblesse", ],
    ["Corde", "Clef", "Potion de force", "Katana", ]
    ["Corde", "Clef", "Anneau de paralysie", "Orbe de paix", ],
    ["Corde", "Clef", "Parchemin de glace", ],
]

def ensemble_persos():
    return sorted(sample([p for l in noms_persos for p in l], 8))

def ensemble_objets():
    return sorted(sample([o for l in noms_objets for o in l], 6))
   
