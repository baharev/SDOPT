'''
Use only read_flattened_ampl, ignore all other functions.
'''
from __future__ import print_function
from itertools import islice
import numpy as np
import scipy.sparse as sp
import ordering.block_sparsity_pattern as bs
import ordering.sparse_plot as splot
from util.file_reader import lines_of
from util.assert_helpers import assertEqual
import ordering.csr_utils as util

def read_flattened_ampl(filename):
    bsp = read_nl(filename)
    bsp.csr_mat = sp.csr_matrix((bsp.csr_data, bsp.csr_indices, bsp.csr_indptr), 
                                 shape=(bsp.nrows,bsp.ncols) ) 
    check_J_segment(bsp)
    dbg_info(bsp)
    has_blocks = bs.set_permutation_with_block_boundaries(bsp)
    bsp.row_names = read_names(filename, 'row', bsp.nrows)
    bsp.col_names = read_names(filename, 'col', bsp.ncols)
    splot.plot(bsp, plot_permuted=False)
    if has_blocks:
        splot.plot(bsp, plot_permuted=True)
    return bsp

def read_nl(filename):
    with lines_of(filename) as lines:
        return parse(lines)

def read_names(filename, kind, count):
    with lines_of(filename[:-2] + kind) as lines:
        names = [line for line in lines]
    assertEqual(len(names), count)
    return names

def parse(f):
    bsp = bs.BlockSparsityPattern(get_problem_name(f), *extract_problem_info(f))
    segments = { 'J': J_segment,
                 'k': k_segment,
                 'S': S_segment }
    for first_char, line in extract_line_with_first_char(f):
        func = segments.get(first_char)
        if func:
            func(bsp, f, line)
    return bsp

def get_problem_name(iterable):
    first_line = next(iterable)
    check_if_text_format(first_line)
    return first_line.split()[-1] # name: last word on first line

def check_if_text_format(first_line):
    if not first_line.startswith('g'):
        print('First line: \'%s\'' % first_line)
        msg = 'only ASCII format files can be parsed (give flag g to AMPL)'
        raise RuntimeError(msg)

def nth(iterable, n, default=None):
    'Returns the nth item or a default value'
    return next(islice(iterable, n, None), default)

def extract_problem_info(iterable_lines):
    second_line = next(iterable_lines)
    data = second_line.split()
    # Magic numbers come from the AMPL doc
    nrows, ncols, neqns = data[1], data[0], data[4]  
    if nrows!=neqns:
        print('WARNING: Not all constraints are equality constraints!')
    eight_line = nth(iterable_lines, 5)
    nzeros = eight_line.split()[0]
    return int(nrows), int(ncols), int(nzeros)

def extract_line_with_first_char(iterable):
    for line in iterable:
        yield line[0], line

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
        # index, value = line.split()
        yield tuple(line.split())

def numpy_index_value(iterable, length, value_type):
    dtype = [('index', np.int32), ('value', value_type)]
    return np.fromiter(extract_index_value(iterable, length), dtype)

def J_segment(bsp, iterable, line):
    # J5 2
    # 1 1   ->  5: [1, 3], linearity info currently discarded
    # 3 1
    row, length = extract_id_len(line)
    index_value = numpy_index_value(iterable, length, value_type=np.float64)  
    # The expected order of the J segments is 0, 1, 2 ..., nrows
    assertEqual(bsp.dbg_prev_row+1, row)
    slc = slice(bsp.csr_pos, bsp.csr_pos + length)
    bsp.csr_indices[slc] = index_value['index']  
    bsp.csr_data[slc]    = index_value['value']
    bsp.csr_indptr[row+1]= bsp.csr_pos + length
    bsp.csr_pos += length
    bsp.dbg_prev_row = row

def k_segment(bsp, iterable, line):
    length = extract_length(line)
    bsp.col_len = np.fromiter(iterable, np.int32, length)

def S_segment(bsp, iterable, line):
    kind, length, name = extract_id_len_name(line)
    # magic numbers from AMPL doc
    suff_type = kind & 3 #  0: col;  1: row;  2: obj;  3: problem
    value_type = np.float64 if kind & 4 else np.int32
    index_value = numpy_index_value(iterable, length, value_type)
    suffixes = { 0: bsp.col_suffixes, 1: bsp.row_suffixes }.get(suff_type, { })
    suffixes[name] = index_value

def check_J_segment(bsp):
    assertEqual(bsp.nrows, bsp.csr_mat.shape[0])
    assertEqual(bsp.ncols, bsp.csr_mat.shape[1])
    count = np.zeros(bsp.ncols, np.int32)
    for cols in util.itr_col_indices(bsp.csr_mat):
        count[cols] += 1
    accum = np.add.accumulate(count) 
    assert np.all(accum[:-1] == bsp.col_len)
    assertEqual(accum[-1], bsp.nzeros)

def dbg_info(bsp):
    print('Problem name:', bsp.name)
    print('k segment')
    print(bsp.col_len)
    print('J segment, sparsity pattern')
    dbg_show_jacobian(bsp.csr_mat)
    print('row S segments')
    dbg_show_S_segm(bsp.row_suffixes)
    print('col S segments')    
    dbg_show_S_segm(bsp.col_suffixes)

def dbg_show_jacobian(m):
    for r, cols in util.itr_col_indices_by_row(m):
        print('%d: %s' % (r, cols))

def dbg_show_S_segm(suffix_dict):
    for name, index_value in sorted(suffix_dict.iteritems()):
        print( '  %s: %s' % (name, index_value) )

if __name__ == '__main__':
    read_flattened_ampl('../data/Luyben.nl')
    read_flattened_ampl('../data/suffix.nl')
    read_flattened_ampl('../data/JacobsenDbg.nl')
    read_flattened_ampl('../data/mssTornDbg.nl')
