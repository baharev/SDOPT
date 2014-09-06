from __future__ import print_function
from os.path import dirname, join
import numpy as np
import scipy.sparse as sp
from util.file_reader import lines_of
from util.misc import advance, nth, skip_until

def read(logfilename):
    x, residuals, name = read_log(logfilename)
    jac = read_gjh(join(dirname(logfilename), name))
    return x, residuals, jac
    
def read_log(filename):
    with lines_of(filename) as lines:
        # Read the variables
        itr = skip_until(lambda s: s=='@@@ Variable vector', lines)
        itr = advance(itr, 1)
        nvars = read_one_int(itr) 
        x = np.fromiter(itr, np.float64, nvars)
        # Skip two lines, an empty one and '@@@ Residual vector'
        itr = advance(lines, 2)
        # Read the residuals
        ncons = read_one_int(itr)
        residuals = np.fromiter(itr, np.float64, ncons)
        # Read the gjh file name
        # <newline> gjh: "/tmp/at3464.gjh" written.  Execute
        s = nth(lines, 1)
        beg = s.find('\"') + 1
        end = s.rfind('\"')
        name = s[beg:end]
    return x, residuals, name
        
def read_one_int(itr):
    return int(next(itr))

def read_gjh(filename):
    with lines_of(filename) as lines:
        return parse(lines)

def parse(lines):
    nrows, ncols = get_J_shape(lines)
    jac = sp.dok_matrix((nrows,ncols), dtype=np.float64)
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
            jac[row,col] = data
        else:
            break
    print('Jacobian:\n%s' % jac.tocsr())
    return jac

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

if __name__=='__main__':
    read('/home/ali/ampl/log.txt')
