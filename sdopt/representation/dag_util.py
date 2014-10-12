from __future__ import print_function
from array import array
from collections import defaultdict
import networkx as nx
import six
from ..nodes.types import is_sum_node, is_var_node
from ..nodes.attributes import NodeAttr

def dbg_info(dag, optional_callable=None):
    print('-------------------------------------------------------------------')
    if optional_callable: optional_callable()
    print('Nodes: %d, edges: %d'%(dag.number_of_nodes(),dag.number_of_edges()) )
    print('Is DAG?', nx.is_directed_acyclic_graph(dag))
    nwcc = nx.number_weakly_connected_components(dag)
    print('Weakly connected components:', nwcc)
    dbg_pprint_source_sink_types(dag)
    print('-------------------------------------------------------------------')
    
def dbg_pprint_source_sink_types(dag):
    source_types = group_node_ids_by_kind(itr_sourcetype_nodeid(dag))
    sink_types   = group_node_ids_by_kind(itr_sinktype_nodeid(  dag))
    print('Sources:')
    dbg_pprint_kind_nodeids(source_types)
    print('Sinks:')
    dbg_pprint_kind_nodeids(sink_types)
    
def dbg_pprint_kind_nodeids(kind_nodeids):
    for kind, nodeids in kind_nodeids.items():
        count = len(nodeids)
        print(' ', kind, nodeids if count <= 20 else '', '(count=%d)' % count)

def group_node_ids_by_kind(itr_kind_nodeid_pairs):
    types = defaultdict(list)
    for kind, n in itr_kind_nodeid_pairs:
        types[kind].append(n)
    return types

def itr_sourcetype_nodeid(dag):
    return ((get_pretty_type_str(dag, n), n) for n in dag if is_source(dag, n))

def itr_sinktype_nodeid(dag):
    return ((get_pretty_type_str(dag, n), n) for n in dag if is_sink(dag, n))

def itr_sink_con_num_nodeid(dag):
    '(con_num, node_id) for sinks only; assumes that the problem has been setup'
    return ((dag.node[n][NodeAttr.con_num], n) for n in dag if is_sink(dag, n))

def is_source(dag, node_id):
    return len(dag.pred[node_id])==0

def is_sink(dag, node_id):
    return len(dag.succ[node_id])==0

# FIXME Part of the dispatching mechanism, revise!
def get_pretty_type_str(dag, n):
    return dag.node[n][NodeAttr.type] + '_node'

# TODO Would be a nice addition to nx
def iter_attr(G, nbunch, name):
    for n in nbunch:
        yield n, G.node[n][name]

def itr_var_num(G, var_node_ids):
    for n in var_node_ids:
        yield n, G.node[n][NodeAttr.var_num]

def itr_sinks(dag, nbunch):
    return (n for n in nbunch if is_sink(dag, n))

def itr_sum_nodes(dag):
    return (n for n in dag if is_sum_node(dag.node[n]))

def itr_siso_sum_nodes(dag):
    return (n for n in itr_sum_nodes(dag) if  len(dag.pred[n])==1
                                          and len(dag.succ[n])==1 )

def itr_single_input_nodes(dag, node_ids):
    return (n for n in node_ids if len(dag.pred[n])==1)

def get_single_pred(dag, n):
    return next(iter(dag.pred[n]))

def get_single_succ(dag, n):
    return next(iter(dag.succ[n]))

def deterministic_topological_sort(dag):
    # This function is stolen from networkx.algorithms.dag.topological_sort
    # made the returned order deterministic by pre-sorting the nodes by their ID
    seen = set()
    order = []
    explored = set()
    nbunch = sorted(dag.nodes_iter())                               # <-- SORTED
    for v in nbunch:     # process all vertices in G
        if v in explored:
            continue
        fringe = [v]   # nodes yet to look at
        while fringe:
            w = fringe[-1]  # depth first search
            if w in explored: # already looked down this branch
                fringe.pop()
                continue
            seen.add(w)     # mark as seen
            # Check successors for cycles and for new nodes
            new_nodes = []
            for n in sorted(six.iterkeys(dag[w])):                  # <-- SORTED
                if n not in explored:
                    if n in seen: #CYCLE !!
                        raise nx.NetworkXUnfeasible("Graph contains a cycle.")
                    new_nodes.append(n)
            if new_nodes:   # Add new_nodes to fringe
                fringe.extend(new_nodes)
            else:           # No new nodes so w is fully explored
                explored.add(w)
                order.append(w)
                fringe.pop()    # done considering this node
    return list(reversed(order))

