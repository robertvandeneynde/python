import random
import time

def jeu(nbytes=1,iterations=20):
        print("""

On va vous demander un nombre hexadécimal composé de {} chiffres hexadécimaux
Vous devez le convertir en binaire sur {} chiffres binaires
        
        """.strip().format(nbytes, nbytes * 4)
        )
        input("Pret ? ")
        t = time.time()
        res = list(range(16 ** nbytes))
        random.shuffle(res)
        iterations = min(iterations, len(res))
        for i in range(iterations):
                n = res.pop()
                r = input(hex(n)[2:].zfill(nbytes).upper() + " ? ")
                while bin(n)[2:].zfill(nbytes * 4) != r:
                        print("Erreur!")
                        r = input(hex(n)[2:].upper() + " ? ")
        print(iterations, ' iterations sur', nbytes, 'bytes en',time.time() - t, ' secondes')
