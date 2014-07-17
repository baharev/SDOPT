import representation.dag_util as du

def parse(problem, elems):
    l = elems[0]
    src, dest, mult = int(l[1]), int(l[0]), float(l[2])
    assert len(l) == 3, 'Elems: {}'.format(elems)
    du.add_edge(problem.dag, src, dest, mult)