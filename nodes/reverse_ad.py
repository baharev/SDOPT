from __future__ import print_function

__all__ = [ 'prepare_evaluation_code' ]

import io, math
from operator import itemgetter
from string import Template
from nodes.attributes import NodeAttr
from itertools import izip
from representation.dag_util import get_pretty_type_str
from util.redirect_stdout import redirect_stdout
from util.misc import get_all_files
from parsers.dag_parser import read_problem
from datagen.paths import DATADIR

# TODO Different formatters for Python and C++ code gen

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

def idx_str(i, base_vars, con_dag):
    if i in base_vars:
        return 'v[%d]' % base_vars[i]
    # a number
    d = con_dag.node[i]
    if NodeAttr.number in d:
        number = d[NodeAttr.number]
        return str(number) if number >= 0 else '({})'.format(number)
    # some intermediate node
    return 't%d' % i

def lin_comb_str(n, d, con_dag, base_vars, op='+'):
    # for 1..n: lambda_1*predec_1 op lambda_2*predec_2 ... op lambda_n*predec_n
    #   where op is + or *
    s = []
    for lam, predec in gen_inedge_mult(n, d, con_dag):
        s.append('%s%s' % (lambda_to_str(lam), idx_str(predec, base_vars, con_dag)))
    return (' %s ' % op).join(s)

def sum_node_str(n, d, con_dag, base_vars):
    d_term = d.get(NodeAttr.d_term, 0.0)
    return lin_comb_str(n, d, con_dag, base_vars) + add_d_term_str(d_term)

def mul_node_str(n, d, con_dag, base_vars):
    d_term = d.get(NodeAttr.d_term, 1.0)
    return  lmul_d_term_str(d_term) + lin_comb_str(n, d, con_dag, base_vars, '*')

# TODO Why are the asserts outside of inedge? Can I move it there?
def div_node_str(n, d, con_dag, base_vars):
    mult, pred = inedge_mult(n, d, con_dag)
    assert sorted(pred)==sorted(con_dag.pred[n]),'%s\n %s'%(pred,con_dag.pred[n])
    assert len(pred)==2, 'Expected exactly two predecessors %s' % d
    nomin  = lambda_to_str(mult[0]) + idx_str(pred[0], base_vars, con_dag)
    denom  = lambda_to_str(mult[1]) + idx_str(pred[1], base_vars, con_dag)
    d_term = d.get(NodeAttr.d_term, 1.0)
    return lmul_d_term_str(d_term) + '(' + nomin + ')/(' + denom + ')'

def pow_node_str(n, d, con_dag, base_vars):
    mult, pred = inedge_mult(n, d, con_dag)
    assert sorted(pred)==sorted(con_dag.pred[n]),'%s\n %s'%(pred,con_dag.pred[n])
    assert len(pred)==2, 'Expected exactly two predecessors %s' % d
    d_term = d.get(NodeAttr.d_term, 0.0)
    base  = lambda_to_str(mult[0]) + idx_str(pred[0], base_vars, con_dag)
    base += add_d_term_str(d_term)
    power = lambda_to_str(mult[1]) + idx_str(pred[1], base_vars, con_dag)
    return  'pow(' + base + ', ' + power + ')'

# TODO Can this thing have a d term?
def exp_node_str(n, d, con_dag, base_vars):
    return 'exp(' + lin_comb_str(n, d, con_dag, base_vars) + ')'

def log_node_str(n, d, con_dag, base_vars):
    return 'log(' + lin_comb_str(n, d, con_dag, base_vars) + ')'

def sqr_node_str(n, d, con_dag, base_vars):
    return '(' + lin_comb_str(n, d, con_dag, base_vars) + ')**2'

### Why are these two needed?
def var_node_str(n, d, con_dag, base_vars):
    # Assumes a defined variable
    assert n not in base_vars
    assert NodeAttr.input_ord in d, '%d, %s' % (n, d)
    pred = d[NodeAttr.input_ord]
    assert len(pred)==1
    return sum_node_str(n, d, con_dag, base_vars)

def num_node_str(n, d, con_dag, base_vars):
    return str(d[NodeAttr.number])
