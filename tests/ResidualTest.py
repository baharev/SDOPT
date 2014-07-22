from __future__ import print_function
import unittest
from coconut_parser.dag_parser import read_problem
from StringIO import StringIO
from util.redirect_stdout import redirect_stdout

# http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
def importCode(code, name):
    import imp
    module = imp.new_module(name)
    exec code in module.__dict__
    return module

# TODO Properly assert nvars == ncons
preamble = \
'''
from math import exp

def eval(v):
    con = [ float('NaN') ] * len(v)

'''

postamble = '    return con\n'

# FIXME Move code generation code to pprinter, where it belongs
def prepare_evaluation_code(f):
    problem = read_problem(f, to_plot=False)
    code = StringIO()
    code.write(preamble)
    for line in get_constraint_evaluation_py_code(problem):
        code.write(line)
    code.write(postamble)
    res = code.getvalue()
    code.close() # FIXME make it with with statement
    return problem, res

def get_constraint_evaluation_py_code(p):
    ostream = StringIO()
    with redirect_stdout(ostream):
        p.pprint_constraints()
    # prepend indentation, keep line ends
    code = ['    %s' % l for l in ostream.getvalue().splitlines(True)]
    ostream.close() # FIXME make it with with statement
    return code

class ResidualTest(unittest.TestCase):

    def test_files(self):
        files = [ '/home/ali/pyton-ws/sparse-matrix-computations/dag/JacobsenDbg.dag' ]
        for f in files:
            problem, code = prepare_evaluation_code(f)
            # TODO Does the name matter?
            m = importCode(code, 'twistedResidualTest')
            cons = m.eval(problem.refsols[0])
            # print(cons)
            maxResidual = abs(max(iter(cons), key=abs))
            # TODO If fails, give the violated constraint name
            self.assertLess(maxResidual, 1.0e-6, \
                            'Large constraint violation\n%s' % cons)

#if __name__ == '__main__':
#    unittest.main()
