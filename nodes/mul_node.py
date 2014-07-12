from node_attributes import NodeAttr

def setup(node_id, node, problem):
    node[NodeAttr.display] = node[NodeAttr.operation]
