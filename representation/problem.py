from __future__ import print_function
import weakref
import networkx as nx
import dag_util as du
from nodes.attributes import NodeAttr
from networkx.algorithms.dag import ancestors, topological_sort

# TODO: dbg_info, show nvars, ncons, cons type
#       parse <H>, contains starting point
#       import sparsity pattern from AMPL
#       try to get defined variable names

class Problem:

    def __init__(self):
        self.dag = nx.DiGraph()
        self.con_ends_num = { } # con sink node -> con num (in AMPL)
        self.con_num_name = { } # con num -> con name (in AMPL)
        self.var_num_name = { } # var num (in AMPL) -> var name (in AMPL)
        self.var_node_ids = set()
        self.defined_vars = [ ] # after elimination, only for debugging for now
        self.model_name   = '(none)'
        self.nvars        = int(-1) # number of variables
        self.con_top_ord  = { } # con sink node -> con topological order

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
        #-------------------------------------------
        self.remove_unused_def_vars()
        #-------------------------------------------
        self.collect_constraint_topological_orders()
        #-------------------------------------------
        self.print_constraints()

    def setup_constraint_names(self):
        for node_id, con_num in self.con_ends_num.iteritems():
            d = self.dag.node[node_id]
            d[NodeAttr.name] = self.con_num_name.get(con_num, '_c%d' % con_num)
            d[NodeAttr.con_num] = con_num

    def setup_nodes(self):
        for node_id, d in self.dag.nodes_iter(data=True):
            d[NodeAttr.dag] = weakref.ref(self.dag)
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
        return

    def get_unnamed_constraints(self):
        return [ n for n in self.con_ends_num   \
                         if self.con_ends_num[n] not in self.con_num_name ]

    def eliminate_def_vars(self, con_ends):
        #  defined variable := its defining constraint
        print('cons: ', sorted(self.con_ends_num.viewkeys()))
        dag = self.dag
        for sum_node_id in con_ends:
            var_node_id = sum_node_id + 1
            du.reverse_edge_to_get_def_var(dag, sum_node_id, var_node_id)
            self.con_ends_num.pop(sum_node_id) # safe: iterating on a copy
            self.defined_vars.append(var_node_id)
        print('cons: ', sorted(self.con_ends_num.viewkeys()))

    def remove_CSE_aliases(self, con_ends):
        dag = self.dag
        # var_num -> defining node
        var_num_def_node = { dag.node[n+1][NodeAttr.var_num] : n+1 \
                                 for n in con_ends }
        print('defined vars, var num -> defining node:\n  %s\n'%var_num_def_node)
        var_node_ids = self.var_node_ids
        du.assert_vars_are_CSEs(dag, var_node_ids, var_num_def_node)
        var_aliases = var_node_ids - set(self.defined_vars)
        for var_node in var_aliases:
            var_num = dag.node[var_node][NodeAttr.var_num]
            def_node = var_num_def_node[var_num]
            assert def_node!=var_node, '%d, %d' % (def_node, var_node)
            du.reparent(dag, def_node, var_node, new_parent_is_source=False)
        self.var_node_ids.clear() # after eliminating the CSEs, we don't need it

    def remove_unused_def_vars(self):
        dag = self.dag
        for n in du.itr_sinks(dag, self.defined_vars):
            deps = ancestors(dag, n)
            deps.add(n)
            con_dag = dag.subgraph(deps)
            reverse_order = topological_sort(con_dag, reverse=True)
            self.delete_sinks_recursively(reverse_order)

    def delete_sinks_recursively(self, reverse_order):
        dag = self.dag
        for n in reverse_order:
            if du.is_sink(dag, n):
                dag.remove_node(n)

    def collect_constraint_topological_orders(self):
        dag = self.dag
        for con_sink in self.con_ends_num:
            dependecies = ancestors(dag, con_sink)
            dependecies.add(con_sink)
            eval_order = topological_sort(dag, dependecies)
            self.con_top_ord[con_sink] = eval_order
            #self.print_con(dag.subgraph(eval_order), eval_order, con_sink)
            assert False, 'continue from here'
            # FIXME Defined var topological orders should be stored as well
            #       Not clear how to avoid recomputations, maybe removing 
            #       aliases wasn't the best idea?

    def print_constraints(self):
        print('Constraint dependencies\n')
        dag = self.dag
        for end_node_id in self.con_ends_num:
            deps = ancestors(dag, end_node_id)
            d = self.dag.node[end_node_id]
            #print('d =',d)
            if len(deps)==0: # something silly, apparently just var bounds
                print(d[NodeAttr.display], 'in', d[NodeAttr.bounds],'\n')
                continue
            print(d[NodeAttr.name])
            deps.add(end_node_id)
            con_dag = dag.subgraph(deps)
            eval_order = topological_sort(con_dag)
            self.print_con(con_dag, eval_order, end_node_id)
        du.dbg_info(dag)

    def print_con(self, sub_dag, order, end_node_id):
        for node_id in order:
            predec = sub_dag.predecessors(node_id)
            d = sub_dag.node[node_id]
            assert NodeAttr.display in d, 'node: %d %s' % (node_id, d)
            if len(predec) > 0:
                print(node_id, '=', d[NodeAttr.display], predec)
            else:
                print(node_id, '=', d[NodeAttr.display], d.get(NodeAttr.bounds, ''))
        # finally show the residual
        lb, ub = d[NodeAttr.bounds]
        if lb == ub == 0.0:
            print('res = node {}'.format(node_id))
        elif lb == ub:
            print('res = node {} - {}'.format(node_id, lb))
        else:
            print('{} <= node {} <= {}'.format(lb, node_id, ub))
        print()
