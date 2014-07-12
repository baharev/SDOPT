from node_attributes import NodeAttr

def setup(node_id, node, problem):
    var_num = node[NodeAttr.var_num]
    name    = problem.var_num_name.get(var_num, 'V{}'.format(var_num))
    node[NodeAttr.var_num] = var_num
    node[NodeAttr.display] = '{}({})'.format(name, node_id)