

'''
Example :
    [{name, addresses:[{id, lat, lng}]]
    [] -> must be a list
    {} -> must be a dict
    {hello, world} -> must be a dict that has "hello" and "world" (and maybe more !)
    int -> must be a int
    str -> must be a string

    {hello:[int]} -> must have hello, that must be a list of int
    [int] -> must be a list of Type

Tokens : remove all spaces, group by "[a-zA-z_]" "[" "]" ":" "{" "}" ","
    [{name, addresses:[{id, lat, lng}]]
    => [ { name , addresses : [ { id , lat , lng } ] ]
    => [ { I , I : [ { I , I , I } ] } ]

Grammar :
    Type := List | Dict | "int" | "str" | "float" | "number"
    List := "[" Type? "]"
    Dict := "{" (I (":" Type)?)? ("," I (":" Type)?)* "}"
'''

import itertools
import re

class Checker:
    def __init__(self, string):
        # TODO : caution of string {hello world} which is currently {helloworld}
        # maybe add space type that can be like the "," so {hello  world  } is like {hello,world,}
        try:
            tokens = [
                (a, ''.join(b))
                for a,b in itertools.groupby(
                    re.sub('\s', '', string),
                    lambda c:
                        'I' if c == '_' or 'a' <= c <= 'z' or 'A' <= c <= 'Z' else
                        c if c in "{[]}:," else None
                )
            ]

            assert not any(a is None for a in tokens), "has a unknown character"

            def in_pre(t):
                return (
                    t[0] == '['
                    or t[0] == '{'
                    or t[0] == 'I' and t[1] in ('str', 'int', 'float', 'number')
                )

            def f(tokens):
                '''
                returns (data, number of read tokens (> 1))
                '''
                assert 0 in range(len(tokens)), "token must be in pre"
                assert in_pre(tokens[0]), "token must be in pre"
                if tokens[0][0] == '[':
                    assert 1 in range(len(tokens)), "must have next token"
                    if tokens[1][0] == ']':
                        return ('List', ''), 2
                    else:
                        d,g = f(tokens[1:])
                        assert 1+g in range(len(tokens)), "next token must be a ]"
                        assert tokens[1+g][0] == ']', "next token must be a ]"
                        return ('List', d), 2+g

                elif tokens[0][0] == '{':
                    assert 1 in range(len(tokens)), "must have next token"
                    if tokens[1][0] == '}':
                        return ('Dict', ''), 2
                    else:
                        inner = tokens[1:]
                        ds = []
                        i = 0
                        found_close = False
                        while i < len(inner):
                            if inner[i][0] == "I":
                                if i+1 not in range(len(inner)) or inner[i+1][0] in (",", "}"):
                                    # empty part
                                    ds.append((inner[i][1], ''))
                                    i = i + 1
                                elif inner[i+1][0] == ":":
                                    d,g = f(inner[i+2:])
                                    ds.append((inner[i][1], d))
                                    i = i + 2 + g
                                else:
                                    assert False
                            elif inner[i][0] == ",":
                                i = i + 1
                            elif inner[i][1] == "}":
                                found_close = True
                                break
                        assert found_close, "must have a }"
                        return ('Dict', ds), 2 + i

                elif tokens[0][0] == 'I':
                    assert tokens[0][1] in ('int', 'str', 'float', 'number'), "must be a correct type"
                    return ('Data', tokens[0][1]), 1
                else:
                    assert False

            d,g = f(tokens)
            assert g == len(tokens), "must eat all the tokens and not {} (on {})".format(g, len(tokens))
        except AssertionError as e:
            if e.args:
                raise ValueError("scheme {} is mal formed : {}".format(string, e))
            else:
                raise ValueError("scheme {} is mal formed".format(string))
        except ValueError as e:
            raise ValueError("scheme {} is mal formed : {}".format(string, e))

        self.scheme = d

    def check(self, data):
        def f(s, d):
            typ, dat = s
            return (
                isinstance(d, list) and (
                    True if dat == '' else
                    # dat is a type
                    all(f(dat, a) for a in d)
                )
                if typ == 'List' else
                isinstance(d, dict) and (
                    True if dat == '' else
                    # dat is a list of (name, type or '')
                    (
                        all(name in d for name,subtype in dat)
                        and all(f(subtype, d[name]) for name,subtype in dat if subtype != '')
                    )
                )
                if typ == 'Dict' else
                (
                    dat == 'int' and isinstance(d, int) or
                    dat == 'float' and isinstance(d, float) or
                    dat == 'str' and isinstance(d, str) or
                    dat == 'number' and isinstance(d, (int,float)) or False
                )
                if typ == 'Data' else
                False # never happens
            )


        return f(self.scheme, data)

def tests():
    x = 1 # something of any type
    i = 1 # something of type int
    f = 2.5 # something of type float
    s = "string" # a string
    D = [
        ('[]', True, [], False, {}),
        ('[int]', True, [], [i], [i,i], False, [i,f], {}, ["hello"]),
        ('{}', True, {}, False, []),
        ('{hello, world}', True, {"hello":x, "world":x}, {"hello":x, "world":x, "yo":x},
                           False, {"hello":x}),
        ("{hello:int, world:{x:float,y:float}}", True, {"hello":5, "world":{"x":5,"y":2}}),
    ]
    for d in D:
        checker = Checker(d[0])
        cur = True
        for x in d[1:]:
            if isinstance(x, bool):
                cur = x
            else:
                if cur:
                    assert checker.check(x), "{} must check {}".format(d[0],x)
                else:
                    assert not checker.check(x), "{} must not check {}".format(d[0],x)
