from __future__ import print_function

__all__ = [ 'Problem' ]

from collections import OrderedDict
import numpy as np
import networkx as nx
from . import dag_util as du
from nodes.attributes import NodeAttr
from networkx.algorithms.dag import ancestors, topological_sort
import ordering.csr_utils as util
import six

# TODO: - In the simplifier, reconstruct exact integer powers (e.g. x**3)
#       - dbg_info: constraint types 
#       - color given nodes on the plot yellow (selected ones for debugging,
#             sinks, def var nodes, etc.)

class Problem:
    '''Use read_problem from parsers.dag_parser to create an instance of 
    Problem. Factory function is not provided here to avoid cyclic imports.
    '''
    def __init__(self):
        self.dag = nx.DiGraph()
        self.con_ends_num = { } # con sink node -> con num (in AMPL)
        self.con_num_name = { } # con num -> con name (in AMPL)
        self.var_num_name = { } # var num (in AMPL) -> var name (in AMPL)
        self.var_node_ids = set() # initially all var node ids
        self.var_num_id   = { }   # only base vars: var num -> smallest node id
        self.base_vars   = { }    # base var node id -> var num
        self.defined_vars = set() # node ids after elimination
        self.model_name   = '(none)'
        self.nvars        = int(-1) # number of variables
        self.con_top_ord  = { } # con sink node -> con topological order
        self.ncons  = None
        self.nzeros = None        
        self.refsols      = [ ]

################################################################################
#            The rest of this module is meant to be private

def setup(prob):
    du.dbg_info(prob.dag)
    prob.dag.graph['name'] = prob.model_name
    setup_constraint_names(prob)
    setup_nodes(prob)
    # for base vars: setup_nodes() only stores the smallest id in var_num_id
    prob.base_vars = { v : k for k, v in six.iteritems(prob.var_num_id) }
    # The followings are simplifications
    #-------------------------------------------
    # remove bogus base var aliasing
    prob.var_node_ids.difference_update(six.iterkeys(prob.base_vars))
    # the rest assumes that base var nodes are no longer in var_node_ids!
    remove_var_aliases(prob)
    #-------------------------------------------
    # nl2dag erroneously turns defined vars into constraints
    reconstruct_CSEs(prob)
    remove_unused_def_vars(prob)
    remove_identity_sum_nodes(prob)
    remove_def_var_aliasing_another_node(prob)
    #-------------------------------------------
    collect_constraint_topological_orders(prob)
    #-------------------------------------------
    # TODO pretty print constraints
    #-------------------------------------------
    du.dbg_info(prob.dag, lambda : dbg_problem_statistics(prob))

def setup_constraint_names(prob):
    for node_id, con_num in six.iteritems(prob.con_ends_num):
        d = prob.dag.node[node_id]
        d[NodeAttr.name] = prob.con_num_name.get(con_num, '_c%d' % con_num)
        d[NodeAttr.con_num] = con_num

def setup_nodes(prob):
    for node_id, d in prob.dag.nodes_iter(data=True):
        d[NodeAttr.type].setup(node_id, d, prob)

def remove_var_aliases(prob):
    var_aliases = get_var_aliases(prob)
    dag = prob.dag
    for aliasing_var_node, base_var_node in six.iteritems(var_aliases):
        du.assert_source(dag, base_var_node)
        du.reparent(dag, base_var_node, aliasing_var_node)
    # difference_update is -=
    prob.var_node_ids.difference_update(six.iterkeys(var_aliases))

def get_var_aliases(prob):
    var_aliases = { } # alias node id -> base var aliased
    # this new dict is needed as we remove nodes from the dag as we reparent
    for node_id, var_num in du.itr_var_num(prob.dag, prob.var_node_ids):
        if var_num < prob.nvars and node_id not in prob.base_vars:
            base_var_node = prob.var_num_id[var_num]
            var_aliases[node_id] = base_var_node
    return var_aliases

