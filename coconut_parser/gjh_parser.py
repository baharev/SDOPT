from __future__ import print_function
from os.path import dirname, join
import numpy as np
import scipy.sparse as sp
from util.file_reader import lines_of
from util.misc import advance, nth, skip_until, import_code
from coconut_parser.dag_parser import read_problem
from nodes.reverse_ad import prepare_evaluation_code
from util.assert_helpers import assertEqual

def read(logfilename):
    x, residuals, name = read_log(logfilename)
    jac = read_gjh(join(dirname(logfilename), name))
    return x, residuals, jac
    
def read_log(filename):
    with lines_of(filename) as lines:
        # Read the variables
        itr = skip_until(lambda s: s=='@@@ Variable vector', lines)
        itr = advance(itr, 1)
        nvars = read_one_int(itr) 
        x = np.fromiter(itr, np.float64, nvars)
        # Skip two lines, an empty one and '@@@ Residual vector'
        itr = advance(lines, 2)
        # Read the residuals
        ncons = read_one_int(itr)
        residuals = np.fromiter(itr, np.float64, ncons)
        # Read the gjh file name
        # <newline> gjh: "/tmp/at3464.gjh" written.  Execute
        s = nth(lines, 1)
        beg = s.find('\"') + 1
        end = s.rfind('\"')
        name = s[beg:end]
    return x, residuals, name
        
def read_one_int(itr):
    return int(next(itr))

def read_gjh(filename):
    with lines_of(filename) as lines:
        return parse(lines)

def parse(lines):
    nrows, ncols = get_J_shape(lines)
    jac = sp.dok_matrix((nrows,ncols), dtype=np.float64)
    lines_from_first_row = skip_until(lambda s: s.startswith('['), lines) 
    for line in lines_from_first_row:
        if line[0]=='[':
            # has hit a new row: [12,*]
            comma = line.find(',')
            row = int(line[1:comma])-1
        elif line[0] == '\t':
            # data in row: <tab> col index <tab> entry
            col_idx, data = line.split()
            col, data = int(col_idx)-1, float(data)
            jac[row,col] = data
        else:
            break
    print('Jacobian:\n%s' % jac.tocsr())
    return jac

def get_J_shape(lines):
    # It's on the 3rd line, something like: 
    # param J{1..16, 1..16} default 0;
    line = nth(lines, 3)
    after_1st_dotdot = line.find('..') + 2
    comma = line.find(',')
    nrows = int(line[after_1st_dotdot:comma])
    after_2nd_dotdot = line.find('..', comma) + 2
    closing_bracket = line.find('}')
    ncols = int(line[after_2nd_dotdot:closing_bracket])
    print('Shape: %dx%d' % (nrows, ncols))
    return nrows, ncols

def differs_at(A_dok_mat, B_dok_mat, sign):
    a = A_dok_mat.tocsr().tocoo() # TODO A rather inefficient way to order it.
    b = B_dok_mat.tocsr().tocoo()
    diff = [ ]
    # FIXME Vectorize with NumPy
    assert a.nnz == b.nnz
    for k in xrange(a.nnz):
        ai, aj, ax = a.row[k], a.col[k], a.data[k]
        bi, bj, bx = b.row[k], b.col[k], sign[ai]*b.data[k]
        assertEqual(ai, bi)
        assertEqual(aj, bj)
        if not abs(ax-bx) < (1.0e-8 + 1.0e-5*abs(bx)):
            diff.append( [ai, aj, (ax, bx)] )
    print('Jacobian diff:\n%s' % diff)

if __name__=='__main__':
    x, residuals, jac = read('/home/ali/ampl/JacobsenTorn.log')
    problem = read_problem('../data/JacobsenTorn.dag', plot_dag=False, show_sparsity=False)
    partial_code = prepare_evaluation_code(problem) 
    print('===============================================')
    #run_code_gen(problem)
    # FIXME Add nrows to problem?
    #dbg_dump_code(partial_code, list(x), \
    #              len(problem.con_ends_num), problem.nvars)
    rev_ad = import_code(partial_code, 'doesThisNameMatterAtAll')
    con, jac_ad = rev_ad.evaluate(x, len(problem.con_ends_num), problem.nvars)
    #
    # A rather messy and risky business to figure out where to flip the signs 
    sign = np.ones(residuals.size, dtype=np.int32)
    close = np.isclose(residuals, con)
    sign[~close] = -1
    #
    allclose = np.allclose(residuals, np.multiply(sign, con))
    print( 'Residuals all close? {}'.format(allclose) )
    differs_at(jac, jac_ad, sign)
    print('===============================================')
    
