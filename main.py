from __future__ import print_function
from coconut_parser.dag_parser import read_problem

if __name__ == '__main__':
    read_problem('./dag/JacobsenDbg.dag')
    print()
    read_problem('./dag/ex9_2_8.txt')