def reconstruct_CSEs(prob):
    con_ends = get_unnamed_constraints(prob)
    du.assert_CSE_defining_constraints(prob.dag, con_ends, prob.base_vars)
    eliminate_def_vars(prob, con_ends)
    remove_CSE_aliases(prob, con_ends)

def get_unnamed_constraints(prob):
    return [ n for n in prob.con_ends_num   \
                     if prob.con_ends_num[n] not in prob.con_num_name ]

def eliminate_def_vars(prob, con_ends):
    #  defined variable := its defining constraint
    print('cons: ', sorted(six.iterkeys(prob.con_ends_num)))
    for sum_node_id in con_ends:
        var_node_id = sum_node_id + 1 # already asserted that it is true
        du.reverse_edge_to_get_def_var(prob.dag, sum_node_id, var_node_id)
        prob.con_ends_num.pop(sum_node_id) # safe: iterating on a copy
        prob.defined_vars.add(var_node_id)
    print('cons: ', sorted(six.iterkeys(prob.con_ends_num)))

def remove_CSE_aliases(prob, con_ends):
    dag = prob.dag
    # var_num -> defining node
    var_num_def_node = { dag.node[n+1][NodeAttr.var_num] : n+1 \
                             for n in con_ends }
    print('defined vars, var num -> defining node:\n  %s\n'%var_num_def_node)
    var_node_ids = prob.var_node_ids
    du.assert_vars_are_CSEs(dag, var_node_ids, var_num_def_node)
    var_aliases = var_node_ids - prob.defined_vars
    for var_node in var_aliases:
        var_num = dag.node[var_node][NodeAttr.var_num]
        def_node = var_num_def_node[var_num]
        assert def_node!=var_node, '%d, %d' % (def_node, var_node)
        du.reparent(dag, def_node, var_node)
    prob.var_node_ids.clear() # after eliminating the CSEs, we don't need it

def remove_unused_def_vars(prob):
    dag = prob.dag
    removed = [ ]
    for n in du.itr_sinks(dag, prob.defined_vars):
        deps = ancestors(dag, n)
        deps.add(n)
        con_dag = dag.subgraph(deps)
        reverse_order = topological_sort(con_dag, reverse=True)
        removed = delete_sinks_recursively(dag, reverse_order)
    print('Unused nodes:', removed)
    prob.defined_vars.difference_update(removed)

def delete_sinks_recursively(dag, reverse_order):
    removed = [ ]
    for n in reverse_order:
        if du.is_sink(dag, n):
            removed.append(n)
            du.remove_node(dag, n)
    return removed

def remove_identity_sum_nodes(prob):
    dag = prob.dag
    to_delete = get_identity_sum_nodes(dag)
    for n, (pred, succ) in six.iteritems(to_delete):
        du.remove_node(dag, n)
        d = dag.node[succ] # may need it to transfer var_num to new parent
        du.reparent(dag, pred, succ)
        update_defined_var_bookkeeping(prob, pred, succ, d)

def get_identity_sum_nodes(dag):
    # SISO sum nodes with in and out edge weight == 1 and d_term == 0
    # This function could be moved to dag_util?
    remove = { }
    for n in du.itr_siso_sum_nodes(dag):
        pred = du.get_single_pred(dag, n)
        succ = du.get_single_succ(dag, n)
        in_mul  = dag.edge[pred][n]['weight']
        out_mul = dag.edge[n][succ]['weight']
        d = dag.node[n]
        d_term  = d.get(NodeAttr.d_term, 0.0)
        assert NodeAttr.bounds not in d, d
        if in_mul==1.0 and out_mul==1.0 and d_term==0.0:
            remove[n] = (pred, succ)
    # We delete moving backwards, otherwise we may delete the node of a
    # later dependence (e.g. JacobsenTorn.dag)
    to_delete = OrderedDict(sorted(remove.items(), key=lambda t: -t[0]))
    print('identity sum nodes:', to_delete)
    return to_delete

