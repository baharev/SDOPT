from nodes.attributes import NodeAttr
from itertools import izip
import math

def str_d_term(d_term):
    pass

def lambda_to_str(number):
    #  1* -> ''
    #  3* -> '3*'
    # -2  -> '(-2)*'
    if number==1:
        return ''
    if number>=0:
        return '%s*' % str(number)
    return '(%s)*' % str(number)

def add_d_term_str(d_term):
    #  0 -> ''
    #  3 -> ' + 3'
    # -2 -> ' - 2'
    if   d_term == 0:
        return ''
    s = ''
    if d_term > 0:
        s += ' + '
    else:
        s += ' - '
    s += str(math.fabs(d_term))
    return s

def str_lin_comb(con_dag, d):
    # lambda_1*child_1 op lambda_2*child_2 ... op lambda_n*child_n
    #   where op is + or *
    op   = d[NodeAttr.operation]
    assert op=='+' or op=='*', op
    n    = d[NodeAttr.node_id]
    pred = d[NodeAttr.input_ord]
    mult = [con_dag[c][n]['weight'] for c in pred]
    s = []
    for c, lam in izip(pred, mult):
        s.append('%st%d' % (lambda_to_str(lam), c))
    return (' %s ' % op).join(s)
