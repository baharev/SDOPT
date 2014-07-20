from __future__ import print_function
from nodes.attributes import NodeAttr
from itertools import izip
import math
import representation.dag_util as du

def to_str(number):
    return str(number) if number >= 0 else '({})'.format(number)

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
    # a true var
    if i<nvars:
        return 'v[%d]' % i
    # a number
    d = con_dag.node[i]
    if NodeAttr.number in d:
        number = d[NodeAttr.number]
        return str(number) if number >= 0 else '({})'.format(number)
    # some intermediate node
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
    # pred == con_dag.pred[n] should hold too
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
    assert NodeAttr.input_ord in d, '%d, %s' % (n, d)
    pred = d[NodeAttr.input_ord]
    assert len(pred)==1
    return sum_node_str(n, d, con_dag, nvars)

def num_node_str(n, d, con_dag, nvars):
    return str(d[NodeAttr.number])

################################################################################

def pprint_one_constraint(sink_node, con_num, con_dag, eval_order, nvars):
    # Handle silly edge case first: apparently just variable bounds
    d_sink = con_dag.node[sink_node]
    if len(eval_order)==1:
        print(d_sink[NodeAttr.display], 'in', d_sink[NodeAttr.bounds],'\n')
        return
    #
    # Pretty-print well-behaving constraint
    # name
    print('#', d_sink[NodeAttr.name])
    # evaluation in topologically sorted order
    for n, d in itr_nodes_to_pprint(con_dag, eval_order, nvars):
        body = get_body(n, d, con_dag, nvars)
        pprint_node_assignment_with_comment(n, d, body, con_dag)
    # residual
    pprint_residual(sink_node, d_sink, con_num, con_dag, nvars)

def itr_nodes_to_pprint(con_dag, eval_order, nvars):
    # Print if NOT a named variable, a number or the last node (residual)
    return ((n, con_dag.node[n]) for n in eval_order[:-1] \
              if n >= nvars and NodeAttr.number not in con_dag.node[n])

def get_body(n, d, con_dag, nvars):
    fmt = du.get_pretty_type_str(con_dag, n) + '_str'
    formatter = globals()[fmt]
    return formatter(n, d, con_dag, nvars)

def pprint_node_assignment_with_comment(n, d, body, con_dag):
    if NodeAttr.var_num in d:
        print('t%d =' % n, body, ' # var_num %d' % d[NodeAttr.var_num])
    else:
        print('t%d =' % n, body,' #', du.get_pretty_type_str(con_dag,n))

def pprint_residual(sink_node, d_sink, con_num, con_dag, nvars):
    body = get_body(sink_node, d_sink, con_dag, nvars)
    lb, ub = d_sink[NodeAttr.bounds]
    if lb == ub == 0.0:
        print('con[%d] = %s  # t%d' % (con_num, body, sink_node))
    elif lb == ub:
        print('con[%d] = %s - %s  # t%d' % (con_num, body, to_str(lb), sink_node))
    else:
        print('%g <= (%s) <= %g  # t%d' % (lb, body, ub, sink_node))
    print()

