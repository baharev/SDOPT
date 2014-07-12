from node_attributes import NodeAttr

def setup(unused1, d, unused2):
    d[NodeAttr.display] = str(d[NodeAttr.number])