import networkx as nx
import nodes
from nodes.node_attributes import NodeAttr
from networkx.algorithms.dag import ancestors, topological_sort

class Problem:

    def __init__(self):
        self.dag = nx.DiGraph()
        self.con_ends_num = { }
        self.con_num_name = { }
        self.var_num_name = { }
        self.model_name = '(none)'
        self.nvars = int(-1)

    def set_node_display(self):
        for node_id, data in self.dag.nodes_iter(data=True):
            nodes.nodes.setup(data, self)

    def setup_constraints(self):
        dag = self.dag
        con_nodes = self.dag.nbunch_iter(self.con_ends_num)
        for end_node, dict in self.dag.nodes(con_nodes):
            print 'node', dict[NodeAttr.display]
            deps = ancestors(dag, end_node)
            deps.add(end_node)
            con_dag = dag.subgraph(deps)
            eval_order = topological_sort(con_dag)
            self.print_con(con_dag, eval_order)

    def print_con(self, sub_dag, order):
        for node_id in order:
            predec = sub_dag.predecessors(node_id)
            if len(predec) > 0:
                            # used to be disp[node_id]
                print node_id, '=', node_id, predec
            else:
                print node_id, '=', node_id
        print
