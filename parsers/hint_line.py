from __future__ import print_function

def parse(problem, elems):
    # <H> t 0 0.976, 0.992, 0.974, 0.706
    assert len(elems)==1, elems
    words = elems[0]
    if words[0] == 'o':
        print('WARNING: Best known objective ignored! (unimplemented)')
        return
    assert words[0]=='t' and words[1]=='0', elems
    sol = [ ]
    for x in words[2:]:
        x = x.rstrip(',')
        sol.append(float(x))
    problem.refsols.append(sol)
