from __future__ import print_function
import fileinput
import edge_line
import hint_line
import info_line
import node_line
from ampl_parser import read_flattened_ampl
# FIXME Misplaced utility function
from ampl_parser import pretty_str_numpy_array
from representation.problem import Problem
import representation.dag_util as du
import numpy as np

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

def read(filename):
    try:
        f = fileinput.input(filename, mode='r')
        return parse(f)
    finally:
        print('Read', f.lineno(), 'lines from file', filename)
        f.close()

# FIXME Misplaced utility
def crosscheck_sparsity_pattern(filename, p):
    bsp = read_flattened_ampl( filename[:-4]+'.nl' )
    checked = [False] * bsp.nrows
    for con_num, n in du.itr_sink_con_num_nodeid(p.dag):
        eval_order = p.con_top_ord[n]
        itr_base_vars = (p.base_vars[i] for i in eval_order if i in p.base_vars) 
        base_vars = np.array(sorted(itr_base_vars), np.int32)
        assert np.all(bsp.jacobian[con_num]==base_vars)
        checked[con_num] = True
    assert all(checked)

def read_problem(filename, to_plot = True):
    problem = read(filename)
    problem.setup()
    crosscheck_sparsity_pattern(filename, problem)
    if to_plot:
        du.plot(problem.dag)
        return None # FIXME Resolve issues with plotting! (Must destroy dictionaries)
    return problem
