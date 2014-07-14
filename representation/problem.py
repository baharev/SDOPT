import networkx as nx
import weakref
import nodes
from nodes.attributes import NodeAttr
from networkx.algorithms.dag import ancestors, topological_sort

def iter_attr(G, nbunch, name):
    for n in nbunch:
        yield n, G.node[n][name]

def is_leaf(dag, node_id):
    return len(dag.pred[node_id])==0

# FIXME Respect children order! Wrap: add_edge, remove_node, remove_edge,
#                                     reverse_edge
def reparent(dag, var_num, node_id, new_parent_is_leaf=True):
    # delete node_id and connect all children to var_num, with edge dict
    out_edges = dag.edge[node_id]
    # print
    # print var_num, node_id, out_edges
    assert is_leaf(dag, node_id), 'node %d %s' % (node_id, dag.node[node_id])
    if new_parent_is_leaf: # TODO Clean up
        assert is_leaf(dag, var_num), 'node %d %s' % (var_num, dag.node[var_num])
    dag.remove_node(node_id)
    for child_id, edge_dict in out_edges.iteritems():
        dag.add_edge(var_num, child_id, edge_dict)

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
        #-------------------------------------------
        # remove bogus named var aliasing
        assert_var_num_equals_node_id_for_named_vars(self.dag, self.var_num_name)
        # remove named vars from var_node_ids, we asserted just above that
        # they are nodes 0:nvars
        self.var_node_ids.difference_update( xrange(self.nvars) )
        # the rest assumes that named var nodes are no longer in var_node_ids!
        self.remove_var_aliases()
        #-------------------------------------------
        # nl2dag erroneously turns defined vars into constraints
        self.reconstruct_CSEs()
        #-------------------------------------------
        self.print_constraints()

    def remove_var_aliases(self):
        var_aliases = self.get_var_aliases()
        for node_id, var_num in var_aliases.iteritems():
            reparent(self.dag, var_num, node_id)
        self.var_node_ids -= var_aliases.viewkeys()

    def get_var_aliases(self):
        var_aliases = { } # alias node id -> named var aliased
        # this new dict is needed as we remove nodes from the dag as we reparent
        nvars = self.nvars
        for node_id, var_num in iter_attr(self.dag, self.var_node_ids, NodeAttr.var_num):
            if var_num < nvars: # true if referencing a named var; false for CSE
                var_aliases[node_id] = var_num
        return var_aliases

    def reconstruct_CSEs(self):
        con_ends = self.get_unnamed_constraints()
        dag = self.dag
        assert_CSE_defining_constraints(dag, con_ends, self.var_num_name)

        print 'cons: ', sorted(self.con_ends_num.viewkeys())
        # FIXME See the comment at the above assert function w.r.t. reversing
        #       the edge
        for n in con_ends:
            # reverse edge
            dag.add_edge(n, n+1, dag[n+1][n]) # multiplier, children order, etc not updated!
            dag.remove_edge(n+1, n)
            # TODO Removed from constraints without updating the defining sum nodes
            self.con_ends_num.pop(n)
        print 'cons: ', sorted(self.con_ends_num.viewkeys())

        # replace all bogus references of defined with defined var

        # var_num -> defining node
        var_num_def_node = { dag.node[n+1][NodeAttr.var_num] : n+1 for n in con_ends }
        print 'defined vars, var num -> defining node:\n  %s\n' % var_num_def_node

        # TODO Move this block to assert; it checks if ALL unnamed var_nodes are
        #      defined vars
        for var_node in self.var_node_ids:
            var_num = dag.node[var_node][NodeAttr.var_num]
            assert var_num in var_num_def_node,'var_num: %d' % var_num

        for var_node in self.var_node_ids:
            var_num = dag.node[var_node][NodeAttr.var_num]
            def_node = var_num_def_node[var_num]
            if def_node!=var_node: # this is a true bogus reference
                reparent(dag, def_node, var_node, new_parent_is_leaf=False)

        # TODO self.var_node_ids -= var_aliases.viewkeys()

        return


    def get_unnamed_constraints(self):
        return [ n for n in self.con_ends_num   \
                         if self.con_ends_num[n] not in self.con_num_name ]

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
        dbg_info(dag)

    def print_con(self, sub_dag, order, end_node_id):
        for node_id in order:
            predec = sub_dag.predecessors(node_id)
            d = sub_dag.node[node_id]
            assert NodeAttr.display in d, 'node: %d %s' % (node_id, d)
            if len(predec) > 0:
                print node_id, '=', d[NodeAttr.display], predec
            else:
                print node_id, '=', d[NodeAttr.display], d.get(NodeAttr.bounds, '')
        # finally show the residual
        lb, ub = d[NodeAttr.bounds]
        if lb == ub == 0.0:
            print 'res = node {}'.format(node_id)
        elif lb == ub:
            print 'res = node {} - {}'.format(node_id, lb)
        else:
            print '{} <= node {} <= {}'.format(lb, node_id, ub)
        print
        
def dbg_info(dag):
    print 
    # TODO Why does this crash?
    #print 'Is connected?', nx.is_connected(dag.to_undirected())
    print 'Is DAG?', nx.is_directed_acyclic_graph(dag)
    print 'Weakly connected components:', nx.number_weakly_connected_components(dag)
    print 'Nodes:', nx.number_of_nodes(dag), 'edges:', nx.number_of_edges(dag)
        

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
