from __future__ import print_function
import fileinput
import numpy as np
from itertools import islice
from representation.block_sparsity_pattern import BlockSparsityPattern

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
    vars_in_row = index_value['index']  # nonlinearity information discarded
    assert row==len(bsp.jacobian), row
    bsp.jacobian.append(np.array(vars_in_row, np.int32))

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
    count = np.zeros(bsp.ncols, np.int32)
    for cols in bsp.jacobian:
        count[cols] += 1
    accum = np.add.accumulate(count) 
    assert np.all(accum[:-1] == bsp.col_len)
    assert accum[-1] == bsp.nzeros        

def extract_line_with_first_char(iterable):
    for line in iterable:
        yield line[0], line

def parse(f):
    bsp = BlockSparsityPattern(get_problem_name(f), *extract_problem_info(f))
    segments = { 'J': J_segment,
                 'k': k_segment,
                 'S': S_segment }
    for first_char, line in extract_line_with_first_char(f):
        func = segments.get(first_char)
        if func:
            func(bsp, f, line)
    check_J_segment(bsp)
    print('Finished reading the nl file')            
    #dbg_info(bsp)
    return bsp

def dbg_info(bsp):
    print('Problem name:', bsp.name)
    print('k segment')
    print(bsp.col_len)
    print('J segment, sparsity pattern')
    dbg_show_jacobian(bsp.jacobian)
    print('row S segments')
    dbg_show_S_segm(bsp.row_suffixes)
    print('col S segments')    
    dbg_show_S_segm(bsp.col_suffixes)

def dbg_show_jacobian(sparse_mat):
    for i, arr in enumerate(sparse_mat):
        print('%d: %s' % (i, pretty_str_numpy_array(arr)))

def dbg_show_S_segm(suffix_dict):
    for name, index_value in sorted(suffix_dict.iteritems()):
        print( '  %s: %s' % (name, pretty_str_numpy_array(index_value)) )

def pretty_str_numpy_array(arr):
    col_ind = str(arr)
    beg = col_ind.find('[')+1
    end = col_ind.rfind(']')
    return col_ind[beg:end]

def lines_with_newline_chars_removed(iterable):
    for line in iterable:
        yield line.rstrip()

def read_flattened_ampl(filename):
    print('Reading \'%s\'' % filename)
    try:
        f = fileinput.input(filename, mode='r')
        return parse(lines_with_newline_chars_removed(f))
    finally:
        print('Read', f.lineno(), 'lines')
        f.close()

if __name__ == '__main__':
    read_flattened_ampl('../dag/Luyben.nl')
    read_flattened_ampl('../dag/suffix.nl')
    read_flattened_ampl('../dag/JacobsenDbg.nl')
    read_flattened_ampl('../dag/mssTornDbg.nl')