def plot(dag):
    from matplotlib import pyplot as plt
    
    node_labels = nx.get_node_attributes(dag, NodeAttr.display)
    edge_labels = nx.get_edge_attributes(dag, 'weight')

    dag_copy = dag.to_directed()
    for _, d in dag_copy.nodes_iter(data=True):
        d.clear()
    # FIXME Why does this try to copy attributes that it cannot?
    positions = nx.graphviz_layout(dag_copy, prog='dot')

    nx.draw_networkx_edge_labels(dag, positions, edge_labels, rotate=False)
    nx.draw_networkx(dag, pos=positions, labels=node_labels, node_size=800)
    mng = plt.get_current_fig_manager()
    mng.resize(1865,1025)
    plt.show()

################################################################################
# Respect children order: add_edge, remove_node, remove_edge, reverse_edge
################################################################################
def add_edge(dag, src, dest, attr_dict):
    dag.add_edge(src, dest, attr_dict)
    dag.node[dest].setdefault(NodeAttr.input_ord, array('l')).append(src)

def reparent(dag, new_parent, node_to_del):
    # delete node_to_del and connect all children to new_parent, with edge dict;
    # update each child's input order array to contain the new parent
    out_edges = dag.edge[node_to_del]
    # In case we already deleted the new parent in a previous round; reparent
    # would insert it again and that node would have an empty dict
    assert new_parent in dag, '{}, {}'.format(new_parent, node_to_del)
    assert_source(dag, node_to_del)
    remove_node(dag, node_to_del)
    for child_id, edge_dict in six.iteritems(out_edges):
        dag.add_edge(new_parent, child_id, edge_dict)
        replace(dag.node[child_id][NodeAttr.input_ord], node_to_del, new_parent)

def remove_node(dag, n):
    d = dag.node[n]
    assert NodeAttr.bounds not in d, d
    dag.remove_node(n)

def reverse_edge_to_get_def_var(dag, sum_node_id, var_node_id):
    # lambda * <var node> + <lin. comb.> + d = bounds
    #   node id:   n+1            n
    # <var node> = (-1/lambda) * ( <lin. comb.> + d - bounds)
    #
    # add the new reversed edge
    e = dag[var_node_id][sum_node_id]
    e['weight'] = -1.0/e['weight']
    add_edge(dag, sum_node_id, var_node_id, e)
    # drop the old edge
    dag.remove_edge(var_node_id, sum_node_id)
    # update the sum node
    d = dag.node[sum_node_id]
    # d_term -= rhs
    d_term = d.get(NodeAttr.d_term, 0.0) - d[NodeAttr.bounds].l# l == u == rhs
    d[NodeAttr.d_term] = d_term                                #already asserted
    del d[NodeAttr.bounds]
    d[NodeAttr.input_ord].remove(var_node_id)

def replace(arr, old_value, new_value):
    for index, item in enumerate(arr):
        if item==old_value:
            arr[index] = new_value

def add_keep_smaller_value(mapping, key, value):
    # mapping[key]=value BUT if key is already present, keeps smaller value
    old_value = mapping.get(key,  value)
    mapping[key] = min(old_value, value)

def assert_source(dag, node_id):
    assert is_source(dag, node_id), 'node %d %s' % (node_id, dag.node[node_id])

def assert_CSE_defining_constraints(dag, con_ends, base_vars):
    # A constraint (sum) node immediately followed by a defined var node; with
    # an edge from the var node to the sum node; and the rhs of the constraint
    # is a real number, not an interval.
    # Basically: lambda * <var node> + <some sum> + d = bounds
    # <N> c 20 145
    # <145> b [0,0]: +
    # <146> V 20
    # <E> 145 146 -1
    for n in con_ends:
        # check the sum_node
        d = dag.node[n]
        assert is_sum_node(d), 'expected a sum_node, found: %s' % d
        assert NodeAttr.bounds in d,'Should have bounds, node: %s' % d
        lb, ub = d[NodeAttr.bounds]
        assert lb==ub,'rhs expected to be a constant, node: %s' % d
        # check the var_node
        assert n+1 in dag,'expected a var_node; not CSE defining constraint: %s'%d
        def_var = dag.node[n+1]
        assert is_var_node(def_var), 'expected a var_node, found: %s' % def_var
        assert n+1 not in base_vars,'expected a defined var, found %s' % def_var
        assert NodeAttr.bounds not in def_var, \
                            'CSEs must not have bounds, found\n  %s' % def_var
        assert n in dag.edge[n+1],'Nodes not connected:\n %s \n %s'%(d,def_var)

def assert_vars_are_CSEs(dag, var_node_ids, var_num_def_node):
        for var_node in var_node_ids:
            var_num = dag.node[var_node][NodeAttr.var_num]
            assert var_num in var_num_def_node,'var_num: %d' % var_num

