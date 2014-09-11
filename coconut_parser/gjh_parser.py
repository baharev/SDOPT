from __future__ import print_function
from os.path import dirname, join
import numpy as np
import scipy.sparse as sp
from util.file_reader import lines_of
from util.misc import advance, nth, skip_until, import_code
from coconut_parser.dag_parser import read_problem
from nodes.reverse_ad import prepare_evaluation_code
from datagen.paths import DATADIR
import os
from util.assert_helpers import assertEqual

def read(logfilename):
    x, residuals, nonzeros, name = read_log(logfilename)
    jac = read_gjh(join(dirname(logfilename), name), nonzeros)
    return x, residuals, jac
    
def read_log(filename):
    with lines_of(filename) as lines:
        # Read problem statistics first: rows, cols, nonzeros
        itr = skip_until(lambda s: s=='@@@ Problem statistics', lines)
        itr = advance(itr, 1)
        data = next(itr).split()
        ncons, nvars, nonzeros = (int(data[i]) for i in (1, 3, 5))
        # Read the variables 
        itr = advance(itr, 1) # skip line 'Variable vector:'
        x = np.fromiter(itr, np.float64, nvars)
        # Skip two lines, an empty one and 'Residual vector:'
        itr = advance(lines, 2)
        residuals = np.fromiter(itr, np.float64, ncons)
        # Read the name of the gjh file containing the Jacobian
        name = read_gjh_filename(lines)
    return x, residuals, nonzeros, name

def read_gjh_filename(lines):
    # <newline> gjh: "/tmp/at3464.gjh" written.  Execute
    s = nth(lines, 1)
    beg = s.find('\"') + 1
    end = s.rfind('\"')
    return s[beg:end]

def read_gjh(filename, nonzeros):
    with lines_of(filename) as lines:
        return parse(lines, nonzeros)

def parse(lines, nonzeros):
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

################################################################################
# These are Jacobian test, move them to a test file?

def assertIntArrayEqual(a, b):
    indices = np.flatnonzero(a!=b)
    if indices.size:
        raise AssertionError('\n%s\n%s\n%s' % (indices, a[indices], b[indices]))

def differs_at(A_spmat, B_spmat, sign):
    # Can produce false positives if: (1) the sign was bogusly reconstructed,
    # (2) there are accidental exact zeros in the Jacobian, (3) the indices are
    # not sorted the way they used to be.
    a = A_spmat.tocsr().tocoo() # A rather inefficient way to order it.
    b = B_spmat.tocsr().tocoo()
    # Indices match
    assertEqual(a.nnz, b.nnz)
    assertIntArrayEqual(a.row, b.row)
    assertIntArrayEqual(a.col, b.col)
    # Entries are all close; if not, dump the mismatch and raise an error
    close =  np.isclose(a.data, np.multiply(sign[b.row], b.data))
    ind = np.flatnonzero(~close)
    if ind.size:
        for i in ind:
            print('(%d,%d) %g  %g' % (a.row[i], a.col[i], a.data[i], b.data[i]))
        raise AssertionError('See the indices and values printed above!')
    else:
        print('Jacobian test passed!')
    
def test_reverse_ad(logfilename, dagfilename):
    x, residuals, jac = read(logfilename)
    problem = read_problem(dagfilename, plot_dag=False, show_sparsity=False)
    partial_code = prepare_evaluation_code(problem) 
    print('===============================================')
    #run_code_gen(problem)
    #dbg_dump_code(partial_code, list(x), \
    #              problem.ncons, problem.nvars)
    rev_ad = import_code(partial_code, 'doesThisNameMatterAtAll')
    con, jac_ad = rev_ad.evaluate(x, problem.ncons, problem.nvars)
    # Check the residuals first
    # A rather messy and risky business to figure out where to flip the signs 
    sign = np.ones(residuals.size, dtype=np.int32)
    close = np.isclose(residuals, con)
    sign[~close] = -1
    # We've hopefully fixed the signs, they should be all close.
    # Unfortunately false positives are possible.
    allclose = np.allclose(residuals, np.multiply(sign, con))
    print( 'Residuals all close? {}'.format(allclose) )
    # Check the Jacobian, raises error if there is a mismatch
    differs_at(jac, jac_ad, sign)
    print('===============================================')        

if __name__=='__main__':
    #logfilename = '/home/ali/ampl/JacobsenTorn.log'
    #dagfilename = '../data/JacobsenTorn.dag'
    # logfilename = '/home/ali/ampl/homepage.log'
    # dagfilename = '../data/example.dag'
    exclude = set(['mss20heatBalance.log'])
    logs = sorted(f for f in os.listdir(DATADIR) if f.endswith('.log') and f not in exclude)
    for logfile in logs:
        logfilename = join(DATADIR, logfile)
        dagfilename = join(DATADIR, logfile[:-4] + '.dag')
        test_reverse_ad(logfilename, dagfilename)

    
