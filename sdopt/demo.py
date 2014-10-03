from __future__ import print_function
from os.path import join
from .parsers.dag_parser import read_problem
from .datagen.paths import DATADIR

def run():
    read_problem(join(DATADIR, 'JacobsenDbg.dag'))
    print()
    read_problem(join(DATADIR, 'ex9_2_8.txt'), crosscheck_nl=False)
