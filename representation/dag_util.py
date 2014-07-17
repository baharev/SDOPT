from __future__ import print_function
from array import array
import networkx as nx
import nodes
from nodes.attributes import NodeAttr
from matplotlib import pyplot as plt

def dbg_info(dag):
    print()
    # TODO Why does this crash?
    #print('Is connected?', nx.is_connected(dag.to_undirected()))
    print('Is DAG?', nx.is_directed_acyclic_graph(dag))
    print('Weakly connected components:', nx.number_weakly_connected_components(dag))
    print('Nodes:', nx.number_of_nodes(dag), 'edges:', nx.number_of_edges(dag))

def is_leaf(dag, node_id):
    return len(dag.pred[node_id])==0

# TODO Would be a nice addition to nx
def iter_attr(G, nbunch, name):
    for n in nbunch:
        yield n, G.node[n][name]

def itr_var_num(G, var_node_ids):
    for n in var_node_ids:
        yield n, G.node[n][NodeAttr.var_num]

def plot(dag):
    node_labels = nx.get_node_attributes(dag, NodeAttr.display)
    edge_labels = nx.get_edge_attributes(dag, 'weight')

    # TODO Why does this crash?
    #dag_copy = dag.to_directed()
    #for _, d in dag_copy.nodes_iter(data=True):
    for _, d in dag.nodes_iter(data=True):
        d.clear()
    # TODO Why does this try to copy attributes that it cannot?
    positions = nx.graphviz_layout(dag, prog='dot')

    nx.draw_networkx_edge_labels(dag, positions, edge_labels, rotate=False)
    nx.draw_networkx(dag, pos=positions, labels=node_labels, node_size=800)
    mng = plt.get_current_fig_manager()
    mng.resize(1865,1025)
    plt.show()

def add_edge(dag, src, dest, mult):
    dag.add_edge(src, dest, weight=mult)
    dag.node[dest].setdefault(NodeAttr.input_ord, array('l')).append(src)

# FIXME Respect children order! Wrap: add_edge, remove_node, remove_edge,
#                                     reverse_edge
def reparent(dag, new_parent, node_to_del, new_parent_is_leaf=True):
    # delete node_to_del and connect all children to new_parent, with edge dict;
    # update each child's input order array to contain the new parent
    out_edges = dag.edge[node_to_del]
    # print()
    # print(new_parent, node_to_del, out_edges)
    assert_leaf(dag, node_to_del)
    if new_parent_is_leaf:
        assert_leaf(dag, new_parent)
    dag.remove_node(node_to_del)
    for child_id, edge_dict in out_edges.iteritems():
        dag.add_edge(new_parent, child_id, edge_dict)
        update_child_input_ord(dag, new_parent, node_to_del, child_id)

def update_child_input_ord(dag, new_parent, node_to_del, child_id):
    in_ord = dag.node[child_id][NodeAttr.input_ord]
    replace(in_ord, node_to_del, new_parent)

def reverse_edge_to_get_def_var():
    pass

def replace(arr, old_value, new_value):
    for index, item in enumerate(arr):
        if item==old_value:
            arr[index] = new_value

def assert_leaf(dag, node_id):
    assert is_leaf(dag, node_id), 'node %d %s' % (node_id, dag.node[node_id])

def assert_var_num_equals_node_id_for_named_vars(dag, var_num_name):
    for var_num in var_num_name:
        assert var_num in dag, 'var_num %d should be a node id' % var_num
        d = dag.node[var_num]
        assert d.has_key(NodeAttr.var_num), 'expected a var node,  found %s' % d
        assert d.has_key(NodeAttr.name),    'expected a named var, found %s' % d
        var_num_on_node = d[NodeAttr.var_num]
        assert var_num_on_node==var_num, 'var_num on node %d, expected %d; %s' % \
                                         (var_num_on_node, var_num, d)

# FIXME When reversing edge, the rhs should be changed accordingly
#       lambda * <var node> + <some sum> + d = bounds
#       <var node> = (-1/lambda) * ( <some sum> + d - bounds)
#       Apparently: reverse edge, update multiplier to -1/lambda,
#       d := d - bounds, delete bounds, and evaluate sum node as before
def assert_CSE_defining_constraints(dag, con_ends, named_vars):
    # A constraint (sum) node immediately followed by an unnamed var node; with
    # an edge from the var node to the sum node; and the rhs of the constraint
    # is a real number, not an interval.
    # Basically: lambda * <var node> + <some sum> + d = bounds
    # <N> c 20 145
    # <145> b [0,0]: +
    # <146> V 20
    # <E> 145 146 -1
    for n in con_ends:
        d = dag.node[n]
        assert d[NodeAttr.type]==nodes.sum_node,'expected a sum_node, found: %s' % d
        assert NodeAttr.bounds in d,'Should have bounds, node: %s' % d
        lb, ub = d[NodeAttr.bounds]
        assert lb==ub,'rhs expected to be a constant, node: %s' % d
        assert n+1 in dag,'expected a var node; not CSE defining constraint: %s' % d
        def_var = dag.node[n+1]
        assert def_var[NodeAttr.type]==nodes.var_node, \
                                 'expected a var_node, found: %s' % def_var
        assert n+1 not in named_vars,'expected an unnamed var, found %s' % def_var
        assert n in dag.edge[n+1],'Nodes not connected:\n %s \n %s'%(d,def_var)

def assert_vars_are_CSEs(dag, var_node_ids, var_num_def_node):
        for var_node in var_node_ids:
            var_num = dag.node[var_node][NodeAttr.var_num]
            assert var_num in var_num_def_node,'var_num: %d' % var_num

