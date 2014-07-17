from nodes.attributes import NodeAttr

def setup(node_id, d, problem):
    var_num = d[NodeAttr.var_num]
    name    = problem.var_num_name.get(var_num, '_v%d' % var_num)
    d[NodeAttr.var_num] = var_num
    d[NodeAttr.name]    = name
    d[NodeAttr.display] = '%s(%d)' % (name, node_id)
