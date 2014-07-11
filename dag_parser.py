import fileinput
import matplotlib.pyplot as plt
import networkx as nx
import weakref
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from autoenum import AutoNumber
from networkx.algorithms.dag import ancestors, topological_sort

class NodeAttr(AutoNumber):
    bounds    = ()
    con_num   = ()
    d         = ()
    display   = ()
    itself    = ()
    n         = ()
    node_id   = ()
    number    = ()
    operation = ()
    var_num   = ()

class Node:
    __metaclass__ = ABCMeta
    def __init__(self, attr_dict_owned_by_DiGraph):
        self.attr = weakref.ref(attr_dict_owned_by_DiGraph)
    @abstractmethod
    def display(self):
        pass

class Constraint(Node):
    def display(self):
        pass

class Variable(Node):
    def display(self):
        pass

class Number(Node):
    def display(self):
        pass

class Operation(Node):
    @abstractmethod
    def display(self):
        pass

class Div(Operation):
    def display(self):
        pass

class Exp(Operation):
    def display(self):
        pass

class Log(Operation):
    def display(self):
        pass

class Mul(Operation):
    def display(self):
        pass

class Sum(Operation):
    def display(self):
        pass

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
        self.lookup_table = {  'b':   self.bounds,
                               'V':   self.var_number,
                               'C':   self.constant,
                               'd':   self.d_term,
                               'n':   self.n_term,
                               '+':   self.sum,
                               '*':   self.mul,
                               '/':   self.div,
                               'exp': self.exp,
                               'log': self.log }
    def __call__(self, elems):
        node_id = elems.pop()
        self.p.dag.add_node(node_id, self.parse_attributes(node_id, elems))
    def parse_attributes(self, node_id, line_as_list):
        attr = { NodeAttr.node_id : node_id}
        for elems in line_as_list:
            kind = elems[0]
            func = self.lookup_table.get(kind, self.unimplemented)
            func(elems, attr)
        attr[NodeAttr.display] = '?'
        print 'node_id', node_id, 'attributes', attr
        return attr
    def bounds(self, elems, attr):
        # b [0,I]
        lb, ub = elems[1][1:-1].replace('I','inf').split(',')
        attr[NodeAttr.bounds] = Bounds(float(lb), float(ub))
    def var_number(self, elems, attr):
        # V 2
        attr[NodeAttr.var_num] = int(elems[1])
    def constant(self, elems, attr):
        # C 0.1
        attr[NodeAttr.number] = float(elems[1])
    def d_term(self, elems, attr):
        # d 0.1; lambda*x1 + d or d/(lambda*x1)
        attr[NodeAttr.d] = float(elems[1])
    def n_term(self, elems, attr):
        # n 3; (lamba*x)^n
        attr[NodeAttr.n] = int(elems[1])
    def sum(self, elems, attr):
        attr[NodeAttr.operation] = '+'
    def mul(self, elems, attr):
        attr[NodeAttr.operation] = '*'
    def div(self, elems, attr):
        attr[NodeAttr.operation] = '/'
    def exp(self, elems, attr):
        attr[NodeAttr.operation] = 'exp'
    def log(self, elems, attr):
        attr[NodeAttr.operation] = 'log'
    def unimplemented(self, elems, attr):
        print 'Unimplemented: ', elems

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
            if   NodeAttr.number in data:
                data[disp] = str(data[NodeAttr.number])
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
