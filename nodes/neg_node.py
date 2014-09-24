from nodes.attributes import NodeAttr
from nodes import sum_node

def setup(node_id, d, problem):
    # Flip the sign of all inedges
    for pred in d[NodeAttr.input_ord]:
        edge = problem.dag[pred][node_id]
        edge['weight'] = -edge['weight']
    # Rewrite the node type to sum_node
    d[NodeAttr.operation] = '+'
    d[NodeAttr.type] = sum_node
    sum_node.setup(node_id, d, problem)