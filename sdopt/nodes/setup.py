from ..nodes.attributes import NodeAttr
from ..nodes.types import ntype
from ..representation.dag_util import add_keep_smaller_value

# TODO Factor out duplication

def div_setup(node_id, d, problem):
    d[NodeAttr.display] = d[NodeAttr.operation]
    
def exp_setup(node_id, d, problem):
    d[NodeAttr.display] = d[NodeAttr.operation]    

def log_setup(node_id, d, problem):
    d[NodeAttr.display] = d[NodeAttr.operation]

def mul_setup(node_id, d, problem):
    d[NodeAttr.display] = d[NodeAttr.operation]

def neg_setup(node_id, d, problem):
    # Flip the sign of all inedges
    for pred in d[NodeAttr.input_ord]:
        edge = problem.dag[pred][node_id]
        edge['weight'] = -edge['weight']
    # Rewrite the node type to ntype.SUM
    d[NodeAttr.operation] = '+'
    d[NodeAttr.type] = ntype.SUM
    sum_setup(node_id, d, problem)

def num_setup(unused1, d, unused2):
    d[NodeAttr.display] = str(d[NodeAttr.number])

def pow_setup(node_id, d, problem):
    d[NodeAttr.display] = d[NodeAttr.operation]

def sqr_setup(node_id, d, problem):
    d[NodeAttr.display] = d[NodeAttr.operation]

def sum_setup(node_id, d, problem):
    # neg_node also calls this
    d[NodeAttr.display] = d[NodeAttr.operation]

def var_setup(node_id, d, problem):
    var_num = d[NodeAttr.var_num]
    # for base vars only: find the node with the smallest node id
    if  var_num < problem.nvars:
        # FIXME We could collect ALL the var aliases (base and defined) here!
        add_keep_smaller_value(problem.var_num_id, var_num, node_id)
    name    = problem.var_num_name.get(var_num, '_v%d' % var_num)
    d[NodeAttr.name]    = name
    d[NodeAttr.display] = '%s(%d)' % (name, node_id)


def setup(node_id, d, prob):
    func = globals()[ d[NodeAttr.type]+'_setup' ]
    func(node_id, d, prob)
