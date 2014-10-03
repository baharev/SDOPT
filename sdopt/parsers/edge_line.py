from __future__ import absolute_import
from ..representation.dag_util import add_edge

def parse(problem, elems):
    l = elems[0]
    src, dest, mult = int(l[1]), int(l[0]), float(l[2])
    assert len(l) == 3, 'Elems: %s' % elems
    # Plotting requires the string keyword
    add_edge(problem.dag, src, dest, { 'weight' : mult } )