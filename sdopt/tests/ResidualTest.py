from __future__ import print_function, absolute_import
import unittest
import numpy as np
from ..parsers.dag_parser import read_problem
from ..datagen.paths import DATADIR
from ..util.misc import import_code, get_all_files
from ..nodes.reverse_ad import prepare_evaluation_code

class ResidualTest(unittest.TestCase):
    def test_files(self):
        check_residuals()

def check_residuals():
    for dag_file in get_all_files(DATADIR, '.dag'):
        problem = read_problem(dag_file, plot_dag=False, show_sparsity=False)
        residual_code = prepare_evaluation_code(problem, only_forward=True)
        f = import_code(residual_code)
        # ignore the returned Jacobian, which is still empty in forward mode
        residuals, _  = f.evaluate( problem.refsols[0], problem.ncons, 
                                    problem.nvars,      problem.nzeros )
        approx_zero = np.isclose(residuals, 0.0, atol=4.0e-6)
        # TODO If fails, give the violated constraint name
        assert np.all(approx_zero), 'Large constraint violation\n%s' % residuals
        print('PASSED:', dag_file)
    # Enable these if coverage is measured:
    #from os.path import join
    #read_problem(join(DATADIR,'ex9_2_8.txt'), crosscheck_nl=False)        
