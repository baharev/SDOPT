from __future__ import print_function
import networkx as nx
import dag_util as du
from nodes.attributes import NodeAttr
from networkx.algorithms.dag import ancestors, topological_sort
from nodes.pprinter import pprint_one_constraint

# TODO: - Put solution to tracepoint in AMPL automatically, maybe .sol file to
#             converter?
#       - Clean up test, improve coverage
#       - import sparsity pattern from AMPL
#       - dbg_info, show nvars, ncons, cons type, num of ref sols, model name
#       - report / fix plotting bugs
#       - code generation for AD and constraint propagation
#       - Where are the var bounds? -> For named ones, at the definition,
#                                      CSEs *must* not have any, assert inserted
#       - color given nodes on the plot yellow (selected ones for debugging,
#             sinks, def var nodes, etc.)
#       - try to get defined variable names
#
#       - defined var topological orders should be stored as well
#         not clear how to avoid recomputations, maybe removing
#         aliases wasn't the best idea? -> Cut corners, ignore inefficiencies
#                                          for now; def vars won't be that
#                                          common anyway with connected units

class Problem:

    def __init__(self):
        self.dag = nx.DiGraph()
        self.con_ends_num = { } # con sink node -> con num (in AMPL)
        self.con_num_name = { } # con num -> con name (in AMPL)
        self.var_num_name = { } # var num (in AMPL) -> var name (in AMPL)
        self.var_node_ids = set()
        self.defined_vars = set() # node ids after elimination
        self.model_name   = '(none)'
        self.nvars        = int(-1) # number of variables
        self.con_top_ord  = { } # con sink node -> con topological order
        self.refsols      = [ ]

    def setup(self):
        dag = self.dag
        du.dbg_info(dag)
        dag.graph['name'] = self.model_name
        self.setup_constraint_names()
        self.setup_nodes()
        # The followings are simplifications
        #-------------------------------------------
        # remove bogus named var aliasing
        du.assert_var_num_equals_node_id_for_named_vars(dag, self.var_num_name)
        # remove named vars from var_node_ids, we asserted just above that
        # they are nodes 0:nvars
        self.var_node_ids.difference_update( xrange(self.nvars) )
        # the rest assumes that named var nodes are no longer in var_node_ids!
        self.remove_var_aliases()
        #-------------------------------------------
        # nl2dag erroneously turns defined vars into constraints
        self.reconstruct_CSEs()
        self.remove_unused_def_vars()
        self.remove_identity_sum_nodes()
        self.remove_def_var_aliasing_another_node()
        #-------------------------------------------
        self.collect_constraint_topological_orders()
        #-------------------------------------------
        self.pprint_constraints()
        #-------------------------------------------
        du.dbg_info(dag)

    def setup_constraint_names(self):
        for node_id, con_num in self.con_ends_num.iteritems():
            d = self.dag.node[node_id]
            d[NodeAttr.name] = self.con_num_name.get(con_num, '_c%d' % con_num)
            d[NodeAttr.con_num] = con_num

    def setup_nodes(self):
        for node_id, d in self.dag.nodes_iter(data=True):
            d[NodeAttr.type].setup(node_id, d, self)

    def remove_var_aliases(self):
        var_aliases = self.get_var_aliases()
        for node_id, var_num in var_aliases.iteritems():
            du.reparent(self.dag, var_num, node_id)
        self.var_node_ids -= var_aliases.viewkeys()

    def get_var_aliases(self):
        var_aliases = { } # alias node id -> named var aliased
        # this new dict is needed as we remove nodes from the dag as we reparent
        nvars = self.nvars
        for node_id, var_num in du.itr_var_num(self.dag, self.var_node_ids):
            if var_num < nvars: # true if referencing a named var; false for CSE
                var_aliases[node_id] = var_num
        return var_aliases

    def reconstruct_CSEs(self):
        con_ends = self.get_unnamed_constraints()
        dag = self.dag
        du.assert_CSE_defining_constraints(dag, con_ends, self.var_num_name)
        self.eliminate_def_vars(con_ends)
        self.remove_CSE_aliases(con_ends)

    def get_unnamed_constraints(self):
        return [ n for n in self.con_ends_num   \
                         if self.con_ends_num[n] not in self.con_num_name ]

    def eliminate_def_vars(self, con_ends):
        #  defined variable := its defining constraint
        print('cons: ', sorted(self.con_ends_num.viewkeys()))
        dag = self.dag
        for sum_node_id in con_ends:
            var_node_id = sum_node_id + 1 # already asserted that it is true
            du.reverse_edge_to_get_def_var(dag, sum_node_id, var_node_id)
            self.con_ends_num.pop(sum_node_id) # safe: iterating on a copy
            self.defined_vars.add(var_node_id)
        print('cons: ', sorted(self.con_ends_num.viewkeys()))

    def remove_CSE_aliases(self, con_ends):
        dag = self.dag
        # var_num -> defining node
        var_num_def_node = { dag.node[n+1][NodeAttr.var_num] : n+1 \
                                 for n in con_ends }
        print('defined vars, var num -> defining node:\n  %s\n'%var_num_def_node)
        var_node_ids = self.var_node_ids
        du.assert_vars_are_CSEs(dag, var_node_ids, var_num_def_node)
        var_aliases = var_node_ids - self.defined_vars
        for var_node in var_aliases:
            var_num = dag.node[var_node][NodeAttr.var_num]
            def_node = var_num_def_node[var_num]
            assert def_node!=var_node, '%d, %d' % (def_node, var_node)
            du.reparent(dag, def_node, var_node, new_parent_is_source=False)
        self.var_node_ids.clear() # after eliminating the CSEs, we don't need it

    def remove_unused_def_vars(self):
        dag = self.dag
        removed = [ ]
        for n in du.itr_sinks(dag, self.defined_vars):
            deps = ancestors(dag, n)
            deps.add(n)
            con_dag = dag.subgraph(deps)
            reverse_order = topological_sort(con_dag, reverse=True)
            removed = self.delete_sinks_recursively(reverse_order)
        print('Unused nodes:', removed)
        self.defined_vars.difference_update(removed)

    def delete_sinks_recursively(self, reverse_order):
        dag = self.dag
        removed = [ ]
        for n in reverse_order:
            if du.is_sink(dag, n):
                removed.append(n)
                du.remove_node(dag, n)
        return removed

    def remove_identity_sum_nodes(self):
        dag = self.dag
        to_delete = self.get_identity_sum_nodes()
        for n, (pred, succ) in to_delete.iteritems():
            du.remove_node(dag, n)
            d = dag.node[succ] # may need it to transfer var_num to new parent
            du.reparent(dag, pred, succ, new_parent_is_source=False)
            self.update_defined_var_bookkeeping(pred, succ, d)

    def get_identity_sum_nodes(self):
        # SISO sum nodes with in and out edge weight == 1 and d_term == 0
        dag = self.dag
        to_delete = { }
        for n in du.itr_siso_sum_nodes(dag):
            pred = dag.pred[n].keys()[0]
            succ = dag.succ[n].keys()[0]
            in_mul  = dag.edge[pred][n]['weight']
            out_mul = dag.edge[n][succ]['weight']
            d = dag.node[n]
            d_term  = d.get(NodeAttr.d_term, 0.0)
            assert NodeAttr.bounds not in d, d
            if in_mul==1.0 and out_mul==1.0 and d_term==0.0:
                to_delete[n] = (pred, succ)
        print('identity sum nodes:', to_delete)
        return to_delete

    def update_defined_var_bookkeeping(self, new_def_var, old_def_var, d):
        if old_def_var in self.defined_vars:
            # move defined var from old_def_var to new_def_var
            self.defined_vars.remove(old_def_var)
            self.defined_vars.add(new_def_var)
            # transfer var_num; if new_def_var is already a defined var
            # then keep the smaller var_num
            var_num = d[NodeAttr.var_num]
            d_pred  = self.dag.node[new_def_var]
            old_var_num = d_pred.get(NodeAttr.var_num, var_num)
            d_pred[NodeAttr.var_num] = min(var_num, old_var_num)

    def remove_def_var_aliasing_another_node(self):
        dag = self.dag
        to_delete = self.get_def_var_aliasing_another_node()
        for n, pred in to_delete.iteritems():
            d = dag.node[n]  # need it to transfer var_num to new parent
            dag.remove_edge(pred, n)
            du.reparent(dag, pred, n, new_parent_is_source=False)
            self.update_defined_var_bookkeeping(pred, n, d)

    def get_def_var_aliasing_another_node(self):
        # def var_node with a single input, edge weight one and no d_term
        dag = self.dag
        to_delete = { }
        for n in du.itr_single_input_nodes(dag, self.defined_vars):
            pred = dag.pred[n].keys()[0]
            in_mul  = dag.edge[pred][n]['weight']
            d = dag.node[n]
            assert NodeAttr.bounds not in d, d
            d_term  = d.get(NodeAttr.d_term, 0.0)
            if in_mul==1.0 and d_term==0.0:
                to_delete[n] = pred
        print('var nodes just aliasing:', to_delete)
        return to_delete

    def collect_constraint_topological_orders(self):
        dag = self.dag
        for sink_node in self.con_ends_num:
            dependecies = ancestors(dag, sink_node)
            dependecies.add(sink_node)
            con_dag = dag.subgraph(dependecies)
            eval_order = du.deterministic_topological_sort(con_dag)
            self.con_top_ord[sink_node] = eval_order

    def pprint_constraints(self):
        for sink_node in self.con_ends_num:
            eval_order = self.con_top_ord[sink_node]
            con_num = self.con_ends_num[sink_node]
            con_dag = self.dag.subgraph(eval_order)
            nvars   = self.nvars
            pprint_one_constraint(sink_node, con_num, con_dag, eval_order, nvars)

    def dbg_show_node_types(self):
        dag = self.dag
        for n in dag:
            print('%d  %s' % (n, du.get_pretty_type_str(dag, n)))
        print()

