class ParsediffResult(dict):
    def __init__(self, name):
        self.name = self['name'] = name
        self.before = self['before'] = []
        self.after = self['after'] = []

def parsediff(filename):
    with open(filename) as f:
        try:
            state = 1
            SS = []
            for i,l in enumerate(x.strip() for x in f):
                i += 1
                # print('number', i, 'state', state, 'line', l)
                if state == 1:
                    assert not(l.startswith('> ') or l.startswith('< '))
                    S = ParsediffResult(l)
                    state = 2
                    # print(S)
                elif state == 2:
                    if l.startswith('< '):
                        l = l[2:]
                        S.before.append(l)
                    elif l.startswith('> '):
                        state = 3
                        # goto state 3
                        l = l[2:]
                        S.after.append(l)
                    elif l == '---':
                        state = 3
                    else:
                        SS.append(S)
                        state = 1
                        S = ParsediffResult(l)
                        state = 2
                    # print(S)
                elif state == 3:
                    assert not(l.startswith('< ') or l == '---')
                    if l.startswith('> '):
                        l = l[2:]
                        S.after.append(l)
                    else:
                        SS.append(S)
                        state = 1
                        S = ParsediffResult(l)
                        state = 2
                    # print(S)
            SS.append(S)
            return SS
        except AssertionError:
            raise ValueError('Error line {}: {}'.format(i, l))