###

def gen_inedge_mult(n, d, con_dag):
    return izip(*inedge_mult(n, d, con_dag)) 

def inedge_mult(n, d, con_dag):
    pred = d[NodeAttr.input_ord]
    mult = [con_dag[p][n]['weight'] for p in pred]
    return mult, pred

################################################################################

def assign(seen, node):
    assign = '+=' if node in seen else '='
    seen.add(node)
    return assign     

def sum_node_rev(n, d, con_dag, base_vars, seen):
    # t_i = lam_p*t_p + lam_q*t_q + ... + lam_z*t_z
    # u_p (+)= lam_p * u_i
    # ... 
    # u_z (+)= lam_z * u_i
    for lam, node in gen_inedge_mult(n, d, con_dag):
        if NodeAttr.number not in con_dag.node[node]:
            print('u%d %s %su%d'%(node, assign(seen,node), lmul_d_term_str(lam), n))

def mul_node_rev(n, d, con_dag, base_vars, seen):
    mult, pred = inedge_mult(n, d, con_dag)
    assert sorted(pred)==sorted(con_dag.pred[n]),'%s\n %s'%(pred,con_dag.pred[n])
    assert len(pred)==2, 'Expected exactly two predecessors %s' % d
    # t_i = d*(lam_r*t_r)*(lam_s*t_s) 
    # u_r (+)= d*lam_r*lam_s * t_s * u_i
    # u_s (+)= d*lam_r*lam_s * t_r * u_i    
    const = lmul_d_term_str(d.get(NodeAttr.d_term, 1.0)*mult[0]*mult[1])
    r = pred[0]
    s = pred[1]
    mul_rev(n, d, con_dag, base_vars, seen, const, r, s)
    mul_rev(n, d, con_dag, base_vars, seen, const, s, r)    
        
def mul_rev(n, d, con_dag, base_vars, seen, const, r, s):
    if NodeAttr.number in con_dag.node[r]:
        return
    s_str = idx_str(s, base_vars, con_dag)
    # u_r (+)= const * t_s * u_i
    print('u%d %s %s%s * u%d' % (r, assign(seen,r), const, s_str, n))

def div_node_rev(n, d, con_dag, base_vars, seen):
    mult, pred = inedge_mult(n, d, con_dag)
    assert sorted(pred)==sorted(con_dag.pred[n]),'%s\n %s'%(pred,con_dag.pred[n])
    assert len(pred)==2, 'Expected exactly two predecessors %s' % d
    # t_i = d*(lam_r*t_r)/(lam_s*t_s) 
    # u_r (+)=  d*lam_r/lam_s * (1/t_s) * u_i
    # u_s (+)=           -(1/t_s) * t_i * u_i
    const = lmul_d_term_str(d.get(NodeAttr.d_term, 1.0)*mult[0]/mult[1])
    r = pred[0]
    s = pred[1]
    recip = 'recip_%d_%d' % (n, s)
    print('%s = 1.0/(%s)' % (recip, idx_str(s, base_vars, con_dag)))
    if NodeAttr.number not in con_dag.node[r]:
        print('u%d %s %s%s * u%d' % (r, assign(seen,r), const, recip, n))
    if NodeAttr.number not in con_dag.node[s]:
        print('u%d %s -%s * t%d * u%d'%(s, assign(seen,s), recip, n, n))
    
def exp_node_rev(n, d, con_dag, base_vars, seen):
    # t_i = exp(lam_j*t_j + ...)
    # u_j = lam_j*t_i * u_i
    for lam, node in gen_inedge_mult(n, d, con_dag):        
        print('u%d %s %st%d * u%d'%(node,assign(seen,node),lmul_d_term_str(lam),n,n))    

def log_node_rev(n, d, con_dag, base_vars, seen):
    # t_i = log(lam_j*t_j + ...)
    # lnarg   = lam_j*t_j + ...
    # u_j  (+)= lam_j*(1/lnarg)*u_i
    lnarg_recip = 'lnarg_recip_%d' % n
    print('%s = 1.0/(%s)' % (lnarg_recip, lin_comb_str(n,d,con_dag,base_vars)))
    for lam, node in gen_inedge_mult(n, d, con_dag):
        args = (node, assign(seen,node), lmul_d_term_str(lam), lnarg_recip, n)
        print('u%d %s %s%s * u%d' % args)
        
