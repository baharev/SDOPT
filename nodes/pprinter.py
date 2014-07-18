from nodes.attributes import NodeAttr
from itertools import izip
import math

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
    # body <+ d_term as string>, this function gives the latter
    #  0 -> ''
    #  3 -> ' + 3'
    # -2 -> ' - 2'
    if   d_term == 0:
        return ''
    s = ' + '
    if d_term < 0:
        s = ' - '
    s += str(math.fabs(d_term))
    return s

def lmul_d_term_str(d_term):
    # <d_term as string> * body, this function gives the former
    #  1 -> ''
    # -1 -> '-'
    #  3 -> '3*'
    # -3 -> '-3*
    assert d_term!=0.0
    if d_term ==  1.0:
        return ''
    if d_term == -1.0:
        return '-'
    return '%s * ' % str(d_term)

def idx_str(i, nvars, con_dag):
    if i<nvars:
        return 'v%d' % i
    d_child = con_dag.node[i]
    if NodeAttr.number in d_child:
        number = d_child[NodeAttr.number]
        return str(number) if number >= 0 else '({})'.format(number)
    return 't%d' % i

def lin_comb_str(n, d, con_dag, nvars, op='+'):
    # for 1..n: lambda_1*child_1 op lambda_2*child_2 ... op lambda_n*child_n
    #   where op is + or *
    pred = d[NodeAttr.input_ord]
    mult = [con_dag[c][n]['weight'] for c in pred]
    s = []
    for c, lam in izip(pred, mult):
        s.append('%s%s' % (lambda_to_str(lam), idx_str(c, nvars, con_dag)))
    return (' %s ' % op).join(s)

def sum_node_str(n, d, con_dag, nvars):
    d_term = d.get(NodeAttr.d_term, 0.0)
    return lin_comb_str(n, d, con_dag, nvars) + add_d_term_str(d_term)

def mul_node_str(n, d, con_dag, nvars):
    d_term = d.get(NodeAttr.d_term, 1.0)
    return  lmul_d_term_str(d_term) + lin_comb_str(n, d, con_dag, nvars, '*')

def div_node_str(n, d, con_dag, nvars):
    assert len(con_dag.pred[n])==2, 'Expected exactly two children %s' % d
    d_term = d.get(NodeAttr.d_term, 1.0)
    pred   = d[NodeAttr.input_ord]
    assert len(pred)==2, 'Expected exactly two children %s' % d
    mult   = [con_dag[c][n]['weight'] for c in pred]
    nomin  = lambda_to_str(mult[0]) + idx_str(pred[0], nvars, con_dag)
    denom  = lambda_to_str(mult[1]) + idx_str(pred[1], nvars, con_dag)
    return lmul_d_term_str(d_term) + '(' + nomin + ')/(' + denom + ')'

def exp_node_str(n, d, con_dag, nvars):
    return 'exp(' + lin_comb_str(n, d, con_dag, nvars) + ')'

def log_node_str(n, d, con_dag, nvars):
    return 'log(' + lin_comb_str(n, d, con_dag, nvars) + ')'

def var_node_str(n, d, con_dag, nvars):
    # FIXME defined vars!
    return 'v%d' % n

def num_node_str(n, d, con_dag, nvars):
    return str(d[NodeAttr.number])
