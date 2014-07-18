from nodes.attributes import NodeAttr
from itertools import izip

def str_d_term(d_term):
    pass

def lambda_to_str(number):
    if number==1:
        return ''
    if number>=0:
        return '%s*' % str(number)
    return '(%s)*' % str(number)

def str_lin_comb(con_dag, d):
    dag  = d[NodeAttr.dag]()
    op   = d[NodeAttr.operation]
    n    = d[NodeAttr.node_id]
    pred = d[NodeAttr.input_ord]
    for c in pred:
        assert c in con_dag, '\nnode  %r\nedges %r\ncnstr %r\nchild %r'%(d, dag.pred[n], con_dag.pred[n], dag.node[c])
    mult = [con_dag[c][n]['weight'] for c in pred]
    s = []
    for c, lam in izip(pred, mult):
        s.append('%st%d' % (lambda_to_str(lam), c))
    return (' %s ' % op).join(s)
