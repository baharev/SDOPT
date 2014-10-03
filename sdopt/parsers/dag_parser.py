from __future__ import print_function
from . import edge_line
from . import hint_line
from . import info_line
from . import node_line
from .ampl_parser import read_flattened_ampl
from ..representation.problem import Problem, setup, \
                                crosscheck_sparsity_pattern, crosscheck_names
from ..representation.dag_util import plot
from ..util.file_reader import lines_of

def read_problem(filename, plot_dag=True, crosscheck_nl=True, show_sparsity=True):
    with lines_of(filename) as lines:
        problem = parse(lines)
    setup(problem)
    if crosscheck_nl:
        nl_filename = filename[:-4]+'.nl' # filename.dag -> filename.nl
        bsp = read_flattened_ampl(nl_filename, show_sparsity)
        crosscheck_sparsity_pattern(problem, bsp.csr_mat)
        crosscheck_names(problem, bsp.row_names, bsp.col_names)
    if plot_dag:
        plot(problem.dag)
        return None # FIXME Resolve issues with plotting! (Must destroy dictionaries)
    return problem

def lines(iterable):
    for line in iterable:
        first_space = line.find(' ')
        kind  = line[1:first_space-1]
        elems = [e.split() for e in line[first_space:].split(':')]
        if kind.isdigit():
            elems.append(int(kind))
            kind = 'I'
        yield kind, elems

def parse(f):
    funcs = { 'N': info_line.parse,
              'I': node_line.parse,
              'E': edge_line.parse,
              'H': hint_line.parse }
    p = Problem()
    for kind, elems in lines(f):
        func = funcs.get(kind)
        if func:
            func(p, elems)
    return p
