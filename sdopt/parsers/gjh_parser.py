from __future__ import print_function
from os.path import dirname, join
import numpy as np
import scipy.sparse as sp
from ..util.file_reader import lines_of
from ..util.misc import advance, nth, skip_until

def read(logfilename):
    x, residuals, nonzeros, name = read_log(logfilename)
    jac = read_gjh(join(dirname(logfilename), name), nonzeros)
    print('Jacobian:\n%s' % jac)
    return x, residuals, jac
    
def read_log(filename):
    with lines_of(filename) as lines:
        # Read problem statistics first: rows, cols, nonzeros
        itr = skip_until(lambda s: s=='@@@ Problem statistics', lines)
        itr = advance(itr, 1)
        data = next(itr).split()
        ncons, nvars, nonzeros = (int(data[i]) for i in (1, 3, 5))
        # Read the variables 
        itr = advance(itr, 1) # skip line 'Variable vector:'
        x = np.fromiter(itr, np.float64, nvars)
        # Skip two lines, an empty one and 'Residual vector:'
        itr = advance(lines, 2)
        residuals = np.fromiter(itr, np.float64, ncons)
        # Read the name of the gjh file containing the Jacobian
        name = read_gjh_filename(lines)
    return x, residuals, nonzeros, name

def read_gjh_filename(lines):
    # <newline> gjh: "/tmp/at3464.gjh" written.  Execute
    s = nth(lines, 1)
    beg = s.find('\"') + 1
    end = s.rfind('\"')
    return s[beg:end]

def read_gjh(filename, nonzeros):
    with lines_of(filename) as lines:
        return parse(lines, nonzeros)

def parse(lines, nonzeros):
    # Construct the Jacobian in coordinate format
    ai, aj = np.zeros(nonzeros,np.int32), np.zeros(nonzeros,np.int32)
    ra, k  = np.zeros(nonzeros, np.float64), 0
    nrows, ncols = get_J_shape(lines)
    lines_from_first_row = skip_until(lambda s: s.startswith('['), lines) 
    for line in lines_from_first_row:
        if line[0]=='[':
            # has hit a new row: [12,*]
            comma = line.find(',')
            row = int(line[1:comma])-1
        elif line[0] == '\t':
            # data in row: <tab> col index <tab> entry
            col_idx, data = line.split()
            col, data = int(col_idx)-1, float(data)
            ai[k], aj[k], ra[k] = row, col, data
            k += 1
        else:
            break
    return sp.coo_matrix((ra, (ai,aj)), shape=(nrows,ncols))

def get_J_shape(lines):
    # It's on the 3rd line, something like: 
    # param J{1..16, 1..16} default 0;
    line = nth(lines, 3)
    after_1st_dotdot = line.find('..') + 2
    comma = line.find(',')
    nrows = int(line[after_1st_dotdot:comma])
    after_2nd_dotdot = line.find('..', comma) + 2
    closing_bracket = line.find('}')
    ncols = int(line[after_2nd_dotdot:closing_bracket])
    print('Shape: %dx%d' % (nrows, ncols))
    return nrows, ncols
