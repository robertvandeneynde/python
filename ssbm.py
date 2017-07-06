import random, sys
noms = 'dr_mario mario luigi bowser peach yoshi dk captain_falcon ganondorf falco fox ness ice_climbers kirby samus zelda link link_enfant peach pikachu rondoudou mewto mr_game_and_watch marth roy'.split()

rob  = list(noms)
aure = list(noms)
the_round = 1

### Enter the saved code here or 'from saved import *'

### End of saved code

just_loaded = 'new_rob' in globals()
while rob and aure:
    print("-- Round {} --\n[[ Rob  ({:2}) : {} ]]\n[[ Aure ({:2}) : {} ]]".format(
        the_round,
        len(rob), ' '.join(rob),
        len(aure), ' '.join(aure)))
    
    if just_loaded:
        just_loaded = False
    else:
        random.shuffle(rob)
        random.shuffle(aure)
        
        new_rob  = []
        new_aure = []
        
    for i, (one, two) in enumerate(zip(rob, aure)):
        choix = input(">> Rob VS Aure : [[ {} ]] VS [[ {} ]] Win ? (r/a/q) ".format(one,two)).strip().lower()
        
        while choix not in ('r', 'a', 'q', 'quit'):
            choix = input("Recommencez... r/a/q")
        
        if choix == "r":
            new_rob.append(one)
        elif choix == "a":
            new_aure.append(two)
        else:
            print("\nnew_rob = {}\nrob = {}\nnew_aure = {}\naure = {}\nthe_round = {}".format(
                new_rob, rob[i:], new_aure, aure[i:], the_round))
            sys.exit(0)
    
    rob  = new_rob + rob[i+1:]
    aure = new_aure + aure[i+1:]
    the_round += 1

if aure:
    print("Aure wins !")
else:
    print("Rob wins !")