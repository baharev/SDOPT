from __future__ import print_function
import six
from ..nodes.attributes import NodeAttr

# I am still not sure how to resolve many of the things in here, so just leaving
# it the way it is.  

class ntype:
    DIV = 'div'
    EXP = 'exp'
    LOG = 'log'
    MUL = 'mul'
    NEG = 'neg'
    NUM = 'num'
    POW = 'pow'
    SQR = 'sqr'
    SUM = 'sum'
    VAR = 'var'
    
def is_var_node(node_dict):
    return node_dict[NodeAttr.type] == ntype.VAR

def is_sum_node(node_dict):
    return node_dict[NodeAttr.type] == ntype.SUM

all_types  = set( k for k in vars(ntype) if k[0].isupper() )

all_values = set( v for k,v in six.iteritems(vars(ntype)) if k[0].isupper() )

#print(all_types)
#print(all_values)

