from __future__ import print_function
import unittest
from coconut_parser.dag_parser import read_problem
from datagen.paths import DATADIR
from util.misc import import_code, get_all_files
from util.assert_helpers import assertLess
from nodes.reverse_ad import prepare_evaluation_code

class ResidualTest(unittest.TestCase):
    def test_files(self):
        check_residuals()

def check_residuals():
    for dag_file in get_all_files(DATADIR, '.dag'):
        problem = read_problem(dag_file, plot_dag=False, show_sparsity=False)
        residual_code = prepare_evaluation_code(problem, only_forward=True)
        # TODO Does the fake module name twistedResidualTest matter?
        f = import_code(residual_code, 'twistedResidualTest')
        residuals, _  = f.evaluate( problem.refsols[0], problem.ncons, 
                                      problem.nvars,      problem.nzeros )
        # print(residuals)
        # FIXME Use NumPy? NaN-s are treated counterintuitively
        max_residual = abs(max(residuals, key=abs))
        # TODO If fails, give the violated constraint name
        assertLess(max_residual, 1.0e-6, \
                                   'Large constraint violation\n%s' % residuals)
        print('PASSED:', dag_file)
    #read_problem('../data/ex9_2_8.txt', crosscheck_sparsity_nl=False)

