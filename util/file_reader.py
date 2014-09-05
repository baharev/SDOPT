from __future__ import print_function
from contextlib import contextmanager
import fileinput

def rstripped_lines(iterable):
    for line in iterable:
        yield line.rstrip()

@contextmanager
def lines_of(filename):
    print('Trying to read file \"%s\"' % filename)
    try:
        f = fileinput.input(filename, mode='r')
        yield rstripped_lines(f)
    finally:
        print('Read ',f.lineno(),' lines from file \"',filename,'\"', sep='')
        f.close()
