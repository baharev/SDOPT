import fileinput
import matplotlib.pyplot as plt
import networkx as nx
from collections import namedtuple
from autoenum import AutoNumber
from networkx.algorithms.dag import ancestors, topological_sort

class NodeAttr(AutoNumber):
    bounds    = ()
    constant  = ()
    d         = ()
    n         = ()
    var_num   = ()
    operation = ()
    display   = ()

Bounds = namedtuple('Bounds', 'l u')

class info_line:
    def __init__(self, problem):
        self.p = problem
    def __call__(self, elems):
        for l in elems:
            self.parse(l[0], l)
    def parse(self, kind, l):
        if   kind=='C': # <N> C 1 'e3'
            self.p.con_num_name[int(l[1])] = l[2][1:-1]
        elif kind=='c': # <N> c 3 1
            self.p.con_ends_num[int(l[2])] = int(l[1])
        elif kind=='N': # <N> N 2 'x3'
            self.p.var_num_name[int(l[1])] = l[2][1:-1]
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
        self.p.dag.add_node(node_id, self.parse_attributes(node_id, elems))
    def parse_attributes(self, node_id, elems):
        attr_dict = { }
        for e in elems: # Clean up when it is clear what can / cannot happen
            kind = e[0]
            if   kind=='b': # b [0,I]
                lb, ub = e[1][1:-1].replace('I','inf').split(',')
                attr_dict[NodeAttr.bounds] = Bounds(float(lb), float(ub))
            elif kind=='V': # V 2
                attr_dict[NodeAttr.var_num] = int(e[1])
            elif kind=='C': # C 0.1
                attr_dict[NodeAttr.constant] = float(e[1])
            elif kind=='d': # d 0.1; lambda*x1 + d or d/(lambda*x1)
                attr_dict[NodeAttr.d] = float(e[1])
            elif kind=='n': # n 3; (lamba*x)^n
                attr_dict[NodeAttr.n] = int(e[1])
            elif kind in {'+', '*', '/', 'exp', 'log'}:
                attr_dict[NodeAttr.operation] = kind
            else:
                pass
        attr_dict[NodeAttr.display] = '?'
        print 'node_id', node_id, 'attributes', attr_dict
        return attr_dict

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
        print self.var_num_name
        for node_id, data in self.dag.nodes_iter(data=True):
            print node_id, data
            if   NodeAttr.constant in data:
                data[disp] = str(data[NodeAttr.constant])
            elif NodeAttr.var_num in data:
                var_num = data[NodeAttr.var_num]
                name = self.var_num_name.get(var_num, 'V{}'.format(var_num))
                data[disp] = '{}({})'.format(name, node_id)
            elif node_id in self.con_ends_num:
                con_num = self.con_ends_num[node_id]
                name = self.con_num_name.get(con_num, '_c{}'.format(con_num))
                data[disp] = '{}({})'.format(name, node_id)
            else:
                data[disp] = data[NodeAttr.operation]

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

    p.set_node_display()

    print 'Constraint dependencies\n'
    for end_node in p.con_ends_num:
        print dag.node[end_node][NodeAttr.display]
        deps = ancestors(dag, end_node)
        deps.add(end_node)
        con_dag = dag.subgraph(deps)
        eval_order = topological_sort(con_dag)
        print_con(con_dag, eval_order)

    nx.draw_networkx(dag, labels=nx.get_node_attributes(dag, NodeAttr.display))
    plt.show()

def print_con(sub_dag, order):
    disp = nx.get_node_attributes(sub_dag, NodeAttr.display)
    for node_id in order:
        predec = sub_dag.predecessors(node_id)
        if len(predec) > 0:
            print node_id, '=', disp[node_id], predec
        else:
            print node_id, '=', disp[node_id]
    print

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
