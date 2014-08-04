from nodes.attributes import NodeAttr
from representation.dag_util import add_keep_smaller

def setup(node_id, d, problem):
    var_num = d[NodeAttr.var_num]
    # for named vars only: find the node smallest node id
    if  var_num < problem.nvars and var_num in problem.var_num_name:
        add_keep_smaller(problem.var_num_id, var_num, node_id)
    name    = problem.var_num_name.get(var_num, '_v%d' % var_num)
    d[NodeAttr.name]    = name
    d[NodeAttr.display] = '%s(%d)' % (name, node_id)