def sqr_node_rev(n, d, con_dag, base_vars, seen):
    # t_i  = sqr(lam_j*t_j + ...)
    # sqrarg   = lam_j*t_j + ...
    # u_j (+)= 2.0*lam_j*sqrarg*u_i
    sqrarg = 'sqrarg_%d' % n
    print('%s = 2.0*%s' % (sqrarg, lin_comb_str(n,d,con_dag,base_vars)))
    for lam, node in gen_inedge_mult(n, d, con_dag):
        args = (node, assign(seen,node), lmul_d_term_str(lam), sqrarg, n)
        print('u%d %s %s%s * u%d' % args)

def pow_node_rev(n, d, con_dag, base_vars, seen):
    # t_i   = pow(base, power)
    # u_j (+)= lam_j*power*pow(base, power-1)*u_i
    mult, pred = inedge_mult(n, d, con_dag)
    assert sorted(pred)==sorted(con_dag.pred[n]),'%s\n %s'%(pred,con_dag.pred[n])
    assert len(pred)==2, 'Expected exactly two predecessors %s' % d
    d_term = d.get(NodeAttr.d_term, 0.0)
    base  = lambda_to_str(mult[0]) + idx_str(pred[0], base_vars, con_dag)
    base += add_d_term_str(d_term)
    power = lambda_to_str(mult[1]) + idx_str(pred[1], base_vars, con_dag)
    new_power = power + ' - 1.0'
    args=(pred[0],assign(seen,pred[0]),lmul_d_term_str(mult[0]),power,base,new_power,n)  
    print('u%d %s %s(%s) * pow(%s, %s) * u%d' % args)   

def print_node(n, d, con_dag, base_vars, seen):
    fmt = get_pretty_type_str(con_dag, n) + '_rev'
    formatter = globals()[fmt]
    formatter(n, d, con_dag, base_vars, seen)

################################################################################

def fwd_sweep(sink_node, con_num, con_dag, eval_order, base_vars, def_var_names):
    # Handle silly edge case first: apparently just variable bounds
    d_sink = con_dag.node[sink_node]
    if len(eval_order)==1:
        print(d_sink[NodeAttr.display], 'in', d_sink[NodeAttr.bounds],'\n')
        return
    # Pretty-print well-behaving constraint
    # name
    print('#', d_sink[NodeAttr.name])
    # evaluation in topologically sorted order
    for n, d in itr_nodes_to_pprint(con_dag, eval_order, base_vars):
        body = get_body(n, d, con_dag, base_vars)
        pprint_node_assignment_with_comment(n, d, body, con_dag, def_var_names)
    # residual
    pprint_residual(sink_node, d_sink, con_num, con_dag, base_vars)

def bwd_sweep(sink_node, con_num, con_dag, eval_order, base_vars, def_var_names):
    print('u%d = 1.0' % sink_node) # setting the seed
    seen = set()
    for n, d in itr_reverse(con_dag, eval_order, base_vars):
        body = get_body(n, d, con_dag, base_vars)
        print('# ', end='')
        pprint_node_assignment_with_comment(n, d, body, con_dag, def_var_names)
        #
        print_node(n, d, con_dag, base_vars, seen)
    # Collect row of the Jacobian
    basevars = sorted(((n,base_vars[n]) for n in eval_order if n in base_vars),
                      key=itemgetter(1)) # sort by var_num
    for n, var_num in basevars:
        print('jac.append(%d, %d, u%d)' % (con_num, var_num, n))
    print()

def itr_nodes_to_pprint(con_dag, eval_order, base_vars):
    # Print if NOT a base variable, a number or the last node (residual)
    return ((n, con_dag.node[n]) for n in eval_order[:-1] \
              if n not in base_vars and NodeAttr.number not in con_dag.node[n])

