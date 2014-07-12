import weakref
from node_attributes import NodeAttr


def display(node):
    print 'name =', node[NodeAttr.type]
    return node[NodeAttr.type].display(node)

def setup(node, problem):
    assert NodeAttr.node_id in node, 'Node: {}'.format(node)
    node_id = node[NodeAttr.node_id]
    node[NodeAttr.dag] = weakref.ref(problem.dag)
    node[NodeAttr.type].setup(node_id, node, problem)
