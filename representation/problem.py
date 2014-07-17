from __future__ import print_function
import weakref
import networkx as nx
import dag_util as du
from nodes.attributes import NodeAttr
from networkx.algorithms.dag import ancestors, topological_sort

class Problem:

    def __init__(self):
        self.dag = nx.DiGraph()
        self.con_ends_num = { } # con root node -> con num (in AMPL)
        self.con_num_name = { } # con num -> con name (in AMPL)
        self.var_num_name = { } # var num (in AMPL) -> var name (in AMPL)
        self.var_node_ids = set()
        self.model_name = '(none)'
        self.nvars = int(-1)

    def setup(self):
        dag = self.dag
        du.dbg_info(dag)
        self.setup_constraint_names()
        self.setup_nodes()
        # The followings are simplifications
        #------------------------------------------
        # remove bogus named var aliasing
        du.assert_var_num_equals_node_id_for_named_vars(dag, self.var_num_name)
        # remove named vars from var_node_ids, we asserted just above that
        # they are nodes 0:nvars
        self.var_node_ids.difference_update( xrange(self.nvars) )
        # the rest assumes that named var nodes are no longer in var_node_ids!
        self.remove_var_aliases()
        #------------------------------------------
        # nl2dag erroneously turns defined vars into constraints
        self.reconstruct_CSEs()
        #-------------------------------------------
        self.print_constraints()

    def setup_constraint_names(self):
        for node_id, con_num in self.con_ends_num.iteritems():
            d = self.dag.node[node_id]
            d[NodeAttr.name] = self.con_num_name.get(con_num, '_c{}'.format(con_num))
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
        # Eliminates defined variables: def var := defining constraint
        print('cons: ', sorted(self.con_ends_num.viewkeys()))
        # FIXME See the comment at assert_CSE_defining_constraints w.r.t.
        #       reversing the edge
        dag = self.dag
        for n in con_ends:
            # reverse edge
            dag.add_edge(n, n+1, dag[n+1][n]) # multiplier, children order, etc not updated!
            dag.remove_edge(n+1, n)
            # TODO Removed from constraints without updating the defining sum nodes
            self.con_ends_num.pop(n)
        print('cons: ', sorted(self.con_ends_num.viewkeys()))

    def remove_CSE_aliases(self, con_ends):
        dag = self.dag
        # var_num -> defining node
        var_num_def_node = { dag.node[n+1][NodeAttr.var_num] : n+1 \
                                 for n in con_ends }
        print('defined vars, var num -> defining node:\n  %s\n'%var_num_def_node)
        var_node_ids = self.var_node_ids
        du.assert_vars_are_CSEs(dag, var_node_ids, var_num_def_node)
        for var_node in var_node_ids:
            var_num = dag.node[var_node][NodeAttr.var_num]
            def_node = var_num_def_node[var_num]
            if def_node!=var_node: # true if var_node is a bogus reference
                du.reparent(dag, def_node, var_node, new_parent_is_leaf=False)
        # TODO var_node_ids -= var_aliases.viewkeys()
        #      There should only be CSEs left in the var_node_ids?

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
            print([NodeAttr.name])
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
