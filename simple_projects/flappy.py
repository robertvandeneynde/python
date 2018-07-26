def next_possib(position, vitesse, dist, hauteur_terrain):
    '''
    En commençant en position, vitesse
    avec une porte à une distance dist
    Renvoie toutes les possibilités d'arrivée
    Qui ne cognent pas le bord du plateau [0, hauteur_terrain[
    Exemples :
    next_possib(10,0,1,20) = [
        (9,-1,'.'), # pas de saut
        (11,2,'^'), # un saut
    ]
    next_possib(10,0,2,20) = [
        (7, -2, '..'), # ne rien faire
        (11, 2, '.^'), # attendre puis sauter
        (13, 1, '^.'), # sauter puis attendre
        (14, 2, '^^') # sauter deux fois
    ]
    '''
    liste = []
    def rec(pos, vit, dist, choix):
        if 0 <= pos < hauteur_terrain:
            if dist == 0:
                liste.append( (pos,vit,choix) )
            else:
                rec(pos + vit-1, vit-1, dist-1, choix + '.')
                rec(pos + 2, 2, dist-1, choix + '^')

    rec(position, vitesse, dist, '')
    return liste

def afficher_regles():
    print('''
À chaque instant flappy avance d'une case. Il a deux choix :
1) Sauter (^) : Mettre sa vitesse à 2 vers le haut
2) Se laisser aller à la gravité (.) : Sa vitesse augmente de 1 vers le bas
Ensuite sa nouvelle position sera l'ancienne + sa vitesse
''')

