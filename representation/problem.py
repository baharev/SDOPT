import networkx as nx
import weakref
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

    def setup_constraint_names(self):
        for node_id, con_num in self.con_ends_num.iteritems():
            d = self.dag.node[node_id]
            d[NodeAttr.name] = self.con_num_name.get(con_num, '_c{}'.format(con_num))
            d[NodeAttr.con_num] = con_num

    def setup_nodes(self):
        self.setup_constraint_names()
        for node_id, d in self.dag.nodes_iter(data=True):
            d[NodeAttr.dag] = weakref.ref(self.dag)
            d[NodeAttr.type].setup(node_id, d, self)
        self.assert_var_num_equals_node_id_for_named_vars()
        self.remove_spurious_vars()
        self.print_constraints()

    def remove_spurious_vars(self):
        # FIXME hack 5
        for node_id in self.var_node_ids:
            d = self.dag.node[node_id]
            var_num =  d[NodeAttr.var_num]
            if node_id > 5 and var_num <= 5:
                self.reparent(var_num, node_id)
        # del self.var_node_ds

    # delete node_id and connect all children to var_num, with edge dict
    def reparent(self, var_num, node_id):
        out_edges = self.dag.edge[node_id]
        print
        print var_num, node_id, out_edges
        assert self.is_leaf(node_id), '%s' % self.dag.node[node_id]
        assert self.is_leaf(var_num), '%s' % self.dag.node[var_num]
        self.dag.remove_node(node_id)
        for child_id, edge_dict in out_edges.iteritems():
            self.dag.add_edge(var_num, child_id, edge_dict)

    def is_leaf(self, node_id):
        return len(self.dag.pred[node_id])==0

    def print_constraints(self):
        print 'Constraint dependencies\n'
        dag = self.dag
        for end_node_id in self.con_ends_num:
            deps = ancestors(dag, end_node_id)
            d = self.dag.node[end_node_id]
            #print 'd =',d
            if len(deps)==0: # something silly, apparently just var bounds
                print d[NodeAttr.display], 'in', d[NodeAttr.bounds],'\n'
                continue
            print d[NodeAttr.name]
            deps.add(end_node_id)
            con_dag = dag.subgraph(deps)
            eval_order = topological_sort(con_dag)
            self.print_con(con_dag, eval_order, end_node_id)

    def print_con(self, sub_dag, order, end_node_id):
        for node_id in order:
            predec = sub_dag.predecessors(node_id)
            d = sub_dag.node[node_id]
            if len(predec) > 0:
                print node_id, '=', d[NodeAttr.display], predec
            else:
                print node_id, '=', d[NodeAttr.display], d.get(NodeAttr.bounds, '')
        # print the residual
        lb, ub = d[NodeAttr.bounds]
        if lb == ub == 0.0:
            print 'res = node {}'.format(node_id)
        elif lb == ub:
            print 'res = node {} - {}'.format(node_id, lb)
        else:
            print '{} <= node {} <= {}'.format(lb, node_id, ub)
        print

    def assert_var_num_equals_node_id_for_named_vars(self):
        for var_num in self.var_num_name:
            # assumption: var_num == node_id
            assert var_num in self.dag, 'var_num %d should be a node id' % var_num
            d = self.dag.node[var_num]
            assert d.has_key(NodeAttr.var_num), 'expected a var node, found %s' % d
            assert d.has_key(NodeAttr.name), 'expected a named var, found %s' % d
            var_num_on_node = d[NodeAttr.var_num]
            assert var_num_on_node==var_num, 'var_num on node %d, expected %d; %s' % \
                                             (var_num_on_node, var_num, d)
