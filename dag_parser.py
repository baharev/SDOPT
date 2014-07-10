import fileinput
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.dag import ancestors, topological_sort

class info_line:
    def __init__(self, graph, con_ends_num):
        self.g = graph
        self.con_ends_num   = con_ends_num
        self.con_num_name = { }
    def __call__(self, elems):
        for l in elems:
            self.dispatch(l[0], l)
    def dispatch(self, kind, l):
        if kind=='C':
            self.con_num_name[int(l[1])] = l[2]
        elif kind=='c':
            self.con_ends_num[int(l[2])] = int(l[1])

class edge_line:
    def __init__(self, graph):
        self.g = graph
    def __call__(self, elems):
        l = elems[0]
        source, dest, mult = int(l[1]), int(l[0]), float(l[2])
        assert len(l) == 3, 'Elems: %s' % elems
        self.g.add_edge(source, dest, weight=mult)

class node_line:
    def __init__(self, graph):
        self.g = graph
    def __call__(self, elems):
        node_id = elems.pop()
        self.g.add_node(node_id, content=elems)

def lines(iterable):
    for line in iterable:
        first_space = line.find(' ')
        kind  = line[1:first_space-1]
        elems = [e.split() for e in line[first_space:].split(':')]
        if kind.isdigit():
            elems.append(int(kind))
            kind = 'I'
        print kind, elems
        yield kind, elems

def parse(f):
    # Make it a problem repr.
    dag = nx.DiGraph()
    con_ends_num = { }

    funcs = { 'N': info_line(dag, con_ends_num),
              'I': node_line(dag),
              'E': edge_line(dag) }

    for kind, elems in lines(f):
        func = funcs.get(kind)
        if func:
            func(elems)

    print 'Finished reading the dag file'
    print 'Some sanity checks'
    print 'Is connected?', nx.is_connected(dag.to_undirected())
    print 'Is DAG?', nx.is_directed_acyclic_graph(dag)
    print 'Nodes:', nx.number_of_nodes(dag), 'edges:', nx.number_of_edges(dag)

    for end_node, con_num in con_ends_num.iteritems():
        print 'con #{} ending in node {} depends on:'.format(con_num, end_node)
        deps = ancestors(dag, end_node)
        deps.add(end_node)
        con_dag = dag.subgraph(deps)
        eval_order = topological_sort(con_dag)
        print_con(con_dag, eval_order)

    nx.draw_networkx(dag, labels=nx.get_node_attributes(dag, 'content'))
    plt.show()

def print_con(sub_dag, order):
    attribs = nx.get_node_attributes(sub_dag, 'content')
    for node_id in order:
        print '{0} = {1} {2}'.format(node_id, attribs[node_id], sub_dag.predecessors(node_id))

def read_dag(filename):
    try:
        f = fileinput.input(filename, mode='r')
        return parse(f)
    finally:
        print 'Read', f.lineno(), 'lines'
        f.close()

if __name__ == '__main__':
    read_dag('/home/ali/pyton-ws/sparse-matrix-computations/dag/JacobsenTorn2D.dag')
    #print
    #read_dag('/home/ali/pyton-ws/sparse-matrix-computations/dag/ex9_2_8.dag')
