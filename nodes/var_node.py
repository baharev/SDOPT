from nodes.attributes import NodeAttr

def setup(node_id, d, problem):
    var_num = d[NodeAttr.var_num]
    name    = problem.var_num_name.get(var_num, 'V{}'.format(var_num))
    d[NodeAttr.var_num] = var_num
    d[NodeAttr.name]    = name
    d[NodeAttr.display] = '{}({})'.format(name, node_id)