def update_defined_var_bookkeeping(prob, new_def_var, old_def_var, d):
    if old_def_var in prob.defined_vars:
        # move defined var from old_def_var to new_def_var
        prob.defined_vars.remove(old_def_var)
        # transfer var_num; if new_def_var is already a defined var
        # then keep the smaller var_num
        var_num = d[NodeAttr.var_num]
        d_pred  = prob.dag.node[new_def_var]
        du.add_keep_smaller_value(d_pred, NodeAttr.var_num, var_num)

def remove_def_var_aliasing_another_node(prob):
    dag = prob.dag
    to_delete = get_def_var_aliasing_another_node(prob)
    for n, pred in six.iteritems(to_delete):
        d = dag.node[n]  # need it to transfer var_num to new parent
        dag.remove_edge(pred, n)
        du.reparent(dag, pred, n)
        update_defined_var_bookkeeping(prob, pred, n, d)

def get_def_var_aliasing_another_node(prob):
    # def var_node with a single input, edge weight one and no d_term
    dag = prob.dag
    to_delete = { }
    for n in du.itr_single_input_nodes(dag, prob.defined_vars):
        pred = du.get_single_pred(dag, n)
        in_mul  = dag.edge[pred][n]['weight']
        d = dag.node[n]
        d_term  = d.get(NodeAttr.d_term, 0.0)
        if in_mul==1.0 and d_term==0.0:
            to_delete[n] = pred
    print('var nodes just aliasing:', to_delete)
    return to_delete

def collect_constraint_topological_orders(prob):
    dag = prob.dag
    for sink_node in prob.con_ends_num:
        dependencies = ancestors(dag, sink_node)
        dependencies.add(sink_node)
        con_dag = dag.subgraph(dependencies)
        eval_order = du.deterministic_topological_sort(con_dag)
        prob.con_top_ord[sink_node] = eval_order
    prob.ncons = len(prob.con_ends_num)
    set_nzeros(prob)

def set_nzeros(prob):
    nzeros = 0
    sink_nodes = (n for n in prob.dag if du.is_sink(prob.dag, n))
    for n in sink_nodes:
        nzeros += len( base_var_nums_in_con(prob, n) )
    prob.nzeros = nzeros

def base_var_nums_in_con(prob, sink_node): 
    var_nums = (prob.base_vars[n] for n in prob.con_top_ord[sink_node] \
                                   if n in prob.base_vars) 
    return sorted(var_nums)

# Not exactly the ideal place for this but couldn't find a better one
def crosscheck_sparsity_pattern(prob, jacobian):
    check_shape(prob, jacobian)
    checked = [False] * jacobian.shape[0]
    for con_num, n in du.itr_sink_con_num_nodeid(prob.dag):
        base_vars = np.array(base_var_nums_in_con(prob, n), np.int32)
        cols = util.cols_in_row(jacobian, con_num)
        assert np.all(cols==base_vars)
        checked[con_num] = True
    assert all(checked)

def check_shape(prob, jacobian):
    nrows = jacobian.shape[0]
    assert nrows == prob.ncons
    assert prob.nvars == jacobian.shape[1]

def crosscheck_names(prob, row_names, col_names):
    assert set(row_names) <= set(six.itervalues(prob.con_num_name))
    assert set(col_names) <= set(six.itervalues(prob.var_num_name))
    assert len(row_names) == prob.ncons
    assert len(col_names) == prob.nvars

def dbg_show_node_types(dag):
    for n in dag:
        print('%d  %s' % (n, du.get_pretty_type_str(dag, n)))
    print()
    
def dbg_problem_statistics(prob):
    fmt = 'Constraints: %d, variables: %d, nonzeros: %d'
    print(fmt % (prob.ncons, prob.nvars, prob.nzeros))
    print('Number of reference solutions:', len(prob.refsols))
