from __future__ import print_function
from contextlib import contextmanager
import fileinput

def lines_with_newline_chars_removed(iterable):
    for line in iterable:
        yield line.rstrip()

@contextmanager
def lines_of(filename):
    print('Trying to read file \"%s\"' % filename)
    try:
        f = fileinput.input(filename, mode='r')
        yield lines_with_newline_chars_removed(f)
    finally:
        print('Read ',f.lineno(),' lines from file \"',filename,'\"', sep='')
        f.close()
