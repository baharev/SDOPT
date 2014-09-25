from __future__ import print_function
import numpy as np
from numpy.linalg import cond, norm
from datagen.paths import DATADIR
from os.path import join
from parsers.dag_parser import read_problem
from nodes.reverse_ad import prepare_evaluation_code
from util.misc import import_code 
import tests.JacobianTest

def diagnostics(basename):
    dagfilename = join(DATADIR, basename+'.dag')
    prob = read_problem(dagfilename, plot_dag=False, show_sparsity=False)
    partial_code = prepare_evaluation_code(prob) 
    rev_ad = import_code(partial_code)
    con, jac_ad = rev_ad.evaluate(prob.refsols[0], prob.ncons, prob.nvars, prob.nzeros)
    print('Constraint infinity norm: ', norm(con, np.inf))
    print('Condition number estimate:', cond(jac_ad.todense()))
    tests.JacobianTest.dump_code(partial_code, dagfilename)

if __name__ == '__main__':
    diagnostics('LLE3dis')
    diagnostics('LLE3disOrig')    
    
     
    

