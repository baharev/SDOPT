from ..nodes.attributes import NodeAttr

def setup(node_id, d, problem):
    # neg_node also calls this
    d[NodeAttr.display] = d[NodeAttr.operation]
