from __future__ import print_function
import os, unittest
from os.path import join
import numpy as np
from coconut_parser.dag_parser import read_problem
from coconut_parser.gjh_parser import read
from nodes.reverse_ad import prepare_evaluation_code
from datagen.paths import DATADIR
from util.assert_helpers import assertEqual
from util.misc import import_code

class Test(unittest.TestCase):
    def test_reverse_ad(self):
        check_reverse_ad()

def check_reverse_ad():
    logs = sorted(f for f in os.listdir(DATADIR) if f.endswith('.log'))
    for logfile in logs:
        logfilename = join(DATADIR, logfile)
        dagfilename = join(DATADIR, logfile[:-4] + '.dag')
        test_reverse_ad(logfilename, dagfilename)

def test_reverse_ad(logfilename, dagfilename):
    x, residuals, jac = read(logfilename)
    prob = read_problem(dagfilename, plot_dag=False, show_sparsity=False)
    partial_code = prepare_evaluation_code(prob) 
    print('===============================================')
    rev_ad = import_code(partial_code)
    con, jac_ad = rev_ad.evaluate(x, prob.ncons, prob.nvars, prob.nzeros)
    # Check the residuals first
    # A rather messy and risky business to figure out where to flip the signs 
    sign = np.ones(residuals.size, dtype=np.int32)
    close = np.isclose(residuals, con)
    sign[~close] = -1
    # We've hopefully fixed the signs; the residuals should be all close now.
    # Unfortunately false positives are possible.
    allclose = np.allclose(residuals, np.multiply(sign, con))
    print( 'Residuals all close? {}'.format(allclose) )
    # Check the Jacobian, raises error if there is a mismatch
    differs_at(jac, jac_ad, sign)
    print('===============================================')   

def differs_at(a, b_unordered, sign):
    # Test whether indices match
    b = b_unordered.tocsr().tocoo() # An ugly way to order row-wise
    assertEqual(a.nnz, b.nnz)
    assertIntArrayEqual(a.row, b.row)
    assertIntArrayEqual(a.col, b.col)
    # Are entries all close?
    close =  np.isclose(a.data, np.multiply(sign[b.row], b.data))
    assertNotCloseIndicesAreEmpty(np.flatnonzero(~close), a, b, sign)

def assertNotCloseIndicesAreEmpty(ind, a, b, sign):
    if ind.size==0:
        print('Jacobian test passed!')
        return
    # The test failed; dump the mismatch and raise an error.
    # Can produce false positives if the sign was bogusly reconstructed!
    bdata = np.multiply(sign[b.row], b.data)
    for i in ind:
        print('(%d,%d) %g  %g' % (a.row[i], a.col[i], a.data[i], bdata[i]))
    raise AssertionError('See the indices and values printed above!')

def assertIntArrayEqual(a, b):
    indices = np.flatnonzero(a!=b)
    if indices.size:
        raise AssertionError('\n%s\n%s\n%s' % (indices, a[indices], b[indices]))
