def find(stack, numbers, operations, cible):
    if len(stack) >= 1 and stack[0] == cible:
        raise Exception(operations)
    if len(stack) >= 2:
        a,b,rem = stack[-1],stack[-2],stack[:-2]
        find(rem + (a+b,), numbers, operations + ('+',), cible)
        if a >= b:
            find(rem + (a-b,), numbers, operations + ('-',), cible)
        find(rem + (a*b,), numbers, operations + ('*',), cible)
        if b != 0 and a % b == 0:
            find(rem + (a // b,), numbers, operations + ('/',), cible)
    for i,n in enumerate(numbers):
        find(stack + (n,), numbers[:i] + numbers[i+1:], operations + (str(n),), cible)
    # Backtrack

# 7 8 10 100 = 140
# => 7 8 10 * 100 - *
# 7 * (100 - (8 * 10))

class Noeud:
    def __init__(self, val, *enfants):
        self.val = val
        self.enfants = enfants

    @staticmethod
    def from_rpn(expr):
        stack = []
        for i in range(len(expr)):
            if expr[i].isdigit():
                stack.append( Noeud(expr[i]) )
            else:
                stack.append( Noeud(expr[i], stack.pop(), stack.pop()) )
        return stack[-1]

    def prefixe(self):
        yield self
        for n in self.enfants:
            yield from n.prefixe()
            
    def infixe(self):
        if len(self.enfants) > 0:
            yield from self.enfants[0].infixe()
        yield self
        if len(self.enfants) > 1:
            yield from self.enfants[1].infixe()
    
    def postfixe(self):
        for n in self.enfants:
            yield from n.postfixe()
        yield self
            
    def str_infixe(self):
        if self.val.isdigit():
            return self.val
        return "(%s %s %s)" \
               % (self.enfants[0].str_infixe(), str(self.val), self.enfants[1].str_infixe())

    def str_fct(self):
        if self.val.isdigit():
            return self.val
        return self.val + "(" + ",".join(n.str_fct() for n in self.enfants) + ")"

    def str_prefixe(self):
        return " ".join(map(lambda n:str(n.val), self.prefixe()))

    def str_postfixe(self):
        return " ".join(map(lambda n:str(n.val), self.postfixe()))


def le_compte_est_bon():
    print("Le programme va jouer au jeu 'le compte est bon'")
    try:
        find((), tuple(map(int,input("Nombres ? (séparés par des espaces) ").split())), (), int(input("Total ? ")))
    except Exception as e:
        rpn = e.args[0]
        n = Noeud.from_rpn(rpn)
        
        from textwrap import indent,dedent
        print(indent(dedent("""
            RPN : {}
            Traditionnel : {}
            Infixe : {}
            Fonction : {}
            """), '  ').format(
                " ".join(rpn),
                n.str_infixe(),
                n.str_prefixe(),
                n.str_fct()
            )
        )
    else:
        print("Pas de solution")

le_compte_est_bon()
