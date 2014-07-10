from collections import namedtuple
from enum import IntEnum
import fileinput
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.dag import ancestors, topological_sort

class AutoNumber(IntEnum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = int.__new__(cls)
        obj._value_ = value
        return obj

class NodeAttr(AutoNumber):
    bounds   = ()
    constant = ()
    d        = ()
    n        = ()
    number   = ()
    operation= ()
    display  = ()

Bounds = namedtuple('Bounds', 'l u')

class info_line:
    def __init__(self, problem):
        self.p = problem
    def __call__(self, elems):
        for l in elems:
            self.parse(l[0], l)
    def parse(self, kind, l):
        if   kind=='C': # <N> C 1 'e3'
            self.p.con_num_name[int(l[1])] = l[2]
        elif kind=='c': # <N> c 3 1
            self.p.con_ends_num[int(l[2])] = int(l[1])
        elif kind=='N': # <N> N 2 'x3'
            self.p.var_num_name[int(l[1])] = l[2]
        elif kind=='V': # <N> V 3
            self.p.nvars = int(l[1])
        elif kind=='m': # <N> m 'ex9_2_8'
            self.p.model_name = l[1]

class edge_line:
    def __init__(self, problem):
        self.p = problem
    def __call__(self, elems):
        l = elems[0]
        source, dest, mult = int(l[1]), int(l[0]), float(l[2])
        assert len(l) == 3, 'Elems: {}'.format(elems)
        self.p.dag.add_edge(source, dest, weight=mult)

class node_line:
    def __init__(self, problem):
        self.p = problem
    def __call__(self, elems):
        node_id = elems.pop()
        self.p.dag.add_node(node_id, self.parse_attributes(elems))
    def parse_attributes(self, elems):
        attr_dict = { }
        for e in elems: # Clean up when it is clear what can / cannot happen
            kind = e[0]
            if   kind=='b': # b [0,I]
                lb, ub = e[1][1:-1].replace('I','inf').split(',')
                attr_dict[NodeAttr.bounds] = Bounds(float(lb), float(ub))
            elif kind=='V': # V 2
                attr_dict[NodeAttr.number] = int(e[1])
            elif kind=='C': # C 0.1
                attr_dict[NodeAttr.constant] = float(e[1])
            elif kind=='d': # d 0.1; lambda*x1 + d or d/(lambda*x1)
                attr_dict[NodeAttr.d] = float(e[1])
            elif kind=='n': # n 3; (lamba*x)^n
                attr_dict[NodeAttr.n] = int(e[1])
            else:
                attr_dict[NodeAttr.operation] = e[0]
        return attr_dict

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

class Problem:
    def __init__(self):
        self.dag = nx.DiGraph()
        self.con_ends_num = { }
        self.con_num_name = { }
        self.var_num_name = { }
        self.model_name = '(none)'
        self.nvars = int(-1)
    def set_node_display(self):
        disp = NodeAttr.display
        for node_id, data in self.dag.nodes_iter(data=True):
            if data.get(NodeAttr.constant):
                data[disp] = str(data[NodeAttr.constant])
            elif data.get(NodeAttr.number):
                var_num = data[NodeAttr.number]
                name = self.var_num_name.get(var_num, str('V'+var_num))
                data[disp] = '{} {}'.format(name, node_id)
            else:
                data[disp] = data[NodeAttr.operation]

def parse(f):
    p = Problem()
    funcs = { 'N': info_line(p),
              'I': node_line(p),
              'E': edge_line(p) }

    for kind, elems in lines(f):
        func = funcs.get(kind)
        if func:
            func(elems)

    dag = p.dag
    print 'Finished reading the dag file'
    print 'Some sanity checks'
    print 'Is connected?', nx.is_connected(dag.to_undirected())
    print 'Is DAG?', nx.is_directed_acyclic_graph(dag)
    print 'Nodes:', nx.number_of_nodes(dag), 'edges:', nx.number_of_edges(dag)

    for end_node, con_num in p.con_ends_num.iteritems():
        print 'con #{} ending in node {} depends on:'.format(con_num, end_node)
        deps = ancestors(dag, end_node)
        deps.add(end_node)
        con_dag = dag.subgraph(deps)
        eval_order = topological_sort(con_dag)
        print_con(con_dag, eval_order)

    nx.draw_networkx(dag, labels=nx.get_node_attributes(dag, NodeAttr.display))
    plt.show()

def print_con(sub_dag, order):
    attribs = nx.get_node_attributes(sub_dag, NodeAttr.display)
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
    print
    read_dag('/home/ali/pyton-ws/sparse-matrix-computations/dag/ex9_2_8.dag')
