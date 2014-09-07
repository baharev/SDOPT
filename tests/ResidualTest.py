from __future__ import print_function
import unittest
import os
from coconut_parser.dag_parser import read_problem
import nodes.pprinter as pprinter
from util.misc import import_code

def dag_files():
    test_dir = '../data/'
    #
    #test_cases = ['JacobsenDbg', 'mssTornDbg', 'Luyben', 'eco9', 'bratu',
    #              'tunnelDiodes', 'mss20heatBalance' ]
    test_cases = sorted(f for f in os.listdir(test_dir) if f.endswith('.dag'))
    #test_cases = ['JacobsenTorn.dag']
    return [ '{dir}{filename}'.format(dir=test_dir, filename=basename) \
               for basename in test_cases ]

class ResidualTest(unittest.TestCase):

    def test_files(self):
        for dag_file in dag_files():
            problem = read_problem(dag_file, plot_dag=False, show_sparsity=False)
            residual_code = pprinter.prepare_evaluation_code(problem)
            # Dumps the debug code being executed
            # pprinter.dbg_dump_code(residual_code, problem.refsols[0])
            # TODO Does the fake module name twistedResidualTest matter?
            f = import_code(residual_code, 'twistedResidualTest')
            residuals = f.eval(problem.refsols[0])
            # print(residuals)
            # FIXME Use NumPy? NaN-s are treated in counterintuitively
            max_residual = abs(max(residuals, key=abs))
            # TODO If fails, give the violated constraint name
            self.assertLess(max_residual, 1.0e-6, \
                            'Large constraint violation\n%s' % residuals)
            print('PASSED:', dag_file)
        #read_problem('../data/ex9_2_8.txt', crosscheck_sparsity_nl=False)

#if __name__ == '__main__':
#    unittest.main()
