from ..nodes.attributes import NodeAttr
from ..representation.dag_util import add_keep_smaller_value

def setup(node_id, d, problem):
    var_num = d[NodeAttr.var_num]
    # for base vars only: find the node with the smallest node id
    if  var_num < problem.nvars:
        # FIXME We could collect ALL the var aliases (base and defined) here!
        add_keep_smaller_value(problem.var_num_id, var_num, node_id)
    name    = problem.var_num_name.get(var_num, '_v%d' % var_num)
    d[NodeAttr.name]    = name
    d[NodeAttr.display] = '%s(%d)' % (name, node_id)
