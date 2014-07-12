from node_attributes import NodeAttr

def setup(unused1, node, unused2):
    node[NodeAttr.display] = str(node[NodeAttr.number])