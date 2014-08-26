'''
Use only read_problem, ignore all other functions.
'''
from __future__ import print_function
import edge_line
import hint_line
import info_line
import node_line
from ampl_parser import read_flattened_ampl
from representation.problem import Problem
import representation.dag_util as du
from util.file_reader import lines_of

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

def read_problem(filename, crosscheck_with_ampl=True, to_plot=True):
    with lines_of(filename) as lines:
        problem = parse(lines)
    problem.setup()
    if crosscheck_with_ampl:
        bsp = read_flattened_ampl( filename[:-4]+'.nl' ) # .dag -> .nl
        problem.crosscheck_sparsity_pattern(bsp.jacobian, bsp.nrows)
        problem.crosscheck_names(bsp.row_names, bsp.col_names)
    if to_plot:
        du.plot(problem.dag)
        return None # FIXME Resolve issues with plotting! (Must destroy dictionaries)
    return problem