def itr_reverse(con_dag, eval_order, base_vars):
    return ((n, con_dag.node[n]) for n in eval_order[::-1] \
              if n not in base_vars and NodeAttr.number not in con_dag.node[n])    

def get_body(n, d, con_dag, base_vars):
    fmt = get_pretty_type_str(con_dag, n) + '_str'
    formatter = globals()[fmt]
    return formatter(n, d, con_dag, base_vars)

def pprint_node_assignment_with_comment(n, d, body, con_dag, def_var_names):
    if NodeAttr.var_num in d:
        print('t%d =' % n, body, ' # %s' % def_var_names[d[NodeAttr.var_num]])
    else:
        print('t%d =' % n, body,' #', get_pretty_type_str(con_dag,n))

def pprint_residual(sink_node, d_sink, con_num, con_dag, base_vars):
    body = get_body(sink_node, d_sink, con_dag, base_vars)
    lb, ub = d_sink[NodeAttr.bounds]
    if lb == ub == 0.0:
        print('con[%d] = %s  # t%d' % (con_num, body, sink_node))
    elif lb == ub:
        print('con[%d] = %s - %s  # t%d' % (con_num, body, to_str(lb), sink_node))
    else:
        print('%g <= (%s) <= %g  # t%d' % (lb, body, ub, sink_node))
    print()

################################################################################

def prepare_evaluation_code(prob, only_forward=False):
    with io.BytesIO() as code: 
        code.write(preamble)
        write_constraint_evaluation_code(prob, code, only_forward)
        code.write(postamble)
        code.write( main_func.substitute(v=prob.refsols[0], ncons =prob.ncons,
                                         nvars=prob.nvars, nzeros=prob.nzeros) )
        return code.getvalue()

def write_constraint_evaluation_code(problem, code, only_forward):
    with io.BytesIO() as ostream: 
        with redirect_stdout(ostream):  # Eliminating the nested with would make 
            run_code_gen(problem, only_forward) # debugging harder: stdout is swallowed!
        # prepend indentation, keep line ends
        code.writelines('    %s' % l for l in ostream.getvalue().splitlines(True))

# TODO This iteration logic belongs to the Problem class
def run_code_gen(problem, only_forward=False):
    for sink_node in problem.con_ends_num:
        eval_order = problem.con_top_ord[sink_node]
        con_num = problem.con_ends_num[sink_node]
        con_dag = problem.dag.subgraph(eval_order)
        base_vars = problem.base_vars
        def_var_names = problem.var_num_name
        fwd_sweep(sink_node, con_num, con_dag, eval_order, base_vars, \
                                                                  def_var_names)
        if not only_forward:
            bwd_sweep(sink_node, con_num, con_dag, eval_order, base_vars, \
                                                                  def_var_names)

preamble = \
'''from __future__ import print_function
from math import exp, log
import numpy as np
import scipy.sparse as sp

class jac_coo_arrays:
    def __init__(self, nonzeros):
        self.k = 0
        self.ai = np.zeros(nonzeros,np.int32) 
        self.aj = np.zeros(nonzeros,np.int32)
        self.ra = np.zeros(nonzeros, np.float64)
    def append(self, i, j, a):
        k = self.k
        self.ai[k], self.aj[k], self.ra[k] = i, j, a
        self.k += 1

def evaluate(v, ncons, nvars, nzeros):
    
    con = np.empty(ncons, dtype=np.float64)
    np.copyto(con, float('NaN'), casting='unsafe')
    
    jac = jac_coo_arrays(nzeros)
    
'''

postamble = '''
    jacobian = sp.coo_matrix((jac.ra, (jac.ai, jac.aj)), shape=(ncons,nvars))

    return con, jacobian
'''

main_func = Template('''
if __name__=='__main__':
    v = $v
    con, jac = evaluate(v, $ncons, $nvars, $nzeros)
    print(con)
    print()    
    print(str(jac))
''')

if __name__=='__main__':
    for dag_file in get_all_files(DATADIR, '.dag'):
        problem = read_problem(dag_file, plot_dag=False, show_sparsity=False)
        print('===============================================')
        print( prepare_evaluation_code(problem) )
        print('===============================================')
