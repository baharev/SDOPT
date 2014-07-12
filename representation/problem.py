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
        self.model_name = '(none)'
        self.nvars = int(-1)

    def setup_constraint_names(self):
        for node_id, con_num in self.con_ends_num.iteritems():
            d = self.dag.node[node_id]
            d[NodeAttr.name] = self.con_num_name[con_num]
            d[NodeAttr.con_num] = con_num

    def setup_nodes(self):
        self.setup_constraint_names()
        for node_id, d in self.dag.nodes_iter(data=True):
            d[NodeAttr.dag] = weakref.ref(self.dag)
            d[NodeAttr.type].setup(node_id, d, self)

    def setup_constraints(self):
        dag = self.dag
        for end_node_id in self.con_ends_num:
            d = self.dag.node[end_node_id]
            #print 'd =',d
            print d[NodeAttr.name]
            deps = ancestors(dag, end_node_id)
            deps.add(end_node_id)
            con_dag = dag.subgraph(deps)
            eval_order = topological_sort(con_dag)
            self.print_con(con_dag, eval_order)

    def print_con(self, sub_dag, order):
        for node_id in order:
            predec = sub_dag.predecessors(node_id)
            d = sub_dag.node[node_id]
            if len(predec) > 0:
                print node_id, '=', d[NodeAttr.display], predec
            else:
                print node_id, '=', d[NodeAttr.display]
        print
