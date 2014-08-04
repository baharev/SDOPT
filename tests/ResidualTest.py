from __future__ import print_function
import unittest
from coconut_parser.dag_parser import read_problem
from nodes.pprinter import prepare_evaluation_code

# http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
def import_code(code, name):
    import imp
    module = imp.new_module(name)
    exec code in module.__dict__
    return module


def gen_testfiles():
    test_dir = '/home/ali/pyton-ws/sparse-matrix-computations/dag/'
    # 
    test_cases = ['JacobsenDbg', 'mssTornDbg', 'Luyben', 'eco9', 'bratu',
                  'tunnelDiodes', 'mss20heatBalance' ]
    for basename in test_cases:
        yield '{dir}{filename}.dag'.format(dir=test_dir, filename=basename)

class ResidualTest(unittest.TestCase):

    def test_files(self):
        for dag_file in gen_testfiles():
            problem = read_problem(dag_file, to_plot=False)
            residual_code = prepare_evaluation_code(problem)
            # Dumps the debug code being executed
            # pprinter.dbg_dump_code(residual_code, problem.refsols[0])
            # TODO Does the fake module name twistedResidualTest matter?
            f = import_code(residual_code, 'twistedResidualTest')
            residuals = f.eval(problem.refsols[0])
            # print(residuals)
            max_residual = abs(max(residuals, key=abs))
            # TODO If fails, give the violated constraint name
            self.assertLess(max_residual, 1.0e-6, \
                            'Large constraint violation\n%s' % residuals)
            print('PASSED:', dag_file)
        #read_problem('/home/ali/pyton-ws/sparse-matrix-computations/dag/ex9_2_8.dag')

#if __name__ == '__main__':
#    unittest.main()
