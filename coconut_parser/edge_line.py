
def parse(problem, elems):
    l = elems[0]
    source, dest, mult = int(l[1]), int(l[0]), float(l[2])
    assert len(l) == 3, 'Elems: {}'.format(elems)
    problem.dag.add_edge(source, dest, weight=mult)