def run(distance, hauteur_porte, hauteur_terrain, portes, *args, JOUER=False, VERBOSE=0):
    
    def afficher_params():
        print('Distance HauteurPorte HauteurTerrain = ({} {} {})\nPortes = [{}]'.format(
            distance, hauteur_porte, hauteur_terrain, ' '.join(map(str,portes))
        ))
        
    def matrice_jeu():
        '''
        Pour l'affichage du terrain
        '''
        return [
            list('{:2}'.format(i)) + [
                ')' if j == 0 else
                ' ' if j % distance != 0 else
                ' ' if portes[j // distance - 1] <= i < portes[j // distance - 1] + hauteur_porte else
                '|'
                for j in range((1+len(portes)) * distance)
            ]
            for i in range(hauteur_terrain)
        ]
    
    
    def print_matrice(matrice, i=0):
        print('\n'.join(' ' * (i*2) + ''.join(sub) for sub in reversed(matrice)))
    
    def format_moves(moves):
        return '({})({})'.format(moves, len(moves))
    
    def matrice_moves(moves, i=0, pos=None, vit=None):
        '''
        Pour l'affichage d'une solution complète. (i = 0)
        La fonction pourrait être un peu modifiée pour accepter le paramètre i afin d'afficher les 
        sous-solutions.
        '''
        def mark_state(x,p,v):
            j = x + 2
            matrice[p][j] = 'f'
            stringv = ('+' if v >= 0 else '') + str(v)
            for h,c in enumerate(stringv):
                matrice[hauteur_terrain + h][j] = c
        
        matrice = matrice_jeu()
        
        matrice.extend([
            list(' ' * len(matrice[0]))
            for n in range(3)
        ])
        matrice.append(list(' ' * (3 + (i*distance)) + moves))
        
        if pos is None:
            pos = hauteur_terrain // 2
        if vit is None:
            vit = 0
            
        x = i * distance
        mark_state(x, pos, vit)
        for m in moves:
            if m == '^':
                vit = 2
            else:
                vit -= 1
            
            pos += vit
            x += 1
            
            mark_state(x, pos, vit)
            
        matrice.append( list('[[ {} porte(s) ]]'.format(len(moves) // distance)) )
            
        return matrice
    
    def jouer():
        pos, vit = hauteur_terrain // 2, 0
        solution = ''
        x = 0
        fini = False
        while not fini:
            print_matrice(matrice_moves(solution))
            
            if input('a pour sauter ou autre pour ne rien faire: ').strip().lower() == 'a':
                solution += '^'
                vit = 2
            else:
                solution += '.'
                vit -= 1
            
            pos += vit
            x += 1
            
            if not(0 <= pos < hauteur_terrain):
                fini = True
            
            if x % distance == 0:
                porte = portes[x // distance - 1]
                if not(porte <= pos < porte + hauteur_porte):
                    fini = True
                    
        print('Fini. Record = {} portes'.format((x-1) // distance))
    
    memo = {}
    
    def flappy(position, vitesse, i):
        '''
        Renvoie le meilleur déplacement possible
        en commençant en position, vitesse
        à partir de la porte i
        '''
        
        def rec_print(carac, *args, **kwargs):
            if VERBOSE >= 1:
                print(carac * (i+1) + '{})'.format((i+1) % 10), *args, **kwargs)
        
        def show_state(choix, j, pos, vit):
            if VERBOSE >= 2:
                print_matrice( matrice_moves(choix, j, pos, vit))
        
        def input_verbose():
            nonlocal VERBOSE
            if VERBOSE >= 3:
                choix = input('Pause... Entrez un nombre pour changer le niveau de verbosité. ').strip()
                try:
                    VERBOSE = int(choix)
                except ValueError:
                    pass
        
        def solution_correcte(solution):
            position, vitesse, choix = solution
            return (
                0 <= position < hauteur_terrain
                and portes[i] <= position < portes[i] + hauteur_porte
            )
        
        if i == len(portes):
            return ''
        
        if (position,vitesse,i) in memo:
            res = memo[position,vitesse,i]
            rec_print('|-', 'MEMOIZED: ' + format_moves(res))
            if res:
                input_verbose()
            return res
        
        best = ''
        for pos, vit, choix in filter(solution_correcte, next_possib(position, vitesse, distance, hauteur_terrain)):
            rec_print('| ', 'Possib ({},{}) |{}| {}'.format(pos,vit,i+1,format_moves(choix)))
            
            show_state(choix, i, position, vitesse)
            input_verbose()
            
            moves = choix + flappy(pos, vit, i+1)
            
            if moves:
                rec_print('| ', 'Sous Meilleur {} vs best {}'.format(format_moves(moves), format_moves(best)))
                show_state(moves, i, position, vitesse)
            
            best = max(best, moves, key=len)
            
            if moves:
                rec_print('| ', 'Meilleur ' + format_moves(best))
                
                show_state(moves, i, position, vitesse)
                input_verbose()
        
        rec_print('|-', 'Résultat ' + format_moves(best))
        
        memo[position,vitesse,i] = best
        
        return best
    
    if JOUER:
        jouer()
        while input('Recommencer ? (O/n)').strip().lower() != 'n':
            jouer()
        afficher_params()
    else:
        if VERBOSE:
            afficher_params()
        solution = flappy(hauteur_terrain // 2, 0, 0)
        print_matrice( matrice_moves(solution) )
        afficher_params()
print(__name__)
if __name__ == '__main__':
    choix = input('''
0) Règles du jeu Pixel Flappy Bird
1) Jouer
2) Analyser
3) Une comparaison de deux problèmes quasi équivalent mais avec deux solutions bien différentes
4) Des exemples aléatoires de résolution
Votre choix ? '''
    ).strip()
    # 4 3 15 | 9 8 6 9 8 10 0 7 0 9 5 7 4 10 3 4
    # Record 12 # .^....^....^^.....^..^......^.^.....^^^^.....^..
    # 4 3 15 | 7 12 7 10 10 0 4 4 0 8 5 2 0 10 7 7
    # MEMOIZED d'un grand cas
    
    if choix == '0':
        afficher_regles()
        
    elif choix in ('1', '2'):
        def read_list_int(string, defaut, **kwargs):
            string = string.strip().lower()
            if string in kwargs:
                return kwargs[string]
            else:
                if string:
                    try:
                        return list(map(int,string.split()))
                    except ValueError:
                        pass
                return defaut
            
        a = input('distance hauteur_porte hauteur_terrain (vide = défaut) ')
        params = read_list_int(a, [4,3,15])
        
        b = input('portes ? pos1 pos2 pos3... (vide = défaut, autre option : long) ')
        portes = read_list_int(b, [6,9,4,6,0,10], long=[7,12,7,10,10,0,4,4,0,8,5,2,0,10,7,7])
        
        args = params + [portes]
        kwargs = dict(JOUER=True) if choix == '1' else dict(VERBOSE=1000)
        
        run(*args, **kwargs)
    
    elif choix == '3':
        run(4, 3, 15, [6,9,4,6,0,10])
        run(4, 3, 15, [6,10,4,6,0,10])
    
    else:
        from random import choice, randrange
        possib_premier = list(set(range(13)) - {0,4})
        for i in range(10):
            run(4, 3, 15, [choice(possib_premier)] + [randrange(13) for i in range(15)])
            