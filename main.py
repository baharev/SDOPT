from __future__ import print_function
from parsers.dag_parser import read_problem
from os.path import join

if __name__ == '__main__':
    read_problem(join('data', 'JacobsenDbg.dag'))
    print()
    read_problem(join('data', 'ex9_2_8.txt'), crosscheck_nl=False)
