import fileinput
import matplotlib.pyplot as plt
import networkx as nx
import edge_line
import info_line
import node_line
from problem_representation.problem_repr import Problem
from nodes.node_attributes import NodeAttr

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
              'E': edge_line.parse }

    p = Problem()

    for kind, elems in lines(f):
        func = funcs.get(kind)
        if func:
            func(p, elems)

    dag = p.dag
    print 'Finished reading the dag file'
    print 'Some sanity checks'
    #print 'Is connected?', nx.is_connected(dag.to_undirected())
    print 'Is DAG?', nx.is_directed_acyclic_graph(dag)
    print 'Nodes:', nx.number_of_nodes(dag), 'edges:', nx.number_of_edges(dag)

    p.set_node_display()

    print 'Constraint dependencies\n'

    p.setup_constraints()

    nx.draw_networkx(dag, labels=nx.get_node_attributes(dag, NodeAttr.display))
    plt.show()

def read_dag(filename):
    try:
        f = fileinput.input(filename, mode='r')
        return parse(f)
    finally:
        print 'Read', f.lineno(), 'lines'
        f.close()
