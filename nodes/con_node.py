from node_attributes import NodeAttr

def setup(node_id, node, problem):
    con_num = problem.con_ends_num[node_id]
    name    = problem.con_num_name.get(con_num, '_c{}'.format(con_num))
    node[NodeAttr.con_num] = con_num
    node[NodeAttr.name]    = name
    node[NodeAttr.display] = '{}({})'.format(name, node_id)