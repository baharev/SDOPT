from __future__ import print_function
import fileinput
import numpy as np
from itertools import islice

def check_if_text_format(first_line):
    if not first_line.startswith('g'):
        print('First line: \'%s\'' % first_line)
        msg = 'only ASCII format files can be parsed (give flag g to AMPL)'
        raise RuntimeError(msg)

def extract_length(line):
    # 'k42 <arbitrary text>' -> 42
    l = line.split()
    return int(l[0][1:])

def extract_id_len(line):
    # 'J5 2 <arbitrary text>' -> id=5, len=2
    l = line.split()
    return int(l[0][1:]), int(l[1])

def extract_id_len_name(line):
    # 'S1 20 blockid <arbitrary text>' -> id=1, len=20, name=blockid
    l = line.split()
    return int(l[0][1:]), int(l[1]), l[2]

def extract_index_value(iterable, length):
    # '3 42.8' -> '3', '42.8'
    for line in islice(iterable, length):
        # index, value = line.strip().split()
        yield tuple(line.strip().split())

def numpy_index_value(iterable, length, value_type):
    dtype = [('index', np.int32), ('value', value_type)]
    return np.fromiter(extract_index_value(iterable, length), dtype)

class J_segment():
    # J5 2
    # 1 1   ->  5: [1, 3], linearity info currently discarded
    # 3 1
    def __init__(self):
        self.jacobian = [ ]
    def __call__(self, iterable, line):
        row, length = extract_id_len(line)
        index_value = numpy_index_value(iterable, length, value_type=np.float64)  
        vars_in_row = index_value['index']  # nonlinearity information discarded
        assert row==len(self.jacobian), row
        self.jacobian.append(np.array(vars_in_row, np.int32))

class k_segment():
    def __call__(self, iterable, line):
        length = extract_length(line)
        self.col_len = np.fromiter(iterable, np.int32, length)

class S_segment():
    def __init__(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols
        self.rows = { }
        self.cols = { }
    def __call__(self, iterable, line):
        kind, length, name = extract_id_len_name(line)
        key_value = numpy_index_value(iterable, length)
        keys = key_value[:,0]
        assert np.all(keys==np.arange(keys.size)),'Unexpected input:\n%s' % keys
        # magic numbers from AMPL doc
        suffixes = { 0: self.cols, 1: self.rows }.get(kind, { })
        suffixes.update( {name: np.array(key_value[:,1]) } )

def extract_problem_info(second_line):
    data = second_line.split()
    nrows = data[1] # These magic numbers come from the AMPL doc
    ncols = data[0]
    neqns = data[4]
    if nrows!=neqns:
        print('WARNING: Not all constraints are equality constraints!')
    return nrows, ncols

def parse(f):
    check_if_text_format(next(f))
    nrows, ncols = extract_problem_info(next(f).strip())
    segments = { 'J': J_segment(),
                 'k': k_segment(),
                 'S': S_segment(nrows, ncols) }
    for line in f:
        first_char = line[0]
        func = segments.get(first_char)
        if func:
            func(f, line)
    print('Finished reading the nl file')
    print('k segment')
    print(segments['k'].col_len)
    print('J segment, sparsity pattern')
    dbg_show_jacobian(segments['J'].jacobian)
    print('row S segments')
    print(segments['S'].rows)
    print('col S segments')    
    print(segments['S'].cols)
    return segments['J'].jacobian, segments['k'].col_len

def dbg_show_jacobian(sparse_mat):
    for i, arr in enumerate(sparse_mat):
        # pretty print numpy array
        col_ind = str(arr)
        beg = col_ind.find('[')+1
        end = col_ind.rfind(']')
        print('%d: %s' % (i, col_ind[beg:end]))

def read_flattened_ampl(filename):
    try:
        f = fileinput.input(filename, mode='r')
        return parse(f)
    finally:
        print('Read', f.lineno(), 'lines')
        f.close()

if __name__ == '__main__':
    read_flattened_ampl('../dag/Luyben.nl')
